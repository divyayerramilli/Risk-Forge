"""Tests for underwriting tier, decision, and recommendation logic."""

import unittest

from dei_underwriting.data import SAMPLE_COMPANIES
from dei_underwriting.scoring import score_company
from dei_underwriting.underwriting import (
    classify_risk_tier,
    premium_range_for_tier,
    underwriting_decision_for_tier,
)


class UnderwritingTests(unittest.TestCase):
    def test_tiers_map_to_expected_underwriting_decisions(self) -> None:
        expected = {
            "Low": "Approve",
            "Moderate": "Approve with Conditions",
            "Elevated": "Escalate for Manual Review",
            "Severe": "Decline",
        }

        for tier, decision in expected.items():
            self.assertEqual(underwriting_decision_for_tier(tier), decision)

    def test_tiers_have_premium_ranges(self) -> None:
        for tier in ["Low", "Moderate", "Elevated", "Severe"]:
            self.assertTrue(premium_range_for_tier(tier))
            self.assertIn("$", premium_range_for_tier(tier))

    def test_classify_risk_tier_uses_expected_boundaries(self) -> None:
        self.assertEqual(classify_risk_tier(35), "Low")
        self.assertEqual(classify_risk_tier(60), "Moderate")
        self.assertEqual(classify_risk_tier(80), "Elevated")
        self.assertEqual(classify_risk_tier(80.1), "Severe")

    def test_high_risk_account_gets_mitigation_actions(self) -> None:
        result = score_company(SAMPLE_COMPANIES[0])

        self.assertEqual(result.risk_tier, "Severe")
        self.assertEqual(result.underwriting_decision, "Decline")
        self.assertTrue(result.recommended_mitigation_actions)
        self.assertTrue(
            any("vendor" in action.lower() for action in result.recommended_mitigation_actions)
        )


if __name__ == "__main__":
    unittest.main()
