"""
Unit tests for tool executors — schema validation and error handling.
"""

import pytest
import pandas as pd
from tools.read_csv_tool import read_csv_file, ToolError
from tools.compute_kpis import compute_kpis


class TestReadCsvTool:
    def test_valid_csv(self):
        df = read_csv_file("data_synthetic/tourism_big.csv")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert "region" in df.columns
        assert "revenue" in df.columns

    def test_missing_file(self):
        with pytest.raises(ToolError, match="FILE_NOT_FOUND"):
            read_csv_file("data_synthetic/nonexistent.csv")

    def test_path_traversal_blocked(self):
        with pytest.raises(ToolError, match="SAFETY_BLOCK"):
            read_csv_file("../../etc/passwd")

    def test_missing_required_columns(self):
        # tourism_kpis.csv is missing the 'stars' column
        with pytest.raises(ToolError, match="SCHEMA_ERROR"):
            read_csv_file(
                "data_synthetic/tourism_kpis.csv",
                required_columns=["region", "revenue", "stars"]
            )


class TestComputeKpis:
    def test_valid_kpis(self):
        df = pd.DataFrame({
            "region": ["Tunis", "Sousse", "Tunis"],
            "occupancy_rate": [0.8, 0.7, 0.9],
            "revenue": [1000, 2000, 1500],
        })
        kpis = compute_kpis(df)
        assert "average_occupancy_rate" in kpis
        assert "total_revenue" in kpis
        assert "top_regions" in kpis
        assert kpis["total_revenue"] == 4500.0

    def test_missing_columns(self):
        df = pd.DataFrame({"region": ["Tunis"], "bookings": [100]})
        with pytest.raises(ToolError, match="SCHEMA_ERROR"):
            compute_kpis(df)
