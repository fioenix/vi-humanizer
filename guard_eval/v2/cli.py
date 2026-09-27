from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .models import (
    CandidateAssessment,
    RecommendationKind,
    RecommendationRunV2,
    JudgmentRunV2,
    PolicyRecommendationV2,
    RunStatus,
    canonical_digest,
    recommendation_run_digest,
    recommendation_run_from_dict,
    judgment_run_from_dict,
    to_jsonable,
)
from .privacy import validate_artifact_privacy


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="guard_eval.v2", description="Evaluate the v2 edit-decision gate")
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate", help="validate v2 dev corpus and locked inputs")
    validate.add_argument("--manifest", required=True)

    evaluate = commands.add_parser("evaluate-dev", help="run absolute judgments on dev")
    for name in ("manifest", "authorization", "config", "output"):
        evaluate.add_argument(f"--{name}", required=True)

    fit = commands.add_parser("fit-policy", help="fit absolute/ranking policy from dev")
    for name in ("manifest", "authorization", "config", "absolute-run", "output-policy", "output-run"):
        fit.add_argument(f"--{name}", required=True)

    apply = commands.add_parser("apply-policy", help="apply a frozen policy offline")
    for name in ("manifest", "run", "policy", "output"):
        apply.add_argument(f"--{name}", required=True)

    compare = commands.add_parser("compare", help="compare paired v1/v2 recommendation runs offline")
    for name in (
        "manifest", "authorization", "v1-run", "v1-recommendations", "v2-run", "v2-recommendations",
        "pricing", "output",
    ):
        compare.add_argument(f"--{name}", required=True)

    holdout = commands.add_parser("holdout", help="run the authorized paired holdout")
    for name in (
        "manifest", "authorization", "v1-config", "v1-policy", "v2-config", "v2-policy",
        "pricing", "output-dir",
    ):
        holdout.add_argument(f"--{name}", required=True)
    return parser


def _read_object(path: str | Path, name: str) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {name}: {type(exc).__name__}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{name} root must be an object")
    return value


def _write_json(path: str | Path, value: Any, *, raw_strings: list[str] | None = None) -> None:
    data = to_jsonable(value)
    validate_artifact_privacy(data, raw_strings=raw_strings or [])
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _reject_output_collision(output: str | Path, inputs: list[str | Path]) -> None:
    if Path(output).resolve() in {Path(value).resolve() for value in inputs}:
        raise ValueError("output must not overwrite an input artifact")


def _read_judgment_run(path: str | Path) -> JudgmentRunV2:
    try:
        data = _read_object(path, "judgment run")
        validate_artifact_privacy(data)
        return judgment_run_from_dict(data)
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"invalid judgment run: {type(exc).__name__}") from exc


def _read_recommendation_run(path: str | Path) -> RecommendationRunV2:
    try:
        data = _read_object(path, "recommendation run")
        validate_artifact_privacy(data)
        return recommendation_run_from_dict(data)
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"invalid recommendation run: {type(exc).__name__}") from exc


def _read_policy(path: str | Path) -> Any:
    from .policy import policy_from_dict

    data = _read_object(path, "policy")
    validate_artifact_privacy(data)
    return policy_from_dict(data)


def _make_v2_adapter(config):
    from .typesafe_adapter import TypeSafeAdapterV2

    return TypeSafeAdapterV2(config)


def _validate_approval(data: dict[str, Any], *, expected: dict[str, Any]) -> dict[str, Any]:
    required = {
        "authorization_version", "status", "approved_by", "approved_at", "manifest_corpus_version",
        "holdout_sha256", "policy_version", "config_version", "absolute_question_set_version",
        "ranking_question_set_version", "v1_artifact_lock_sha256", "v1_artifact_lock_digest",
        "v1_config_version", "v1_policy_version", "v1_question_set_version", "v1_model_version",
    }
    if set(data) != required or data.get("authorization_version") != "1.0.0":
        raise ValueError("holdout authorization schema mismatch")
    if data.get("status") != "approved" or data.get("approved_by") not in {
        "maintainer",
        "owner_authorized_agent",
    }:
        raise ValueError("holdout authorization lacks an authorized approval")
    if any(data.get(key) != value for key, value in expected.items()):
        raise ValueError("holdout authorization digests do not match frozen inputs")
    return data


