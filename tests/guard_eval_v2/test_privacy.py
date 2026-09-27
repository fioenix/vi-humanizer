from __future__ import annotations

import unittest

from guard_eval.v2.privacy import PrivacyError, validate_artifact_privacy


class PrivacyContractTests(unittest.TestCase):
    def test_rejects_forbidden_keys_at_any_depth(self) -> None:
        with self.assertRaises(PrivacyError):
            validate_artifact_privacy({"rows": [{"request_body": "secret"}]})

    def test_rejects_raw_string_canaries_and_identity_tokens(self) -> None:
        with self.assertRaises(PrivacyError):
            validate_artifact_privacy(
                {"case_id": "safe"},
                raw_strings=["Tôi thấy hơi hụt."],
                serialized_override='{"note":"Tôi thấy hơi hụt."}',
            )
        with self.assertRaises(PrivacyError):
            validate_artifact_privacy({"note": "ORG_CANARY_42"}, identity_tokens=["ORG_CANARY_42"])

    def test_allows_typed_scores_and_allowlisted_reason(self) -> None:
        validate_artifact_privacy({"case_id": "case-1", "score": 0.7, "reason_code": "timeout"})
        with self.assertRaises(PrivacyError):
            validate_artifact_privacy({"case_id": "case-1", "reason_code": "socket exploded"})


if __name__ == "__main__":
    unittest.main()
