from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from guard_eval.config import canonical_json
from guard_eval.models import (
    CandidateOriginKind,
    EditDecision,
    EvaluationCase,
    GuardAction,
    GuardDimension,
    NaturalnessReason,
    Split,
    ValidationError,
    to_jsonable,
)


class CorpusError(ValueError):
    """Raised when corpus contents fail schema, integrity, or coverage checks."""


@dataclass(frozen=True)
class ValidatedCorpus:
    manifest: dict[str, Any]
    dev: list[EvaluationCase]
    holdout: list[EvaluationCase]

    @property
    def corpus_version(self) -> str:
        return self.manifest["corpus_version"]


def normalize_text(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).split())


def _normalized_tree(value: Any) -> Any:
    if isinstance(value, str):
        return normalize_text(value)
    if isinstance(value, list):
        return [_normalized_tree(item) for item in value]
    if isinstance(value, dict):
        return {key: _normalized_tree(child) for key, child in value.items()}
    return value


def case_fingerprint(case: dict[str, Any] | EvaluationCase) -> str:
    data = to_jsonable(case)
    payload = {
        "source_span": data["source_span"],
        "candidates": sorted(
            [{"candidate_id": item["candidate_id"], "candidate_span": item["candidate_span"]} for item in data["candidates"]],
            key=lambda item: item["candidate_id"],
        ),
        "context_before": data["context_before"],
        "context_after": data["context_after"],
        "current_intent": data["current_intent"],
        "genre": data["genre"],
    }
    encoded = canonical_json(_normalized_tree(payload)).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def file_digest(path: str | Path) -> str:
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _semantic_case(case: dict[str, Any] | EvaluationCase) -> dict[str, Any]:
    data = to_jsonable(case)
    data["candidates"] = sorted(data["candidates"], key=lambda item: item["candidate_id"])
    return data


def compute_corpus_version(dev: list[Any], holdout: list[Any]) -> str:
    payload = {
        "dev": sorted((_semantic_case(case) for case in dev), key=lambda item: item["case_id"]),
        "holdout": sorted((_semantic_case(case) for case in holdout), key=lambda item: item["case_id"]),
    }
    return "sha256:" + hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def _safe_relative_path(value: Any, field: str) -> Path:
    if not isinstance(value, str) or not value:
        raise CorpusError(f"{field} must be a repo-relative path")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise CorpusError(f"{field} escapes repository root")
    return path


