
╔══════════════════════════════════════════════════════════════════════╗
  HypatiaX Complete Analysis Pipeline
╚══════════════════════════════════════════════════════════════════════╝

Started at: Fri Dec 26 12:13:32 PM GMT 2025
Project Root: /home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab
Log File: /home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab/logs/pipeline_20251226_121332.log

⚠ Running in QUICK mode (skipping baselines)
🤖 LLM Interpretation: ENABLED

▶ Checking prerequisites
✓ Python found: Python 3.12.2
✓ Results directory is writable
✓ Disk space: 6GB available


╔══════════════════════════════════════════════════════════════════════╗
║  PHASE 1: EXPERIMENTATION
╚══════════════════════════════════════════════════════════════════════╝

▶ Running Hybrid System Experiments
✓ 🤖 LLM Interpretation: ENABLED (Hybrid Mode)
▶ Running: complete_hybrid_system_all_domains.py
[2025-12-26 12:13:32] Starting: Hybrid System (All Domains)
✓ Working directory: /home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab
2025-12-26 12:15:31,965 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 12:15:31,965 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: biology | Primary LLM: anthropic | Fallback: True
2025-12-26 12:15:31,966 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 12:15:31,966 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=biology)...
2025-12-26 12:15:33,233 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:15:33,235 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:15:33,249 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 12:15:33,467 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 12:15:34,587 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 12:15:34,587 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 12:17:13,936 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 12:17:13,936 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: biology | Primary LLM: anthropic | Fallback: True
2025-12-26 12:17:13,936 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 12:17:13,937 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=biology)...
2025-12-26 12:17:14,820 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:17:14,822 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:17:14,832 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 12:17:14,955 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 12:17:15,054 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 12:17:15,054 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(

================================================================================
                 HYBRID SYSTEM - BATCH TEST SUITE (ALL DOMAINS)                 
================================================================================

📋 Test Cases: 18
📊 Samples per test: 200
🤖 LLM Interpretation: Enabled

================================================================================
TEST 1/18: michaelis_menten
================================================================================

================================================================================
                BIOLOGY Hybrid System: Michaelis-Menten Kinetics                
================================================================================

📝 Description: v = (Vmax * [S]) / (Km + [S])
🎯 Ground Truth: (Vmax * S) / (Km + S)
📊 Samples: 200
🤖 LLM Enabled: True

⏳ Generating synthetic data...
✅ Data generated: Features (200, 3), Targets (200,)

⏳ Initializing Hybrid Discovery System...
✅ Anthropic Provider initialized
   Model: claude-sonnet-4-20250514
   Max tokens: 4096
   ✅ Using model: models/gemini-2.5-flash
✅ Google Provider initialized
   Model: models/gemini-2.5-flash
   Max output tokens: 8192
✅ System initialized

================================================================================
                           EXECUTING HYBRID WORKFLOW                            
================================================================================

======================================================================
WORKFLOW: Michaelis-Menten Kinetics
Domain: BIOLOGY | Primary LLM: ANTHROPIC
Fallback: Enabled
======================================================================

[1/3] 🔍 Discovering symbolic expression from 200 samples...
✅ Found: -sqrt(vmax)*log(km) + 1.21721087257448*sqrt(vmax*sqrt(substrate_concentration*vmax))
   R² Score: 0.9657
   Complexity: 15

[2/3] ✓ Validating expression across 4 layers...
✗ Overall Score: 52.5/100
   Layer Scores:
     ✓ Symbolic: 71.0
     ⚠ Dimensional: 54.0
     ✓ Domain: 100.0
     ✓ Numerical: 100.0

   ⚠ Errors: 1 detected
     - Incompatible units in addition: micrometer ** 0.5 / second ** 0.5 ((-sqrt(vmax))*log(km)) vs micrometer / second ** 0.75 (1.21721087257448*sqrt(vmax*sqrt(substrate_concentration*vmax)))

   ℹ Warnings: 7

[3/3] ⊗ Interpretation skipped (score 52.5 < 85.0)
   Top recommendations:
     • 🔴 FIX CRITICAL: Resolve dimensional inconsistencies before deployment
     •   → Incompatible units in addition: micrometer ** 0.5 / second ** 0.5 ((-sqrt(vmax))*log(km)) vs micrometer / second ** 0.75 (1.21721087257448*sqrt(vmax*sqrt(substrate_concentration*vmax)))
     • 🟡 IMPROVE: Simplify to: -sqrt(vmax)*log(km) + 1.21721087257448*sqrt(vmax*sqrt(substrate_concentration*vmax))

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   -sqrt(vmax)*log(km) + 1.21721087257448*sqrt(vmax*sqrt(substrate_concentration*vmax))

📊 Model Performance:
   • R² Score:    0.965704
   • Complexity:  15

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

❌ FAIL Overall Valid: False
📊 Total Score: 52.50/100

📋 Layer Performance:
   ✅ Symbolic      :  71.00/100
   ⚠ Dimensional   :  54.00/100
   ✅ Domain        : 100.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9657
❌ Validation: Score = 52.50/100

========================================
      OVERALL: ❌ NEEDS IMPROVEMENT      
========================================


================================================================================
TEST 2/18: logistic_growth
================================================================================

================================================================================
                  BIOLOGY Hybrid System: Logistic Growth Model                  
================================================================================

📝 Description: dN/dt = r * N * (1 - N/K)
🎯 Ground Truth: r * N * (1 - N / K)
📊 Samples: 200
🤖 LLM Enabled: True

⏳ Generating synthetic data...
✅ Data generated: Features (200, 3), Targets (200,)

⏳ Initializing Hybrid Discovery System...
✅ Anthropic Provider initialized
   Model: claude-sonnet-4-20250514
   Max tokens: 4096
   ✅ Using model: models/gemini-2.5-flash
✅ Google Provider initialized
   Model: models/gemini-2.5-flash
   Max output tokens: 8192
✅ System initialized

================================================================================
                           EXECUTING HYBRID WORKFLOW                            
================================================================================

======================================================================
WORKFLOW: Logistic Growth Model
Domain: BIOLOGY | Primary LLM: ANTHROPIC
Fallback: Enabled
======================================================================

[1/3] 🔍 Discovering symbolic expression from 200 samples...
✅ Found: 1.94143430413872*sqrt(carrying_capacity**growth_rate*(population - 865.1896*population/carrying_capacity))
   R² Score: 0.9142
   Complexity: 18

[2/3] ✓ Validating expression across 4 layers...
✗ Overall Score: 76.1/100
   Layer Scores:
     ✓ Symbolic: 71.0
     ⚠ Dimensional: 69.0
     ✓ Domain: 97.0
     ✓ Numerical: 100.0

   ℹ Warnings: 9

[3/3] ⊗ Interpretation skipped (score 76.1 < 85.0)
   Top recommendations:
     • 🟡 VERIFY: Check dimensional analysis warnings
     • 🟡 IMPROVE: Simplify to: 1.94143430413872*sqrt(carrying_capacity**(growth_rate - 1)*population*(carrying_capacity - 865.1896))
     • 🟡 REVIEW: Address biology domain warnings

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   1.94143430413872*sqrt(carrying_capacity**growth_rate*(population - 865.1896*population/carrying_capacity))

📊 Model Performance:
   • R² Score:    0.914212
   • Complexity:  18

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

❌ FAIL Overall Valid: False
📊 Total Score: 76.10/100

📋 Layer Performance:
   ✅ Symbolic      :  71.00/100
   ⚠ Dimensional   :  69.00/100
   ✅ Domain        :  97.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9142
❌ Validation: Score = 76.10/100

========================================
      OVERALL: ❌ NEEDS IMPROVEMENT      
========================================


================================================================================
TEST 3/18: allometric_scaling
================================================================================

================================================================================
                 BIOLOGY Hybrid System: Allometric Scaling Law                  
2025-12-26 12:18:03,025 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 12:18:03,026 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: biology | Primary LLM: anthropic | Fallback: True
2025-12-26 12:18:03,026 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 12:18:03,026 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=biology)...
2025-12-26 12:18:03,880 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:18:03,882 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:18:03,892 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 12:18:03,919 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 12:18:04,033 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 12:18:04,034 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 12:18:48,304 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 12:18:48,304 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: chemistry | Primary LLM: anthropic | Fallback: True
2025-12-26 12:18:48,305 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 12:18:48,305 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=chemistry)...
2025-12-26 12:18:49,208 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:18:49,210 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:18:49,219 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 12:18:49,246 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 12:18:49,340 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 12:18:49,341 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 12:19:46,507 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 12:19:46,507 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: chemistry | Primary LLM: anthropic | Fallback: True
2025-12-26 12:19:46,507 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 12:19:46,508 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=chemistry)...
2025-12-26 12:19:47,448 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:19:47,450 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:19:47,464 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 12:19:47,493 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 12:19:47,606 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 12:19:47,606 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
================================================================================

