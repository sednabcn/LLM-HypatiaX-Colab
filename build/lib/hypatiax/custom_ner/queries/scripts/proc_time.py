#!/usr/bin/env python3
import subprocess
import time
import os
# Record the start time
start_time = time.perf_counter()

# Run the external Python scripts
subprocess.run(["python3.11","../components/ruler_queries.py"])
subprocess.run(["python3.11", "../tests/test_queries.py"])

# Record the end time
end_time = time.perf_counter()

# Calculate the elapsed time
elapsed_time = end_time - start_time
if elapsed_time < 60:
    print(f"The function took {elapsed_time} seconds to run.")
elif 60<= elapsed_time and elapsed_time < 3600:
    elap,res=divmod(elapsed_time,60)
    print(f"The function took {elap} minutes and {res} seconds to run.")
else:
     elap,res=divmod(elapsed_time,3600)
     elapm,resm=divmod(elap,60)
     
     print(f"The function took {elap} hours, {elapm} minutes and {resm} seconds to run.")
     