def validate_case(data: dict[str, Any], *, expected_split: str) -> EvaluationCase:
    try:
        case = EvaluationCase.from_dict(data)
    except (ValidationError, KeyError, TypeError, ValueError) as exc:
        raise CorpusError(str(exc)) from exc
    if case.split.value != expected_split:
        raise CorpusError("case split does not match split file")
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", case.case_id):
        raise CorpusError("case_id must be a stable slug")
    if not case.source_span.strip() or not case.current_intent.strip() or not case.genre.strip():
        raise CorpusError("source, intent, and genre must be non-empty")
    if not 1 <= len(case.candidates) <= 3:
        raise CorpusError("each case needs one to three candidates")
    ids = [candidate.candidate_id for candidate in case.candidates]
    if len(ids) != len(set(ids)) or any(not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", item) for item in ids):
        raise CorpusError("candidate ids must be unique stable slugs")
    source = normalize_text(case.source_span)
    texts = [normalize_text(candidate.candidate_span) for candidate in case.candidates]
    if source in texts:
        raise CorpusError("candidate cannot be a normalized no-op")
    if len(texts) != len(set(texts)):
        raise CorpusError("candidate normalized text must be unique")
    if len(set(case.expected_naturalness_reasons)) != len(case.expected_naturalness_reasons):
        raise CorpusError("naturalness reasons must be unique")
    option_ids = {f"candidate:{candidate_id}" for candidate_id in ids}
    if not case.expected_needs_edit:
        if case.expected_naturalness_reasons or case.expected_preferred_option != "keep_original" or case.expected_edit_decision is not EditDecision.KEEP:
            raise CorpusError("no-edit labels are inconsistent")
    else:
        if not case.expected_naturalness_reasons or case.expected_preferred_option == "keep_original":
            raise CorpusError("edit-needed labels are inconsistent")
        if case.expected_preferred_option == "none_of_candidates":
            if case.expected_edit_decision is not EditDecision.REVIEW:
                raise CorpusError("none_of_candidates must map to review")
        elif case.expected_preferred_option not in option_ids:
            raise CorpusError("preferred candidate is not present")
    if case.expected_edit_decision is EditDecision.REPLACE:
        if case.expected_preferred_option not in option_ids:
            raise CorpusError("replace must select an existing candidate")
        selected = next(item for item in case.candidates if f"candidate:{item.candidate_id}" == case.expected_preferred_option)
        if selected.expected_guard_action is not GuardAction.PASS:
            raise CorpusError("replace candidate must pass expected safety")
    if "V20" not in case.pattern_refs:
        raise CorpusError("V20 corpus case must reference V20")
    if not case.label_source.get("authority") or not case.label_source.get("reference"):
        raise CorpusError("label source must have authority and reference")
    if expected_split == Split.HOLDOUT.value and case.label_source.get("authority") != "maintainer":
        raise CorpusError("holdout labels require maintainer authority")
    baseline = case.baseline
    try:
        baseline_decision = EditDecision(baseline["edit_decision"])
    except (KeyError, ValueError) as exc:
        raise CorpusError("baseline decision is invalid") from exc
    if baseline.get("authority") != "maintainer" or not baseline.get("reference") or not baseline.get("version"):
        raise CorpusError("baseline requires maintainer authority, version, and reference")
    selected_id = baseline.get("selected_candidate_id")
    if baseline_decision is EditDecision.KEEP and selected_id is not None:
        raise CorpusError("baseline keep cannot select a candidate")
    if baseline_decision is EditDecision.REPLACE and selected_id not in ids:
        raise CorpusError("baseline replace must select a candidate")
    if baseline_decision is EditDecision.REVIEW and selected_id is not None and selected_id not in ids:
        raise CorpusError("baseline review candidate must exist")
    _safe_relative_path(case.provenance.get("path"), "provenance.path")
    if not case.provenance.get("section") and not case.provenance.get("line"):
        raise CorpusError("provenance needs a section or line")
    return case


def _load_jsonl(path: Path, split: str) -> list[EvaluationCase]:
    cases: list[EvaluationCase] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise CorpusError(f"cannot read split: {type(exc).__name__}") from exc
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CorpusError(f"invalid JSONL at {path}:{number}") from exc
        if not isinstance(raw, dict):
            raise CorpusError(f"case at {path}:{number} must be an object")
        cases.append(validate_case(raw, expected_split=split))
    if not cases:
        raise CorpusError(f"{split} split is empty")
    return cases


def _validate_coverage(cases: list[EvaluationCase], split: str) -> None:
    positives = {reason: 0 for reason in NaturalnessReason}
    hard_negatives = {reason: 0 for reason in NaturalnessReason}
    safety_positive = {dimension: 0 for dimension in GuardDimension}
    safety_negative = {dimension: 0 for dimension in GuardDimension}
    none_with_safe = 0
    for case in cases:
        reasons = set(case.expected_naturalness_reasons)
        for reason in NaturalnessReason:
            if reason in reasons:
                positives[reason] += 1
            elif not case.expected_needs_edit:
                hard_negatives[reason] += 1
        if case.expected_preferred_option == "none_of_candidates" and any(
            candidate.expected_guard_action is GuardAction.PASS for candidate in case.candidates
        ):
            none_with_safe += 1
        for candidate in case.candidates:
            for dimension, expected in candidate.expected_dimensions.items():
                (safety_positive if expected else safety_negative)[dimension] += 1
    missing = [f"{reason.value}:positive" for reason, count in positives.items() if not count]
    missing += [f"{reason.value}:hard_negative" for reason, count in hard_negatives.items() if not count]
    missing += [f"{dimension.value}:positive" for dimension, count in safety_positive.items() if not count]
    missing += [f"{dimension.value}:hard_negative" for dimension, count in safety_negative.items() if not count]
    if not none_with_safe:
        missing.append("none_of_candidates_with_safe_candidate")
    if missing:
        raise CorpusError(f"{split} coverage missing: {', '.join(missing)}")


def validate_manifest(path: str | Path, *, repo_root: str | Path | None = None) -> ValidatedCorpus:
    manifest_path = Path(path)
    root = Path(repo_root or Path.cwd()).resolve()
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CorpusError(f"cannot read manifest: {type(exc).__name__}") from exc
    if not isinstance(manifest, dict):
        raise CorpusError("manifest root must be an object")
    required = {"schema_version", "corpus_version", "dev", "holdout", "baseline_workflow_version", "coverage_requirements", "created_at"}
    if missing := required - manifest.keys():
        raise CorpusError(f"manifest missing fields: {sorted(missing)}")
    loaded: dict[str, list[EvaluationCase]] = {}
    for split in (Split.DEV.value, Split.HOLDOUT.value):
        descriptor = manifest.get(split)
        if not isinstance(descriptor, dict):
            raise CorpusError(f"manifest {split} descriptor is invalid")
        relative = _safe_relative_path(descriptor.get("path"), f"{split}.path")
        split_path = (root / relative).resolve()
        if root not in split_path.parents:
            raise CorpusError(f"{split}.path escapes repository root")
        if descriptor.get("sha256") != file_digest(split_path):
            raise CorpusError(f"{split} file digest mismatch")
        loaded[split] = _load_jsonl(split_path, split)
    all_ids = [case.case_id for cases in loaded.values() for case in cases]
    if len(all_ids) != len(set(all_ids)):
        raise CorpusError("case ids must be unique across corpus")
    dev_fingerprints = {case_fingerprint(case) for case in loaded[Split.DEV.value]}
    holdout_fingerprints = {case_fingerprint(case) for case in loaded[Split.HOLDOUT.value]}
    if overlap := dev_fingerprints & holdout_fingerprints:
        raise CorpusError(f"dev/holdout fingerprint leakage: {len(overlap)} case(s)")
    expected_version = compute_corpus_version(loaded[Split.DEV.value], loaded[Split.HOLDOUT.value])
    if manifest.get("corpus_version") != expected_version:
        raise CorpusError("corpus version mismatch")
    if manifest.get("baseline_workflow_version") != "vi-humanizer-0.7.1":
        raise CorpusError("baseline workflow version mismatch")
    _validate_coverage(loaded[Split.DEV.value], Split.DEV.value)
    _validate_coverage(loaded[Split.HOLDOUT.value], Split.HOLDOUT.value)
    return ValidatedCorpus(manifest, loaded[Split.DEV.value], loaded[Split.HOLDOUT.value])