📝 Description: Y = a * M^b (e.g., metabolic rate ∝ mass^0.75)
🎯 Ground Truth: a * M**b
📊 Samples: 200
🤖 LLM Enabled: True

⏳ Generating synthetic data...
✅ Data generated: Features (200, 3), Targets (200,)

⏳ Initializing Hybrid Discovery System...
✅ Anthropic Provider initialized
   Model: claude-sonnet-4-20250514
   Max tokens: 4096
   ✅ Using model: models/gemini-2.5-flash
✅ Google Provider initialized
   Model: models/gemini-2.5-flash
   Max output tokens: 8192
✅ System initialized

================================================================================
                           EXECUTING HYBRID WORKFLOW                            
================================================================================

======================================================================
WORKFLOW: Allometric Scaling Law
Domain: BIOLOGY | Primary LLM: ANTHROPIC
Fallback: Enabled
======================================================================

[1/3] 🔍 Discovering symbolic expression from 200 samples...
✅ Found: coefficient*mass**exponent
   R² Score: 0.9994
   Complexity: 5

[2/3] ✓ Validating expression across 4 layers...
✗ Overall Score: 81.4/100
   Layer Scores:
     ✓ Symbolic: 73.0
     ⚠ Dimensional: 65.0
     ✓ Domain: 100.0
     ✓ Numerical: 100.0

   ⚠ Errors: 2 detected
     - Invalid unit for 'coefficient': 'dimensionless' - 'Unit' object has no attribute 'units'
     - Invalid unit for 'exponent': 'dimensionless' - 'Unit' object has no attribute 'units'

   ℹ Warnings: 4

[3/3] ⊗ Interpretation skipped (score 81.4 < 85.0)
   Top recommendations:
     • 🔴 FIX CRITICAL: Resolve dimensional inconsistencies before deployment
     •   → Invalid unit for 'coefficient': 'dimensionless' - 'Unit' object has no attribute 'units'
     •   → Invalid unit for 'exponent': 'dimensionless' - 'Unit' object has no attribute 'units'

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   coefficient*mass**exponent

📊 Model Performance:
   • R² Score:    0.999374
   • Complexity:  5

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

❌ FAIL Overall Valid: False
📊 Total Score: 81.40/100

📋 Layer Performance:
   ✅ Symbolic      :  73.00/100
   ⚠ Dimensional   :  65.00/100
   ✅ Domain        : 100.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9994
❌ Validation: Score = 81.40/100

========================================
      OVERALL: ❌ NEEDS IMPROVEMENT      
========================================


================================================================================
TEST 4/18: arrhenius_equation
================================================================================

================================================================================
                  CHEMISTRY Hybrid System: Arrhenius Equation                   
================================================================================

📝 Description: k = A * exp(-Ea / (R * T))
🎯 Ground Truth: A * np.exp(-Ea / (R * T))
📊 Samples: 200
🤖 LLM Enabled: True

⏳ Generating synthetic data...
✅ Data generated: Features (200, 3), Targets (200,)

⏳ Initializing Hybrid Discovery System...
✅ Anthropic Provider initialized
   Model: claude-sonnet-4-20250514
   Max tokens: 4096
   ✅ Using model: models/gemini-2.5-flash
✅ Google Provider initialized
   Model: models/gemini-2.5-flash
   Max output tokens: 8192
✅ System initialized

================================================================================
                           EXECUTING HYBRID WORKFLOW                            
================================================================================

======================================================================
WORKFLOW: Arrhenius Equation
Domain: CHEMISTRY | Primary LLM: ANTHROPIC
Fallback: Enabled
======================================================================

[1/3] 🔍 Discovering symbolic expression from 200 samples...
✅ Found: pre_exponential**(3/2)*temperature**21.82253*log(pre_exponential)/activation_energy**14.998832
   R² Score: 0.9882
   Complexity: 23

[2/3] ✓ Validating expression across 4 layers...
✗ Overall Score: 78.7/100
   Layer Scores:
     ⚠ Symbolic: 67.0
     ✓ Dimensional: 72.0
     ✓ Domain: 90.0
     ✓ Numerical: 100.0

   ℹ Warnings: 10

[3/3] ⊗ Interpretation skipped (score 78.7 < 85.0)
   Top recommendations:
     • 🟡 VERIFY: Check dimensional analysis warnings
     • 🟡 IMPROVE: Simplify to: pre_exponential**(3/2)*temperature**21.82253*log(pre_exponential)/activation_energy**14.998832

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   pre_exponential**(3/2)*temperature**21.82253*log(pre_exponential)/activation_energy**14.998832

📊 Model Performance:
   • R² Score:    0.988249
   • Complexity:  23

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

❌ FAIL Overall Valid: False
📊 Total Score: 78.70/100

📋 Layer Performance:
   ⚠ Symbolic      :  67.00/100
   ✅ Dimensional   :  72.00/100
   ✅ Domain        :  90.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9882
❌ Validation: Score = 78.70/100

========================================
      OVERALL: ❌ NEEDS IMPROVEMENT      
========================================


================================================================================
TEST 5/18: henderson_hasselbalch
================================================================================

================================================================================
            CHEMISTRY Hybrid System: Henderson-Hasselbalch Equation             
================================================================================

📝 Description: pH = pKa + log10([A-]/[HA])
🎯 Ground Truth: pKa + np.log10(base / acid + 1e-10)
📊 Samples: 200
🤖 LLM Enabled: True

⏳ Generating synthetic data...
✅ Data generated: Features (200, 3), Targets (200,)

⏳ Initializing Hybrid Discovery System...
✅ Anthropic Provider initialized
   Model: claude-sonnet-4-20250514
   Max tokens: 4096
   ✅ Using model: models/gemini-2.5-flash
✅ Google Provider initialized
   Model: models/gemini-2.5-flash
   Max output tokens: 8192
✅ System initialized

================================================================================
                           EXECUTING HYBRID WORKFLOW                            
================================================================================

======================================================================
WORKFLOW: Henderson-Hasselbalch Equation
Domain: CHEMISTRY | Primary LLM: ANTHROPIC
Fallback: Enabled
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 12:20:34,220 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 12:20:34,220 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: chemistry | Primary LLM: anthropic | Fallback: True
2025-12-26 12:20:34,221 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 12:20:34,221 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=chemistry)...
2025-12-26 12:20:35,148 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:20:35,150 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:20:35,161 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 12:20:35,267 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 12:20:35,371 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 12:20:35,371 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 12:21:14,626 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 12:21:14,626 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: economics | Primary LLM: anthropic | Fallback: True
2025-12-26 12:21:14,626 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 12:21:14,627 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=economics)...
2025-12-26 12:21:15,480 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:21:15,481 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:21:15,492 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 12:21:15,537 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 12:21:15,633 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 12:21:15,633 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
======================================================================

