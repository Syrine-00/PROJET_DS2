"""
Unit tests for backtracking planner — feasibility, pruning, stats.
"""

import pytest
from orchestrator.planner import Planner


class TestPlanner:
    def test_csv_task_plan(self):
        planner = Planner(max_steps=10)
        task = {"type": "csv", "file": "data_synthetic/tourism_big.csv"}
        steps = planner.plan(task)

        assert "read_csv" in steps
        assert "compute_kpis" in steps
        assert "report" in steps
        assert planner.stats.plan_found is True

    def test_api_task_plan(self):
        planner = Planner(max_steps=10)
        task = {"type": "api"}
        steps = planner.plan(task)

        assert "call_api" in steps
        assert "report" in steps
        assert planner.stats.plan_found is True

    def test_no_plan_for_invalid_task(self):
        planner = Planner(max_steps=10)
        task = {"type": "unknown"}

        with pytest.raises(ValueError, match="No feasible plan"):
            planner.plan(task)

    def test_pruning_stats(self):
        planner = Planner(max_steps=10)
        task = {"type": "csv", "file": "data_synthetic/tourism_big.csv"}
        planner.plan(task)

        stats = planner.get_stats()
        assert stats["branches_explored"] > 0
        assert stats["plan_found"] is True
