import matplotlib.pyplot as plt

def plot_revenue_by_region(data):
    regions = list(data["top_regions"].keys())
    revenues = list(data["top_regions"].values())

    plt.figure()
    plt.bar(regions, revenues)
    plt.title("Revenue by Region")
    plt.xlabel("Region")
    plt.ylabel("Revenue")

    plt.show()