[1/3] 🔍 Discovering symbolic expression from 200 samples...
✅ Found: (1.07488821431293*pKa - log(acid_concentration) + 0.517341932745452*log(acid_concentration*base_concentration) - 0.0642504401398516)**0.9707528
   R² Score: 0.9983
   Complexity: 17

[2/3] ✓ Validating expression across 4 layers...
✗ Overall Score: 71.9/100
   Layer Scores:
     ✓ Symbolic: 71.0
     ⚠ Dimensional: 62.0
     ✓ Domain: 90.0
     ✓ Numerical: 100.0

   ⚠ Errors: 1 detected
     - Invalid unit for 'pKa': 'dimensionless' - 'Unit' object has no attribute 'units'

   ℹ Warnings: 7

[3/3] ⊗ Interpretation skipped (score 71.9 < 85.0)
   Top recommendations:
     • 🔴 FIX CRITICAL: Resolve dimensional inconsistencies before deployment
     •   → Invalid unit for 'pKa': 'dimensionless' - 'Unit' object has no attribute 'units'
     • 🟡 IMPROVE: Simplify to: (1.07488821431293*pKa - log(acid_concentration) + 0.517341932745452*log(acid_concentration*base_concentration) - 0.0642504401398516)**0.9707528

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   (1.07488821431293*pKa - log(acid_concentration) + 0.517341932745452*log(acid_concentration*base_concentration) - 0.0642504401398516)**0.9707528

📊 Model Performance:
   • R² Score:    0.998335
   • Complexity:  17

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

❌ FAIL Overall Valid: False
📊 Total Score: 71.90/100

📋 Layer Performance:
   ✅ Symbolic      :  71.00/100
   ⚠ Dimensional   :  62.00/100
   ✅ Domain        :  90.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9983
❌ Validation: Score = 71.90/100

========================================
      OVERALL: ❌ NEEDS IMPROVEMENT      
========================================


================================================================================
TEST 6/18: nernst_equation
================================================================================

================================================================================
             CHEMISTRY Hybrid System: Nernst Equation (Simplified)              
================================================================================

📝 Description: E = E0 - (RT/nF) * ln(Q)
🎯 Ground Truth: E0 - (R * T / (n * F)) * np.log(Q)
📊 Samples: 200
🤖 LLM Enabled: True

⏳ Generating synthetic data...
✅ Data generated: Features (200, 4), Targets (200,)

⏳ Initializing Hybrid Discovery System...
✅ Anthropic Provider initialized
   Model: claude-sonnet-4-20250514
   Max tokens: 4096
   ✅ Using model: models/gemini-2.5-flash
✅ Google Provider initialized
   Model: models/gemini-2.5-flash
   Max output tokens: 8192
✅ System initialized

================================================================================
                           EXECUTING HYBRID WORKFLOW                            
================================================================================

======================================================================
WORKFLOW: Nernst Equation (Simplified)
Domain: CHEMISTRY | Primary LLM: ANTHROPIC
Fallback: Enabled
======================================================================

[1/3] 🔍 Discovering symbolic expression from 200 samples...
✅ Found: standard_potential + (2.92148695016767*sqrt(1/(reaction_quotient*temperature)) - 0.13172275)/charge
   R² Score: 0.9990
   Complexity: 12

[2/3] ✓ Validating expression across 4 layers...
✗ Overall Score: 67.2/100
   Layer Scores:
     ✓ Symbolic: 98.0
     ⚠ Dimensional: 54.0
     ✓ Domain: 72.0
     ✓ Numerical: 100.0

   ⚠ Errors: 3 detected
     - Invalid unit for 'charge': 'dimensionless' - 'Unit' object has no attribute 'units'
     - Invalid unit for 'reaction_quotient': 'dimensionless' - 'Unit' object has no attribute 'units'
     ... and 1 more

   ℹ Warnings: 7

[3/3] ⊗ Interpretation skipped (score 67.2 < 85.0)
   Top recommendations:
     • 🔴 FIX CRITICAL: Resolve dimensional inconsistencies before deployment
     •   → Invalid unit for 'charge': 'dimensionless' - 'Unit' object has no attribute 'units'
     •   → Invalid unit for 'reaction_quotient': 'dimensionless' - 'Unit' object has no attribute 'units'

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   standard_potential + (2.92148695016767*sqrt(1/(reaction_quotient*temperature)) - 0.13172275)/charge

📊 Model Performance:
   • R² Score:    0.998982
   • Complexity:  12

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

❌ FAIL Overall Valid: False
📊 Total Score: 67.20/100

📋 Layer Performance:
   ✅ Symbolic      :  98.00/100
   ⚠ Dimensional   :  54.00/100
   ✅ Domain        :  72.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9990
❌ Validation: Score = 67.20/100

========================================
      OVERALL: ❌ NEEDS IMPROVEMENT      
========================================


================================================================================
TEST 7/18: elasticity_demand
================================================================================

================================================================================
              ECONOMICS Hybrid System: Price Elasticity of Demand               
================================================================================

📝 Description: Ed = (% change in Q) / (% change in P)
🎯 Ground Truth: (delta_Q / Q) / (delta_P / P + 1e-10)
📊 Samples: 200
🤖 LLM Enabled: True

⏳ Generating synthetic data...
✅ Data generated: Features (200, 4), Targets (200,)

⏳ Initializing Hybrid Discovery System...
✅ Anthropic Provider initialized
   Model: claude-sonnet-4-20250514
   Max tokens: 4096
   ✅ Using model: models/gemini-2.5-flash
✅ Google Provider initialized
   Model: models/gemini-2.5-flash
   Max output tokens: 8192
✅ System initialized

================================================================================
                           EXECUTING HYBRID WORKFLOW                            
================================================================================

======================================================================
WORKFLOW: Price Elasticity of Demand
Domain: ECONOMICS | Primary LLM: ANTHROPIC
Fallback: Enabled
======================================================================

[1/3] 🔍 Discovering symbolic expression from 200 samples...
✅ Found: price*(delta_quantity + 0.033015758/delta_price)/(delta_price*quantity)
   R² Score: 0.9999
   Complexity: 11

[2/3] ✓ Validating expression across 4 layers...
✓ Overall Score: 85.0/100
   Layer Scores:
     ✓ Symbolic: 71.0
     ✓ Dimensional: 82.0
     ✓ Domain: 97.0
     ✓ Numerical: 100.0
2025-12-26 12:21:41,960 - hypatiax.tools.symbolic.hybrid_system - INFO - 🤖 Interpreting with ANTHROPIC...
2025-12-26 12:21:56,603 - httpx - INFO - HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2025-12-26 12:21:56,887 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Interpretation completed via ANTHROPIC in 14.93s
2025-12-26 12:21:56,889 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 12:21:56,889 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: economics | Primary LLM: anthropic | Fallback: True
2025-12-26 12:21:56,890 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 12:21:56,891 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=economics)...
2025-12-26 12:21:57,683 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:21:57,684 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:21:57,695 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 12:21:57,730 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 12:21:57,830 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 12:21:57,831 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 12:22:38,669 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 12:22:38,669 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: engineering | Primary LLM: anthropic | Fallback: True
2025-12-26 12:22:38,670 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 12:22:38,670 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=engineering)...
2025-12-26 12:22:39,692 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:22:39,693 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:22:39,704 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 12:22:39,771 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 12:22:39,925 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 12:22:39,925 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 12:23:20,621 - hypatiax.tools.symbolic.hybrid_system - INFO - 🤖 Interpreting with ANTHROPIC...
2025-12-26 12:23:33,025 - httpx - INFO - HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2025-12-26 12:23:33,151 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Interpretation completed via ANTHROPIC in 12.53s

   ℹ Warnings: 7

