import subprocess
import sys


for i in range(7000, 70001):
    print("Running HTML and JSON download script")
    subprocess.run([sys.executable, "dwnload.py", str(i)], check=True)
    print("HTML and JSON dwnload done")

    print("Running send JSON to postgres script")
    subprocess.run([sys.executable, "jsonsender.py", str(i)], check=True)
    print(f"Game {i} saved to postgres!")


