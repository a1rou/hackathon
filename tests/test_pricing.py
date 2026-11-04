import unittest

from pricing import acceptance_probability, calculate_price


class PricingTests(unittest.TestCase):
    def test_calculates_loan_with_financial_rounding(self):
        result = calculate_price(
            {
                "item_type": "Кольцо",
                "fineness": "585",
                "condition": "Среднее",
                "weight": "3.55",
            }
        )

        self.assertEqual(result["price_per_gram"], 5600)
        self.assertEqual(result["loan_amount"], 19880)
        self.assertEqual(result["daily_interest_rate"], 0.29)

    def test_rejects_unsupported_fineness(self):
        with self.assertRaisesRegex(ValueError, "Неподдерживаемая проба"):
            calculate_price({"fineness": "999", "weight": 1})

    def test_critical_text_overrides_inconsistent_ai_severity(self):
        result = acceptance_probability(
            {
                "condition": "Как новое",
                "weight": 3,
                "has_defects": False,
                "defect_severity": "нет",
                "defects_description": "На кольце заметна трещина",
                "repairable": True,
            }
        )

        self.assertEqual(result["probability"], 25)
        self.assertIn("Критичный дефект", result["reasons"][0])


if __name__ == "__main__":
    unittest.main()