[3/3] 🤖 Interpreting with real LLM API...
✅ Interpretation complete via ANTHROPIC
   Summary: This expression calculates a modified price elasticity measure that incorporates both the standard elasticity ratio and an additional constant term no...
   Suggested name: Hybrid Elasticity Adjustment Ratio

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   price*(delta_quantity + 0.033015758/delta_price)/(delta_price*quantity)

📊 Model Performance:
   • R² Score:    0.999915
   • Complexity:  11

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

✅ PASS Overall Valid: True
📊 Total Score: 85.00/100

📋 Layer Performance:
   ✅ Symbolic      :  71.00/100
   ✅ Dimensional   :  82.00/100
   ✅ Domain        :  97.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9999
✅ Validation: Score = 85.00/100

========================================
           OVERALL: ✅ SUCCESS           
========================================


================================================================================
TEST 8/18: cobb_douglas
================================================================================

================================================================================
           ECONOMICS Hybrid System: Cobb-Douglas Production Function            
================================================================================

📝 Description: Y = A * K^α * L^β
🎯 Ground Truth: A * K**alpha * L**beta
📊 Samples: 200
🤖 LLM Enabled: True

⏳ Generating synthetic data...
✅ Data generated: Features (200, 5), Targets (200,)

⏳ Initializing Hybrid Discovery System...
✅ Anthropic Provider initialized
   Model: claude-sonnet-4-20250514
   Max tokens: 4096
   ✅ Using model: models/gemini-2.5-flash
✅ Google Provider initialized
   Model: models/gemini-2.5-flash
   Max output tokens: 8192
✅ System initialized

================================================================================
                           EXECUTING HYBRID WORKFLOW                            
================================================================================

======================================================================
WORKFLOW: Cobb-Douglas Production Function
Domain: ECONOMICS | Primary LLM: ANTHROPIC
Fallback: Enabled
======================================================================

[1/3] 🔍 Discovering symbolic expression from 200 samples...
✅ Found: 41.892166*productivity*(-0.00119208834805165*capital + 0.0180584623898073*sqrt(labor*(capital + labor)))
   R² Score: 0.9984
   Complexity: 20

[2/3] ✓ Validating expression across 4 layers...
✗ Overall Score: 78.5/100
   Layer Scores:
     ✓ Symbolic: 98.0
     ✗ Dimensional: 47.0
     ✓ Domain: 100.0
     ✓ Numerical: 100.0

   ⚠ Errors: 3 detected
     - Invalid unit for 'productivity': 'dimensionless' - 'Unit' object has no attribute 'units'
     - Invalid unit for 'capital_share': 'dimensionless' - 'Unit' object has no attribute 'units'
     ... and 1 more

   ℹ Warnings: 5

[3/3] ⊗ Interpretation skipped (score 78.5 < 85.0)
   Top recommendations:
     • 🔴 FIX CRITICAL: Resolve dimensional inconsistencies before deployment
     •   → Invalid unit for 'productivity': 'dimensionless' - 'Unit' object has no attribute 'units'
     •   → Invalid unit for 'capital_share': 'dimensionless' - 'Unit' object has no attribute 'units'

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   41.892166*productivity*(-0.00119208834805165*capital + 0.0180584623898073*sqrt(labor*(capital + labor)))

📊 Model Performance:
   • R² Score:    0.998366
   • Complexity:  20

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

❌ FAIL Overall Valid: False
📊 Total Score: 78.50/100

📋 Layer Performance:
   ✅ Symbolic      :  98.00/100
   ❌ Dimensional   :  47.00/100
   ✅ Domain        : 100.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9984
❌ Validation: Score = 78.50/100

========================================
      OVERALL: ❌ NEEDS IMPROVEMENT      
========================================


================================================================================
TEST 9/18: reynolds_number
================================================================================

================================================================================
                   ENGINEERING Hybrid System: Reynolds Number                   
================================================================================

📝 Description: Re = (ρ * v * L) / µ
🎯 Ground Truth: (rho * v * L) / mu
📊 Samples: 200
🤖 LLM Enabled: True

⏳ Generating synthetic data...
✅ Data generated: Features (200, 4), Targets (200,)

⏳ Initializing Hybrid Discovery System...
✅ Anthropic Provider initialized
   Model: claude-sonnet-4-20250514
   Max tokens: 4096
   ✅ Using model: models/gemini-2.5-flash
✅ Google Provider initialized
   Model: models/gemini-2.5-flash
   Max output tokens: 8192
✅ System initialized

================================================================================
                           EXECUTING HYBRID WORKFLOW                            
================================================================================

======================================================================
WORKFLOW: Reynolds Number
Domain: ENGINEERING | Primary LLM: ANTHROPIC
Fallback: Enabled
======================================================================

[1/3] 🔍 Discovering symbolic expression from 200 samples...
✅ Found: density*length*velocity/viscosity
   R² Score: 0.9999
   Complexity: 7

[2/3] ✓ Validating expression across 4 layers...
✓ Overall Score: 87.1/100
   Layer Scores:
     ✓ Symbolic: 73.0
     ✓ Dimensional: 92.0
     ✓ Domain: 92.0
     ✓ Numerical: 100.0

   ℹ Warnings: 4

[3/3] 🤖 Interpreting with real LLM API...
✅ Interpretation complete via ANTHROPIC
   Summary: This expression calculates the Reynolds number, a dimensionless parameter that characterizes the flow regime of a fluid, determining whether flow will...
   Suggested name: Reynolds Number

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   density*length*velocity/viscosity

📊 Model Performance:
2025-12-26 12:23:33,153 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 12:23:33,154 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: engineering | Primary LLM: anthropic | Fallback: True
2025-12-26 12:23:33,154 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 12:23:33,154 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=engineering)...
2025-12-26 12:23:35,238 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:23:35,239 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:23:35,249 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 12:23:35,317 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 12:23:35,428 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 12:23:35,428 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 12:24:08,508 - hypatiax.tools.symbolic.hybrid_system - INFO - 🤖 Interpreting with ANTHROPIC...
2025-12-26 12:24:19,987 - httpx - INFO - HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2025-12-26 12:24:19,992 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Interpretation completed via ANTHROPIC in 11.48s
2025-12-26 12:24:19,993 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 12:24:19,993 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: engineering | Primary LLM: anthropic | Fallback: True
2025-12-26 12:24:19,993 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 12:24:19,993 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=engineering)...
2025-12-26 12:24:20,834 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:24:20,835 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:24:20,846 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 12:24:20,872 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 12:24:21,123 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 12:24:21,123 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
   • R² Score:    0.999856
   • Complexity:  7

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

✅ PASS Overall Valid: True
📊 Total Score: 87.10/100

📋 Layer Performance:
   ✅ Symbolic      :  73.00/100
   ✅ Dimensional   :  92.00/100
   ✅ Domain        :  92.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9999
✅ Validation: Score = 87.10/100

========================================
           OVERALL: ✅ SUCCESS           
========================================


================================================================================
TEST 10/18: hookes_law
================================================================================

================================================================================
                     ENGINEERING Hybrid System: Hooke's Law                     
================================================================================

📝 Description: F = -k * x
🎯 Ground Truth: k * x
📊 Samples: 200
🤖 LLM Enabled: True

⏳ Generating synthetic data...
✅ Data generated: Features (200, 2), Targets (200,)

⏳ Initializing Hybrid Discovery System...
✅ Anthropic Provider initialized
   Model: claude-sonnet-4-20250514
   Max tokens: 4096
   ✅ Using model: models/gemini-2.5-flash
