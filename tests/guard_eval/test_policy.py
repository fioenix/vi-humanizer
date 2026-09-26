import copy
import unittest

from guard_eval.config import load_evaluation_config
from guard_eval.corpus import case_fingerprint, validate_manifest
from guard_eval.models import (
    CheckStatus, DecisionPolicy, EditDecision, EvaluationRun, GuardAction,
    GuardDimension, JudgmentSet, NaturalnessReason, RunStatus, Split,
)
from guard_eval.policy import PolicyError, apply_policy, fit_policy, guard_action
from guard_eval.questions import question_set_version


def policy_fixture(corpus, config):
    return DecisionPolicy(
        policy_version=None, corpus_version_fitted=corpus.corpus_version,
        config_version=config.config_version, question_set_version=config.question_set_version,
        model_version=config.model_version,
        needs_edit_thresholds={reason: 0.6 for reason in NaturalnessReason},
        preference_confidence_threshold=0.7, preference_margin_threshold=0.2,
        safety_review_threshold=0.5, safety_reject_threshold=0.8,
        selection_order=["need_to_edit_recall", "candidate_choice_accuracy", "error_rates", "review_rate", "conservative_thresholds"],
        created_at="2026-09-26T00:00:00Z",
    )


def judgment_for(case, *, choice=None, naturalness=0.9, safety=0.1, confidence=0.9):
    options = ["keep_original", *[f"candidate:{c.candidate_id}" for c in case.candidates], "none_of_candidates"]
    choice = choice or (f"candidate:{case.candidates[0].candidate_id}")
    rest = (1 - confidence) / (len(options) - 1)
    probabilities = {option: (confidence if option == choice else rest) for option in options}
    return JudgmentSet(
        case_id=case.case_id, case_fingerprint=case_fingerprint(case), status=CheckStatus.CHECKED,
        naturalness_scores={reason: naturalness for reason in NaturalnessReason},
        preference_probabilities=probabilities, preference_choice=choice, preference_confidence=confidence,
        candidate_safety_scores={candidate.candidate_id: {dimension: safety for dimension in GuardDimension} for candidate in case.candidates},
        latency_ms=10, input_tokens=100, output_tokens=10, model_version="jev-1.13.0",
    )


def run_for(cases, corpus, config, *, split=Split.DEV, status=RunStatus.COMPLETE):
    judgments = [judgment_for(case, choice=case.expected_preferred_option if case.expected_preferred_option != "keep_original" else "keep_original", naturalness=0.9 if case.expected_needs_edit else 0.1) for case in cases]
    for case, judgment in zip(cases, judgments):
        for candidate in case.candidates:
            for dimension, expected in candidate.expected_dimensions.items():
                judgment.candidate_safety_scores[candidate.candidate_id][dimension] = 0.9 if expected else 0.1
    return EvaluationRun(
        run_id="run", started_at="2026-09-26T00:00:00Z", completed_at="2026-09-26T00:00:01Z",
        split=split, corpus_version=corpus.corpus_version, config_version=config.config_version,
        question_set_version=config.question_set_version, requested_model=config.model_version,
        observed_models=[config.model_version], policy_version=None, pricing_version=None,
        run_status=status, counts={"total": len(cases), "checked": len(cases), "unchecked": 0, "unchecked_by_reason": {}}, judgments=judgments,
    )


class PolicyContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = validate_manifest("eval/guard/manifest.json")
        cls.config = load_evaluation_config("eval/guard/evaluation-config.json")
        cls.policy = policy_fixture(cls.corpus, cls.config)

    def test_guard_action_uses_max_dimension_and_ordered_thresholds(self):
        case = self.corpus.dev[0]
        judgment = judgment_for(case, safety=0.1)
        self.assertEqual(guard_action(judgment, case.candidates[0].candidate_id, self.policy), GuardAction.PASS)
        judgment.candidate_safety_scores[case.candidates[0].candidate_id][GuardDimension.ADDS_CLAIM] = 0.6
        self.assertEqual(guard_action(judgment, case.candidates[0].candidate_id, self.policy), GuardAction.REVIEW)
        judgment.candidate_safety_scores[case.candidates[0].candidate_id][GuardDimension.ADDS_CLAIM] = 0.9
        self.assertEqual(guard_action(judgment, case.candidates[0].candidate_id, self.policy), GuardAction.REJECT)

    def test_routes_keep_replace_and_none_to_review_without_new_text(self):
        positive = self.corpus.dev[0]
        replace = apply_policy(positive, judgment_for(positive), self.policy)
        self.assertEqual((replace.edit_decision, replace.selected_candidate_id), (EditDecision.REPLACE, positive.candidates[0].candidate_id))
        negative = self.corpus.dev[2]
        keep = apply_policy(negative, judgment_for(negative, choice="keep_original", naturalness=0.1), self.policy)
        self.assertEqual((keep.edit_decision, keep.selected_candidate_id), (EditDecision.KEEP, None))
        none = self.corpus.dev[3]
        review = apply_policy(none, judgment_for(none, choice="none_of_candidates"), self.policy)
        self.assertEqual((review.edit_decision, review.selected_candidate_id), (EditDecision.REVIEW, None))

    def test_low_choice_margin_or_unsafe_candidate_routes_review(self):
        case = self.corpus.dev[0]
        low = judgment_for(case, confidence=0.55)
        self.assertEqual(apply_policy(case, low, self.policy).edit_decision, EditDecision.REVIEW)
        unsafe = judgment_for(case, safety=0.9)
        self.assertEqual(apply_policy(case, unsafe, self.policy).edit_decision, EditDecision.REVIEW)

    def test_fit_is_deterministic_and_rejects_holdout_or_incomplete(self):
        run = run_for(self.corpus.dev, self.corpus, self.config)
        first = fit_policy(self.corpus.dev, run)
        second = fit_policy(list(reversed(self.corpus.dev)), copy.deepcopy(run))
        self.assertEqual(first.policy_version, second.policy_version)
        with self.assertRaises(PolicyError):
            fit_policy(self.corpus.holdout, run_for(self.corpus.holdout, self.corpus, self.config, split=Split.HOLDOUT))
        with self.assertRaises(PolicyError):
            fit_policy(self.corpus.dev, run_for(self.corpus.dev, self.corpus, self.config, status=RunStatus.INCOMPLETE))

    def test_fit_does_not_reduce_review_rate_by_replacing_an_unacceptable_candidate(self):
        run = run_for(self.corpus.dev, self.corpus, self.config)
        none_case = next(case for case in self.corpus.dev if case.expected_preferred_option == "none_of_candidates")
        wrong_choice = judgment_for(
            none_case,
            choice=f"candidate:{none_case.candidates[0].candidate_id}",
            confidence=0.51,
        )
        run.judgments = [wrong_choice if item.case_id == none_case.case_id else item for item in run.judgments]

        fitted = fit_policy(self.corpus.dev, run)
        decisions = {
            case.case_id: apply_policy(case, next(item for item in run.judgments if item.case_id == case.case_id), fitted)
            for case in self.corpus.dev
        }

        self.assertEqual(decisions[none_case.case_id].edit_decision, EditDecision.REVIEW)
        for case in self.corpus.dev:
            if case is not none_case:
                self.assertEqual(decisions[case.case_id].edit_decision, case.expected_edit_decision)


if __name__ == "__main__":
    unittest.main()
