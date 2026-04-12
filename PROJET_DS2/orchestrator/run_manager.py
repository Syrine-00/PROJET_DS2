import uuid
import json
import os
from datetime import datetime

from orchestrator.planner import Planner
from orchestrator.executor import Executor
from orchestrator.critic import Critic


class RunManager:
    def __init__(self):
        self.run_id = f"RUN-{uuid.uuid4()}"
        self.logs = []

    def log_step(self, step_id, step_name, event):
        self.logs.append({
            "run_id": self.run_id,
            "step_id": step_id,
            "step_name": step_name,
            "event": event,
            "timestamp": str(datetime.now())
        })

    def save_logs(self):
        os.makedirs("logs", exist_ok=True)

        with open(f"logs/{self.run_id}.json", "w") as f:
            json.dump(self.logs, f, indent=4)

    def run(self, task):
        planner = Planner()
        executor = Executor()
        critic = Critic()

        steps = planner.plan(task)

        result = None

        for i, step in enumerate(steps):
            step_id = f"STEP_{i+1:03}"

            try:
                self.log_step(step_id, step, "STARTED")

                result = executor.execute(step, task)

                self.log_step(step_id, step, "SUCCESS")

            except Exception as e:
                self.log_step(step_id, step, f"FAILED: {str(e)}")
                self.save_logs()
                return {"error": str(e)}

        if critic.validate(result):
            self.log_step("FINAL", "critic", "VALIDATED")
        else:
            self.log_step("FINAL", "critic", "INVALID")

        self.save_logs()

        return result
