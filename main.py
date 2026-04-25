from orchestrator.run_manager import RunManager
from workflow import scenario1, scenario2
import json


choice = input("Choose scenario (1 or 2): ")

if choice == "1":
    task = scenario1.build_task()

elif choice == "2":
    task = scenario2.build_task()

else:
    print("Invalid choice")
    exit()

result = RunManager().run(task)

print("\n" + "="*60)
print("RESULT:")
print("="*60)
print(json.dumps(result, indent=2))
print("="*60)
