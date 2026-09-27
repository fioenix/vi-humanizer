from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from guard_eval.v2.corpus import (
    CorpusError,
    case_fingerprint,
    compute_corpus_version,
    compute_dev_version,
    file_digest,
    open_holdout,
    validate_dev_manifest,
)
from guard_eval.v2.models import RecommendationCaseV2, canonical_digest, to_jsonable
from tests.guard_eval_v2.helpers import candidate_dict, case_dict


class CorpusContractTests(unittest.TestCase):
    def test_case_fingerprint_excludes_labels_split_and_lineage(self) -> None:
        left = RecommendationCaseV2.from_dict(case_dict())
        changed = case_dict(split="dev")
        changed["expected_recommendation"] = "review"
        changed["expected_selected_candidate_id"] = None
        changed["candidates"][0]["expected_acceptable"] = False
        changed["candidates"][0]["expected_components"]["fixes_issue"] = False
        right = RecommendationCaseV2.from_dict(changed)
        self.assertEqual(case_fingerprint(left), case_fingerprint(right))
        self.assertNotEqual(compute_corpus_version([left], "sha256:" + "a" * 64), compute_corpus_version([right], "sha256:" + "a" * 64))

    def _repo(self):
        root = Path(tempfile.mkdtemp())
        (root / "eval/guard/v2").mkdir(parents=True)
        dev = root / "eval/guard/v2/dev.jsonl"
        dev.write_text(json.dumps(case_dict(), ensure_ascii=False) + "\n", encoding="utf-8")
        v1_manifest = root / "eval/guard/manifest.json"
        v1_manifest.parent.mkdir(parents=True, exist_ok=True)
        v1_manifest.write_text(json.dumps({"corpus_version": "sha256:" + "c" * 64}), encoding="utf-8")
        lock = root / "eval/guard/v2/v1-artifact-lock.json"
        lock_data = {
            "lock_version": "1.0.0",
            "lock_digest": "",
            "entries": [{"path": "eval/guard/manifest.json", "sha256": file_digest(v1_manifest)}],
        }
        lock_data["lock_digest"] = canonical_digest(lock_data, "lock_digest")
        lock.write_text(json.dumps(lock_data), encoding="utf-8")
        registry = root / "eval/guard/v2/observed-holdouts.json"
        registry_data = {"registry_version": "1.0.0", "registry_digest": "", "holdouts": []}
        registry_data["registry_digest"] = canonical_digest(registry_data, "registry_digest")
        registry.write_text(json.dumps(registry_data), encoding="utf-8")
        holdout_digest = "sha256:" + "b" * 64
        case = RecommendationCaseV2.from_dict(case_dict())
        manifest = {
            "schema_version": "2.0.0",
            "dev_version": compute_dev_version([case]),
            "corpus_version": compute_corpus_version([case], holdout_digest),
            "dev": {"path": "eval/guard/v2/dev.jsonl", "sha256": file_digest(dev), "case_count": 1},
            "holdout": {"path": "eval/guard/v2/holdout.jsonl", "status": "sealed", "sha256": holdout_digest, "case_count": 1, "sealed": True},
            "observed_holdouts_registry": {"path": "eval/guard/v2/observed-holdouts.json", "sha256": file_digest(registry)},
            "v1_artifact_lock": {"path": "eval/guard/v2/v1-artifact-lock.json", "sha256": file_digest(lock)},
            "coverage_requirements": {"minimum_per_required_slice": 5},
            "created_at": "2026-09-27T00:00:00Z",
        }
        manifest_path = root / "eval/guard/v2/manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return root, manifest_path, manifest

    def test_dev_validation_does_not_open_sealed_holdout(self) -> None:
        root, manifest_path, _ = self._repo()
        corpus = validate_dev_manifest(manifest_path, repo_root=root)
        self.assertEqual(len(corpus.dev), 1)
        self.assertFalse((root / "eval/guard/v2/holdout.jsonl").exists())

    def test_pending_holdout_allows_dev_validation_but_cannot_be_opened(self) -> None:
        root, manifest_path, manifest = self._repo()
        manifest["holdout"] = {
            "path": "eval/guard/v2/holdout.jsonl",
            "status": "pending",
            "sha256": None,
            "case_count": None,
            "sealed": False,
        }
        manifest["corpus_version"] = compute_corpus_version(
            [RecommendationCaseV2.from_dict(case_dict())], "pending"
        )
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        validate_dev_manifest(manifest_path, repo_root=root)
        with self.assertRaisesRegex(CorpusError, "pending"):
            open_holdout(manifest_path, repo_root=root, authorized=True, policy_frozen=True)

    def test_full_holdout_requires_both_authorization_and_frozen_policy(self) -> None:
        root, manifest_path, manifest = self._repo()
        holdout = root / manifest["holdout"]["path"]
        holdout_case = case_dict(case_id="holdout-1", split="holdout")
        holdout.write_text(json.dumps(holdout_case, ensure_ascii=False) + "\n", encoding="utf-8")
        manifest["holdout"]["sha256"] = file_digest(holdout)
        manifest["corpus_version"] = compute_corpus_version(
            [RecommendationCaseV2.from_dict(case_dict())], manifest["holdout"]["sha256"]
        )
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaises(CorpusError):
            open_holdout(manifest_path, repo_root=root, authorized=False, policy_frozen=True)
        with self.assertRaises(CorpusError):
            open_holdout(manifest_path, repo_root=root, authorized=True, policy_frozen=False)

    def test_holdout_labels_accept_owner_authorized_agent_as_actual_actor(self) -> None:
        root, manifest_path, manifest = self._repo()
        holdout_data = case_dict(case_id="holdout-owner-agent", split="holdout")
        holdout_data["source_span"] = "Người viết còn thấy bỡ trước công cụ này."
        holdout_data["candidates"][0]["candidate_span"] = "Người viết còn thấy bỡ ngỡ trước công cụ này."
        holdout_data["label_authority"]["authority"] = "owner_authorized_agent"
        holdout = root / manifest["holdout"]["path"]
        holdout.write_text(json.dumps(holdout_data, ensure_ascii=False) + "\n", encoding="utf-8")
        manifest["holdout"]["sha256"] = file_digest(holdout)
        manifest["corpus_version"] = compute_corpus_version(
            [RecommendationCaseV2.from_dict(case_dict())], manifest["holdout"]["sha256"]
        )
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        corpus = open_holdout(manifest_path, repo_root=root, authorized=True, policy_frozen=True)

        self.assertEqual(corpus.holdout[0].label_authority["authority"], "owner_authorized_agent")

    def test_holdout_rejects_historical_fingerprint(self) -> None:
        root, manifest_path, manifest = self._repo()
        holdout_data = case_dict(case_id="holdout-1", split="holdout")
        holdout = root / manifest["holdout"]["path"]
        holdout.write_text(json.dumps(holdout_data, ensure_ascii=False) + "\n", encoding="utf-8")
        fingerprint = case_fingerprint(RecommendationCaseV2.from_dict(holdout_data))
        registry_path = root / manifest["observed_holdouts_registry"]["path"]
        registry = {"registry_version": "1.0.0", "registry_digest": "", "holdouts": [{"feature": "001", "fingerprints": [fingerprint]}]}
        registry["registry_digest"] = canonical_digest(registry, "registry_digest")
        registry_path.write_text(json.dumps(registry), encoding="utf-8")
        manifest["observed_holdouts_registry"]["sha256"] = file_digest(registry_path)
        manifest["holdout"]["sha256"] = file_digest(holdout)
        manifest["corpus_version"] = compute_corpus_version(
            [RecommendationCaseV2.from_dict(case_dict())], manifest["holdout"]["sha256"]
        )
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaises(CorpusError):
            open_holdout(manifest_path, repo_root=root, authorized=True, policy_frozen=True)

    def test_promoted_lineage_must_resolve_exact_semantic_fingerprint(self) -> None:
        root, manifest_path, manifest = self._repo()
        source_path = root / "eval/guard/old.jsonl"
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source = case_dict(case_id="old-1", split="holdout")
        source_path.write_text(json.dumps(source, ensure_ascii=False) + "\n", encoding="utf-8")
        source_fingerprint = case_fingerprint(RecommendationCaseV2.from_dict(source))
        lock_path = root / manifest["v1_artifact_lock"]["path"]
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        lock["entries"].append({"path": "eval/guard/old.jsonl", "sha256": file_digest(source_path)})
        lock["lock_digest"] = canonical_digest(lock, "lock_digest")
        lock_path.write_text(json.dumps(lock), encoding="utf-8")
        manifest["v1_artifact_lock"]["sha256"] = file_digest(lock_path)
        registry_path = root / manifest["observed_holdouts_registry"]["path"]
        registry = {
            "registry_version": "1.0.0",
            "registry_digest": "",
            "holdouts": [{
                "feature": "001-edit-guard-eval",
                "artifact_path": "eval/guard/old.jsonl",
                "artifact_sha256": file_digest(source_path),
                "corpus_version": "sha256:" + "c" * 64,
                "fingerprints": [source_fingerprint],
            }],
        }
        registry["registry_digest"] = canonical_digest(registry, "registry_digest")
        registry_path.write_text(json.dumps(registry), encoding="utf-8")
        manifest["observed_holdouts_registry"]["sha256"] = file_digest(registry_path)
        dev_data = case_dict()
        dev_data["lineage"] = {
            "kind": "promoted_observed_holdout",
            "source_feature": "001-edit-guard-eval",
            "source_split": "holdout",
            "source_case_id": "old-1",
            "source_case_fingerprint": source_fingerprint,
            "source_corpus_version": "sha256:" + "c" * 64,
            "source_artifact_path": "eval/guard/old.jsonl",
            "source_artifact_sha256": file_digest(source_path),
            "promotion_decision_ref": "specs/002-edit-decision-gate/spec.md#user-story-2",
        }
        dev_path = root / manifest["dev"]["path"]
        dev_path.write_text(json.dumps(dev_data, ensure_ascii=False) + "\n", encoding="utf-8")
        manifest["dev"]["sha256"] = file_digest(dev_path)
        manifest["dev_version"] = compute_dev_version([RecommendationCaseV2.from_dict(dev_data)])
        manifest["corpus_version"] = compute_corpus_version(
            [RecommendationCaseV2.from_dict(dev_data)], manifest["holdout"]["sha256"]
        )
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        validate_dev_manifest(manifest_path, repo_root=root)
        dev_data["source_span"] = "Nội dung đã bị đổi."
        dev_path.write_text(json.dumps(dev_data, ensure_ascii=False) + "\n", encoding="utf-8")
        manifest["dev"]["sha256"] = file_digest(dev_path)
        manifest["dev_version"] = compute_dev_version([RecommendationCaseV2.from_dict(dev_data)])
        manifest["corpus_version"] = compute_corpus_version(
            [RecommendationCaseV2.from_dict(dev_data)], manifest["holdout"]["sha256"]
        )
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaises(CorpusError):
            validate_dev_manifest(manifest_path, repo_root=root)


if __name__ == "__main__":
    unittest.main()
