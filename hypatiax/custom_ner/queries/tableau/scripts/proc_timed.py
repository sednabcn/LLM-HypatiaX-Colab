#!/usr/bin/env python3
import os
import subprocess
import time

from hypatiax.utils.utils import elapsed_run_time, run_script

# Record the start time
start_time = time.perf_counter()

# Run scripts
run_script("../components/ruler_tableau_desc.py")
run_script("../tests/test_tableau_desc.py")

# Record the end time
end_time = time.perf_counter()

# Calculate the elapsed time
elapsed_run_time(start_time, end_time)
