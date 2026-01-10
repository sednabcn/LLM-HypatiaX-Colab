To run for all 5 domains, use the --all flag:
🚀 Run All Domains
Neural Network Baseline (5 domains, 20 test cases):
bashpython hypatiax/core/training/baseline_neural_network.py --all
Pure LLM Baseline (5 domains, 20 test cases):
bashpython hypatiax/core/generation/baseline_pure_llm.py --all
```

---

## ⏱️ Expected Runtime

**Neural Network:**
- ~200 epochs × 8 test cases = **~2-3 minutes total**
- Fast because it's just gradient descent

**Pure LLM:**
- ~8 seconds per API call × 20 test cases = **~160 seconds = ~3 minutes**
- Plus 1 second delays between calls = **~5-6 minutes total**

---

## 📊 The 5 Domains You'll Test

1. **Materials** (4 test cases)
   - Hall-Petch ⭐
   - Gibson-Ashby
   - Thermal expansion
   - Power law creep

2. **Fluids** (4 test cases)
   - Darcy-Weisbach ⭐
   - Reynolds number
   - Bernoulli equation
   - Hagen-Poiseuille

3. **Thermodynamics** (4 test cases)
   - Newton's law of cooling
   - Ideal gas law
   - Carnot efficiency
   - Stefan-Boltzmann law

4. **Mechanics** (4 test cases)
   - Euler buckling
   - Hooke's law
   - Torsional stress
   - Bending stress

5. **Chemistry** (4 test cases)
   - Arrhenius equation
   - Henderson-Hasselbalch
   - Beer-Lambert law
   - Nernst equation

---

## 💾 Output Files

Both will create timestamped files in `hypatiax/data/results/`:

**Neural Network:**
- `baseline_neural_network_YYYYMMDD_HHMMSS.json`
- `nn_experiment_report_YYYYMMDD_HHMMSS.json`

**Pure LLM:**
- `baseline_pure_llm_YYYYMMDD_HHMMSS.json`
- `experiment_report_YYYYMMDD_HHMMSS.json`

---

## 🎯 What to Look For in Results

Compare the final summaries:

### Expected Neural Network Performance:
```
📈 R² Score Statistics:
   Mean:   ~0.95-0.99  (excellent interpolation)

🎯 Performance by Domain:
   materials   : 4/4 (100.0%)  R²=0.998
   fluids      : 4/4 (100.0%)  R²=0.956
   thermodynamics: 4/4 (100.0%)  R²=0.992
   mechanics   : 4/4 (100.0%)  R²=0.989
   chemistry   : 4/4 (100.0%)  R²=0.971
```

### Expected Pure LLM Performance:
```
📈 R² Score Statistics:
   Mean:   ~0.70-0.95?  (depends on formula accuracy)

🎯 Performance by Domain:
   materials   : ?/4 (?%)  R²=???
   fluids      : ?/4 (?%)  R²=???
   ...

🔬 Key Research Questions to Answer
After running both:

Which method gets better R² scores?

Likely: NN wins on interpolation


Which method provides interpretable formulas?

Only: Pure LLM (NN is black box)


Which test cases does Pure LLM nail perfectly?

Look for R² = 1.0 (exact formula match)


Which test cases does Pure LLM struggle with?

Complex formulas with multiple terms
Non-standard mathematical relationships


How often does Pure LLM generate executable code?

Success rate across all 20 test cases




🏃 Quick Command Summary
bash# Run everything (recommended for complete comparison)
python hypatiax/core/training/baseline_neural_network.py --all
python hypatiax/core/generation/baseline_pure_llm.py --all

# Or run specific domains
python hypatiax/core/training/baseline_neural_network.py --domain materials,fluids,thermodynamics
python hypatiax/core/generation/baseline_pure_llm.py --domain materials,fluids,thermodynamics
