# check_if_should_run.py
import os
from datetime import datetime


# Get total minutes used this month from a file
def get_minutes_used():
    try:
        with open(".ci/minutes.txt", "r") as f:
            return int(f.read())
    except:
        return 0


def save_minutes(total):
    os.makedirs(".ci", exist_ok=True)
    with open(".ci/minutes.txt", "w") as f:
        f.write(str(total))


# Check limit
used = get_minutes_used()
if used > 900:  # 90% of 1000
    print("⛔ Skip - near monthly limit")
    exit(1)

print("✅ OK to run")
