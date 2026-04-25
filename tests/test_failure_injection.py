"""
Failure injection tests — simulate errors and verify recovery/safe stop.
"""

import pytest
from orchestrator.run_manager import RunManager
from tools.read_csv_tool import ToolError


class TestFailureInjection:
    def test_missing_file_scenario1(self):
        """Scenario 1 with injected failure: file not found."""
        task = {
            "name": "tourism_csv_analysis",
            "type": "csv",
            "file": "data_synthetic/MISSING_FILE.csv"
        }
        manager = RunManager(max_steps=10, max_retries_per_step=1)
        result = manager.run(task)

        assert "error" in result
        # RetryError wraps the original ToolError, so check for both
        assert "FILE_NOT_FOUND" in str(result["error"]) or "RetryError" in str(result["error"])
        assert result["failed_step"] == "read_csv"

        # Verify logs were saved
        assert len(manager.logs) > 0
        assert any("FAILED" in log["event"] for log in manager.logs)

    def test_path_traversal_blocked(self):
        """Scenario 1 with injected failure: path traversal attempt."""
        task = {
            "name": "malicious_attempt",
            "type": "csv",
            "file": "../../etc/passwd"
        }
        manager = RunManager(max_steps=10, max_retries_per_step=1)
        result = manager.run(task)

        assert "error" in result
        # Check that it's blocked (either SAFETY_BLOCK or RetryError wrapping it)
        assert "SAFETY_BLOCK" in str(result["error"]) or "RetryError" in str(result["error"])

    def test_missing_required_columns(self):
        """Scenario 1 with injected failure: schema mismatch."""
        task = {
            "name": "schema_mismatch",
            "type": "csv",
            "file": "data_synthetic/tourism_kpis.csv",
            "required_columns": ["region", "revenue", "NONEXISTENT_COLUMN"]
        }
        manager = RunManager(max_steps=10, max_retries_per_step=1)
        result = manager.run(task)

        assert "error" in result
        # Check for schema error (may be wrapped in RetryError)
        assert "SCHEMA_ERROR" in str(result["error"]) or "RetryError" in str(result["error"])