✅ Google Provider initialized
   Model: models/gemini-2.5-flash
   Max output tokens: 8192
✅ System initialized

================================================================================
                           EXECUTING HYBRID WORKFLOW                            
================================================================================

======================================================================
WORKFLOW: Hooke's Law
Domain: ENGINEERING | Primary LLM: ANTHROPIC
Fallback: Enabled
======================================================================

[1/3] 🔍 Discovering symbolic expression from 200 samples...
✅ Found: spring_constant*sqrt(displacement**2)
   R² Score: 0.9998
   Complexity: 6

[2/3] ✓ Validating expression across 4 layers...
✓ Overall Score: 94.6/100
   Layer Scores:
     ✓ Symbolic: 100.0
     ✓ Dimensional: 82.0
     ✓ Domain: 100.0
     ✓ Numerical: 100.0

   ℹ Warnings: 4

[3/3] 🤖 Interpreting with real LLM API...
✅ Interpretation complete via ANTHROPIC
   Summary: This expression calculates the restoring force in a spring system, representing the magnitude of force proportional to the absolute displacement from ...
   Suggested name: Spring Force Magnitude Formula

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   spring_constant*sqrt(displacement**2)

📊 Model Performance:
   • R² Score:    0.999768
   • Complexity:  6

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

✅ PASS Overall Valid: True
📊 Total Score: 94.60/100

📋 Layer Performance:
   ✅ Symbolic      : 100.00/100
   ✅ Dimensional   :  82.00/100
   ✅ Domain        : 100.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9998
✅ Validation: Score = 94.60/100

========================================
           OVERALL: ✅ SUCCESS           
========================================


================================================================================
TEST 11/18: bernoulli_equation
================================================================================

================================================================================
          ENGINEERING Hybrid System: Bernoulli's Equation (Simplified)          
================================================================================

📝 Description: P + 0.5*ρ*v² + ρ*g*h = constant
🎯 Ground Truth: P + 0.5 * rho * v**2 + rho * g * h
📊 Samples: 200
🤖 LLM Enabled: True

⏳ Generating synthetic data...
✅ Data generated: Features (200, 4), Targets (200,)

⏳ Initializing Hybrid Discovery System...
✅ Anthropic Provider initialized
   Model: claude-sonnet-4-20250514
   Max tokens: 4096
   ✅ Using model: models/gemini-2.5-flash
✅ Google Provider initialized
   Model: models/gemini-2.5-flash
   Max output tokens: 8192
✅ System initialized

================================================================================
                           EXECUTING HYBRID WORKFLOW                            
================================================================================

======================================================================
WORKFLOW: Bernoulli's Equation (Simplified)
Domain: ENGINEERING | Primary LLM: ANTHROPIC
Fallback: Enabled
======================================================================

[1/3] 🔍 Discovering symbolic expression from 200 samples...
✅ Found: density*(height + velocity - 3.741516)*9.894315 + pressure
   R² Score: 0.9903
   Complexity: 11

[2/3] ✓ Validating expression across 4 layers...
✗ Overall Score: 71.0/100
   Layer Scores:
     ✓ Symbolic: 100.0
     ✓ Dimensional: 75.0
     ✓ Domain: 95.0
     ✓ Numerical: 100.0

   ⚠ Errors: 1 detected
     - Incompatible units in addition: kilogram / meter ** 3 (density*(height + velocity - 1*3.741516)*9.894315) vs picoyear (pressure)

   ℹ Warnings: 1

[3/3] ⊗ Interpretation skipped (score 71.0 < 85.0)
   Top recommendations:
     • 🔴 FIX CRITICAL: Resolve dimensional inconsistencies before deployment
     •   → Incompatible units in addition: kilogram / meter ** 3 (density*(height + velocity - 1*3.741516)*9.894315) vs picoyear (pressure)

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   density*(height + velocity - 3.741516)*9.894315 + pressure

📊 Model Performance:
   • R² Score:    0.990287
   • Complexity:  11

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

❌ FAIL Overall Valid: False
📊 Total Score: 71.00/100

📋 Layer Performance:
   ✅ Symbolic      : 100.00/100
   ✅ Dimensional   :  75.00/100
   ✅ Domain        :  95.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9903
❌ Validation: Score = 71.00/100

========================================
      OVERALL: ❌ NEEDS IMPROVEMENT      
========================================


================================================================================
TEST 12/18: pythagorean_theorem
================================================================================

================================================================================
                 MATHEMATICS Hybrid System: Pythagorean Theorem                 
================================================================================

📝 Description: c = sqrt(a² + b²)
🎯 Ground Truth: np.sqrt(a**2 + b**2)
📊 Samples: 200
2025-12-26 12:25:11,624 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 12:25:11,624 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: mathematics | Primary LLM: anthropic | Fallback: True
2025-12-26 12:25:11,624 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 12:25:11,624 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=mathematics)...
2025-12-26 12:25:12,579 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:25:12,581 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:25:12,592 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 12:25:12,619 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 12:25:12,713 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 12:25:12,713 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 12:26:21,955 - hypatiax.tools.symbolic.hybrid_system - INFO - 🤖 Interpreting with ANTHROPIC...
2025-12-26 12:26:35,260 - httpx - INFO - HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2025-12-26 12:26:35,266 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Interpretation completed via ANTHROPIC in 13.31s
2025-12-26 12:26:35,357 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 12:26:35,358 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: mathematics | Primary LLM: anthropic | Fallback: True
2025-12-26 12:26:35,358 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 12:26:35,358 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=mathematics)...
2025-12-26 12:26:36,232 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:26:36,234 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:26:36,246 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 12:26:36,292 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 12:26:36,391 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 12:26:36,391 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 12:27:16,319 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 12:27:16,319 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: mathematics | Primary LLM: anthropic | Fallback: True
2025-12-26 12:27:16,319 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 12:27:16,320 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=mathematics)...
2025-12-26 12:27:17,238 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:27:17,240 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:27:17,250 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 12:27:17,292 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 12:27:17,417 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 12:27:17,417 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
🤖 LLM Enabled: True

⏳ Generating synthetic data...
✅ Data generated: Features (200, 2), Targets (200,)

⏳ Initializing Hybrid Discovery System...
✅ Anthropic Provider initialized
   Model: claude-sonnet-4-20250514
   Max tokens: 4096
   ✅ Using model: models/gemini-2.5-flash
✅ Google Provider initialized
   Model: models/gemini-2.5-flash
   Max output tokens: 8192
✅ System initialized

================================================================================
                           EXECUTING HYBRID WORKFLOW                            
================================================================================

======================================================================
WORKFLOW: Pythagorean Theorem
Domain: MATHEMATICS | Primary LLM: ANTHROPIC
Fallback: Enabled
======================================================================

[1/3] 🔍 Discovering symbolic expression from 200 samples...
✅ Found: sqrt(side_a**2 + side_b**1.9995787)
   R² Score: 0.9989
   Complexity: 8

[2/3] ✓ Validating expression across 4 layers...
✓ Overall Score: 99.1/100
   Layer Scores:
     ✓ Symbolic: 100.0
     ✓ Dimensional: 97.0
     ✓ Domain: 100.0
     ✓ Numerical: 100.0

   ℹ Warnings: 1

[3/3] 🤖 Interpreting with real LLM API...
✅ Interpretation complete via ANTHROPIC
   Summary: This expression calculates an approximate hypotenuse length using a modified Pythagorean theorem where the second side is raised to approximately 2.0 ...
   Suggested name: Modified Asymmetric Distance Formula

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   sqrt(side_a**2 + side_b**1.9995787)

📊 Model Performance:
   • R² Score:    0.998859
   • Complexity:  8

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

✅ PASS Overall Valid: True
📊 Total Score: 99.10/100

