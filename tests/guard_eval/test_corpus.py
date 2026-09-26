import copy
import json
import tempfile
import unittest
from pathlib import Path

from guard_eval.corpus import CorpusError, case_fingerprint, normalize_text, validate_case, validate_manifest
from guard_eval.models import GuardDimension


def candidate(candidate_id="c1", text="đầy đủ", *, harmful=False, origin_kind="maintainer_fixture"):
    origin = {"kind": origin_kind, "reference": "SKILL.md#V20", "authority": "maintainer"}
    if origin_kind == "baseline_observation":
        origin["workflow_version"] = "vi-humanizer-0.7.1"
    if origin_kind == "host_llm_output":
        origin.update(model_version="host-model-1", workflow_version="vi-humanizer-0.7.1")
    return {
        "candidate_id": candidate_id,
        "candidate_span": text,
        "candidate_origin": origin,
        "expected_dimensions": {dimension.value: harmful for dimension in GuardDimension},
        "expected_guard_action": "reject" if harmful else "pass",
    }


def valid_case(case_id="full-word", split="dev", *, reason="lexically_incomplete", preferred="candidate:c1"):
    return {
        "case_id": case_id,
        "split": split,
        "source_span": "Câu này đọc lên thấy hụt",
        "candidates": [candidate()],
        "context_before": "",
        "context_after": "",
        "current_intent": "Giữ nghĩa, làm câu tự nhiên hơn",
        "genre": "blog-ca-nhan",
        "inseparable_edit_ids": [],
        "expected_needs_edit": True,
        "expected_naturalness_reasons": [reason],
        "expected_preferred_option": preferred,
        "expected_edit_decision": "review" if preferred == "none_of_candidates" else "replace",
        "label_source": {"kind": "golden_edit", "authority": "maintainer", "reference": "calibration/LOG.md#2026-07-30"},
        "pattern_refs": ["V20"],
        "baseline": {"edit_decision": "replace", "selected_candidate_id": "c1", "guard_action": "pass", "version": "vi-humanizer-0.7.1", "reference": "SKILL.md#V20", "authority": "maintainer"},
        "provenance": {"path": "calibration/LOG.md", "section": "2026-07-30"},
    }