def _v1_authorization_expected(manifest: dict[str, Any]) -> dict[str, Any]:
    from guard_eval.config import load_evaluation_config as load_v1_config
    from guard_eval.policy import load_policy as load_v1_policy

    lock_descriptor = manifest["v1_artifact_lock"]
    lock = _read_object(lock_descriptor["path"], "v1 artifact lock")
    config = load_v1_config("eval/guard/evaluation-config.json")
    policy = load_v1_policy("eval/guard/policy.json")
    return {
        "v1_artifact_lock_sha256": lock_descriptor["sha256"],
        "v1_artifact_lock_digest": lock["lock_digest"],
        "v1_config_version": config.config_version,
        "v1_policy_version": policy.policy_version,
        "v1_question_set_version": config.question_set_version,
        "v1_model_version": config.model_version,
    }


def _approval(path: str | Path, *, manifest: dict[str, Any], policy: Any, config: Any) -> dict[str, Any]:
    data = _read_object(path, "holdout authorization")
    return _validate_approval(data, expected={
        "manifest_corpus_version": manifest["corpus_version"],
        "holdout_sha256": manifest["holdout"]["sha256"],
        "policy_version": policy.policy_version,
        "config_version": config.config_version,
        "absolute_question_set_version": config.absolute_question_set_version,
        "ranking_question_set_version": config.ranking_question_set_version,
        **_v1_authorization_expected(manifest),
    })


def _dev_approval(path: str | Path, *, corpus: Any, config: Any) -> dict[str, Any]:
    from .corpus import file_digest

    data = _read_object(path, "dev label approval")
    required = {
        "approval_version", "status", "approved_by", "approved_at", "proposal_path",
        "proposal_sha256", "dev_version", "dev_sha256", "config_version", "model_version",
        "absolute_question_set_version", "ranking_question_set_version",
    }
    if set(data) != required or data.get("approval_version") != "1.0.0":
        raise ValueError("dev label approval schema mismatch")
    if data.get("status") != "approved" or data.get("approved_by") not in {
        "maintainer",
        "owner_authorized_agent",
    }:
        raise ValueError("dev labels lack an authorized approval")
    proposal = Path(str(data.get("proposal_path", "")))
    if proposal.is_absolute() or ".." in proposal.parts or not proposal.parts:
        raise ValueError("dev label proposal path must be repo-relative")
    expected = {
        "proposal_sha256": file_digest(proposal),
        "dev_version": corpus.dev_version,
        "dev_sha256": corpus.manifest["dev"]["sha256"],
        "config_version": config.config_version,
        "model_version": config.model_version,
        "absolute_question_set_version": config.absolute_question_set_version,
        "ranking_question_set_version": config.ranking_question_set_version,
    }
    if any(data.get(key) != value for key, value in expected.items()):
        raise ValueError("dev label approval does not match corpus/config/proposal")
    return data


def _validate_v1_runtime_inputs(manifest: dict[str, Any], *, config_path: str | Path, policy_path: str | Path) -> None:
    from .corpus import file_digest

    lock = _read_object(manifest["v1_artifact_lock"]["path"], "v1 artifact lock")
    locked = {entry["path"]: entry["sha256"] for entry in lock.get("entries", [])}
    required = {
        "eval/guard/evaluation-config.json": config_path,
        "eval/guard/policy.json": policy_path,
        "guard_eval/config.py": "guard_eval/config.py",
        "guard_eval/corpus.py": "guard_eval/corpus.py",
        "guard_eval/evaluator.py": "guard_eval/evaluator.py",
        "guard_eval/models.py": "guard_eval/models.py",
        "guard_eval/policy.py": "guard_eval/policy.py",
        "guard_eval/questions.py": "guard_eval/questions.py",
        "guard_eval/typesafe_adapter.py": "guard_eval/typesafe_adapter.py",
    }
    if any(locked.get(canonical) != file_digest(actual) for canonical, actual in required.items()):
        raise ValueError("v1 runtime config/policy bytes do not match the artifact lock")


def _usage_from_v2(run: JudgmentRunV2) -> dict[str, int]:
    totals = {"input_tokens": 0, "output_tokens": 0, "latency_ms": 0, "requests": 0}
    for item in run.judgments:
        for judgment in (item.absolute, item.ranking):
            if judgment is None:
                continue
            totals["input_tokens"] += judgment.input_tokens or 0
            totals["output_tokens"] += judgment.output_tokens or 0
            totals["latency_ms"] += judgment.latency_ms or 0
            totals["requests"] += 1
    return totals


