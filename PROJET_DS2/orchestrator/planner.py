class Planner:
    def plan(self, task):

        if task["type"] == "api":
            return ["api_call", "report"]

        return ["read_csv", "compute_kpis", "report"]
