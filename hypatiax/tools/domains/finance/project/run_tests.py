# run_tests.py
import sys
import subprocess

def run(cmd):
    print(">", " ".join(cmd))
    subprocess.check_call(cmd)

if __name__ == "__main__":
    # Default: run full tests with coverage
    run([sys.executable, "-m", "pytest", "--cov=uniswap_v2_formulas_extended", "--cov-report=term-missing"])