def _usage_from_v1(run: Any) -> dict[str, int]:
    return {
        "input_tokens": sum(item.input_tokens or 0 for item in run.judgments),
        "output_tokens": sum(item.output_tokens or 0 for item in run.judgments),
        "latency_ms": sum(item.latency_ms or 0 for item in run.judgments),
        "requests": len(run.judgments),
    }


def _read_and_validate_v1_run(
    path: str | Path,
    *,
    cases: list[Any],
    corpus_version: str,
    config: Any,
) -> Any:
    from guard_eval.corpus import case_fingerprint as v1_case_fingerprint
    from guard_eval.models import (
        CheckStatus as V1CheckStatus,
        EvaluationRun as V1EvaluationRun,
        RunStatus as V1RunStatus,
    )

    data = _read_object(path, "v1 raw run")
    validate_artifact_privacy(data)
    required = {
        "run_id", "started_at", "completed_at", "split", "corpus_version", "config_version",
        "question_set_version", "requested_model", "observed_models", "policy_version",
        "pricing_version", "run_status", "counts", "judgments",
    }
    if set(data) != required:
        raise ValueError("v1 raw run schema mismatch")
    judgment_fields = {
        "case_id", "case_fingerprint", "status", "naturalness_scores", "preference_probabilities",
        "preference_choice", "preference_confidence", "candidate_safety_scores", "reason_code",
        "latency_ms", "input_tokens", "output_tokens", "model_version",
    }
    if any(not isinstance(item, dict) or set(item) != judgment_fields for item in data["judgments"]):
        raise ValueError("v1 raw judgment schema mismatch")
    run = V1EvaluationRun.from_dict(data)
    by_id = {case.case_id: case for case in cases}
    if (
        run.split.value != "holdout"
        or run.corpus_version != corpus_version
        or run.config_version != config.config_version
        or run.question_set_version != config.question_set_version
        or run.requested_model != config.model_version
        or run.policy_version is not None
        or len(run.judgments) != len(cases)
        or {item.case_id for item in run.judgments} != set(by_id)
    ):
        raise ValueError("v1 raw run provenance does not match the authorized holdout")
    checked = 0
    reasons: dict[str, int] = {}
    observed: set[str] = set()
    for judgment in run.judgments:
        case = by_id[judgment.case_id]
        for name, value in (
            ("latency_ms", judgment.latency_ms),
            ("input_tokens", judgment.input_tokens),
            ("output_tokens", judgment.output_tokens),
        ):
            if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value < 0):
                raise ValueError(f"v1 raw run {name} must be null or a non-negative integer")
        if judgment.case_fingerprint != v1_case_fingerprint(case):
            raise ValueError("v1 raw run fingerprint mismatch")
        judgment.validate([f"candidate:{candidate.candidate_id}" for candidate in case.candidates])
        if judgment.status is V1CheckStatus.CHECKED:
            checked += 1
            observed.add(str(judgment.model_version))
        else:
            reason = str(judgment.reason_code)
            reasons[reason] = reasons.get(reason, 0) + 1
    expected_counts = {
        "total": len(cases),
        "checked": checked,
        "unchecked": len(cases) - checked,
        "unchecked_by_reason": dict(sorted(reasons.items())),
    }
    if run.counts != expected_counts or run.observed_models != sorted(observed):
        raise ValueError("v1 raw run counts or observed models are inconsistent")
    expected_status = (
        V1RunStatus.INVALID
        if any(model != run.requested_model for model in observed)
        else V1RunStatus.INCOMPLETE
        if expected_counts["unchecked"]
        else V1RunStatus.COMPLETE
    )
    if run.run_status is not expected_status:
        raise ValueError("v1 raw run status does not match its judgments")
    return run


