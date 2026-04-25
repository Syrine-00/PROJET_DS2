"""
visualisation — generates charts and saves them to disk.
Never calls plt.show() to avoid blocking in server/test environments.
"""

import os
import matplotlib
matplotlib.use("Agg")  # non-interactive backend — must be set before pyplot import
import matplotlib.pyplot as plt


OUTPUT_DIR = "logs/charts"


def plot_revenue_by_region(data: dict, run_id: str = "latest") -> str:
    """
    Plot revenue by region as a bar chart.
    Saves to logs/charts/{run_id}_revenue.png and returns the file path.
    """
    top_regions = data.get("top_regions", {})
    if not top_regions:
        return ""

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{run_id}_revenue.png")

    regions = list(top_regions.keys())
    revenues = list(top_regions.values())

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(regions, revenues, color="#2196F3")
    ax.set_title("Revenue by Region — Tunisia Tourism")
    ax.set_xlabel("Region")
    ax.set_ylabel("Revenue (TND)")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)

    return out_path
