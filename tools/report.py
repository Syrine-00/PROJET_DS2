"""
report — builds the final structured report.
Does NOT call plt.show() to avoid blocking in non-interactive environments.
Chart is saved to file instead.
"""

from tools.schemas import BuildReportInput, BuildReportOutput
from tools.visualisation import plot_revenue_by_region


def build_report(data: dict) -> dict:
    """
    Build and return a structured report dict.
    Saves a chart to disk (non-blocking).
    """
    # Validate input
    inp = BuildReportInput(data=data)

    # Generate chart (saved to file, not shown interactively)
    if "top_regions" in inp.data:
        plot_revenue_by_region(inp.data)

    output = BuildReportOutput(status="success", data=inp.data)
    return output.model_dump()
