from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import RecommendationKind, RecommendationCaseV2, Split, ValidationError, canonical_digest, canonical_json, to_jsonable


class CorpusError(ValueError):
    """Raised when corpus contents, lineage, or byte locks are invalid."""


@dataclass(frozen=True)
class ValidatedCorpusV2:
    manifest: dict[str, Any]
    dev: list[RecommendationCaseV2]
    holdout: list[RecommendationCaseV2] | None = None

    @property
    def corpus_version(self) -> str:
        return self.manifest["corpus_version"]

    @property
    def dev_version(self) -> str:
        return self.manifest["dev_version"]


@dataclass(frozen=True)
class ProjectedV1Candidate:
    candidate_id: str
    candidate_span: str


@dataclass(frozen=True)
class ProjectedV1Case:
    case_id: str
    source_span: str
    candidates: list[ProjectedV1Candidate]
    context_before: str
    context_after: str
    current_intent: str
    genre: str


def _normalized_tree(value: Any) -> Any:
    if isinstance(value, str):
        return " ".join(unicodedata.normalize("NFC", value).split())
    if isinstance(value, list):
        return [_normalized_tree(item) for item in value]
    if isinstance(value, dict):
        return {key: _normalized_tree(child) for key, child in value.items()}
    return value


def case_fingerprint(case: dict[str, Any] | RecommendationCaseV2) -> str:
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
    return "sha256:" + hashlib.sha256(canonical_json(_normalized_tree(payload)).encode("utf-8")).hexdigest()


def case_set_digest(cases: list[Any]) -> str:
    rows = sorted(
        ({"case_id": case.case_id, "case_fingerprint": case_fingerprint(case)} for case in cases),
        key=lambda item: item["case_id"],
    )
    return "sha256:" + hashlib.sha256(canonical_json(rows).encode("utf-8")).hexdigest()


def file_digest(path: str | Path) -> str:
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compute_dev_version(dev: list[RecommendationCaseV2]) -> str:
    payload = {"dev": sorted((to_jsonable(case) for case in dev), key=lambda item: item["case_id"])}
    return "sha256:" + hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def compute_corpus_version(dev: list[RecommendationCaseV2], holdout_sha256: str) -> str:
    payload = {"dev_version": compute_dev_version(dev), "holdout_sha256": holdout_sha256}
    return "sha256:" + hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def coverage_diagnostics(cases: list[RecommendationCaseV2], *, minimum: int = 5) -> dict[str, dict[str, Any]]:
    counts = {
        "expected_keep": sum(case.expected_recommendation is RecommendationKind.KEEP for case in cases),
        "expected_review": sum(case.expected_recommendation is RecommendationKind.REVIEW for case in cases),
        "expected_replace": sum(case.expected_recommendation is RecommendationKind.REPLACE for case in cases),
        "no_acceptable_candidate": sum(
            case.expected_recommendation is RecommendationKind.REVIEW
            and not any(candidate.expected_acceptable for candidate in case.candidates)
            for case in cases
        ),
        "harmful_candidate_case": sum(
            any(any(candidate.expected_safety.values()) for candidate in case.candidates)
            for case in cases
        ),
    }
    return {
        name: {"count": count, "minimum": minimum, "status": "sufficient" if count >= minimum else "insufficient"}
        for name, count in counts.items()
    }


def _safe_path(root: Path, value: Any, name: str) -> Path:
    if not isinstance(value, str) or not value:
        raise CorpusError(f"{name} must be a repo-relative path")
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise CorpusError(f"{name} escapes repository root")
    path = (root / relative).resolve()
    if root != path and root not in path.parents:
        raise CorpusError(f"{name} escapes repository root")
    return path


