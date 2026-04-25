"""
Unit tests for security layer — allow-lists and path validation.
"""

import pytest
from security.allow_list import is_host_allowed, is_path_safe, redact_sensitive


class TestAllowList:
    def test_allowed_host(self):
        assert is_host_allowed("https://api.open-meteo.com/v1/forecast")
        assert is_host_allowed("http://localhost:8000/data")

    def test_blocked_host(self):
        assert not is_host_allowed("https://evil.com/steal")
        assert not is_host_allowed("https://unknown-api.net/data")

    def test_path_inside_sandbox(self):
        assert is_path_safe("data_synthetic/tourism_big.csv")

    def test_path_traversal_blocked(self):
        assert not is_path_safe("../../etc/passwd")
        assert not is_path_safe("../../../secrets.txt")

    def test_redaction(self):
        data = {
            "user": "alice",
            "api_key": "secret123",
            "token": "bearer xyz",
            "value": 42,
        }
        redacted = redact_sensitive(data)
        assert redacted["user"] == "alice"
        assert redacted["api_key"] == "***REDACTED***"
        assert redacted["token"] == "***REDACTED***"
        assert redacted["value"] == 42
