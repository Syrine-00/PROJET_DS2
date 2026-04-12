from orchestrator.run_manager import RunManager
from workflow import scenario1, scenario2
import os

print(os.listdir())
print(os.listdir("data_synthetic"))

choice = input("Choose scenario (1 or 2): ")

if choice == "1":
    task = scenario1.build_task()

elif choice == "2":
    task = scenario2.build_task()

else:
    print("Invalid choice")
    exit()

result = RunManager().run(task)

print(result)
