#!/usr/bin/env python3
import subprocess
import time
import os
from hypatiax.utils.utils import run_script,elapsed_run_time
# Record the start time
start_time = time.perf_counter()

# Run scripts
run_script("../components/ruler_queries_desc.py")
run_script("../tests/test_queries_desc.py")

# Record the end time
end_time = time.perf_counter()

# Calculate the elapsed time
elapsed_run_time(start_time,end_time)
     
