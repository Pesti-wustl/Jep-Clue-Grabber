import subprocess
import sys


for i in range(18, 19):
    print("Running HTML and JSON download script")
    subprocess.run([sys.executable, "dwnload.py", str(i)], check=True)
    print("HTML and JSON dwnload done")

    print("Running send JSON to mongo script")
    subprocess.run([sys.executable, "jsonsender.py", str(i)], check=True)
    print(f"Game {i} saved to mongoDB!")