def _report_provenance(
    *,
    v1_run: Any,
    v2_run: JudgmentRunV2,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    return {
        "v1": {
            "artifact_lock_sha256": manifest["v1_artifact_lock"]["sha256"],
            "config_version": v1_run.config_version,
            "question_set_version": v1_run.question_set_version,
            "requested_model": v1_run.requested_model,
            "observed_models": list(v1_run.observed_models),
        },
        "v2": {
            "config_version": v2_run.config_version,
            "absolute_question_set_version": v2_run.absolute_question_set_version,
            "ranking_question_set_version": v2_run.ranking_question_set_version,
            "requested_model": v2_run.requested_model,
            "observed_models": list(v2_run.observed_models),
        },
    }


def _with_cost(usage: dict[str, int], pricing: Any) -> dict[str, Any]:
    result = dict(usage)
    result["estimated_cost"] = (
        usage["input_tokens"] * pricing.input_cost_per_million_tokens
        + usage["output_tokens"] * pricing.output_cost_per_million_tokens
    ) / 1_000_000
    result["currency"] = pricing.currency
    return result


def _v1_recommendation_run(cases: list[Any], projected: list[Any], raw_run: Any, policy: Any) -> RecommendationRunV2:
    from .corpus import case_fingerprint
    from .evaluator import apply_v1_policy_compat

    judgments = {item.case_id: item for item in raw_run.judgments}
    recommendations: list[PolicyRecommendationV2] = []
    for case, v1_case in sorted(zip(cases, projected, strict=True), key=lambda pair: pair[0].case_id):
        result = apply_v1_policy_compat(
            v1_case, judgments[case.case_id], policy, evaluation_corpus_version=raw_run.corpus_version
        )
        recommendation = RecommendationKind(result.edit_decision.value)
        if recommendation is RecommendationKind.KEEP:
            reasons = ["source_already_sufficient"]
        elif recommendation is RecommendationKind.REPLACE:
            reasons = ["ranked_candidate_selected"]
        else:
            reasons = ["ranking_uncertain"]
        recommendations.append(PolicyRecommendationV2(
            case_id=case.case_id,
            case_fingerprint=case_fingerprint(case),
            recommendation=recommendation,
            selected_candidate_id=result.selected_candidate_id,
            reason_codes=reasons,
            candidate_assessments={key: CandidateAssessment(value.value) for key, value in result.candidate_guard_actions.items()},
            eligible_candidate_ids=sorted(
                key for key, value in result.candidate_guard_actions.items() if value.value == "pass"
            ),
        ))
    raw_digest = canonical_digest(to_jsonable(raw_run))
    result = RecommendationRunV2(
        recommendation_run_version="2.0.0",
        recommendation_run_digest=None,
        pipeline_version="v1_compat",
        judgment_run_digest=raw_digest,
        evaluation_corpus_version=raw_run.corpus_version,
        policy_version=policy.policy_version,
        policy_fitted_corpus_version=policy.corpus_version_fitted,
        run_status=RunStatus(raw_run.run_status.value),
        recommendations=recommendations if raw_run.run_status.value == "complete" else [],
    )
    result.recommendation_run_digest = recommendation_run_digest(result)
    return result


def _validate_command(args: Any) -> int:
    from .corpus import coverage_diagnostics, validate_dev_manifest

    corpus = validate_dev_manifest(args.manifest)
    coverage = coverage_diagnostics(corpus.dev)
    summary = ", ".join(f"{key}={value['count']}/{value['minimum']}" for key, value in coverage.items())
    print(
        f"valid v2 dev corpus {corpus.corpus_version}: {len(corpus.dev)} cases; "
        f"holdout={corpus.manifest['holdout']['status']}; coverage {summary}"
    )
    return 0


def _evaluate_dev_command(args: Any) -> int:
    from .config import load_evaluation_config
    from .corpus import validate_dev_manifest
    from .evaluator import evaluate_absolute_cases

    _reject_output_collision(args.output, [args.manifest, args.authorization, args.config])
    corpus = validate_dev_manifest(args.manifest)
    config = load_evaluation_config(args.config)
    _dev_approval(args.authorization, corpus=corpus, config=config)
    run = evaluate_absolute_cases(
        corpus.dev, _make_v2_adapter(config), split="dev", corpus_version=corpus.dev_version, config=config
    )
    _write_json(args.output, run, raw_strings=[
        text for case in corpus.dev for text in [case.source_span, *(item.candidate_span for item in case.candidates)]
    ])
    if run.run_status is RunStatus.INVALID:
        return 1
    if run.run_status is RunStatus.INCOMPLETE:
        return 2
    return 0


def _fit_policy_command(args: Any) -> int:
    from .config import load_evaluation_config
    from .corpus import validate_dev_manifest
    from .evaluator import add_rankings
    from .policy import fit_policy, fit_ranking_policy

    corpus = validate_dev_manifest(args.manifest)
    config = load_evaluation_config(args.config)
    _dev_approval(args.authorization, corpus=corpus, config=config)
    if Path(args.output_policy).resolve() == Path("eval/guard/v2/policy.json").resolve():
        raise ValueError("fit-policy cannot overwrite the canonical frozen policy")
    protected = {Path(value).resolve() for value in (args.manifest, args.authorization, args.config, args.absolute_run)}
    if Path(args.output_run).resolve() in protected or Path(args.output_policy).resolve() in protected:
        raise ValueError("fit outputs cannot overwrite an input artifact")
    if Path(args.output_run).resolve() == Path(args.output_policy).resolve():
        raise ValueError("fit run and policy outputs must be different files")
    run = _read_judgment_run(args.absolute_run)
    if (
        run.corpus_version != corpus.dev_version
        or run.config_version != config.config_version
        or run.requested_model != config.model_version
        or run.absolute_question_set_version != config.absolute_question_set_version
        or run.ranking_question_set_version != config.ranking_question_set_version
    ):
        raise ValueError("absolute run does not match manifest/config")
    absolute_policy = fit_policy(corpus.dev, run)
    output_run = Path(args.output_run)
    if output_run.exists():
        ranked = _read_judgment_run(output_run)
        if (
            ranked.corpus_version != run.corpus_version
            or ranked.case_set_digest != run.case_set_digest
            or [to_jsonable(item.absolute) for item in ranked.judgments]
            != [to_jsonable(item.absolute) for item in run.judgments]
        ):
            raise ValueError("cached ranked run does not match the absolute run")
        class NoQuotaAdapter:
            @staticmethod
            def evaluate_ranking(case: Any, eligible: list[str]) -> Any:
                raise ValueError("cached ranked run is missing required ranking evidence")

        ranked = add_rankings(corpus.dev, ranked, NoQuotaAdapter(), absolute_policy)
    else:
        ranked = add_rankings(corpus.dev, run, _make_v2_adapter(config), absolute_policy)
        _write_json(output_run, ranked, raw_strings=[
            text for case in corpus.dev for text in [case.source_span, *(item.candidate_span for item in case.candidates)]
        ])
    if ranked.run_status is RunStatus.INCOMPLETE:
        return 2
    if ranked.run_status is RunStatus.INVALID:
        return 1
    policy = fit_ranking_policy(corpus.dev, ranked, absolute_policy)
    _write_json(args.output_policy, policy)
    return 0


def _apply_policy_command(args: Any) -> int:
    from .corpus import validate_dev_manifest
    from .policy import apply_policy_run

    _reject_output_collision(args.output, [args.manifest, args.run, args.policy])
    corpus = validate_dev_manifest(args.manifest)
    run = _read_judgment_run(args.run)
    policy = _read_policy(args.policy)
    recommendation_run = apply_policy_run(corpus.dev, run, policy)
    _write_json(args.output, recommendation_run)
    return 0 if recommendation_run.run_status is RunStatus.COMPLETE else 2


def _compare_command(args: Any) -> int:
    from guard_eval.config import load_evaluation_config as load_v1_config
    from guard_eval.policy import load_policy as load_v1_policy

    from .config import load_pricing_snapshot
    from .corpus import open_holdout, project_case_to_v1, validate_dev_manifest
    from .report import generate_comparison_report

    _reject_output_collision(args.output, [
        args.manifest, args.authorization, args.v1_run, args.v1_recommendations,
        args.v2_run, args.v2_recommendations, args.pricing,
    ])
    dev = validate_dev_manifest(args.manifest)
    v2_raw = _read_judgment_run(args.v2_run)
    v2_decisions = _read_recommendation_run(args.v2_recommendations)
    authorization = _read_object(args.authorization, "holdout authorization")
    from .questions import absolute_question_set_version, ranking_question_set_version
    if (
        v2_raw.pipeline_version != "v2"
        or v2_decisions.pipeline_version != "v2"
        or v2_raw.absolute_question_set_version != absolute_question_set_version()
        or v2_raw.ranking_question_set_version != ranking_question_set_version()
    ):
        raise ValueError("v2 paired artifacts do not match the current pipeline contract")
    _validate_approval(authorization, expected={
        "manifest_corpus_version": dev.corpus_version,
        "holdout_sha256": dev.manifest["holdout"]["sha256"],
        "policy_version": v2_decisions.policy_version,
        "config_version": v2_raw.config_version,
        "absolute_question_set_version": v2_raw.absolute_question_set_version,
        "ranking_question_set_version": v2_raw.ranking_question_set_version,
        **_v1_authorization_expected(dev.manifest),
    })
    corpus = open_holdout(args.manifest, authorized=True, policy_frozen=True)
    holdout = corpus.holdout or []
    from .corpus import case_fingerprint as v2_case_fingerprint, case_set_digest as v2_case_set_digest
    v2_by_id = {item.absolute.case_id: item for item in v2_raw.judgments}
    if (
        v2_raw.case_set_digest != v2_case_set_digest(holdout)
        or set(v2_by_id) != {case.case_id for case in holdout}
        or any(v2_by_id[case.case_id].absolute.case_fingerprint != v2_case_fingerprint(case) for case in holdout)
        or v2_raw.absolute_question_set_version != absolute_question_set_version()
        or v2_raw.ranking_question_set_version != ranking_question_set_version()
    ):
        raise ValueError("v2 raw run provenance does not match the authorized holdout")
    projected = [project_case_to_v1(case) for case in holdout]
    v1_decisions = _read_recommendation_run(args.v1_recommendations)
    v1_config = load_v1_config("eval/guard/evaluation-config.json")
    v1_policy = load_v1_policy("eval/guard/policy.json")
    v1_raw = _read_and_validate_v1_run(
        args.v1_run, cases=projected, corpus_version=corpus.corpus_version, config=v1_config
    )
    v1_raw_data = to_jsonable(v1_raw)
    if (
        v2_raw.corpus_version != corpus.corpus_version
        or v2_decisions.evaluation_corpus_version != corpus.corpus_version
        or v2_decisions.judgment_run_digest != v2_raw.run_digest
        or v2_decisions.run_status is not v2_raw.run_status
        or v1_decisions.evaluation_corpus_version != corpus.corpus_version
        or v1_decisions.judgment_run_digest != canonical_digest(v1_raw_data)
        or v1_decisions.run_status.value != v1_raw.run_status.value
        or v1_decisions.pipeline_version != "v1_compat"
        or v1_decisions.policy_version != v1_policy.policy_version
        or v1_decisions.policy_fitted_corpus_version != v1_policy.corpus_version_fitted
    ):
        raise ValueError("paired runs do not match the authorized holdout")
    v1_model = v1_raw.requested_model
    v1_observed = v1_raw.observed_models
    if (
        v1_model != v2_raw.requested_model
        or any(model != v2_raw.requested_model for model in v2_raw.observed_models)
        or any(model != v1_model for model in v1_observed)
        or (v2_raw.run_status is RunStatus.COMPLETE and v2_raw.observed_models != [v2_raw.requested_model])
        or (v1_decisions.run_status is RunStatus.COMPLETE and v1_observed != [v1_model])
    ):
        raise ValueError("paired comparison requires the same exact observed model")
    pricing = load_pricing_snapshot(args.pricing, expected_model=v2_raw.requested_model)
    usage = {
        "v1": _with_cost({
            "input_tokens": sum(item.input_tokens or 0 for item in v1_raw.judgments),
            "output_tokens": sum(item.output_tokens or 0 for item in v1_raw.judgments),
            "latency_ms": sum(item.latency_ms or 0 for item in v1_raw.judgments),
            "requests": len(v1_raw.judgments),
        }, pricing),
        "v2": _with_cost(_usage_from_v2(v2_raw), pricing),
    }
    usage["total"] = {
        key: usage["v1"].get(key, 0) + usage["v2"].get(key, 0)
        for key in ("input_tokens", "output_tokens", "latency_ms", "requests", "estimated_cost")
    }
    usage["total"]["currency"] = pricing.currency
    report = generate_comparison_report(
        holdout, v1_decisions, v2_decisions, usage=usage,
        provenance=_report_provenance(v1_run=v1_raw, v2_run=v2_raw, manifest=corpus.manifest),
    )
    _write_json(args.output, report)
    return 0 if report["decision"] is not None else 2


def _holdout_command(args: Any) -> int:
    from guard_eval.config import load_evaluation_config as load_v1_config
    from guard_eval.evaluator import evaluate_cases as evaluate_v1_cases
    from guard_eval.policy import load_policy as load_v1_policy
    from guard_eval.typesafe_adapter import TypeSafeAdapter as TypeSafeAdapterV1

    from .config import load_evaluation_config as load_v2_config, load_pricing_snapshot
    from .corpus import open_holdout, project_case_to_v1, validate_dev_manifest
    from .evaluator import add_rankings, evaluate_absolute_cases
    from .policy import apply_policy_run
    from .questions import absolute_question_set_version, ranking_question_set_version
    from .report import generate_comparison_report

    dev = validate_dev_manifest(args.manifest)
    v2_config = load_v2_config(args.v2_config)
    v2_policy = _read_policy(args.v2_policy)
    if (
        v2_policy.fitted_corpus_version != dev.dev_version
        or v2_policy.config_version != v2_config.config_version
        or v2_policy.absolute_question_set_version != v2_config.absolute_question_set_version
        or v2_policy.ranking_question_set_version != v2_config.ranking_question_set_version
        or v2_policy.model_version != v2_config.model_version
        or v2_config.absolute_question_set_version != absolute_question_set_version()
        or v2_config.ranking_question_set_version != ranking_question_set_version()
    ):
        raise ValueError("frozen v2 policy does not match approved dev/config provenance")
    v1_config = load_v1_config(args.v1_config)
    v1_policy = load_v1_policy(args.v1_policy)
    _validate_v1_runtime_inputs(dev.manifest, config_path=args.v1_config, policy_path=args.v1_policy)
    if v1_config.model_version != v2_config.model_version:
        raise ValueError("paired comparison requires the same exact model version")
    pricing = load_pricing_snapshot(args.pricing, expected_model=v2_config.model_version)
    _approval(args.authorization, manifest=dev.manifest, policy=v2_policy, config=v2_config)
    corpus = open_holdout(args.manifest, authorized=True, policy_frozen=True)
    holdout = corpus.holdout or []

    projected = [project_case_to_v1(case) for case in holdout]
    v1_run = evaluate_v1_cases(
        projected, TypeSafeAdapterV1(v1_config), split="holdout",
        corpus_version=corpus.corpus_version, config=v1_config,
    )
    v2_run = evaluate_absolute_cases(
        holdout, _make_v2_adapter(v2_config), split="holdout",
        corpus_version=corpus.corpus_version, config=v2_config,
    )
    if v2_run.run_status is RunStatus.COMPLETE:
        v2_run = add_rankings(holdout, v2_run, _make_v2_adapter(v2_config), v2_policy)
    v1_decisions = _v1_recommendation_run(holdout, projected, v1_run, v1_policy)
    v2_decisions = apply_policy_run(holdout, v2_run, v2_policy)

    output = Path(args.output_dir)
    raw_strings = [text for case in holdout for text in [case.source_span, *(item.candidate_span for item in case.candidates)]]
    _write_json(output / "v1-judgments.json", v1_run, raw_strings=raw_strings)
    _write_json(output / "v2-judgments.json", v2_run, raw_strings=raw_strings)
    _write_json(output / "v1-recommendations.json", v1_decisions)
    _write_json(output / "v2-recommendations.json", v2_decisions)

    usage = {
        "v1": _with_cost(_usage_from_v1(v1_run), pricing),
        "v2": _with_cost(_usage_from_v2(v2_run), pricing),
    }
    usage["total"] = {
        key: usage["v1"].get(key, 0) + usage["v2"].get(key, 0)
        for key in ("input_tokens", "output_tokens", "latency_ms", "requests", "estimated_cost")
    }
    usage["total"]["currency"] = pricing.currency
    report = generate_comparison_report(
        holdout, v1_decisions, v2_decisions, usage=usage,
        provenance=_report_provenance(v1_run=v1_run, v2_run=v2_run, manifest=corpus.manifest),
    )
    _write_json(output / "comparison-report.json", report)
    if v1_decisions.run_status is not RunStatus.COMPLETE or v2_decisions.run_status is not RunStatus.COMPLETE:
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    handlers = {
        "validate": _validate_command,
        "evaluate-dev": _evaluate_dev_command,
        "fit-policy": _fit_policy_command,
        "apply-policy": _apply_policy_command,
        "compare": _compare_command,
        "holdout": _holdout_command,
    }
    try:
        return handlers[args.command](args)
    except Exception as exc:
        print(f"invalid {args.command}: {exc}", file=sys.stderr)
        return 1
