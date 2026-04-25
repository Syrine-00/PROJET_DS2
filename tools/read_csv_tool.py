"""
read_csv_tool — loads a tourism CSV from the sandbox.
Validates path safety, file existence, and required columns.
"""

import pandas as pd
from pathlib import Path

from security.allow_list import is_path_safe
from tools.schemas import ReadCsvInput, ReadCsvOutput


class ToolError(Exception):
    """Raised when a tool call fails validation or execution."""
    pass


# Get the sandbox root (same as in allow_list.py)
_SANDBOX_ROOT = Path(__file__).resolve().parent.parent / "data_synthetic"


def read_csv_file(file: str, required_columns: list[str] | None = None) -> pd.DataFrame:
    """
    Validated CSV reader.
    - Checks path is inside sandbox (no traversal)
    - Checks file exists
    - Checks required columns are present
    Returns a pandas DataFrame on success, raises ToolError on failure.
    """
    required_columns = required_columns or ["region", "occupancy_rate", "revenue"]

    # Schema validation
    inp = ReadCsvInput(file=file, required_columns=required_columns)

    # Safety check
    if not is_path_safe(inp.file):
        raise ToolError(
            f"SAFETY_BLOCK: path '{inp.file}' is outside the allowed sandbox."
        )

    # Resolve path relative to sandbox root
    resolved = (_SANDBOX_ROOT / inp.file).resolve()

    if not resolved.exists():
        raise ToolError(f"FILE_NOT_FOUND: '{inp.file}' does not exist.")

    df = pd.read_csv(resolved)

    missing = [c for c in inp.required_columns if c not in df.columns]
    if missing:
        raise ToolError(f"SCHEMA_ERROR: missing required columns: {missing}")

    return df
