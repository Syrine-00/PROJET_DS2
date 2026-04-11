from tools.read_csv_tool import read_csv_file
from tools.compute_kpis import compute_kpis
from tools.report import build_report
from tools.api_tool import fetch_weather

class Executor:
    def __init__(self):
        self.data = None

    def execute(self, step):
        if step == "read_csv":
            self.data = read_csv_file("data_synthetic/tourism_kpis.csv")

        elif step == "compute_kpis":
            self.data = compute_kpis(self.data)
        elif step == "api_call":
            self.data = fetch_weather()

        elif step == "report":
            return build_report(self.data)
