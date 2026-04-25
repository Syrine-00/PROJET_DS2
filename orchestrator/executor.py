"""
Executor — runs individual steps with schema-validated tools.

Each Executor instance is isolated per run (no shared mutable state).
State is carried explicitly: self.df holds the loaded DataFrame,
self.kpis holds computed KPIs — both set correctly before use.
"""

import pandas as pd
from typing import Any

from tools.read_csv_tool import read_csv_file, ToolError
from tools.compute_kpis import compute_kpis
from tools.report import build_report
from tools.api_tool import fetch_weather_data, fetch_api_data


class Executor:
    def __init__(self):
        # Explicit, separate state fields — never mixed up
        self.df: pd.DataFrame | None = None
        self.kpis: dict | None = None

    def execute(self, step: str, task: dict) -> Any:
        """
        Execute a single step. Returns the step result.
        Raises ToolError on validation or execution failure.
        """

        if step == "read_csv":
            self.df = read_csv_file(
                file=task["file"],
                required_columns=task.get("required_columns"),
            )
            return {"rows_loaded": len(self.df), "columns": list(self.df.columns)}

        elif step == "compute_kpis":
            if self.df is None:
                raise ToolError("PRECONDITION_FAILED: read_csv must run before compute_kpis")
            self.kpis = compute_kpis(self.df)
            return self.kpis

        elif step == "call_api":
            self.kpis = fetch_api_data()
            return self.kpis

        elif step == "fetch_weather":
            weather = fetch_weather_data()
            # Merge weather into kpis
            combined = {"kpis": self.kpis or {}, "weather": weather}
            self.kpis = combined
            return combined

        elif step == "report":
            data = self.kpis or {}
            return build_report(data)

        else:
            raise ToolError(f"UNKNOWN_STEP: '{step}' is not a registered tool.")