📋 Layer Performance:
   ✅ Symbolic      : 100.00/100
   ✅ Dimensional   :  97.00/100
   ✅ Domain        : 100.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9989
✅ Validation: Score = 99.10/100

========================================
           OVERALL: ✅ SUCCESS           
========================================


================================================================================
TEST 13/18: compound_interest
================================================================================

================================================================================
                  MATHEMATICS Hybrid System: Compound Interest                  
================================================================================

📝 Description: A = P * (1 + r/n)^(n*t)
🎯 Ground Truth: P * (1 + r/n)**(n*t)
📊 Samples: 200
🤖 LLM Enabled: True

⏳ Generating synthetic data...
✅ Data generated: Features (200, 4), Targets (200,)

⏳ Initializing Hybrid Discovery System...
✅ Anthropic Provider initialized
   Model: claude-sonnet-4-20250514
   Max tokens: 4096
   ✅ Using model: models/gemini-2.5-flash
✅ Google Provider initialized
   Model: models/gemini-2.5-flash
   Max output tokens: 8192
✅ System initialized

================================================================================
                           EXECUTING HYBRID WORKFLOW                            
================================================================================

======================================================================
WORKFLOW: Compound Interest
Domain: MATHEMATICS | Primary LLM: ANTHROPIC
Fallback: Enabled
======================================================================

[1/3] 🔍 Discovering symbolic expression from 200 samples...
✅ Found: (compounds_per_year*time + principal - 19.463768)*exp(time*rate*0.9689725)
   R² Score: 0.9990
   Complexity: 14

[2/3] ✓ Validating expression across 4 layers...
✗ Overall Score: 84.4/100
   Layer Scores:
     ✓ Symbolic: 73.0
     ✓ Dimensional: 75.0
     ✓ Domain: 100.0
     ✓ Numerical: 100.0

   ⚠ Errors: 1 detected
     - Invalid unit for 'rate': 'dimensionless' - 'Unit' object has no attribute 'units'

   ℹ Warnings: 4

[3/3] ⊗ Interpretation skipped (score 84.4 < 85.0)
   Top recommendations:
     • 🔴 FIX CRITICAL: Resolve dimensional inconsistencies before deployment
     •   → Invalid unit for 'rate': 'dimensionless' - 'Unit' object has no attribute 'units'
     • 🟡 IMPROVE: Simplify to: (compounds_per_year*time + principal - 19.463768)*exp(0.9689725*rate*time)

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   (compounds_per_year*time + principal - 19.463768)*exp(time*rate*0.9689725)

📊 Model Performance:
   • R² Score:    0.998983
   • Complexity:  14

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

❌ FAIL Overall Valid: False
📊 Total Score: 84.40/100

📋 Layer Performance:
   ✅ Symbolic      :  73.00/100
   ✅ Dimensional   :  75.00/100
   ✅ Domain        : 100.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9990
❌ Validation: Score = 84.40/100

========================================
      OVERALL: ❌ NEEDS IMPROVEMENT      
========================================


================================================================================
TEST 14/18: quadratic_formula
================================================================================

================================================================================
          MATHEMATICS Hybrid System: Quadratic Formula (discriminant)           
================================================================================

📝 Description: discriminant = b² - 4ac
🎯 Ground Truth: b**2 - 4*a*c
📊 Samples: 200
🤖 LLM Enabled: True

⏳ Generating synthetic data...
✅ Data generated: Features (200, 3), Targets (200,)

⏳ Initializing Hybrid Discovery System...
✅ Anthropic Provider initialized
   Model: claude-sonnet-4-20250514
   Max tokens: 4096
   ✅ Using model: models/gemini-2.5-flash
✅ Google Provider initialized
   Model: models/gemini-2.5-flash
   Max output tokens: 8192
✅ System initialized

================================================================================
                           EXECUTING HYBRID WORKFLOW                            
================================================================================

======================================================================
WORKFLOW: Quadratic Formula (discriminant)
Domain: MATHEMATICS | Primary LLM: ANTHROPIC
Fallback: Enabled
======================================================================

[1/3] 🔍 Discovering symbolic expression from 200 samples...
✅ Found: -3.9990518*coefficient_a*coefficient_c + coefficient_b*coefficient_b
   R² Score: 0.9998
   Complexity: 9

[2/3] ✓ Validating expression across 4 layers...
✗ Overall Score: 89.5/100
2025-12-26 12:27:43,056 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 12:27:43,057 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: physics | Primary LLM: anthropic | Fallback: True
2025-12-26 12:27:43,057 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 12:27:43,057 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=physics)...
2025-12-26 12:27:43,886 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:27:43,888 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:27:43,898 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 12:27:43,924 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 12:27:44,027 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 12:27:44,027 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 12:28:18,144 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 12:28:18,144 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: physics | Primary LLM: anthropic | Fallback: True
2025-12-26 12:28:18,144 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 12:28:18,144 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=physics)...
2025-12-26 12:28:19,015 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:28:19,017 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:28:19,027 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 12:28:19,064 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 12:28:19,161 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 12:28:19,161 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 12:28:48,983 - hypatiax.tools.symbolic.hybrid_system - INFO - 🤖 Interpreting with ANTHROPIC...
2025-12-26 12:28:59,382 - httpx - INFO - HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2025-12-26 12:28:59,393 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Interpretation completed via ANTHROPIC in 10.41s
   Layer Scores:
     ✓ Symbolic: 100.0
     ⚠ Dimensional: 65.0
     ✓ Domain: 100.0
     ✓ Numerical: 100.0

   ⚠ Errors: 3 detected
     - Invalid unit for 'coefficient_a': 'dimensionless' - 'Unit' object has no attribute 'units'
     - Invalid unit for 'coefficient_b': 'dimensionless' - 'Unit' object has no attribute 'units'
     ... and 1 more

   ℹ Warnings: 1

[3/3] ⊗ Interpretation skipped (validation failed)

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   -3.9990518*coefficient_a*coefficient_c + coefficient_b*coefficient_b

📊 Model Performance:
   • R² Score:    0.999843
   • Complexity:  9

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

❌ FAIL Overall Valid: False
📊 Total Score: 89.50/100

📋 Layer Performance:
   ✅ Symbolic      : 100.00/100
   ⚠ Dimensional   :  65.00/100
   ✅ Domain        : 100.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9998
❌ Validation: Score = 89.50/100

========================================
      OVERALL: ❌ NEEDS IMPROVEMENT      
========================================


================================================================================
TEST 15/18: projectile_motion
================================================================================

================================================================================
                PHYSICS Hybrid System: Projectile Motion - Range                
================================================================================

📝 Description: Range R = (v^2 * sin(2θ)) / g
🎯 Ground Truth: (v**2 * np.sin(2 * theta)) / g
📊 Samples: 200
🤖 LLM Enabled: True

⏳ Generating synthetic data...
✅ Data generated: Features (200, 3), Targets (200,)

⏳ Initializing Hybrid Discovery System...
✅ Anthropic Provider initialized
   Model: claude-sonnet-4-20250514
   Max tokens: 4096
   ✅ Using model: models/gemini-2.5-flash
✅ Google Provider initialized
   Model: models/gemini-2.5-flash
   Max output tokens: 8192
✅ System initialized

================================================================================
                           EXECUTING HYBRID WORKFLOW                            
================================================================================

======================================================================
WORKFLOW: Projectile Motion - Range
Domain: PHYSICS | Primary LLM: ANTHROPIC
Fallback: Enabled
======================================================================

[1/3] 🔍 Discovering symbolic expression from 200 samples...
✅ Found: angle*(2.25187280248299 - 1.4381657*angle)*(2.5505708049933*initial_velocity - 25.0522522687965)*log(0.2803203*initial_velocity - 0.62181248831442)
   R² Score: 0.9922
   Complexity: 26

