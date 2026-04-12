from visualisation import plot_revenue_by_region

def build_report(data):
    plot_revenue_by_region(data)

    return {
        "status": "success",
        "data": data
    }
