"""
RunManager — orchestrates the full agent loop with:
- Bounded retries per step (via tenacity)
- Max-step policy enforcement
- Per-run isolated state (no shared mutable state)
- Structured logging with redaction
"""

import uuid
import json
import os
from datetime import datetime
from tenacity import retry, stop_after_attempt, RetryError

from orchestrator.planner import Planner
from orchestrator.executor import Executor
from orchestrator.critic import Critic
from tools.read_csv_tool import ToolError
from security.allow_list import redact_sensitive


class RunManager:
    def __init__(self, max_steps: int = 10, max_retries_per_step: int = 2):
        self.run_id = f"RUN-{uuid.uuid4()}"
        self.logs = []
        self.max_steps = max_steps
        self.max_retries_per_step = max_retries_per_step

    def log_step(self, step_id: str, step_name: str, event: str, metadata: dict = None):
        """Append a log entry with optional metadata (redacted)."""
        entry = {
            "run_id": self.run_id,
            "step_id": step_id,
            "step_name": step_name,
            "event": event,
            "timestamp": str(datetime.now()),
        }
        if metadata:
            entry["metadata"] = redact_sensitive(metadata)
        self.logs.append(entry)

    def save_logs(self):
        """Persist logs to disk as JSON."""
        os.makedirs("logs", exist_ok=True)
        with open(f"logs/{self.run_id}.json", "w") as f:
            json.dump(self.logs, f, indent=4)

    def run(self, task: dict) -> dict:
        """
        Main orchestration loop:
        1. Planner generates a feasible step sequence (backtracking)
        2. Executor runs each step with bounded retries
        3. Critic validates final output
        4. Logs are saved
        """
        self.log_step("INIT", "run_manager", "STARTED", {"task": task})

        planner = Planner(max_steps=self.max_steps)
        executor = Executor()
        critic = Critic()

        # ── Planning phase ────────────────────────────────────────────────
        try:
            steps = planner.plan(task)
            planner_stats = planner.get_stats()
            self.log_step(
                "PLAN", "planner", "SUCCESS",
                {"steps": steps, "stats": planner_stats}
            )
        except ValueError as e:
            self.log_step("PLAN", "planner", f"FAILED: {e}")
            self.save_logs()
            return {"error": str(e), "run_id": self.run_id}

        # ── Execution phase ───────────────────────────────────────────────
        result = None

        for i, step in enumerate(steps):
            step_id = f"STEP_{i+1:03}"

            try:
                self.log_step(step_id, step, "STARTED")

                # Execute with bounded retries
                result = self._execute_with_retry(executor, step, task)

                self.log_step(step_id, step, "SUCCESS", {"result_summary": str(result)[:200]})

            except (ToolError, RetryError) as e:
                self.log_step(step_id, step, f"FAILED: {str(e)}")
                self.save_logs()
                return {"error": str(e), "run_id": self.run_id, "failed_step": step}

        # ── Validation phase ──────────────────────────────────────────────
        if critic.validate(result):
            self.log_step("FINAL", "critic", "VALIDATED")
        else:
            self.log_step("FINAL", "critic", "INVALID")
            self.save_logs()
            return {"error": "Critic validation failed", "run_id": self.run_id}

        self.save_logs()
        return result

    def _execute_with_retry(self, executor: Executor, step: str, task: dict):
        """
        Execute a single step with bounded retries.
        Uses tenacity to retry on ToolError up to max_retries_per_step times.
        """
        @retry(stop=stop_after_attempt(self.max_retries_per_step + 1))
        def _attempt():
            return executor.execute(step, task)

        return _attempt()
