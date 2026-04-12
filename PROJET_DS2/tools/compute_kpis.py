def compute_kpis(df):
    kpis = {}

    kpis["average_occupancy_rate"] = df["occupancy_rate"].mean()
    kpis["total_revenue"] = df["revenue"].sum()

    revenue_by_region = df.groupby("region")["revenue"].sum()

    kpis["top_regions"] = revenue_by_region.sort_values(
        ascending=False
    ).to_dict()

    return kpis
