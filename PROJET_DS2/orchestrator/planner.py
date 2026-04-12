class Planner:
    def plan(self, task):

        if task.get("type") == "csv":
            return ["read_csv", "compute_kpis", "report"]

        elif task.get("type") == "api":
            return ["call_api", "process_api", "report"]

        return []
