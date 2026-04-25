"""
Allow-list and safety enforcement for tool calls.
Protects against path traversal, unauthorized HTTP hosts,
and unsafe tool arguments.
"""

import os
from pathlib import Path

#HTTP allow-list
ALLOWED_HOSTS = {
    "api.open-meteo.com",
    "api.worldbank.org",
    "localhost",
    "127.0.0.1",
}

#Filesystem sandbox
# All CSV/file reads must stay inside this directory
# Use __file__ to get the script location, then go up to project root
_SANDBOX_ROOT = Path(__file__).resolve().parent.parent / "data_synthetic"


def is_host_allowed(url: str) -> bool:
    """Return True if the URL's hostname is in the allow-list."""
    from urllib.parse import urlparse
    host = urlparse(url).hostname or ""
    return host in ALLOWED_HOSTS


def is_path_safe(file_path: str) -> bool:
    """
    Return True if file_path resolves inside the sandbox root.
    Blocks path traversal (../../etc/passwd style attacks).
    """
    try:
        # Resolve the file path relative to the sandbox root, not cwd
        resolved = (_SANDBOX_ROOT / file_path).resolve()
        resolved.relative_to(_SANDBOX_ROOT.resolve())
        return True
    except ValueError:
        return False


def redact_sensitive(data: dict) -> dict:
    """
    Return a copy of data with sensitive keys masked.
    Used before writing to logs or displaying in GUI.
    """
    SENSITIVE_KEYS = {"token", "api_key", "password", "secret", "authorization"}
    result = {}
    for k, v in data.items():
        if k.lower() in SENSITIVE_KEYS:
            result[k] = "***REDACTED***"
        elif isinstance(v, dict):
            result[k] = redact_sensitive(v)
        else:
            result[k] = v
    return result
