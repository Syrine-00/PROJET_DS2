"""Quick test script for Scenario 1"""
from workflow.scenario1 import build_task
from orchestrator.run_manager import RunManager
import json

print("=" * 60)
print("Testing Scenario 1: CSV Analysis")
print("=" * 60)

task = build_task()
print(f"\nTask: {task}")

manager = RunManager(max_steps=10, max_retries_per_step=2)
result = manager.run(task)

print("\n" + "=" * 60)
print("RESULT:")
print("=" * 60)
print(json.dumps(result, indent=2))
print("=" * 60)
