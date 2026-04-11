from orchestrator.planner import Planner
from orchestrator.executor import Executor
from orchestrator.critic import Critic

class RunManager:
    def run(self, task):
        planner = Planner()
        executor = Executor()
        critic = Critic()

        steps = planner.plan(task)

        result = None
        for step in steps:
            result = executor.execute(step)

        if critic.validate(result):
            return result
        else:
            return {"error": "Invalid result"}