def _read_object(path: Path, name: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CorpusError(f"cannot read {name}: {type(exc).__name__}") from exc
    if not isinstance(value, dict):
        raise CorpusError(f"{name} root must be an object")
    return value


def _load_jsonl(path: Path, expected_split: Split) -> tuple[list[RecommendationCaseV2], list[dict[str, Any]]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise CorpusError(f"cannot read {expected_split.value} split: {type(exc).__name__}") from exc
    cases: list[RecommendationCaseV2] = []
    raw_rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
            if not isinstance(raw, dict):
                raise TypeError("record root is not an object")
            case = RecommendationCaseV2.from_dict(raw)
        except (json.JSONDecodeError, TypeError, KeyError, ValueError, ValidationError) as exc:
            raise CorpusError(f"invalid {expected_split.value} case at line {line_number}: {exc}") from exc
        if case.split is not expected_split:
            raise CorpusError("case split does not match split file")
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", case.case_id):
            raise CorpusError("case_id must be a stable slug")
        cases.append(case)
        raw_rows.append(raw)
    if not cases:
        raise CorpusError(f"{expected_split.value} split is empty")
    if len({case.case_id for case in cases}) != len(cases):
        raise CorpusError("case ids must be unique within split")
    return cases, raw_rows


def validate_v1_artifact_lock(path: str | Path, *, repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    lock_path = Path(path)
    if not lock_path.is_absolute():
        lock_path = (root / lock_path).resolve()
    data = _read_object(lock_path, "v1 artifact lock")
    if data.get("lock_version") != "1.0.0" or data.get("lock_digest") != canonical_digest(data, "lock_digest"):
        raise CorpusError("v1 artifact lock digest or version mismatch")
    entries = data.get("entries")
    if not isinstance(entries, list):
        raise CorpusError("v1 artifact lock entries must be a list")
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256"}:
            raise CorpusError("v1 artifact lock entry is invalid")
        if entry["path"] in seen:
            raise CorpusError("v1 artifact lock paths must be unique")
        seen.add(entry["path"])
        artifact = _safe_path(root, entry["path"], "v1 lock path")
        try:
            actual = file_digest(artifact)
        except OSError as exc:
            raise CorpusError(f"locked v1 artifact is missing: {entry['path']}") from exc
        if actual != entry["sha256"]:
            raise CorpusError(f"v1 artifact byte drift: {entry['path']}")
    return data


def _load_registry(path: Path) -> dict[str, Any]:
    data = _read_object(path, "observed holdout registry")
    if data.get("registry_version") != "1.0.0" or data.get("registry_digest") != canonical_digest(data, "registry_digest"):
        raise CorpusError("observed holdout registry digest or version mismatch")
    if not isinstance(data.get("holdouts"), list):
        raise CorpusError("observed holdout registry needs a holdouts list")
    return data


def _validate_descriptor(root: Path, manifest: dict[str, Any], name: str, *, read_bytes: bool) -> Path:
    descriptor = manifest.get(name)
    if not isinstance(descriptor, dict):
        raise CorpusError(f"manifest {name} descriptor is invalid")
    path = _safe_path(root, descriptor.get("path"), f"{name}.path")
    if read_bytes:
        try:
            actual = file_digest(path)
        except OSError as exc:
            raise CorpusError(f"cannot read {name} file") from exc
        if descriptor.get("sha256") != actual:
            raise CorpusError(f"{name} file digest mismatch")
    return path


def _validate_lineage(
    case: RecommendationCaseV2,
    raw: dict[str, Any],
    root: Path,
    lock: dict[str, Any],
    registry: dict[str, Any],
) -> None:
    lineage = case.lineage
    if lineage is None:
        return
    locked = {entry["path"]: entry["sha256"] for entry in lock["entries"]}
    v1_manifest_path = "eval/guard/manifest.json"
    try:
        v1_manifest = _read_object(_safe_path(root, v1_manifest_path, "v1 manifest"), "v1 manifest")
    except (CorpusError, OSError) as exc:
        raise CorpusError("promoted lineage needs the locked v1 manifest") from exc
    registry_entry = next((
        entry for entry in registry["holdouts"]
        if entry.get("feature") == lineage.source_feature
        and entry.get("artifact_path") == lineage.source_artifact_path
    ), None)
    if (
        lineage.source_feature != "001-edit-guard-eval"
        or v1_manifest_path not in locked
        or file_digest(root / v1_manifest_path) != locked[v1_manifest_path]
        or v1_manifest.get("corpus_version") != lineage.source_corpus_version
        or locked.get(lineage.source_artifact_path) != lineage.source_artifact_sha256
        or registry_entry is None
        or registry_entry.get("artifact_sha256") != lineage.source_artifact_sha256
        or registry_entry.get("corpus_version") != lineage.source_corpus_version
        or lineage.source_case_fingerprint not in registry_entry.get("fingerprints", [])
        or not lineage.promotion_decision_ref.startswith("specs/002-edit-decision-gate/")
    ):
        raise CorpusError("promoted lineage does not resolve to the locked observed holdout")
    source_path = _safe_path(root, lineage.source_artifact_path, "lineage.source_artifact_path")
    try:
        if file_digest(source_path) != lineage.source_artifact_sha256:
            raise CorpusError("promoted source artifact digest mismatch")
        rows = [json.loads(line) for line in source_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except (OSError, json.JSONDecodeError) as exc:
        raise CorpusError("cannot resolve promoted source artifact") from exc
    source = next((row for row in rows if row.get("case_id") == lineage.source_case_id), None)
    if source is None:
        raise CorpusError("promoted source case is missing")
    source_fingerprint = case_fingerprint(source)
    if source_fingerprint != lineage.source_case_fingerprint or source_fingerprint != case_fingerprint(raw):
        raise CorpusError("promoted case semantic fingerprint drift")


def _manifest(path: str | Path, root: Path) -> tuple[dict[str, Any], Path]:
    manifest_path = Path(path)
    if not manifest_path.is_absolute():
        manifest_path = (root / manifest_path).resolve()
    manifest = _read_object(manifest_path, "manifest")
    required = {
        "schema_version", "dev_version", "corpus_version", "dev", "holdout", "observed_holdouts_registry",
        "v1_artifact_lock", "coverage_requirements", "created_at",
    }
    if set(manifest) != required or manifest.get("schema_version") != "2.0.0":
        raise CorpusError("manifest fields or schema version mismatch")
    return manifest, manifest_path


def validate_dev_manifest(path: str | Path, *, repo_root: str | Path | None = None) -> ValidatedCorpusV2:
    root = Path(repo_root or Path.cwd()).resolve()
    manifest, _ = _manifest(path, root)
    dev_path = _validate_descriptor(root, manifest, "dev", read_bytes=True)
    holdout_path = _validate_descriptor(root, manifest, "holdout", read_bytes=False)
    holdout_descriptor = manifest["holdout"]
    holdout_status = holdout_descriptor.get("status")
    if holdout_status == "pending":
        if (
            holdout_descriptor.get("sealed") is not False
            or holdout_descriptor.get("sha256") is not None
            or holdout_descriptor.get("case_count") is not None
        ):
            raise CorpusError("pending holdout cannot declare bytes or case count")
        holdout_identity = "pending"
    elif holdout_status == "sealed":
        if (
            holdout_descriptor.get("sealed") is not True
            or not isinstance(holdout_descriptor.get("sha256"), str)
            or isinstance(holdout_descriptor.get("case_count"), bool)
            or not isinstance(holdout_descriptor.get("case_count"), int)
            or holdout_descriptor["case_count"] <= 0
        ):
            raise CorpusError("sealed holdout needs a declared digest and positive case count")
        holdout_identity = holdout_descriptor["sha256"]
    else:
        raise CorpusError("holdout status must be pending or sealed")
    if manifest.get("coverage_requirements") != {"minimum_per_required_slice": 5}:
        raise CorpusError("coverage requirements must preserve the approved minimum of 5")
    lock_descriptor = manifest["v1_artifact_lock"]
    lock_path = _safe_path(root, lock_descriptor.get("path"), "v1_artifact_lock.path")
    if file_digest(lock_path) != lock_descriptor.get("sha256"):
        raise CorpusError("v1 artifact lock file digest mismatch")
    lock = validate_v1_artifact_lock(lock_path, repo_root=root)
    registry_descriptor = manifest["observed_holdouts_registry"]
    registry_path = _safe_path(root, registry_descriptor.get("path"), "observed_holdouts_registry.path")
    if file_digest(registry_path) != registry_descriptor.get("sha256"):
        raise CorpusError("observed holdout registry file digest mismatch")
    registry = _load_registry(registry_path)
    dev, raw_rows = _load_jsonl(dev_path, Split.DEV)
    if manifest["dev"].get("case_count") != len(dev):
        raise CorpusError("dev case count mismatch")
    for case, raw in zip(dev, raw_rows, strict=True):
        _validate_lineage(case, raw, root, lock, registry)
    if len({case_fingerprint(case) for case in dev}) != len(dev):
        raise CorpusError("dev contains duplicate semantic fingerprints")
    if manifest.get("dev_version") != compute_dev_version(dev):
        raise CorpusError("dev version mismatch")
    expected_version = compute_corpus_version(dev, holdout_identity)
    if manifest.get("corpus_version") != expected_version:
        raise CorpusError("corpus version mismatch")
    if holdout_path == dev_path:
        raise CorpusError("dev and holdout paths must differ")
    return ValidatedCorpusV2(manifest=manifest, dev=dev, holdout=None)


def open_holdout(
    path: str | Path,
    *,
    repo_root: str | Path | None = None,
    authorized: bool,
    policy_frozen: bool,
) -> ValidatedCorpusV2:
    if not authorized or not policy_frozen:
        raise CorpusError("holdout requires separate authorization and a frozen policy")
    root = Path(repo_root or Path.cwd()).resolve()
    dev_corpus = validate_dev_manifest(path, repo_root=root)
    manifest = dev_corpus.manifest
    descriptor = manifest["holdout"]
    if descriptor.get("status") != "sealed" or descriptor.get("sealed") is not True:
        raise CorpusError("holdout is pending and cannot be opened")
    holdout_path = _validate_descriptor(root, manifest, "holdout", read_bytes=True)
    holdout, _ = _load_jsonl(holdout_path, Split.HOLDOUT)
    if any(case.lineage is not None for case in holdout):
        raise CorpusError("holdout cannot contain promoted lineage")
    if any(
        case.label_authority.get("authority") not in {"maintainer", "owner_authorized_agent"}
        or not case.label_authority.get("confirmed_at")
        for case in holdout
    ):
        raise CorpusError("holdout labels require confirmed authorized authority")
    dev_fingerprints = {case_fingerprint(case) for case in dev_corpus.dev}
    holdout_fingerprints = {case_fingerprint(case) for case in holdout}
    if len(holdout_fingerprints) != len(holdout) or dev_fingerprints & holdout_fingerprints:
        raise CorpusError("holdout contains duplicate or dev-leaked fingerprints")
    registry_path = _safe_path(root, manifest["observed_holdouts_registry"]["path"], "registry.path")
    registry = _load_registry(registry_path)
    observed = {
        fingerprint
        for entry in registry["holdouts"]
        if isinstance(entry, dict)
        for fingerprint in entry.get("fingerprints", [])
    }
    if observed & holdout_fingerprints:
        raise CorpusError("holdout reuses a historically observed fingerprint")
    if len(holdout) != manifest["holdout"].get("case_count"):
        raise CorpusError("holdout case count mismatch")
    return ValidatedCorpusV2(manifest=manifest, dev=dev_corpus.dev, holdout=holdout)


def project_case_to_v1(case: RecommendationCaseV2) -> ProjectedV1Case:
    """Return only the state shape consumed by v1 questions and policy."""
    candidates = [
        ProjectedV1Candidate(candidate_id=item.candidate_id, candidate_span=item.candidate_span)
        for item in sorted(case.candidates, key=lambda candidate: candidate.candidate_id)
    ]
    return ProjectedV1Case(
        case_id=case.case_id,
        source_span=case.source_span,
        candidates=candidates,
        context_before=case.context_before,
        context_after=case.context_after,
        current_intent=case.current_intent,
        genre=case.genre,
    )
