from orchestrator.run_manager import RunManager
from workflow.scenario1 import build_task

task = build_task()
result = RunManager().run(task)

print(result)