[2/3] ✓ Validating expression across 4 layers...
✗ Overall Score: 78.2/100
   Layer Scores:
     ⚠ Symbolic: 67.0
     ✓ Dimensional: 77.0
     ✓ Domain: 100.0
     ✓ Numerical: 100.0

   ℹ Warnings: 8

[3/3] ⊗ Interpretation skipped (score 78.2 < 85.0)
   Top recommendations:
     • 🟡 VERIFY: Check dimensional analysis warnings
     • 🟡 IMPROVE: Simplify to: -angle*(1.4381657*angle - 2.25187280248299)*(2.5505708049933*initial_velocity - 25.0522522687965)*log(0.2803203*initial_velocity - 0.62181248831442)

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   angle*(2.25187280248299 - 1.4381657*angle)*(2.5505708049933*initial_velocity - 25.0522522687965)*log(0.2803203*initial_velocity - 0.62181248831442)

📊 Model Performance:
   • R² Score:    0.992201
   • Complexity:  26

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

❌ FAIL Overall Valid: False
📊 Total Score: 78.20/100

📋 Layer Performance:
   ⚠ Symbolic      :  67.00/100
   ✅ Dimensional   :  77.00/100
   ✅ Domain        : 100.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9922
❌ Validation: Score = 78.20/100

========================================
      OVERALL: ❌ NEEDS IMPROVEMENT      
========================================


================================================================================
TEST 16/18: kinetic_energy
================================================================================

================================================================================
                     PHYSICS Hybrid System: Kinetic Energy                      
================================================================================

📝 Description: KE = 0.5 * m * v^2
🎯 Ground Truth: 0.5 * m * v**2
📊 Samples: 200
🤖 LLM Enabled: True

⏳ Generating synthetic data...
✅ Data generated: Features (200, 2), Targets (200,)

⏳ Initializing Hybrid Discovery System...
✅ Anthropic Provider initialized
   Model: claude-sonnet-4-20250514
   Max tokens: 4096
   ✅ Using model: models/gemini-2.5-flash
✅ Google Provider initialized
   Model: models/gemini-2.5-flash
   Max output tokens: 8192
✅ System initialized

================================================================================
                           EXECUTING HYBRID WORKFLOW                            
================================================================================

======================================================================
WORKFLOW: Kinetic Energy
Domain: PHYSICS | Primary LLM: ANTHROPIC
Fallback: Enabled
======================================================================

[1/3] 🔍 Discovering symbolic expression from 200 samples...
✅ Found: velocity*mass*velocity*0.5003452
   R² Score: 0.9997
   Complexity: 7

[2/3] ✓ Validating expression across 4 layers...
✓ Overall Score: 97.0/100
   Layer Scores:
     ✓ Symbolic: 100.0
     ✓ Dimensional: 95.0
     ✓ Domain: 95.0
     ✓ Numerical: 100.0

   ℹ Warnings: 1

[3/3] 🤖 Interpreting with real LLM API...
✅ Interpretation complete via ANTHROPIC
   Summary: This expression calculates the kinetic energy of a moving object, representing the energy possessed due to its motion with a coefficient very close to...
   Suggested name: Empirical Kinetic Energy Formula

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   velocity*mass*velocity*0.5003452

📊 Model Performance:
   • R² Score:    0.999719
   • Complexity:  7

VALIDATION BREAKDOWN
2025-12-26 12:28:59,401 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 12:28:59,401 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: physics | Primary LLM: anthropic | Fallback: True
2025-12-26 12:28:59,402 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 12:28:59,402 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=physics)...
2025-12-26 12:29:01,450 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:29:01,452 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:29:01,463 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 12:29:01,496 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 12:29:01,594 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 12:29:01,594 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 12:29:57,386 - hypatiax.tools.symbolic.hybrid_system - INFO - 🤖 Interpreting with ANTHROPIC...
2025-12-26 12:30:08,479 - httpx - INFO - HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2025-12-26 12:30:08,482 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Interpretation completed via ANTHROPIC in 11.10s
2025-12-26 12:30:08,483 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 12:30:08,483 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: physics | Primary LLM: anthropic | Fallback: True
2025-12-26 12:30:08,483 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 12:30:08,484 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=physics)...
2025-12-26 12:30:09,310 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:30:09,312 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 12:30:09,322 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 12:30:09,350 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 12:30:09,449 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 12:30:09,449 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 12:30:39,101 - hypatiax.tools.symbolic.hybrid_system - INFO - 🤖 Interpreting with ANTHROPIC...
2025-12-26 12:30:49,825 - httpx - INFO - HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2025-12-26 12:30:49,828 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Interpretation completed via ANTHROPIC in 10.73s
--------------------------------------------------------------------------------

✅ PASS Overall Valid: True
📊 Total Score: 97.00/100

📋 Layer Performance:
   ✅ Symbolic      : 100.00/100
   ✅ Dimensional   :  95.00/100
   ✅ Domain        :  95.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9997
✅ Validation: Score = 97.00/100

========================================
           OVERALL: ✅ SUCCESS           
========================================


================================================================================
TEST 17/18: ideal_gas_law
================================================================================

================================================================================
                      PHYSICS Hybrid System: Ideal Gas Law                      
================================================================================

📝 Description: PV = nRT
🎯 Ground Truth: n * R * T / V
📊 Samples: 200
🤖 LLM Enabled: True

⏳ Generating synthetic data...
✅ Data generated: Features (200, 3), Targets (200,)

⏳ Initializing Hybrid Discovery System...
✅ Anthropic Provider initialized
   Model: claude-sonnet-4-20250514
   Max tokens: 4096
   ✅ Using model: models/gemini-2.5-flash
✅ Google Provider initialized
   Model: models/gemini-2.5-flash
   Max output tokens: 8192
✅ System initialized

================================================================================
                           EXECUTING HYBRID WORKFLOW                            
================================================================================

======================================================================
WORKFLOW: Ideal Gas Law
Domain: PHYSICS | Primary LLM: ANTHROPIC
Fallback: Enabled
======================================================================

[1/3] 🔍 Discovering symbolic expression from 200 samples...
✅ Found: moles*temperature*8.320247/volume
   R² Score: 0.9999
   Complexity: 7

[2/3] ✓ Validating expression across 4 layers...
✓ Overall Score: 87.1/100
   Layer Scores:
     ✓ Symbolic: 73.0
     ✓ Dimensional: 92.0
     ✓ Domain: 92.0
     ✓ Numerical: 100.0

   ℹ Warnings: 4

[3/3] 🤖 Interpreting with real LLM API...
✅ Interpretation complete via ANTHROPIC
   Summary: This expression calculates pressure using an ideal gas law relationship, with the coefficient 8.320247 representing a close approximation to the unive...
   Suggested name: Modified Ideal Gas Pressure Law

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   moles*temperature*8.320247/volume

📊 Model Performance:
   • R² Score:    0.999872
   • Complexity:  7

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

✅ PASS Overall Valid: True
📊 Total Score: 87.10/100

📋 Layer Performance:
   ✅ Symbolic      :  73.00/100
   ✅ Dimensional   :  92.00/100
   ✅ Domain        :  92.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9999
✅ Validation: Score = 87.10/100

========================================
           OVERALL: ✅ SUCCESS           
========================================


================================================================================
TEST 18/18: ohms_law
================================================================================

================================================================================
                        PHYSICS Hybrid System: Ohm's Law                        
================================================================================

📝 Description: V = I * R
🎯 Ground Truth: I * R
📊 Samples: 200
🤖 LLM Enabled: True

⏳ Generating synthetic data...
✅ Data generated: Features (200, 2), Targets (200,)

