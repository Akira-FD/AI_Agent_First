import unittest

from app.tools.ops_tools import RestartMockServiceTool
from app.tools.validators import validate_tool_input


class ToolValidationTests(unittest.TestCase):
    def test_repairs_common_service_name_aliases(self) -> None:
        valid, repaired, error = validate_tool_input(
            {"service": "redis"},
            required_fields=["service_name"],
            aliases={"service_name": ["service", "serviceName", "name"]},
        )

        self.assertTrue(valid)
        self.assertIsNone(error)
        self.assertEqual(repaired["service_name"], "redis")

    def test_returns_structured_error_for_missing_required_fields(self) -> None:
        valid, repaired, error = validate_tool_input(
            {},
            required_fields=["service_name"],
            aliases={"service_name": ["service"]},
        )

        self.assertFalse(valid)
        self.assertIsNone(repaired)
        self.assertEqual(error["error_type"], "validation_error")
        self.assertEqual(error["missing_fields"], ["service_name"])

    def test_tool_returns_validation_result_instead_of_raising(self) -> None:
        result = RestartMockServiceTool().run({})

        self.assertFalse(result.success)
        self.assertEqual(result.code, "VALIDATION_ERROR")
        self.assertEqual(result.error_code, "VALIDATION_ERROR")
        self.assertTrue(result.retryable)
        self.assertEqual(result.data["missing_fields"], ["service_name"])
        self.assertIn("missing_fields", result.diagnostics)


if __name__ == "__main__":
    unittest.main()
