# run_extrapolation_tests.sh

#!/bin/bash

echo "Running extrapolation tests for all methods..."

# Test 1: Arrhenius (Chemistry)
python extrapolation_test_protocol.py --test arrhenius --plot --save results/arrhenius_extrap.json

# Test 2: Hall-Petch (Materials)
python extrapolation_test_protocol.py --test hall_petch --plot --save results/hall_petch_extrap.json

# Test 3: Impermanent Loss (DeFi)
python extrapolation_test_protocol.py --test impermanent_loss --plot --save results/il_extrap.json

# Generate summary
python generate_extrapolation_summary.py --results results/*.json --output paper_table_1.tex
