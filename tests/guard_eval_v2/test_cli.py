from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from guard_eval.v2.cli import (
    _dev_approval,
    _validate_approval,
    _v1_authorization_expected,
    build_parser,
    main,
)
from guard_eval.v2.config import load_evaluation_config
from guard_eval.v2.corpus import (
    ValidatedCorpusV2, case_fingerprint, case_set_digest, file_digest, project_case_to_v1,
    validate_dev_manifest,
)
from guard_eval.v2.evaluator import evaluate_absolute_cases
from guard_eval.v2.models import (
    AbsoluteJudgmentV2,
    CandidateAssessment,
    CandidateComponent,
    CaseJudgmentV2,
    CheckStatus,
    RecommendationKind,
    RecommendationCaseV2,
    RecommendationRunV2,
    JudgmentRunV2,
    PolicyRecommendationV2,
    RankingJudgmentV2,
    RunStatus,
    SafetyDimension,
    SourceIssue,
    Split,
    canonical_digest,
    recommendation_run_digest,
    judgment_run_digest,
    to_jsonable,
)
from guard_eval.v2.policy import RecommendationPolicyV2, apply_policy_run, policy_version
from tests.guard_eval_v2.helpers import case_dict
from guard_eval.models import (
    CheckStatus as V1CheckStatus,
    EvaluationRun as V1EvaluationRun,
    JudgmentSet as V1JudgmentSet,
    RunStatus as V1RunStatus,
    Split as V1Split,
    GuardDimension as V1GuardDimension,
    NaturalnessReason as V1NaturalnessReason,
)
from guard_eval.config import load_evaluation_config as load_v1_config
from guard_eval.corpus import case_fingerprint as v1_case_fingerprint


