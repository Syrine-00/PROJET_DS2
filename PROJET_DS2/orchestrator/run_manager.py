import uuid
import json
import os
from datetime import datetime

from orchestrator.planner import Planner
from orchestrator.executor import Executor
from orchestrator.critic import Critic


class RunManager:
    def __init__(self):
        self.run_id = str(uuid.uuid4())
        self.logs = []

    def log_step(self, step, status):
        self.logs.append({
            "step": step,
            "status": status,
            "timestamp": str(datetime.now())
        })

    def save_logs(self):
        os.makedirs("logs", exist_ok=True)

        with open(f"logs/{self.run_id}.json", "w") as f:
            json.dump({
                "run_id": self.run_id,
                "steps": self.logs
            }, f, indent=4)

    def run(self, task):
        planner = Planner()
        executor = Executor()
        critic = Critic()

        steps = planner.plan(task)
        result = None

        for step in steps:
            try:
                result = executor.execute(step, task)
                self.log_step(step, "success")
            except Exception as e:
                self.log_step(step, f"error: {str(e)}")
                self.save_logs()
                return {"error": str(e)}

        self.save_logs()

        if critic.validate(result):
            return result
        else:
            return {"error": "Invalid result"}
