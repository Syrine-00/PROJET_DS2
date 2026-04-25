"""
compute_kpis — computes tourism KPIs from a DataFrame.
Validates that required columns exist before computing.
"""

import pandas as pd
from tools.schemas import ComputeKpisOutput
from tools.read_csv_tool import ToolError


def compute_kpis(df: pd.DataFrame) -> dict:
    """
    Compute KPIs from a tourism DataFrame.
    Returns a validated dict matching ComputeKpisOutput.
    Raises ToolError if required columns are missing.
    """
    required = ["occupancy_rate", "revenue", "region"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ToolError(f"SCHEMA_ERROR: missing columns for KPI computation: {missing}")

    average_occupancy_rate = round(float(df["occupancy_rate"].mean()), 4)
    total_revenue = round(float(df["revenue"].sum()), 2)

    revenue_by_region = (
        df.groupby("region")["revenue"]
        .sum()
        .sort_values(ascending=False)
        .to_dict()
    )
    top_regions = {k: round(float(v), 2) for k, v in revenue_by_region.items()}

    # Validate output shape
    output = ComputeKpisOutput(
        average_occupancy_rate=average_occupancy_rate,
        total_revenue=total_revenue,
        top_regions=top_regions,
    )

    return output.model_dump()
