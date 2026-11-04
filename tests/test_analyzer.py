import unittest

from analyzer import _extract_json, _normalize


class AnalyzerNormalizationTests(unittest.TestCase):
    def test_extracts_json_from_markdown_fence(self):
        result = _extract_json("```json\n{\"type\": \"Кольцо\"}\n```")
        self.assertEqual(result, {"type": "Кольцо"})

    def test_normalizes_string_booleans_and_invalid_enums(self):
        result = _normalize(
            {
                "type": "Неизвестный тип",
                "has_inserts": "false",
                "condition": "Среднее",
                "has_defects": "true",
                "repairable": "false",
                "insert_damage": "false",
                "defect_severity": "критичный",
                "estimated_weight_g": "4.2",
                "weight_min_g": "5",
                "weight_max_g": "3",
            },
            {"type": "Кольцо", "has_inserts": True, "condition": "Как новое"},
        )

        self.assertEqual(result["type"], "Кольцо")
        self.assertFalse(result["has_inserts"])
        self.assertTrue(result["has_defects"])
        self.assertFalse(result["repairable"])
        self.assertFalse(result["insert_damage"])
        self.assertEqual((result["weight_min_g"], result["weight_max_g"]), (3.0, 5.0))


if __name__ == "__main__":
    unittest.main()