⏳ Initializing Hybrid Discovery System...
✅ Anthropic Provider initialized
   Model: claude-sonnet-4-20250514
   Max tokens: 4096
   ✅ Using model: models/gemini-2.5-flash
✅ Google Provider initialized
   Model: models/gemini-2.5-flash
   Max output tokens: 8192
✅ System initialized

================================================================================
                           EXECUTING HYBRID WORKFLOW                            
================================================================================

======================================================================
WORKFLOW: Ohm's Law
Domain: PHYSICS | Primary LLM: ANTHROPIC
Fallback: Enabled
======================================================================

[1/3] 🔍 Discovering symbolic expression from 200 samples...
✅ Found: current*resistance
   R² Score: 0.9997
   Complexity: 3

[2/3] ✓ Validating expression across 4 layers...
✓ Overall Score: 97.0/100
   Layer Scores:
     ✓ Symbolic: 100.0
     ✓ Dimensional: 90.0
     ✓ Domain: 100.0
     ✓ Numerical: 100.0

   ℹ Warnings: 2

[3/3] 🤖 Interpreting with real LLM API...
✅ Interpretation complete via ANTHROPIC
   Summary: This expression calculates electrical voltage (potential difference) across a circuit component by multiplying electric current by resistance.
   Suggested name: Ohm's Law (Voltage Calculation)

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   current*resistance

📊 Model Performance:
   • R² Score:    0.999720
   • Complexity:  3

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

✅ PASS Overall Valid: True
📊 Total Score: 97.00/100

📋 Layer Performance:
   ✅ Symbolic      : 100.00/100
   ✅ Dimensional   :  90.00/100
   ✅ Domain        : 100.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9997
✅ Validation: Score = 97.00/100

========================================
           OVERALL: ✅ SUCCESS           
========================================


================================================================================
                               BATCH TEST SUMMARY                               
================================================================================

📊 Overall Statistics:
   • Total Tests:     18
   • Successful:      7
   • Failed:          11
   • Success Rate:    38.9%

🏆 Domain Breakdown:
   Biology     : 0/3 (0%)
   Chemistry   : 0/3 (0%)
   Economics   : 1/2 (50%)
   Engineering : 2/3 (67%)
   Mathematics : 1/3 (33%)
   Physics     : 3/4 (75%)

📋 Individual Results:
   ❌ michaelis_menten              : R²=0.9657, Val=52.5/100
   ❌ logistic_growth               : R²=0.9142, Val=76.1/100
   ❌ allometric_scaling            : R²=0.9994, Val=81.4/100
   ❌ arrhenius_equation            : R²=0.9882, Val=78.7/100
   ❌ henderson_hasselbalch         : R²=0.9983, Val=71.9/100
   ❌ nernst_equation               : R²=0.9990, Val=67.2/100
   ✅ elasticity_demand             : R²=0.9999, Val=85.0/100
   ❌ cobb_douglas                  : R²=0.9984, Val=78.5/100
   ✅ reynolds_number               : R²=0.9999, Val=87.1/100
   ✅ hookes_law                    : R²=0.9998, Val=94.6/100
   ❌ bernoulli_equation            : R²=0.9903, Val=71.0/100
   ✅ pythagorean_theorem           : R²=0.9989, Val=99.1/100
   ❌ compound_interest             : R²=0.9990, Val=84.4/100
   ❌ quadratic_formula             : R²=0.9998, Val=89.5/100
   ❌ projectile_motion             : R²=0.9922, Val=78.2/100
   ✅ kinetic_energy                : R²=0.9997, Val=97.0/100
   ✅ ideal_gas_law                 : R²=0.9999, Val=87.1/100
   ✅ ohms_law                      : R²=0.9997, Val=97.0/100
✓ Completed: complete_hybrid_system_all_domains.py
[2025-12-26 12:31:06] SUCCESS: Hybrid System (All Domains)
⚠ Hybrid system completed but no new files created


╔══════════════════════════════════════════════════════════════════════╗                                                        
║  PHASE 2: UNIFIED ANALYSIS                                                                                                    
╚══════════════════════════════════════════════════════════════════════╝                                                        
                                                                                                                                
▶ Running Master Analyzer
▶ Running: master_analyzer.py
[2025-12-26 12:31:06] Starting: Master Analyzer (All Modules)
✓ Working directory: /home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab
📊 Master Analyzer initialized
   Results dir: hypatiax/data/results
   Output dir:  hypatiax/analysis
================================================================================
                     HYPATIAX MASTER ANALYSIS ORCHESTRATOR                      
================================================================================

🔍 Detected result files:
   ⊘ hybrid: Not found
   ✅ llm: baseline_pure_llm_20251225_215328.json
   ✅ nn: nn_experiment_report_20251225_215506.json
   ⊘ comparison: Not found

📋 Modules to execute: tables, figures, hybrid_viz, analysis, defi_viz

⚡ Running 5 modules in parallel...

📄 Master report saved: hypatiax/analysis/master_report.json

================================================================================
                            MASTER ANALYSIS SUMMARY                             
================================================================================

📊 Modules:
   Executed:   5
   Successful: 0
   Failed:     5

📋 Results by Module:
   ❌ Publication Tables
      Error: Script not found: generate_tables.py
   ❌ Publication Figures
      Error: Script not found: generate_figures.py
   ❌ Hybrid System Comparison
      Error: Script not found: hypatiax_hybrid_system_visualization.py
   ❌ Comprehensive Analysis
      Error: Script not found: analyze_hybrid_results.py
   ❌ DeFi Visualizations
      Error: Script not found: hypatiax_visualizer.py

📁 Output directory: hypatiax/analysis
================================================================================
✗ ERROR: Failed: master_analyzer.py (exit code: 1)
[2025-12-26 12:31:09] FAILED: Master Analyzer (All Modules) (exit code: 1)
⚠ Master analyzer had issues but continuing...


╔══════════════════════════════════════════════════════════════════════╗                                                        
║  PHASE 3: COMPREHENSIVE REPORTS                                                                                               
╚══════════════════════════════════════════════════════════════════════╝                                                        
                                                                                                                                
▶ Generating Comprehensive Reports
▶ Running: analyze_hybrid_results.py
[2025-12-26 12:31:09] Starting: Comprehensive Analysis Report
✓ Working directory: /home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab
❌ No comparison_results directory found
✗ ERROR: Failed: analyze_hybrid_results.py (exit code: 1)
[2025-12-26 12:31:31] FAILED: Comprehensive Analysis Report (exit code: 1)


╔══════════════════════════════════════════════════════════════════════╗                                                        
  Pipeline Execution Summary                                                                                                    
╚══════════════════════════════════════════════════════════════════════╝                                                        
                                                                                                                                
Configuration:
  • Domain: All domains (biology, chemistry, economics, engineering, physics, mathematics)
  • Mode: Quick (baselines skipped)
  • LLM Interpretation: ENABLED ✓

Results Location: /home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab/hypatiax/data/results
Analysis Location: /home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab/analysis
Log File: /home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab/logs/pipeline_20251226_121332.log

Files Created in This Run:

Total new files: 0

Total Files in Results Directory:
  • JSON results: 13
  • CSV tables: 2
  • PNG figures: 3

⚠ WARNING: No new files were created!
  Check the log file: /home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab/logs/pipeline_20251226_121332.log

Next Steps:
  1. Review results in: /home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab/hypatiax/data/results
  2. Check analysis in: /home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab/analysis
  3. View full log: /home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab/logs/pipeline_20251226_121332.log


Total execution time: 17m 59s
Finished at: Fri Dec 26 12:31:32 PM GMT 2025


┌──(py312)(agagora㉿localhost)-[~/Downloads/GITHUB/LLM-HypatiaX-Colab/tests]
└─$                                                                                                              
