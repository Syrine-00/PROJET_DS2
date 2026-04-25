"""
Backtracking Planner — models planning as a constrained search problem.

State: (step_index, remaining_objectives, budget_remaining)
Decision: which tool to call next
Pruning rules:
- budget exhausted → prune
- required objective already satisfied → skip
- step not in allow-list for task type → prune

The planner returns an ordered list of steps (a feasible plan).
It records explored branches and pruned branches for observability.
"""

from dataclasses import dataclass, field
from typing import Optional


# ── Step definitions ──────────────────────────────────────────────────────────

# Maps task type → candidate step sequences (ordered alternatives)
STEP_CANDIDATES = {
    "csv": [
        ["read_csv", "compute_kpis", "report"],
        ["read_csv", "report"],                   # fallback: skip KPIs
    ],
    "api": [
        ["call_api", "report"],
        ["call_api", "fetch_weather", "report"],  # enriched variant
    ],
}

# Steps that satisfy each objective
OBJECTIVE_STEPS = {
    "data_loaded":    {"read_csv", "call_api"},
    "kpis_computed":  {"compute_kpis", "call_api"},
    "report_ready":   {"report"},
}

# Required objectives per task type
REQUIRED_OBJECTIVES = {
    "csv": ["data_loaded", "kpis_computed", "report_ready"],
    "api": ["data_loaded", "kpis_computed", "report_ready"],
}


@dataclass
class PlannerStats:
    branches_explored: int = 0
    branches_pruned: int = 0
    depth_reached: int = 0
    plan_found: bool = False


class Planner:
    def __init__(self, max_steps: int = 10):
        self.max_steps = max_steps
        self.stats = PlannerStats()

    def plan(self, task: dict) -> list[str]:
        """
        Entry point. Returns a feasible ordered step list for the task.
        Uses backtracking over candidate sequences.
        Raises ValueError if no feasible plan is found.
        """
        task_type = task.get("type", "")
        candidates = STEP_CANDIDATES.get(task_type, [])
        required_objectives = REQUIRED_OBJECTIVES.get(task_type, [])

        self.stats = PlannerStats()

        for sequence in candidates:
            self.stats.branches_explored += 1

            result = self._backtrack(
                steps=sequence,
                index=0,
                satisfied=set(),
                required=set(required_objectives),
                budget=self.max_steps,
                task=task,
            )

            if result is not None:
                self.stats.plan_found = True
                self.stats.depth_reached = len(result)
                return result

            self.stats.branches_pruned += 1

        raise ValueError(
            f"No feasible plan found for task type '{task_type}'. "
            f"Explored {self.stats.branches_explored} branches, "
            f"pruned {self.stats.branches_pruned}."
        )

    def _backtrack(
        self,
        steps: list[str],
        index: int,
        satisfied: set,
        required: set,
        budget: int,
        task: dict,
    ) -> Optional[list[str]]:
        """
        Recursive backtracking search.
        Returns a valid step list or None if this branch is infeasible.
        """
        # ── Pruning: budget exhausted ─────────────────────────────────────
        if budget <= 0:
            self.stats.branches_pruned += 1
            return None

        # ── Base case: all steps consumed ─────────────────────────────────
        if index >= len(steps):
            # Check all required objectives are satisfied
            if required.issubset(satisfied):
                return []
            self.stats.branches_pruned += 1
            return None

        step = steps[index]

        # ── Pruning: step not valid for this task ─────────────────────────
        if not self._is_step_feasible(step, task):
            self.stats.branches_pruned += 1
            return None

        # ── Include this step ─────────────────────────────────────────────
        new_satisfied = satisfied | self._objectives_satisfied_by(step)
        rest = self._backtrack(
            steps, index + 1, new_satisfied, required, budget - 1, task
        )
        if rest is not None:
            return [step] + rest

        # ── Skip this step (only if it's not strictly required) ───────────
        if not self._is_step_required(step, required, satisfied):
            rest_skip = self._backtrack(
                steps, index + 1, satisfied, required, budget - 1, task
            )
            if rest_skip is not None:
                return rest_skip

        return None

    def _is_step_feasible(self, step: str, task: dict) -> bool:
        """Check if a step is valid given the task context."""
        task_type = task.get("type", "")

        # csv tasks must not call API steps
        if task_type == "csv" and step in {"call_api", "fetch_weather"}:
            return False

        # api tasks must not call read_csv
        if task_type == "api" and step == "read_csv":
            return False

        # read_csv requires a file path
        if step == "read_csv" and not task.get("file"):
            return False

        return True

    def _objectives_satisfied_by(self, step: str) -> set:
        """Return the set of objectives this step satisfies."""
        return {
            obj for obj, steps in OBJECTIVE_STEPS.items()
            if step in steps
        }

    def _is_step_required(self, step: str, required: set, satisfied: set) -> bool:
        """Return True if skipping this step would leave a required objective unsatisfied."""
        would_satisfy = self._objectives_satisfied_by(step)
        still_needed = required - satisfied
        return bool(would_satisfy & still_needed)

    def get_stats(self) -> dict:
        return {
            "branches_explored": self.stats.branches_explored,
            "branches_pruned": self.stats.branches_pruned,
            "depth_reached": self.stats.depth_reached,
            "plan_found": self.stats.plan_found,
        }