class CorpusContractTests(unittest.TestCase):
    def test_normalization_and_candidate_order_do_not_change_fingerprint(self):
        case = valid_case()
        case["source_span"] = "Câu   này\nđọc lên thấy hụt"
        case["candidates"] = [candidate("c2", "hụt hơi"), candidate("c1", "hụt hẫng")]
        reordered = copy.deepcopy(case)
        reordered["source_span"] = "Câu này đọc lên thấy hụt"
        reordered["candidates"].reverse()
        self.assertEqual(normalize_text(case["source_span"]), normalize_text(reordered["source_span"]))
        self.assertEqual(case_fingerprint(case), case_fingerprint(reordered))

    def test_case_rejects_missing_fields_candidate_count_noop_duplicate_and_bad_origin(self):
        mutations = []
        missing = valid_case(); missing.pop("genre"); mutations.append(missing)
        no_candidates = valid_case(); no_candidates["candidates"] = []; mutations.append(no_candidates)
        noop = valid_case(); noop["candidates"][0]["candidate_span"] = noop["source_span"]; mutations.append(noop)
        duplicate = valid_case(); duplicate["candidates"].append(candidate("c2", "đầy   đủ")); mutations.append(duplicate)
        bad_origin = valid_case(); bad_origin["candidates"][0]["candidate_origin"].pop("authority"); mutations.append(bad_origin)
        for payload in mutations:
            with self.subTest(payload=payload.get("case_id")), self.assertRaises(CorpusError):
                validate_case(payload, expected_split="dev")

    def test_case_rejects_inconsistent_labels_dimensions_and_baseline_mapping(self):
        keep = valid_case(); keep.update(expected_needs_edit=False, expected_naturalness_reasons=[], expected_preferred_option="candidate:c1", expected_edit_decision="keep")
        dimensions = valid_case(); dimensions["candidates"][0]["expected_dimensions"].pop("adds_claim")
        baseline = valid_case(); baseline["baseline"].update(edit_decision="keep", selected_candidate_id="c1")
        authority = valid_case(split="holdout"); authority["label_source"]["authority"] = "agent"
        traversal = valid_case(); traversal["provenance"]["path"] = "../secret.md"
        for payload in (keep, dimensions, baseline, authority, traversal):
            with self.subTest(payload=payload.get("case_id")), self.assertRaises(CorpusError):
                validate_case(payload, expected_split=payload["split"])

    def test_manifest_rejects_digest_version_leakage_and_missing_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dev = [valid_case("dev-pos")]
            holdout = [valid_case("hold-pos", "holdout")]
            # Same semantic content under another id/split is leakage.
            holdout[0].update({k: copy.deepcopy(v) for k, v in dev[0].items() if k not in {"case_id", "split"}})
            self._write_manifest(root, dev, holdout)
            with self.assertRaisesRegex(CorpusError, "leakage"):
                validate_manifest(root / "manifest.json", repo_root=root)

            holdout[0]["source_span"] = "Câu khác nhưng vẫn hụt"
            self._write_manifest(root, dev, holdout, corpus_version="sha256:" + "0" * 64)
            with self.assertRaisesRegex(CorpusError, "corpus version"):
                validate_manifest(root / "manifest.json", repo_root=root)

    def test_manifest_accepts_full_positive_hard_negative_and_none_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dev = self._covered_split("dev")
            holdout = self._covered_split("holdout")
            self._write_manifest(root, dev, holdout)
            corpus = validate_manifest(root / "manifest.json", repo_root=root)
            self.assertEqual(len(corpus.dev), len(dev))
            self.assertEqual(len(corpus.holdout), len(holdout))

    def _covered_split(self, split):
        prefix = split
        lexical = valid_case(prefix + "-lex", split)
        lexical["source_span"] = prefix + " câu đọc lên thấy hụt"
        collocation = valid_case(prefix + "-coll", split, reason="unnatural_collocation")
        collocation["source_span"] = prefix + " danh sách việc rời"
        collocation["candidates"][0]["candidate_span"] = "danh sách các đầu việc rời rạc"
        negative = valid_case(prefix + "-negative", split)
        negative.update(source_span=prefix + " cốc nước đã đầy", expected_needs_edit=False,
                        expected_naturalness_reasons=[], expected_preferred_option="keep_original", expected_edit_decision="keep")
        negative["candidates"] = [candidate("c1", "cốc nước đã đầy đủ")]
        negative["baseline"].update(edit_decision="keep", selected_candidate_id=None, guard_action=None)
        none = valid_case(prefix + "-none", split, preferred="none_of_candidates")
        none["source_span"] = prefix + " quy trình còn rườm"
        none["candidates"] = [candidate("c1", "quy trình còn dài dòng")]
        harmful = candidate("c2", "quy trình chắc chắn thất bại", harmful=True)
        none["candidates"].append(harmful)
        none["baseline"].update(edit_decision="review", selected_candidate_id=None, guard_action=None)
        return [lexical, collocation, negative, none]

    def _write_manifest(self, root, dev, holdout, corpus_version=None):
        import hashlib
        for name, rows in (("dev", dev), ("holdout", holdout)):
            (root / f"{name}.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
        from guard_eval.corpus import compute_corpus_version, file_digest
        manifest = {
            "schema_version": "1.0.0",
            "corpus_version": corpus_version or compute_corpus_version(dev, holdout),
            "dev": {"path": "dev.jsonl", "sha256": file_digest(root / "dev.jsonl")},
            "holdout": {"path": "holdout.jsonl", "sha256": file_digest(root / "holdout.jsonl")},
            "baseline_workflow_version": "vi-humanizer-0.7.1",
            "coverage_requirements": {"naturalness_positive_and_hard_negative": True, "safety_positive_and_hard_negative": True, "none_of_candidates_with_safe_candidate": True},
            "created_at": "2026-09-26T00:00:00Z",
        }
        (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
