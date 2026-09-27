from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any

from .config import EvaluationConfigV2
from .corpus import case_fingerprint, case_set_digest
from .models import CaseJudgmentV2, CheckStatus, JudgmentRunV2, RunStatus, Split, judgment_run_digest
from .policy import RecommendationPolicyV2, eligible_candidate_ids
from .questions import absolute_question_set_version, ranking_question_set_version


def apply_v1_policy_compat(case: Any, judgment: Any, policy: Any, *, evaluation_corpus_version: str) -> Any:
    """Apply frozen v1 semantics without conflating fit and evaluation corpora."""
    from guard_eval.policy import apply_policy

    if not evaluation_corpus_version.startswith("sha256:"):
        raise ValueError("evaluation corpus version must be a digest")
    return apply_policy(case, judgment, policy)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def evaluate_absolute_cases(
    cases: list[Any],
    adapter: Any,
    *,
    split: str,
    corpus_version: str,
    config: EvaluationConfigV2,
) -> JudgmentRunV2:
    if (
        config.absolute_question_set_version != absolute_question_set_version()
        or config.ranking_question_set_version != ranking_question_set_version()
    ):
        raise ValueError("evaluation config question versions do not match the current contract")
    if any(len(case.candidates) > config.max_candidates for case in cases):
        raise ValueError("case candidate count exceeds evaluation config max_candidates")
    started = _now()
    absolute = [adapter.evaluate_absolute(case) for case in cases]
    judgments = [CaseJudgmentV2(item) for item in absolute]
    checked = [item for item in absolute if item.status is CheckStatus.CHECKED]
    unchecked = [item for item in absolute if item.status is CheckStatus.UNCHECKED]
    expected = {case.case_id: case_fingerprint(case) for case in cases}
    identity_valid = (
        len(absolute) == len(cases)
        and {item.case_id for item in absolute} == set(expected)
        and all(item.case_fingerprint == expected.get(item.case_id) for item in absolute)
    )
    observed_models = sorted({item.observed_model for item in checked if item.observed_model})
    versions_valid = not observed_models or observed_models == [config.model_version]
    if not identity_valid or not versions_valid:
        status = RunStatus.INVALID
    elif unchecked:
        status = RunStatus.INCOMPLETE
    else:
        status = RunStatus.COMPLETE
    reasons = Counter(item.reason_code for item in unchecked)
    run = JudgmentRunV2(
        judgment_run_version="2.0.0",
        pipeline_version="v2",
        run_digest=None,
        corpus_version=corpus_version,
        case_set_digest=case_set_digest(cases),
        split=Split(split),
        config_version=config.config_version,
        absolute_question_set_version=absolute_question_set_version(),
        ranking_question_set_version=ranking_question_set_version(),
        requested_model=config.model_version,
        observed_models=observed_models,
        policy_version=None,
        run_status=status,
        counts={
            "total": len(cases),
            "checked": len(checked),
            "unchecked": len(unchecked),
            "unchecked_by_reason": dict(sorted(reasons.items())),
        },
        judgments=judgments,
        started_at=started,
        completed_at=_now(),
    )
    run.run_digest = judgment_run_digest(run)
    run.validate()
    return run


def add_rankings(
    cases: list[Any],
    run: JudgmentRunV2,
    adapter: Any,
    policy: RecommendationPolicyV2,
) -> JudgmentRunV2:
    if (
        run.absolute_question_set_version != absolute_question_set_version()
        or run.ranking_question_set_version != ranking_question_set_version()
        or policy.absolute_question_set_version != run.absolute_question_set_version
        or policy.ranking_question_set_version != run.ranking_question_set_version
        or policy.model_version != run.requested_model
    ):
        raise ValueError("ranking preflight contract mismatch")
    by_id = {case.case_id: case for case in cases}
    if (
        run.run_status is RunStatus.INVALID
        or any(item.absolute.status is not CheckStatus.CHECKED for item in run.judgments)
        or set(by_id) != {item.absolute.case_id for item in run.judgments}
    ):
        raise ValueError("ranking requires a complete matching absolute run")
    for item in run.judgments:
        case = by_id[item.absolute.case_id]
        eligible = eligible_candidate_ids(case, item.absolute, policy)
        if len(eligible) >= 2:
            if item.ranking is not None:
                if item.ranking.eligible_candidate_ids != eligible:
                    raise ValueError("cached ranking shortlist does not match the fitted absolute gate")
            else:
                item.ranking = adapter.evaluate_ranking(case, eligible)
        elif item.ranking is not None:
            raise ValueError("cached ranking exists for a case without a current shortlist")
    absolute = [item.absolute for item in run.judgments]
    rankings = [item.ranking for item in run.judgments if item.ranking is not None]
    checked = [item for item in [*absolute, *rankings] if item.status is CheckStatus.CHECKED]
    unchecked = [item for item in [*absolute, *rankings] if item.status is CheckStatus.UNCHECKED]
    reasons = Counter(item.reason_code for item in unchecked)
    run.counts = {
        "total": len(absolute) + len(rankings),
        "checked": len(checked),
        "unchecked": len(unchecked),
        "unchecked_by_reason": dict(sorted(reasons.items())),
    }
    run.observed_models = sorted({item.observed_model for item in checked if item.observed_model})
    if run.observed_models != [run.requested_model]:
        run.run_status = RunStatus.INVALID
    elif unchecked:
        run.run_status = RunStatus.INCOMPLETE
    else:
        run.run_status = RunStatus.COMPLETE
    run.run_digest = judgment_run_digest(run)
    run.completed_at = _now()
    run.validate()
    return run
