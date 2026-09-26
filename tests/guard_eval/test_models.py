import unittest

from guard_eval.models import (
    ALLOWED_REASON_CODES,
    CandidateEdit,
    CandidateOriginKind,
    CheckStatus,
    DecisionPolicy,
    EditDecision,
    EvaluationCase,
    EvaluationRun,
    GuardAction,
    GuardDimension,
    JudgmentSet,
    NaturalnessReason,
    RunStatus,
    Split,
    ValidationError,
    to_jsonable,
)


class ModelContractTests(unittest.TestCase):
    def test_enum_values_match_contract(self):
        self.assertEqual({item.value for item in NaturalnessReason}, {"lexically_incomplete", "unnatural_collocation"})
        self.assertEqual(len(CandidateOriginKind), 3)
        self.assertEqual(len(GuardDimension), 6)
        self.assertEqual({item.value for item in GuardAction}, {"pass", "review", "reject"})
        self.assertEqual({item.value for item in EditDecision}, {"keep", "replace", "review"})
        self.assertEqual({item.value for item in CheckStatus}, {"checked", "unchecked"})
        self.assertEqual({item.value for item in RunStatus}, {"complete", "incomplete", "invalid"})

    def test_checked_judgment_requires_all_scores(self):
        with self.assertRaises(ValidationError):
            JudgmentSet(case_id="case", case_fingerprint="sha256:" + "a" * 64, status=CheckStatus.CHECKED).validate(["candidate:c1"])

    def test_unchecked_judgment_has_allowlisted_reason_and_no_scores(self):
        judgment = JudgmentSet(
            case_id="case",
            case_fingerprint="sha256:" + "a" * 64,
            status=CheckStatus.UNCHECKED,
            reason_code="timeout",
        )
        judgment.validate(["candidate:c1"])
        self.assertIn(judgment.reason_code, ALLOWED_REASON_CODES)
        judgment.naturalness_scores = {NaturalnessReason.LEXICALLY_INCOMPLETE: 0.1}
        with self.assertRaises(ValidationError):
            judgment.validate(["candidate:c1"])

    def test_policy_reject_threshold_cannot_precede_review(self):
        policy = DecisionPolicy(
            policy_version=None,
            corpus_version_fitted="sha256:" + "a" * 64,
            config_version="sha256:" + "b" * 64,
            question_set_version="sha256:" + "c" * 64,
            model_version="jev-1.13.0",
            needs_edit_thresholds={reason: 0.5 for reason in NaturalnessReason},
            preference_confidence_threshold=0.7,
            preference_margin_threshold=0.2,
            safety_review_threshold=0.8,
            safety_reject_threshold=0.6,
            selection_order=["need_to_edit_recall"],
            created_at="2026-09-26T00:00:00Z",
        )
        with self.assertRaises(ValidationError):
            policy.validate()

    def test_policy_thresholds_must_be_probabilities(self):
        policy = DecisionPolicy(
            policy_version=None,
            corpus_version_fitted="sha256:" + "a" * 64,
            config_version="sha256:" + "b" * 64,
            question_set_version="sha256:" + "c" * 64,
            model_version="jev-1.13.0",
            needs_edit_thresholds={reason: 1.1 for reason in NaturalnessReason},
            preference_confidence_threshold=0.7,
            preference_margin_threshold=0.2,
            safety_review_threshold=0.6,
            safety_reject_threshold=0.8,
            selection_order=["need_to_edit_recall"],
            created_at="2026-09-26T00:00:00Z",
        )
        with self.assertRaises(ValidationError):
            policy.validate()

    def test_candidate_and_case_required_fields_are_explicit(self):
        candidate = CandidateEdit.from_dict({
            "candidate_id": "c1",
            "candidate_span": "đầy đủ",
            "candidate_origin": {"kind": "maintainer_fixture", "reference": "SKILL.md#V20", "authority": "maintainer"},
            "expected_dimensions": {dimension.value: False for dimension in GuardDimension},
            "expected_guard_action": "pass",
        })
        case = EvaluationCase.from_dict({
            "case_id": "full-word",
            "split": "dev",
            "source_span": "đầy",
            "candidates": [to_jsonable(candidate)],
            "context_before": "",
            "context_after": "",
            "current_intent": "Làm câu tự nhiên hơn",
            "genre": "blog-ca-nhan",
            "inseparable_edit_ids": [],
            "expected_needs_edit": True,
            "expected_naturalness_reasons": ["lexically_incomplete"],
            "expected_preferred_option": "candidate:c1",
            "expected_edit_decision": "replace",
            "label_source": {"kind": "review", "authority": "maintainer", "reference": "SKILL.md#V20"},
            "pattern_refs": ["V20"],
            "baseline": {"edit_decision": "replace", "selected_candidate_id": "c1", "guard_action": "pass", "version": "vi-humanizer-0.7.1", "reference": "SKILL.md", "authority": "maintainer"},
            "provenance": {"path": "SKILL.md", "section": "V20"},
        })
        self.assertEqual(case.split, Split.DEV)
        self.assertEqual(case.candidates[0].expected_guard_action, GuardAction.PASS)

    def test_raw_run_versions_are_nullable(self):
        run = EvaluationRun(
            run_id="run-1", started_at="2026-09-26T00:00:00Z", completed_at="2026-09-26T00:00:01Z",
            split=Split.DEV, corpus_version="sha256:" + "a" * 64, config_version="sha256:" + "b" * 64,
            question_set_version="sha256:" + "c" * 64, requested_model="jev-1.13.0", observed_models=[],
            policy_version=None, pricing_version=None, run_status=RunStatus.INCOMPLETE,
            counts={"total": 0, "checked": 0, "unchecked": 0, "unchecked_by_reason": {}}, judgments=[],
        )
        self.assertIsNone(to_jsonable(run)["policy_version"])


if __name__ == "__main__":
    unittest.main()
