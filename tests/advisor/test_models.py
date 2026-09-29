from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from advisor.models import ContractError, case_binding, validate_advisor_request, validate_ranking_request


FIXTURES = Path(__file__).parent / "fixtures"


def valid_request() -> dict[str, object]:
    return json.loads((FIXTURES / "valid-v20.json").read_text(encoding="utf-8"))


class AdvisorModelsTest(unittest.TestCase):
    def test_accepts_the_exact_v20_schema_and_preserves_raw_text(self) -> None:
        request = valid_request()

        validated = validate_advisor_request(request)

        self.assertEqual(validated, request)
        self.assertEqual(validated["source"]["pattern"], "V20")

    def test_rejects_unknown_fields_without_echoing_their_values(self) -> None:
        request = valid_request()
        request["protected_region"] = "PRIVATE-CANARY-005-DO-NOT-ECHO"

        with self.assertRaises(ContractError) as caught:
            validate_advisor_request(request)

        self.assertNotIn("PRIVATE-CANARY", str(caught.exception))

    def test_rejects_unstable_ids_and_more_than_three_candidates(self) -> None:
        request = valid_request()
        request["case_id"] = "0-position"
        with self.assertRaises(ContractError):
            validate_advisor_request(request)

        request = valid_request()
        request["candidates"] = {
            f"candidate_{index}": {"text": f"Bản sửa {index}."}
            for index in range(1, 5)
        }
        with self.assertRaises(ContractError):
            validate_advisor_request(request)

    def test_rejects_source_or_candidate_duplicates_after_unicode_and_whitespace_normalization(self) -> None:
        request = valid_request()
        request["candidates"]["candidate_2"] = {
            "text": "  Câu này   đọc lên thấy hụt hẫng.  "
        }
        with self.assertRaises(ContractError):
            validate_advisor_request(request)

        request = valid_request()
        request["source"]["text"] = "Café"
        request["candidates"] = {"candidate_1": {"text": "Cafe\u0301"}}
        with self.assertRaises(ContractError):
            validate_advisor_request(request)

    def test_binding_is_independent_of_candidate_insertion_order(self) -> None:
        request = valid_request()
        request["candidates"] = {
            "candidate_b": {"text": "Câu này nghe vẫn còn hụt hẫng."},
            "candidate_a": {"text": "Câu này đọc lên thấy hụt hẫng."},
        }
        reordered = copy.deepcopy(request)
        reordered["candidates"] = dict(reversed(list(request["candidates"].items())))

        self.assertEqual(
            case_binding(validate_advisor_request(request)),
            case_binding(validate_advisor_request(reordered)),
        )

    def test_binding_changes_when_any_semantic_input_changes(self) -> None:
        request = validate_advisor_request(valid_request())
        changed = copy.deepcopy(request)
        changed["current_intent"] = "Giữ giọng nhận xét trang trọng."

        self.assertNotEqual(case_binding(request), case_binding(validate_advisor_request(changed)))

    def test_ranking_requires_two_to_three_unique_known_candidate_ids(self) -> None:
        request = valid_request()
        request["candidates"]["candidate_2"] = {"text": "Câu này nghe còn hụt hẫng."}
        request["eligible_candidate_ids"] = ["candidate_2", "candidate_1"]

        validated = validate_ranking_request(request)

        self.assertEqual(validated["eligible_candidate_ids"], ["candidate_1", "candidate_2"])
        for invalid in (
            ["candidate_1"],
            ["candidate_1", "candidate_1"],
            ["candidate_1", "unknown"],
            ["candidate_1", "keep_original"],
        ):
            broken = copy.deepcopy(request)
            broken["eligible_candidate_ids"] = invalid
            with self.assertRaises(ContractError):
                validate_ranking_request(broken)


if __name__ == "__main__":
    unittest.main()
