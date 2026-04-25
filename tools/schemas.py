"""
Pydantic schemas for all tool inputs and outputs.
Every tool call must be validated against these before execution.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any


# ── read_csv_tool ────────────────────────────────────────────────────────────

class ReadCsvInput(BaseModel):
    file: str = Field(..., description="Relative path to CSV file inside sandbox")
    required_columns: list[str] = Field(
        default=["region", "occupancy_rate", "revenue"],
        description="Columns that must exist in the CSV"
    )

class ReadCsvOutput(BaseModel):
    row_count: int
    columns: list[str]
    status: str = "ok"


# ── compute_kpis ─────────────────────────────────────────────────────────────

class ComputeKpisInput(BaseModel):
    source: str = Field(default="dataframe", description="Source identifier")

class ComputeKpisOutput(BaseModel):
    average_occupancy_rate: float
    total_revenue: float
    top_regions: Dict[str, float]
    status: str = "ok"


# ── fetch_api_data ────────────────────────────────────────────────────────────

class FetchApiInput(BaseModel):
    url: Optional[str] = Field(default=None, description="Optional override URL")
    timeout: int = Field(default=10, ge=1, le=30)

class FetchApiOutput(BaseModel):
    top_regions: Dict[str, float]
    total_revenue: float
    average_occupancy_rate: float
    status: str = "ok"


# ── fetch_weather_data ────────────────────────────────────────────────────────

class FetchWeatherInput(BaseModel):
    latitude: float = Field(default=36.8)
    longitude: float = Field(default=10.1)
    timeout: int = Field(default=10, ge=1, le=30)

class FetchWeatherOutput(BaseModel):
    temperature: float
    windspeed: float
    tourism_impact: str
    status: str = "ok"


# ── report ────────────────────────────────────────────────────────────────────

class BuildReportInput(BaseModel):
    data: Dict[str, Any]

class BuildReportOutput(BaseModel):
    status: str
    data: Dict[str, Any]