class CliContractTests(unittest.TestCase):
    def test_holdout_authorization_accepts_owner_authorized_agent_as_actual_actor(self) -> None:
        expected = {
            "manifest_corpus_version": "sha256:" + "a" * 64,
            "holdout_sha256": "sha256:" + "b" * 64,
            "policy_version": "sha256:" + "c" * 64,
            "config_version": "sha256:" + "d" * 64,
            "absolute_question_set_version": "sha256:" + "e" * 64,
            "ranking_question_set_version": "sha256:" + "f" * 64,
            "v1_artifact_lock_sha256": "sha256:" + "1" * 64,
            "v1_artifact_lock_digest": "sha256:" + "2" * 64,
            "v1_config_version": "sha256:" + "3" * 64,
            "v1_policy_version": "sha256:" + "4" * 64,
            "v1_question_set_version": "sha256:" + "5" * 64,
            "v1_model_version": "jev-1.13.0",
        }
        authorization = {
            "authorization_version": "1.0.0",
            "status": "approved",
            "approved_by": "owner_authorized_agent",
            "approved_at": "2026-09-28T00:00:00Z",
            **expected,
        }

        validated = _validate_approval(authorization, expected=expected)

        self.assertEqual(validated["approved_by"], "owner_authorized_agent")

    def write_dev_approval(
        self,
        path: Path,
        *,
        status: str = "approved",
        approved_by: str = "maintainer",
    ) -> None:
        corpus = validate_dev_manifest("eval/guard/v2/manifest.json")
        config = load_evaluation_config("eval/guard/v2/evaluation-config.json")
        proposal = Path("specs/002-edit-decision-gate/evidence/dev-label-proposal.json")
        data = {
            "approval_version": "1.0.0",
            "status": status,
            "approved_by": approved_by,
            "approved_at": "2026-09-27T00:00:00Z",
            "proposal_path": str(proposal),
            "proposal_sha256": file_digest(proposal),
            "dev_version": corpus.dev_version,
            "dev_sha256": corpus.manifest["dev"]["sha256"],
            "config_version": config.config_version,
            "model_version": config.model_version,
            "absolute_question_set_version": config.absolute_question_set_version,
            "ranking_question_set_version": config.ranking_question_set_version,
        }
        path.write_text(json.dumps(data), encoding="utf-8")

    def test_dev_approval_accepts_owner_authorized_agent_as_actual_actor(self) -> None:
        corpus = validate_dev_manifest("eval/guard/v2/manifest.json")
        config = load_evaluation_config("eval/guard/v2/evaluation-config.json")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dev-approval.json"
            self.write_dev_approval(path, approved_by="owner_authorized_agent")
            approval = _dev_approval(path, corpus=corpus, config=config)
        self.assertEqual(approval["approved_by"], "owner_authorized_agent")

    def run_cli(self, *args, env=None):
        return subprocess.run(
            [sys.executable, "-m", "guard_eval.v2", *args],
            text=True,
            capture_output=True,
            env={**os.environ, "PYTHONPATH": ".", **(env or {})},
        )

    def test_help_parser_lists_v2_subcommands(self) -> None:
        parser = build_parser()
        help_text = parser.format_help()
        for command in ("validate", "evaluate-dev", "fit-policy", "apply-policy", "compare", "holdout"):
            self.assertIn(command, help_text)

    def test_compare_contract_uses_recommendation_artifact_names(self) -> None:
        parser = build_parser()
        subparsers = next(action for action in parser._actions if isinstance(getattr(action, "choices", None), dict))
        help_text = subparsers.choices["compare"].format_help()
        self.assertIn("--v1-recommendations", help_text)
        self.assertIn("--v2-recommendations", help_text)
        self.assertNotIn("--v1-decisions", help_text)
        self.assertNotIn("--v2-decisions", help_text)

    def test_unknown_command_is_contract_error(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            main(["evaluate", "--split", "holdout"])
        self.assertNotEqual(raised.exception.code, 0)

    def test_validate_is_offline_and_no_key_evaluation_is_incomplete(self) -> None:
        env = {**os.environ, "PYTHONPATH": "."}
        env.pop("TYPESAFE_API_KEY", None)
        validated = subprocess.run(
            [sys.executable, "-m", "guard_eval.v2", "validate", "--manifest", "eval/guard/v2/manifest.json"],
            text=True,
            capture_output=True,
            env=env,
        )
        self.assertEqual(validated.returncode, 0, validated.stderr)
        self.assertIn("holdout=sealed", validated.stdout)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "no-key.json"
            authorization = Path(directory) / "dev-approval.json"
            self.write_dev_approval(authorization)
            evaluated = subprocess.run(
                [
                    sys.executable, "-m", "guard_eval.v2", "evaluate-dev",
                    "--manifest", "eval/guard/v2/manifest.json",
                    "--authorization", str(authorization),
                    "--config", "eval/guard/v2/evaluation-config.json",
                    "--output", str(output),
                ],
                text=True,
                capture_output=True,
                env=env,
            )
            self.assertEqual(evaluated.returncode, 2, evaluated.stderr)
            run = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(run["run_status"], "incomplete")
            self.assertEqual(run["counts"]["unchecked_by_reason"], {"missing_api_key": 9})
            self.assertIsNone(run["policy_version"])

    def test_holdout_rejects_unapproved_authorization_before_open_or_quota(self) -> None:
        corpus = validate_dev_manifest("eval/guard/v2/manifest.json")
        config = load_evaluation_config("eval/guard/v2/evaluation-config.json")
        policy = RecommendationPolicyV2.conservative_fixture(
            fitted_corpus_version=corpus.dev_version,
            config_version=config.config_version,
            absolute_question_set_version=config.absolute_question_set_version,
            ranking_question_set_version=config.ranking_question_set_version,
            model_version=config.model_version,
        )
        policy.policy_version = policy_version(policy)
        authorization = {
            "authorization_version": "1.0.0",
            "status": "draft",
            "approved_by": "maintainer",
            "approved_at": "2026-09-27T00:00:00Z",
            "manifest_corpus_version": corpus.corpus_version,
            "holdout_sha256": None,
            "policy_version": policy.policy_version,
            "config_version": config.config_version,
            "absolute_question_set_version": config.absolute_question_set_version,
            "ranking_question_set_version": config.ranking_question_set_version,
            **_v1_authorization_expected(corpus.manifest),
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            policy_path = root / "policy.json"
            auth_path = root / "authorization.json"
            policy_path.write_text(json.dumps(to_jsonable(policy)), encoding="utf-8")
            auth_path.write_text(json.dumps(authorization), encoding="utf-8")
            with (
                patch("guard_eval.v2.corpus.open_holdout") as opened,
                patch("guard_eval.v2.cli._make_v2_adapter") as adapter,
            ):
                code = main([
                    "holdout",
                    "--manifest", "eval/guard/v2/manifest.json",
                    "--authorization", str(auth_path),
                    "--v1-config", "eval/guard/evaluation-config.json",
                    "--v1-policy", "eval/guard/policy.json",
                    "--v2-config", "eval/guard/v2/evaluation-config.json",
                    "--v2-policy", str(policy_path),
                    "--pricing", "eval/guard/v2/pricing.json",
                    "--output-dir", str(root / "output"),
                ])
            self.assertEqual(code, 1)
            opened.assert_not_called()
            adapter.assert_not_called()

            copied_v1_policy = root / "v1-policy-copy.json"
            copied_v1_policy.write_bytes(Path("eval/guard/policy.json").read_bytes() + b" ")
            authorization["status"] = "approved"
            auth_path.write_text(json.dumps(authorization), encoding="utf-8")
            with patch("guard_eval.v2.corpus.open_holdout") as copied_opened:
                copied_code = main([
                    "holdout",
                    "--manifest", "eval/guard/v2/manifest.json",
                    "--authorization", str(auth_path),
                    "--v1-config", "eval/guard/evaluation-config.json",
                    "--v1-policy", str(copied_v1_policy),
                    "--v2-config", "eval/guard/v2/evaluation-config.json",
                    "--v2-policy", str(policy_path),
                    "--pricing", "eval/guard/v2/pricing.json",
                    "--output-dir", str(root / "copied-output"),
                ])
            self.assertEqual(copied_code, 1)
            copied_opened.assert_not_called()

    def test_dev_evaluation_rejects_unapproved_labels_before_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            authorization = root / "dev-approval.json"
            self.write_dev_approval(authorization, status="draft")
            with patch("guard_eval.v2.cli._make_v2_adapter") as adapter:
                code = main([
                    "evaluate-dev",
                    "--manifest", "eval/guard/v2/manifest.json",
                    "--authorization", str(authorization),
                    "--config", "eval/guard/v2/evaluation-config.json",
                    "--output", str(root / "run.json"),
                ])
            self.assertEqual(code, 1)
            adapter.assert_not_called()

    def test_fit_policy_cannot_overwrite_canonical_frozen_policy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            authorization = Path(directory) / "dev-approval.json"
            self.write_dev_approval(authorization)
            code = main([
                "fit-policy",
                "--manifest", "eval/guard/v2/manifest.json",
                "--authorization", str(authorization),
                "--config", "eval/guard/v2/evaluation-config.json",
                "--absolute-run", str(Path(directory) / "not-read.json"),
                "--output-policy", "eval/guard/v2/policy.json",
                "--output-run", str(Path(directory) / "ranked.json"),
            ])
        self.assertEqual(code, 1)

    def test_fit_and_apply_policy_cli_replay_complete_dev_run_offline(self) -> None:
        corpus = validate_dev_manifest("eval/guard/v2/manifest.json")
        config = load_evaluation_config("eval/guard/v2/evaluation-config.json")
        judgments = []
        for case in corpus.dev:
            judgments.append(CaseJudgmentV2(AbsoluteJudgmentV2(
                case_id=case.case_id,
                case_fingerprint=case_fingerprint(case),
                status=CheckStatus.CHECKED,
                source_context_sufficient=0.9,
                source_issue_scores={key: 0.9 if value else 0.1 for key, value in case.expected_source_issues.items()},
                candidate_component_scores={
                    candidate.candidate_id: {
                        key: 0.9 if value else 0.1 for key, value in candidate.expected_components.items()
                    }
                    for candidate in case.candidates
                },
                candidate_safety_scores={
                    candidate.candidate_id: {
                        key: 0.9 if value else 0.1 for key, value in candidate.expected_safety.items()
                    }
                    for candidate in case.candidates
                },
                input_tokens=0,
                output_tokens=0,
                observed_model=config.model_version,
            )))
        run = JudgmentRunV2(
            judgment_run_version="2.0.0",
            pipeline_version="v2",
            run_digest=None,
            corpus_version=corpus.dev_version,
            case_set_digest=case_set_digest(corpus.dev),
            split=Split.DEV,
            config_version=config.config_version,
            absolute_question_set_version=config.absolute_question_set_version,
            ranking_question_set_version=config.ranking_question_set_version,
            requested_model=config.model_version,
            observed_models=[config.model_version],
            policy_version=None,
            run_status=RunStatus.COMPLETE,
            counts={"total": len(corpus.dev), "checked": len(corpus.dev), "unchecked": 0, "unchecked_by_reason": {}},
            judgments=judgments,
            started_at="2026-09-27T00:00:00Z",
            completed_at="2026-09-27T00:00:01Z",
        )
        run.run_digest = judgment_run_digest(run)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            absolute_path = root / "absolute.json"
            policy_path = root / "candidate-policy.json"
            ranked_path = root / "ranked.json"
            decisions_path = root / "decisions.json"
            absolute_path.write_text(json.dumps(to_jsonable(run)), encoding="utf-8")
            authorization_path = root / "dev-approval.json"
            self.write_dev_approval(authorization_path)
            class RankingAdapter:
                @staticmethod
                def evaluate_ranking(case, eligible):
                    return RankingJudgmentV2(
                        eligible_candidate_ids=eligible,
                        probabilities={eligible[0]: 0.8, eligible[1]: 0.2},
                        choice=eligible[0],
                        confidence=0.8,
                        input_tokens=1,
                        output_tokens=1,
                        observed_model=config.model_version,
                    )

            with patch("guard_eval.v2.cli._make_v2_adapter", return_value=RankingAdapter()) as adapter:
                fit_code = main([
                    "fit-policy",
                    "--manifest", "eval/guard/v2/manifest.json",
                    "--authorization", str(authorization_path),
                    "--config", "eval/guard/v2/evaluation-config.json",
                    "--absolute-run", str(absolute_path),
                    "--output-policy", str(policy_path),
                    "--output-run", str(ranked_path),
                ])
            self.assertEqual(fit_code, 0)
            adapter.assert_called_once()
            apply_code = main([
                "apply-policy",
                "--manifest", "eval/guard/v2/manifest.json",
                "--run", str(ranked_path),
                "--policy", str(policy_path),
                "--output", str(decisions_path),
            ])
            self.assertEqual(apply_code, 0)
            recommendations = {
                item["case_id"]: item["recommendation"]
                for item in json.loads(decisions_path.read_text())["recommendations"]
            }
            self.assertEqual(
                recommendations,
                {case.case_id: case.expected_recommendation.value for case in corpus.dev},
            )

    def test_compare_replays_offline_with_exact_authorization_and_does_not_mutate_inputs(self) -> None:
        config = load_evaluation_config("eval/guard/v2/evaluation-config.json")
        case = RecommendationCaseV2.from_dict(case_dict(case_id="holdout-1", split="holdout"))
        corpus_version = "sha256:" + "9" * 64

        class Adapter:
            @staticmethod
            def evaluate_absolute(item):
                return AbsoluteJudgmentV2(
                    case_id=item.case_id,
                    case_fingerprint=case_fingerprint(item),
                    status=CheckStatus.CHECKED,
                    source_context_sufficient=0.9,
                    source_issue_scores={
                        SourceIssue.LEXICALLY_INCOMPLETE: 0.9,
                        SourceIssue.UNNATURAL_COLLOCATION: 0.1,
                    },
                    candidate_component_scores={
                        "c1": {key: 0.9 for key in CandidateComponent},
                    },
                    candidate_safety_scores={
                        "c1": {key: 0.05 for key in SafetyDimension},
                    },
                    input_tokens=10,
                    output_tokens=2,
                    observed_model=config.model_version,
                )

        v2_raw = evaluate_absolute_cases(
            [case], Adapter(), split="holdout", corpus_version=corpus_version, config=config
        )
        policy = RecommendationPolicyV2.conservative_fixture(
            fitted_corpus_version="sha256:" + "8" * 64,
            config_version=config.config_version,
            absolute_question_set_version=config.absolute_question_set_version,
            ranking_question_set_version=config.ranking_question_set_version,
            model_version=config.model_version,
        )
        policy.policy_version = policy_version(policy)
        v2_decisions = apply_policy_run([case], v2_raw, policy)
        v1_config = load_v1_config("eval/guard/evaluation-config.json")
        projected = project_case_to_v1(case)
        v1_raw = V1EvaluationRun(
            run_id="offline-compare-fixture",
            started_at="2026-09-27T00:00:00Z",
            completed_at="2026-09-27T00:00:01Z",
            split=V1Split.HOLDOUT,
            corpus_version=corpus_version,
            config_version=v1_config.config_version,
            question_set_version=v1_config.question_set_version,
            requested_model=v1_config.model_version,
            observed_models=[v1_config.model_version],
            policy_version=None,
            pricing_version=None,
            run_status=V1RunStatus.COMPLETE,
            counts={"total": 1, "checked": 1, "unchecked": 0, "unchecked_by_reason": {}},
            judgments=[V1JudgmentSet(
                case_id=case.case_id,
                case_fingerprint=v1_case_fingerprint(projected),
                status=V1CheckStatus.CHECKED,
                naturalness_scores={
                    V1NaturalnessReason.LEXICALLY_INCOMPLETE: 0.9,
                    V1NaturalnessReason.UNNATURAL_COLLOCATION: 0.1,
                },
                preference_probabilities={"keep_original": 0.05, "none_of_candidates": 0.05, "candidate:c1": 0.9},
                preference_choice="candidate:c1",
                preference_confidence=0.9,
                candidate_safety_scores={"c1": {key: 0.05 for key in V1GuardDimension}},
                latency_ms=3,
                input_tokens=8,
                output_tokens=1,
                model_version=v1_config.model_version,
            )],
        )
        locked_v1_policy = json.loads(Path("eval/guard/policy.json").read_text())
        v1_decisions = RecommendationRunV2(
            recommendation_run_version="2.0.0",
            recommendation_run_digest=None,
            pipeline_version="v1_compat",
            judgment_run_digest=canonical_digest(to_jsonable(v1_raw)),
            evaluation_corpus_version=corpus_version,
            policy_version=locked_v1_policy["policy_version"],
            policy_fitted_corpus_version=locked_v1_policy["corpus_version_fitted"],
            run_status=RunStatus.COMPLETE,
            recommendations=[PolicyRecommendationV2(
                case_id=case.case_id,
                case_fingerprint=case_fingerprint(case),
                recommendation=RecommendationKind.REPLACE,
                selected_candidate_id="c1",
                reason_codes=["ranked_candidate_selected"],
                candidate_assessments={"c1": CandidateAssessment.PASS},
                eligible_candidate_ids=["c1"],
            )],
        )
        v1_decisions.recommendation_run_digest = recommendation_run_digest(v1_decisions)
        manifest = {
            "dev_version": "sha256:" + "8" * 64,
            "corpus_version": corpus_version,
            "holdout": {"sha256": "sha256:" + "5" * 64, "status": "sealed", "sealed": True},
            "v1_artifact_lock": json.loads(Path("eval/guard/v2/manifest.json").read_text())["v1_artifact_lock"],
        }
        dev = ValidatedCorpusV2(manifest=manifest, dev=[])
        full = ValidatedCorpusV2(manifest=manifest, dev=[], holdout=[case])
        authorization = {
            "authorization_version": "1.0.0",
            "status": "approved",
            "approved_by": "maintainer",
            "approved_at": "2026-09-27T00:00:00Z",
            "manifest_corpus_version": corpus_version,
            "holdout_sha256": manifest["holdout"]["sha256"],
            "policy_version": policy.policy_version,
            "config_version": config.config_version,
            "absolute_question_set_version": config.absolute_question_set_version,
            "ranking_question_set_version": config.ranking_question_set_version,
            **_v1_authorization_expected(manifest),
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = {
                "authorization": authorization,
                "v1-run": to_jsonable(v1_raw),
                "v1-recommendations": to_jsonable(v1_decisions),
                "v2-run": to_jsonable(v2_raw),
                "v2-recommendations": to_jsonable(v2_decisions),
            }
            input_bytes = {}
            for name, data in paths.items():
                path = root / f"{name}.json"
                path.write_text(json.dumps(data), encoding="utf-8")
                input_bytes[path] = path.read_bytes()
            output = root / "report.json"
            with (
                patch("guard_eval.v2.corpus.validate_dev_manifest", return_value=dev),
                patch("guard_eval.v2.corpus.open_holdout", return_value=full),
            ):
                code = main([
                    "compare",
                    "--manifest", str(root / "unused-manifest.json"),
                    "--authorization", str(root / "authorization.json"),
                    "--v1-run", str(root / "v1-run.json"),
                    "--v1-recommendations", str(root / "v1-recommendations.json"),
                    "--v2-run", str(root / "v2-run.json"),
                    "--v2-recommendations", str(root / "v2-recommendations.json"),
                    "--pricing", "eval/guard/v2/pricing.json",
                    "--output", str(output),
                ])
            self.assertEqual(code, 0)
            report = json.loads(output.read_text())
            self.assertEqual(report["decision"], "collect_more_labels")
            self.assertEqual(report["v1"]["config_version"], v1_config.config_version)
            self.assertEqual(report["v2"]["config_version"], config.config_version)
            self.assertIn("case_set_digest", report)
            self.assertTrue(all(path.read_bytes() == before for path, before in input_bytes.items()))

            absolute = v2_raw.judgments[0].absolute
            absolute.status = CheckStatus.UNCHECKED
            absolute.source_context_sufficient = None
            absolute.source_issue_scores = None
            absolute.candidate_component_scores = None
            absolute.candidate_safety_scores = None
            absolute.reason_code = "timeout"
            absolute.input_tokens = None
            absolute.output_tokens = None
            absolute.observed_model = None
            v2_raw.run_status = RunStatus.INCOMPLETE
            v2_raw.observed_models = []
            v2_raw.counts = {"total": 1, "checked": 0, "unchecked": 1, "unchecked_by_reason": {"timeout": 1}}
            v2_raw.run_digest = judgment_run_digest(v2_raw)
            incomplete_decisions = apply_policy_run([case], v2_raw, policy)
            (root / "v2-run.json").write_text(json.dumps(to_jsonable(v2_raw)), encoding="utf-8")
            (root / "v2-recommendations.json").write_text(
                json.dumps(to_jsonable(incomplete_decisions)), encoding="utf-8"
            )
            incomplete_output = root / "incomplete-report.json"
            with (
                patch("guard_eval.v2.corpus.validate_dev_manifest", return_value=dev),
                patch("guard_eval.v2.corpus.open_holdout", return_value=full),
            ):
                incomplete_code = main([
                    "compare",
                    "--manifest", str(root / "unused-manifest.json"),
                    "--authorization", str(root / "authorization.json"),
                    "--v1-run", str(root / "v1-run.json"),
                    "--v1-recommendations", str(root / "v1-recommendations.json"),
                    "--v2-run", str(root / "v2-run.json"),
                    "--v2-recommendations", str(root / "v2-recommendations.json"),
                    "--pricing", "eval/guard/v2/pricing.json",
                    "--output", str(incomplete_output),
                ])
            self.assertEqual(incomplete_code, 2)
            self.assertIsNone(json.loads(incomplete_output.read_text())["decision"])

    def test_holdout_orchestrates_paired_runs_without_fitting_or_overwriting_policy(self) -> None:
        config = load_evaluation_config("eval/guard/v2/evaluation-config.json")
        case = RecommendationCaseV2.from_dict(case_dict(case_id="holdout-1", split="holdout"))
        corpus_version = "sha256:" + "4" * 64

        class Adapter:
            @staticmethod
            def evaluate_absolute(item):
                return AbsoluteJudgmentV2(
                    case_id=item.case_id,
                    case_fingerprint=case_fingerprint(item),
                    status=CheckStatus.CHECKED,
                    source_context_sufficient=0.9,
                    source_issue_scores={
                        SourceIssue.LEXICALLY_INCOMPLETE: 0.9,
                        SourceIssue.UNNATURAL_COLLOCATION: 0.1,
                    },
                    candidate_component_scores={"c1": {key: 0.9 for key in CandidateComponent}},
                    candidate_safety_scores={"c1": {key: 0.05 for key in SafetyDimension}},
                    input_tokens=10,
                    output_tokens=2,
                    observed_model=config.model_version,
                )

        v2_raw = evaluate_absolute_cases(
            [case], Adapter(), split="holdout", corpus_version=corpus_version, config=config
        )
        policy = RecommendationPolicyV2.conservative_fixture(
            fitted_corpus_version=corpus_version,
            config_version=config.config_version,
            absolute_question_set_version=config.absolute_question_set_version,
            ranking_question_set_version=config.ranking_question_set_version,
            model_version=config.model_version,
        )
        policy.policy_version = policy_version(policy)
        v2_decisions = apply_policy_run([case], v2_raw, policy)
        v1_raw = V1EvaluationRun(
            run_id="offline-fixture",
            started_at="2026-09-27T00:00:00Z",
            completed_at="2026-09-27T00:00:01Z",
            split=V1Split.HOLDOUT,
            corpus_version=corpus_version,
            config_version="sha256:" + "3" * 64,
            question_set_version="sha256:" + "2" * 64,
            requested_model=config.model_version,
            observed_models=[config.model_version],
            policy_version=None,
            pricing_version=None,
            run_status=V1RunStatus.COMPLETE,
            counts={"total": 1, "checked": 1, "unchecked": 0, "unchecked_by_reason": {}},
            judgments=[V1JudgmentSet(
                case_id=case.case_id,
                case_fingerprint=case_fingerprint(case),
                status=V1CheckStatus.CHECKED,
                latency_ms=3,
                input_tokens=8,
                output_tokens=1,
                model_version=config.model_version,
            )],
        )
        v1_decisions = RecommendationRunV2(
            recommendation_run_version="2.0.0",
            recommendation_run_digest=None,
            pipeline_version="v1_compat",
            judgment_run_digest=canonical_digest(to_jsonable(v1_raw)),
            evaluation_corpus_version=corpus_version,
            policy_version="sha256:" + "1" * 64,
            policy_fitted_corpus_version="sha256:" + "0" * 64,
            run_status=RunStatus.COMPLETE,
            recommendations=[PolicyRecommendationV2(
                case_id=case.case_id,
                case_fingerprint=case_fingerprint(case),
                recommendation=RecommendationKind.REPLACE,
                selected_candidate_id="c1",
                reason_codes=["ranked_candidate_selected"],
                candidate_assessments={"c1": CandidateAssessment.PASS},
                eligible_candidate_ids=["c1"],
            )],
        )
        v1_decisions.recommendation_run_digest = recommendation_run_digest(v1_decisions)
        manifest = {
            "dev_version": corpus_version,
            "corpus_version": corpus_version,
            "holdout": {"sha256": "sha256:" + "5" * 64, "status": "sealed", "sealed": True},
            "v1_artifact_lock": json.loads(Path("eval/guard/v2/manifest.json").read_text())["v1_artifact_lock"],
        }
        dev = ValidatedCorpusV2(manifest=manifest, dev=[])
        full = ValidatedCorpusV2(manifest=manifest, dev=[], holdout=[case])
        authorization = {
            "authorization_version": "1.0.0",
            "status": "approved",
            "approved_by": "maintainer",
            "approved_at": "2026-09-27T00:00:00Z",
            "manifest_corpus_version": corpus_version,
            "holdout_sha256": manifest["holdout"]["sha256"],
            "policy_version": policy.policy_version,
            "config_version": config.config_version,
            "absolute_question_set_version": config.absolute_question_set_version,
            "ranking_question_set_version": config.ranking_question_set_version,
            **_v1_authorization_expected(manifest),
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            policy_path = root / "policy.json"
            auth_path = root / "authorization.json"
            policy_path.write_text(json.dumps(to_jsonable(policy)), encoding="utf-8")
            auth_path.write_text(json.dumps(authorization), encoding="utf-8")
            before = policy_path.read_bytes()
            with (
                patch("guard_eval.v2.corpus.validate_dev_manifest", return_value=dev),
                patch("guard_eval.v2.corpus.open_holdout", return_value=full),
                patch("guard_eval.evaluator.evaluate_cases", return_value=v1_raw),
                patch("guard_eval.v2.evaluator.evaluate_absolute_cases", return_value=v2_raw),
                patch("guard_eval.v2.evaluator.add_rankings", return_value=v2_raw),
                patch("guard_eval.v2.cli._v1_recommendation_run", return_value=v1_decisions),
                patch("guard_eval.v2.policy.fit_policy") as fitted,
            ):
                code = main([
                    "holdout",
                    "--manifest", str(root / "unused-manifest.json"),
                    "--authorization", str(auth_path),
                    "--v1-config", "eval/guard/evaluation-config.json",
                    "--v1-policy", "eval/guard/policy.json",
                    "--v2-config", "eval/guard/v2/evaluation-config.json",
                    "--v2-policy", str(policy_path),
                    "--pricing", "eval/guard/v2/pricing.json",
                    "--output-dir", str(root / "output"),
                ])
            self.assertEqual(code, 0)
            self.assertEqual(policy_path.read_bytes(), before)
            fitted.assert_not_called()
            self.assertTrue((root / "output/comparison-report.json").exists())


if __name__ == "__main__":
    unittest.main()
