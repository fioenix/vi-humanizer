from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from guard_eval.config import EvaluationConfig
from guard_eval.models import CheckStatus, EvaluationRun, RunStatus, Split
from guard_eval.questions import question_set_version


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def evaluate_cases(
    cases: list[Any],
    adapter: Any,
    *,
    split: str,
    corpus_version: str,
    config: EvaluationConfig,
) -> EvaluationRun:
    started = _now()
    judgments = [adapter.evaluate(case) for case in cases]
    checked = [item for item in judgments if item.status is CheckStatus.CHECKED]
    unchecked = [item for item in judgments if item.status is CheckStatus.UNCHECKED]
    observed_models = sorted({item.model_version for item in checked if item.model_version is not None})
    ids_match = {item.case_id for item in judgments} == {case.case_id for case in cases} and len(judgments) == len(cases)
    fingerprints_match = all(item.case_fingerprint for item in judgments)
    model_valid = not observed_models or observed_models == [config.model_version]
    question_valid = config.question_set_version == question_set_version()
    if not ids_match or not fingerprints_match or not model_valid or not question_valid:
        status = RunStatus.INVALID
    elif unchecked:
        status = RunStatus.INCOMPLETE
    else:
        status = RunStatus.COMPLETE
    reasons = Counter(item.reason_code for item in unchecked)
    return EvaluationRun(
        run_id=str(uuid4()), started_at=started, completed_at=_now(), split=Split(split),
        corpus_version=corpus_version, config_version=config.config_version,
        question_set_version=question_set_version(), requested_model=config.model_version,
        observed_models=observed_models, policy_version=None, pricing_version=None,
        run_status=status,
        counts={"total": len(cases), "checked": len(checked), "unchecked": len(unchecked), "unchecked_by_reason": dict(sorted(reasons.items()))},
        judgments=judgments,
    )
