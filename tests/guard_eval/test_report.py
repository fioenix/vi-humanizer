import copy
import json
import unittest

from guard_eval.config import load_evaluation_config, load_pricing_snapshot
from guard_eval.corpus import validate_manifest
from guard_eval.models import RunStatus, Split
from guard_eval.report import generate_report
from tests.guard_eval.test_policy import policy_fixture, run_for


class ReportContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = validate_manifest("eval/guard/manifest.json")
        cls.config = load_evaluation_config("eval/guard/evaluation-config.json")
        cls.pricing = load_pricing_snapshot("eval/guard/pricing.json", expected_model=cls.config.model_version)
        cls.policy = policy_fixture(cls.corpus, cls.config)

    def test_report_contains_metric_families_usage_cost_coverage_and_no_raw_prose(self):
        run = run_for(self.corpus.holdout, self.corpus, self.config, split=Split.HOLDOUT)
        report = generate_report(self.corpus.holdout, run, self.policy, self.pricing)
        required = {
            "need_to_edit_recall", "unnecessary_edit_rate", "candidate_choice_accuracy",
            "no_acceptable_candidate_recall", "harmful_edit_recall",
            "valid_edit_false_block_rate", "safety_false_accept_rate", "review_rate",
        }
        self.assertTrue(required <= set(report["metrics"]["baseline_metrics"]))
        self.assertTrue(required <= set(report["metrics"]["candidate_metrics"]))
        self.assertIn("latency_ms", report["metrics"]["candidate_metrics"])
        self.assertIn("estimated_cost", report["metrics"]["candidate_metrics"])
        self.assertEqual(set(report["metrics"]["by_reason"]), {"lexically_incomplete", "unnatural_collocation"})
        self.assertEqual(len(report["metrics"]["by_dimension"]), 6)
        encoded = json.dumps(report, ensure_ascii=False)
        for forbidden in ("source_span", "candidate_span", "candidate_origin", "baseline", "provenance", "request_body", "exception"):
            self.assertNotIn(f'"{forbidden}"', encoded)

    def test_invalid_and_incomplete_have_null_decision(self):
        for status in (RunStatus.INVALID, RunStatus.INCOMPLETE):
            run = run_for(self.corpus.holdout, self.corpus, self.config, split=Split.HOLDOUT, status=status)
            report = generate_report(self.corpus.holdout, run, self.policy, self.pricing)
            self.assertEqual(report["run_status"], status.value)
            self.assertIsNone(report["decision"])

    def test_zero_mandatory_denominator_collects_more_labels(self):
        only_positive = [case for case in self.corpus.holdout if case.expected_needs_edit]
        run = run_for(only_positive, self.corpus, self.config, split=Split.HOLDOUT)
        report = generate_report(only_positive, run, self.policy, self.pricing)
        self.assertEqual((report["run_status"], report["decision"]), ("complete", "collect_more_labels"))

    def test_go_no_go_stops_without_improvement_and_continues_with_safe_improvement(self):
        run = run_for(self.corpus.holdout, self.corpus, self.config, split=Split.HOLDOUT)
        stop = generate_report(self.corpus.holdout, run, self.policy, self.pricing)
        self.assertIn(stop["decision"], {"stop", "continue_shadow"})
        # Make baseline deliberately miss every expected edit while candidate judgments remain correct.
        improved_cases = copy.deepcopy(self.corpus.holdout)
        first_missed = next(case for case in improved_cases if case.expected_edit_decision.value == "replace")
        first_missed.baseline.update(edit_decision="keep", selected_candidate_id=None, guard_action=None)
        none_case = next(case for case in improved_cases if case.expected_preferred_option == "none_of_candidates")
        none_case.baseline.update(edit_decision="keep", selected_candidate_id=None, guard_action=None)
        improved = generate_report(improved_cases, run_for(improved_cases, self.corpus, self.config, split=Split.HOLDOUT), self.policy, self.pricing)
        self.assertEqual(improved["decision"], "continue_shadow")


if __name__ == "__main__":
    unittest.main()
