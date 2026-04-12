from tools.read_csv_tool import read_csv_file
from tools.compute_kpis import compute_kpis
from tools.report import build_report
from tools.api_tool import fetch_weather_data
from tools.api_tool import fetch_api_data


class Executor:
    def __init__(self):
        self.data = None
        self.kpis = None

    def execute(self, step, task):

        if step == "read_csv":
            self.data = read_csv_file(task["file"])

        elif step == "compute_kpis":
            self.data = compute_kpis(self.data)
        
        elif step == "call_api":
            self.data = fetch_api_data()

        elif step == "api_call":
            weather = fetch_weather_data()

            #fusion KPI + météo
            self.data = {
                "kpis": self.kpis,
                "weather": weather
            }

        elif step == "report":
            return build_report(self.data)
