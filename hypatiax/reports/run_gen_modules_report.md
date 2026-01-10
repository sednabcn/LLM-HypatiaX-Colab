
╔══════════════════════════════════════════════════════════════════════╗
  HypatiaX Complete Analysis Pipeline
╚══════════════════════════════════════════════════════════════════════╝

Started at: Fri Dec 26 07:42:30 PM GMT 2025
Project Root: /home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab
Visualization Dir: /home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab/hypatiax/tools/visualization
Log File: /home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab/logs/pipeline_20251226_194230.log

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
[2025-12-26 19:42:31] Starting: Hybrid System (All Domains)
✓ Working directory: /home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab
2025-12-26 19:44:45,405 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 19:44:45,405 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: biology | Primary LLM: anthropic | Fallback: True
2025-12-26 19:44:45,405 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 19:44:45,406 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=biology)...
2025-12-26 19:44:46,378 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 19:44:46,379 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 19:44:46,389 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 19:44:46,569 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 19:44:47,562 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 19:44:47,562 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 19:46:52,521 - hypatiax.tools.symbolic.hybrid_system - INFO - 🤖 Interpreting with ANTHROPIC...
2025-12-26 19:47:08,205 - httpx - INFO - HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2025-12-26 19:47:08,301 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Interpretation completed via ANTHROPIC in 15.78s
2025-12-26 19:47:08,303 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 19:47:08,303 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: biology | Primary LLM: anthropic | Fallback: True
2025-12-26 19:47:08,303 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 19:47:08,303 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=biology)...
2025-12-26 19:47:09,066 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 19:47:09,067 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 19:47:09,077 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 19:47:09,103 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 19:47:09,325 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 19:47:09,325 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 19:47:43,385 - hypatiax.tools.symbolic.hybrid_system - INFO - 🤖 Interpreting with ANTHROPIC...
2025-12-26 19:47:58,628 - httpx - INFO - HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2025-12-26 19:47:58,631 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Interpretation completed via ANTHROPIC in 15.25s
2025-12-26 19:47:58,632 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 19:47:58,633 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: biology | Primary LLM: anthropic | Fallback: True
2025-12-26 19:47:58,633 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 19:47:58,633 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=biology)...
2025-12-26 19:47:59,391 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 19:47:59,392 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 19:47:59,402 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...

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
✅ Found: (vmax**(-1.0537927) + vmax)*sqrt((0.93964253179163*km/substrate_concentration**0.9973239 + 1.00336880640498)**(-2.0616388))
   R² Score: 0.9997
   Complexity: 18

[2/3] ✓ Validating expression across 4 layers...
✓ Overall Score: 86.9/100
   Layer Scores:
     ✓ Symbolic: 98.0
     ✓ Dimensional: 75.0
     ✓ Domain: 100.0
     ✓ Numerical: 100.0

   ℹ Warnings: 7

[3/3] 🤖 Interpreting with real LLM API...
✅ Interpretation complete via ANTHROPIC
   Summary: This expression calculates a modified enzyme kinetic parameter that combines maximum velocity effects with substrate-dependent kinetic behavior, appea...
   Suggested name: Modified Allosteric Enzyme Kinetics Model

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   (vmax**(-1.0537927) + vmax)*sqrt((0.93964253179163*km/substrate_concentration**0.9973239 + 1.00336880640498)**(-2.0616388))

📊 Model Performance:
   • R² Score:    0.999714
   • Complexity:  18

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

✅ PASS Overall Valid: True
📊 Total Score: 86.90/100

📋 Layer Performance:
   ✅ Symbolic      :  98.00/100
   ✅ Dimensional   :  75.00/100
   ✅ Domain        : 100.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9997
✅ Validation: Score = 86.90/100

========================================
           OVERALL: ✅ SUCCESS           
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
✅ Found: growth_rate*(population - 11.278202)**1.942147*sqrt(log(0.88553476*carrying_capacity/population))/population
   R² Score: 0.9980
   Complexity: 17

[2/3] ✓ Validating expression across 4 layers...
✓ Overall Score: 85.0/100
   Layer Scores:
     ⚠ Symbolic: 69.0
     ✓ Dimensional: 84.0
     ✓ Domain: 97.0
     ✓ Numerical: 100.0

   ℹ Warnings: 10

[3/3] 🤖 Interpreting with real LLM API...
✅ Interpretation complete via ANTHROPIC
   Summary: This expression calculates a modified population growth rate that incorporates threshold effects, non-linear scaling, and logarithmic constraints base...
   Suggested name: Threshold-Enhanced Logistic Growth Model

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   growth_rate*(population - 11.278202)**1.942147*sqrt(log(0.88553476*carrying_capacity/population))/population

📊 Model Performance:
   • R² Score:    0.998021
   • Complexity:  17

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

✅ PASS Overall Valid: True
📊 Total Score: 85.00/100

📋 Layer Performance:
   ⚠ Symbolic      :  69.00/100
   ✅ Dimensional   :  84.00/100
   ✅ Domain        :  97.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9980
✅ Validation: Score = 85.00/100

========================================
           OVERALL: ✅ SUCCESS           
========================================


================================================================================
TEST 3/18: allometric_scaling
================================================================================

================================================================================
                 BIOLOGY Hybrid System: Allometric Scaling Law                  
================================================================================

📝 Description: Y = a * M^b (e.g., metabolic rate ∝ mass^0.75)
🎯 Ground Truth: a * M**b
📊 Samples: 200
🤖 LLM Enabled: True

⏳ Generating synthetic data...
✅ Data generated: Features (200, 3), Targets (200,)

⏳ Initializing Hybrid Discovery System...
✅ Anthropic Provider initialized
2025-12-26 19:47:59,428 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 19:47:59,550 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 19:47:59,550 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 19:48:38,380 - hypatiax.tools.symbolic.hybrid_system - INFO - 🤖 Interpreting with ANTHROPIC...
2025-12-26 19:48:51,799 - httpx - INFO - HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2025-12-26 19:48:51,802 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Interpretation completed via ANTHROPIC in 13.42s
2025-12-26 19:48:51,804 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 19:48:51,804 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: chemistry | Primary LLM: anthropic | Fallback: True
2025-12-26 19:48:51,805 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 19:48:51,806 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=chemistry)...
2025-12-26 19:48:52,578 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 19:48:52,580 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 19:48:52,589 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 19:48:52,616 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 19:48:52,714 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 19:48:52,714 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 19:49:32,351 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 19:49:32,351 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: chemistry | Primary LLM: anthropic | Fallback: True
2025-12-26 19:49:32,352 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 19:49:32,352 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=chemistry)...
2025-12-26 19:49:33,144 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 19:49:33,145 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 19:49:33,155 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 19:49:33,181 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 19:49:33,304 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 19:49:33,304 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 19:50:14,808 - hypatiax.tools.symbolic.hybrid_system - INFO - 🤖 Interpreting with ANTHROPIC...
2025-12-26 19:50:28,511 - httpx - INFO - HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2025-12-26 19:50:28,514 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Interpretation completed via ANTHROPIC in 13.71s
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
✅ Found: mass**0.7518387*3.4750466
   R² Score: 0.9995
   Complexity: 5

[2/3] ✓ Validating expression across 4 layers...
✓ Overall Score: 100.0/100
   Layer Scores:
     ✓ Symbolic: 100.0
     ✓ Dimensional: 100.0
     ✓ Domain: 100.0
     ✓ Numerical: 100.0

[3/3] 🤖 Interpreting with real LLM API...
✅ Interpretation complete via ANTHROPIC
   Summary: This expression calculates a biological rate or metabolic parameter that scales allometrically with body mass, following the classic 3/4 power law obs...
   Suggested name: Allometric Metabolic Scaling Formula

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   mass**0.7518387*3.4750466

📊 Model Performance:
   • R² Score:    0.999543
   • Complexity:  5

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

✅ PASS Overall Valid: True
📊 Total Score: 100.00/100

📋 Layer Performance:
   ✅ Symbolic      : 100.00/100
   ✅ Dimensional   : 100.00/100
   ✅ Domain        : 100.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9995
✅ Validation: Score = 100.00/100

========================================
           OVERALL: ✅ SUCCESS           
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
✅ Found: 0.000349408581461734*exp((temperature*(temperature + 1828.0557) + sqrt(pre_exponential*(temperature + 1121.6212)/activation_energy))/activation_energy)
   R² Score: 0.9971
   Complexity: 19

[2/3] ✓ Validating expression across 4 layers...
✗ Overall Score: 77.0/100
   Layer Scores:
     ✓ Symbolic: 73.0
     ✓ Dimensional: 77.0
     ✓ Domain: 90.0
     ✓ Numerical: 100.0

   ℹ Warnings: 7

[3/3] ⊗ Interpretation skipped (score 77.0 < 85.0)
   Top recommendations:
     • 🟡 VERIFY: Check dimensional analysis warnings
     • 🟡 IMPROVE: Simplify to: 0.000349408581461734*exp((temperature*(temperature + 1828.0557) + sqrt(pre_exponential*(temperature + 1121.6212)/activation_energy))/activation_energy)

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   0.000349408581461734*exp((temperature*(temperature + 1828.0557) + sqrt(pre_exponential*(temperature + 1121.6212)/activation_energy))/activation_energy)

📊 Model Performance:
   • R² Score:    0.997070
   • Complexity:  19

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

❌ FAIL Overall Valid: False
📊 Total Score: 77.00/100

📋 Layer Performance:
   ✅ Symbolic      :  73.00/100
   ✅ Dimensional   :  77.00/100
   ✅ Domain        :  90.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9971
❌ Validation: Score = 77.00/100

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
======================================================================

[1/3] 🔍 Discovering symbolic expression from 200 samples...
✅ Found: pKa - 0.4321526*log(acid_concentration/base_concentration)
   R² Score: 0.9991
   Complexity: 8

[2/3] ✓ Validating expression across 4 layers...
✓ Overall Score: 85.0/100
   Layer Scores:
     ✓ Symbolic: 73.0
     ✓ Dimensional: 90.0
     ✓ Domain: 87.0
     ✓ Numerical: 100.0

   ℹ Warnings: 6

[3/3] 🤖 Interpreting with real LLM API...
2025-12-26 19:50:28,515 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 19:50:28,516 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: chemistry | Primary LLM: anthropic | Fallback: True
2025-12-26 19:50:28,516 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 19:50:28,516 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=chemistry)...
2025-12-26 19:50:29,311 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 19:50:29,312 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 19:50:29,322 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 19:50:29,349 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 19:50:29,488 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 19:50:29,489 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 19:51:10,191 - hypatiax.tools.symbolic.hybrid_system - INFO - 🤖 Interpreting with ANTHROPIC...
2025-12-26 19:51:24,596 - httpx - INFO - HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2025-12-26 19:51:24,599 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Interpretation completed via ANTHROPIC in 14.41s
2025-12-26 19:51:24,600 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 19:51:24,600 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: economics | Primary LLM: anthropic | Fallback: True
2025-12-26 19:51:24,600 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 19:51:24,600 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=economics)...
2025-12-26 19:51:25,356 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 19:51:25,357 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 19:51:25,366 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 19:51:25,393 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 19:51:25,494 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 19:51:25,494 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 19:51:50,573 - hypatiax.tools.symbolic.hybrid_system - INFO - 🤖 Interpreting with ANTHROPIC...
2025-12-26 19:52:03,198 - httpx - INFO - HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2025-12-26 19:52:03,200 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Interpretation completed via ANTHROPIC in 12.63s
✅ Interpretation complete via ANTHROPIC
   Summary: This expression calculates the pH of a buffer solution using a modified Henderson-Hasselbalch equation, where the coefficient 0.4321526 represents an ...
   Suggested name: Modified Henderson-Hasselbalch Buffer Equation

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   pKa - 0.4321526*log(acid_concentration/base_concentration)

📊 Model Performance:
   • R² Score:    0.999086
   • Complexity:  8

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

✅ PASS Overall Valid: True
📊 Total Score: 85.00/100

📋 Layer Performance:
   ✅ Symbolic      :  73.00/100
   ✅ Dimensional   :  90.00/100
   ✅ Domain        :  87.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9991
✅ Validation: Score = 85.00/100

========================================
           OVERALL: ✅ SUCCESS           
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
✅ Found: standard_potential + reaction_quotient**0.32803386*(-0.02932316)/charge
   R² Score: 0.9989
   Complexity: 9

[2/3] ✓ Validating expression across 4 layers...
✓ Overall Score: 96.1/100
   Layer Scores:
     ✓ Symbolic: 100.0
     ✓ Dimensional: 95.0
     ✓ Domain: 92.0
     ✓ Numerical: 100.0

   ℹ Warnings: 3

[3/3] 🤖 Interpreting with real LLM API...
✅ Interpretation complete via ANTHROPIC
   Summary: This expression calculates the actual electrode potential under non-standard conditions, representing a modified version of the Nernst equation with a...
   Suggested name: Modified Power-Law Electrode Potential Equation

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   standard_potential + reaction_quotient**0.32803386*(-0.02932316)/charge

📊 Model Performance:
   • R² Score:    0.998907
   • Complexity:  9

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

✅ PASS Overall Valid: True
📊 Total Score: 96.10/100

📋 Layer Performance:
   ✅ Symbolic      : 100.00/100
   ✅ Dimensional   :  95.00/100
   ✅ Domain        :  92.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9989
✅ Validation: Score = 96.10/100

========================================
           OVERALL: ✅ SUCCESS           
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
✅ Found: price*(delta_quantity*1.0099146 - (delta_quantity - 1*(-25.090302))/quantity)/(delta_price*quantity)
   R² Score: 1.0000
   Complexity: 15

[2/3] ✓ Validating expression across 4 layers...
✓ Overall Score: 88.9/100
   Layer Scores:
     ✓ Symbolic: 71.0
     ✓ Dimensional: 95.0
     ✓ Domain: 97.0
     ✓ Numerical: 100.0

   ℹ Warnings: 5

[3/3] 🤖 Interpreting with real LLM API...
✅ Interpretation complete via ANTHROPIC
   Summary: This expression calculates a price-adjusted elasticity-like measure that combines quantity changes with a baseline adjustment factor, normalized by pr...
   Suggested name: Adjusted Price Sensitivity Coefficient

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   price*(delta_quantity*1.0099146 - (delta_quantity - 1*(-25.090302))/quantity)/(delta_price*quantity)

📊 Model Performance:
   • R² Score:    0.999959
   • Complexity:  15

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

✅ PASS Overall Valid: True
📊 Total Score: 88.90/100
2025-12-26 19:52:03,202 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 19:52:03,202 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: economics | Primary LLM: anthropic | Fallback: True
2025-12-26 19:52:03,203 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 19:52:03,203 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=economics)...
2025-12-26 19:52:04,268 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 19:52:04,269 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 19:52:04,279 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 19:52:04,305 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 19:52:04,408 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 19:52:04,409 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 19:54:03,668 - hypatiax.tools.symbolic.hybrid_system - INFO - 🤖 Interpreting with ANTHROPIC...
2025-12-26 19:54:19,108 - httpx - INFO - HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2025-12-26 19:54:19,111 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Interpretation completed via ANTHROPIC in 15.44s
2025-12-26 19:54:19,112 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 19:54:19,112 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: engineering | Primary LLM: anthropic | Fallback: True
2025-12-26 19:54:19,113 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 19:54:19,113 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=engineering)...
2025-12-26 19:54:19,868 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 19:54:19,869 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 19:54:19,878 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 19:54:19,903 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 19:54:19,992 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 19:54:19,992 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 19:54:53,970 - hypatiax.tools.symbolic.hybrid_system - INFO - 🤖 Interpreting with ANTHROPIC...
2025-12-26 19:55:07,393 - httpx - INFO - HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2025-12-26 19:55:07,396 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Interpretation completed via ANTHROPIC in 13.43s
2025-12-26 19:55:07,397 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 19:55:07,398 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: engineering | Primary LLM: anthropic | Fallback: True
2025-12-26 19:55:07,398 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 19:55:07,399 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=engineering)...
2025-12-26 19:55:08,136 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 19:55:08,137 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 19:55:08,146 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 19:55:08,172 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized

📋 Layer Performance:
   ✅ Symbolic      :  71.00/100
   ✅ Dimensional   :  95.00/100
   ✅ Domain        :  97.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 1.0000
✅ Validation: Score = 88.90/100

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
✅ Found: productivity*sqrt(labor*(capital**0.6543326 + sqrt((capital_share*labor*(capital - capital**labor_share))**1.1300058)))
   R² Score: 0.9995
   Complexity: 21

[2/3] ✓ Validating expression across 4 layers...
✓ Overall Score: 87.4/100
   Layer Scores:
     ✓ Symbolic: 73.0
     ✓ Dimensional: 85.0
     ✓ Domain: 100.0
     ✓ Numerical: 100.0

   ℹ Warnings: 6

[3/3] 🤖 Interpreting with real LLM API...
✅ Interpretation complete via ANTHROPIC
   Summary: This expression calculates an enhanced production function that modifies the traditional Cobb-Douglas framework by incorporating a complex capital adj...
   Suggested name: Constrained Capital Adjustment Production Function

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   productivity*sqrt(labor*(capital**0.6543326 + sqrt((capital_share*labor*(capital - capital**labor_share))**1.1300058)))

📊 Model Performance:
   • R² Score:    0.999468
   • Complexity:  21

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

✅ PASS Overall Valid: True
📊 Total Score: 87.40/100

📋 Layer Performance:
   ✅ Symbolic      :  73.00/100
   ✅ Dimensional   :  85.00/100
   ✅ Domain        : 100.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9995
✅ Validation: Score = 87.40/100

========================================
           OVERALL: ✅ SUCCESS           
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
✓ Overall Score: 88.0/100
   Layer Scores:
     ✓ Symbolic: 73.0
     ✓ Dimensional: 95.0
     ✓ Domain: 92.0
     ✓ Numerical: 100.0

   ℹ Warnings: 4

[3/3] 🤖 Interpreting with real LLM API...
✅ Interpretation complete via ANTHROPIC
   Summary: This expression calculates the Reynolds number, a dimensionless quantity that characterizes the flow regime of a fluid, determining whether flow is la...
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
   • R² Score:    0.999885
   • Complexity:  7

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

✅ PASS Overall Valid: True
📊 Total Score: 88.00/100

📋 Layer Performance:
   ✅ Symbolic      :  73.00/100
   ✅ Dimensional   :  95.00/100
   ✅ Domain        :  92.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9999
✅ Validation: Score = 88.00/100

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
2025-12-26 19:55:08,270 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 19:55:08,270 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 19:55:42,089 - hypatiax.tools.symbolic.hybrid_system - INFO - 🤖 Interpreting with ANTHROPIC...
2025-12-26 19:59:29,110 - httpx - INFO - HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2025-12-26 19:59:29,112 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Interpretation completed via ANTHROPIC in 227.02s
2025-12-26 19:59:29,113 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 19:59:29,114 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: engineering | Primary LLM: anthropic | Fallback: True
2025-12-26 19:59:29,114 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 19:59:29,114 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=engineering)...
2025-12-26 19:59:29,858 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 19:59:29,859 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 19:59:29,868 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 19:59:29,893 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 19:59:30,032 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 19:59:30,032 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 20:00:13,893 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 20:00:13,893 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: mathematics | Primary LLM: anthropic | Fallback: True
2025-12-26 20:00:13,893 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 20:00:13,894 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=mathematics)...
2025-12-26 20:00:14,633 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 20:00:14,635 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 20:00:14,644 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 20:00:14,669 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 20:00:14,770 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 20:00:14,770 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 20:00:47,347 - hypatiax.tools.symbolic.hybrid_system - INFO - 🤖 Interpreting with ANTHROPIC...
2025-12-26 20:01:52,158 - httpx - INFO - HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2025-12-26 20:01:52,161 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Interpretation completed via ANTHROPIC in 64.81s
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
   R² Score: 0.9997
   Complexity: 6

[2/3] ✓ Validating expression across 4 layers...
✓ Overall Score: 97.0/100
   Layer Scores:
     ✓ Symbolic: 100.0
     ✓ Dimensional: 90.0
     ✓ Domain: 100.0
     ✓ Numerical: 100.0

   ℹ Warnings: 3

[3/3] 🤖 Interpreting with real LLM API...
✅ Interpretation complete via ANTHROPIC
   Summary: This expression calculates the restoring force in a spring system, representing the magnitude of force required to maintain a given displacement from ...
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
   • R² Score:    0.999744
   • Complexity:  6

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
✅ Found: pressure + (density*(height + velocity) - 1*2685.9924)*9.649457
   R² Score: 0.9893
   Complexity: 11

[2/3] ✓ Validating expression across 4 layers...
✗ Overall Score: 71.9/100
   Layer Scores:
     ✓ Symbolic: 100.0
     ✓ Dimensional: 78.0
     ✓ Domain: 95.0
     ✓ Numerical: 100.0

   ⚠ Errors: 1 detected
     - Incompatible units in addition: picoyear (pressure) vs dimensionless ((density*(height + velocity) - 2685.9924)*9.649457)

   ℹ Warnings: 1

[3/3] ⊗ Interpretation skipped (score 71.9 < 85.0)
   Top recommendations:
     • 🔴 FIX CRITICAL: Resolve dimensional inconsistencies before deployment
     •   → Incompatible units in addition: picoyear (pressure) vs dimensionless ((density*(height + velocity) - 2685.9924)*9.649457)

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   pressure + (density*(height + velocity) - 1*2685.9924)*9.649457

📊 Model Performance:
   • R² Score:    0.989303
   • Complexity:  11

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

❌ FAIL Overall Valid: False
📊 Total Score: 71.90/100

📋 Layer Performance:
   ✅ Symbolic      : 100.00/100
   ✅ Dimensional   :  78.00/100
   ✅ Domain        :  95.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9893
❌ Validation: Score = 71.90/100

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
✅ Found: sqrt(side_a**2 + side_b**2)
   R² Score: 0.9987
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
2025-12-26 20:01:52,162 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 20:01:52,163 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: mathematics | Primary LLM: anthropic | Fallback: True
2025-12-26 20:01:52,163 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 20:01:52,163 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=mathematics)...
2025-12-26 20:01:53,219 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 20:01:53,221 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 20:01:53,229 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 20:01:53,255 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 20:01:53,382 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 20:01:53,383 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 20:02:26,423 - hypatiax.tools.symbolic.hybrid_system - INFO - 🤖 Interpreting with ANTHROPIC...
2025-12-26 20:02:39,438 - httpx - INFO - HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2025-12-26 20:02:39,441 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Interpretation completed via ANTHROPIC in 13.02s
2025-12-26 20:02:39,442 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 20:02:39,442 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: mathematics | Primary LLM: anthropic | Fallback: True
2025-12-26 20:02:39,442 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 20:02:39,443 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=mathematics)...
2025-12-26 20:02:40,174 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 20:02:40,176 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 20:02:40,185 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 20:02:40,210 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 20:02:40,309 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 20:02:40,309 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 20:03:02,297 - hypatiax.tools.symbolic.hybrid_system - INFO - 🤖 Interpreting with ANTHROPIC...
2025-12-26 20:03:16,187 - httpx - INFO - HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2025-12-26 20:03:16,192 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Interpretation completed via ANTHROPIC in 13.89s
   Summary: This expression calculates the Euclidean distance between two points or the hypotenuse of a right triangle using the Pythagorean theorem. It represent...
   Suggested name: Pythagorean Distance Formula

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   sqrt(side_a**2 + side_b**2)

📊 Model Performance:
   • R² Score:    0.998710
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

✅ Discovery:   R² = 0.9987
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
✅ Found: principal*exp(rate*(time - 1*(-0.092833996) - 0.8542683/compounds_per_year))
   R² Score: 0.9995
   Complexity: 12

[2/3] ✓ Validating expression across 4 layers...
✓ Overall Score: 88.3/100
   Layer Scores:
     ✓ Symbolic: 71.0
     ✓ Dimensional: 93.0
     ✓ Domain: 97.0
     ✓ Numerical: 100.0

   ℹ Warnings: 6

[3/3] 🤖 Interpreting with real LLM API...
✅ Interpretation complete via ANTHROPIC
   Summary: This expression calculates a modified compound interest formula with an adjusted time parameter that incorporates a constant offset and a compounding ...
   Suggested name: Modified Compound Interest with Frequency-Adjusted Time

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   principal*exp(rate*(time - 1*(-0.092833996) - 0.8542683/compounds_per_year))

📊 Model Performance:
   • R² Score:    0.999538
   • Complexity:  12

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

✅ PASS Overall Valid: True
📊 Total Score: 88.30/100

📋 Layer Performance:
   ✅ Symbolic      :  71.00/100
   ✅ Dimensional   :  93.00/100
   ✅ Domain        :  97.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9995
✅ Validation: Score = 88.30/100

========================================
           OVERALL: ✅ SUCCESS           
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
✅ Found: coefficient_c*coefficient_a*(-4.006882) + coefficient_b*coefficient_b
   R² Score: 0.9998
   Complexity: 9

[2/3] ✓ Validating expression across 4 layers...
✓ Overall Score: 99.4/100
   Layer Scores:
     ✓ Symbolic: 100.0
     ✓ Dimensional: 98.0
     ✓ Domain: 100.0
     ✓ Numerical: 100.0

   ℹ Warnings: 1

[3/3] 🤖 Interpreting with real LLM API...
✅ Interpretation complete via ANTHROPIC
   Summary: This expression calculates a modified discriminant-like quantity for quadratic functions, combining the square of the linear coefficient with a scaled...
   Suggested name: Modified Quadratic Discriminant

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   coefficient_c*coefficient_a*(-4.006882) + coefficient_b*coefficient_b

📊 Model Performance:
   • R² Score:    0.999843
   • Complexity:  9

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

✅ PASS Overall Valid: True
📊 Total Score: 99.40/100

📋 Layer Performance:
   ✅ Symbolic      : 100.00/100
   ✅ Dimensional   :  98.00/100
   ✅ Domain        : 100.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
2025-12-26 20:03:16,193 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 20:03:16,193 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: physics | Primary LLM: anthropic | Fallback: True
2025-12-26 20:03:16,194 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 20:03:16,194 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=physics)...
2025-12-26 20:03:16,938 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 20:03:16,939 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 20:03:16,948 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 20:03:16,973 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 20:03:17,095 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 20:03:17,096 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 20:03:50,872 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 20:03:50,872 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: physics | Primary LLM: anthropic | Fallback: True
2025-12-26 20:03:50,872 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 20:03:50,873 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=physics)...
2025-12-26 20:03:51,611 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 20:03:51,612 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 20:03:51,622 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 20:03:51,647 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 20:03:51,746 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 20:03:51,746 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 20:04:27,246 - hypatiax.tools.symbolic.hybrid_system - INFO - 🤖 Interpreting with ANTHROPIC...
2025-12-26 20:04:37,242 - httpx - INFO - HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2025-12-26 20:04:37,244 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Interpretation completed via ANTHROPIC in 10.00s
2025-12-26 20:04:37,246 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 20:04:37,246 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: physics | Primary LLM: anthropic | Fallback: True
2025-12-26 20:04:37,246 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 20:04:37,246 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=physics)...
2025-12-26 20:04:37,981 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 20:04:37,982 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 20:04:37,991 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 20:04:38,016 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 20:04:38,108 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 20:04:38,108 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9998
✅ Validation: Score = 99.40/100

========================================
           OVERALL: ✅ SUCCESS           
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
✅ Found: (2.7055237*angle**gravity - 2.7055237*initial_velocity + 11.3149186579164/angle)*log(gravity/initial_velocity) + 11.359551
   R² Score: 0.9489
   Complexity: 18

[2/3] ✓ Validating expression across 4 layers...
✗ Overall Score: 76.4/100
   Layer Scores:
     ⚠ Symbolic: 69.0
     ✓ Dimensional: 72.0
     ✓ Domain: 97.0
     ✓ Numerical: 100.0

   ℹ Warnings: 12

[3/3] ⊗ Interpretation skipped (score 76.4 < 85.0)
   Top recommendations:
     • 🟡 VERIFY: Check dimensional analysis warnings
     • 🟡 IMPROVE: Simplify to: (11.359551*angle + (2.7055237*angle*(angle**gravity - initial_velocity) + 11.3149186579164)*log(gravity/initial_velocity))/angle
     • 🟡 REVIEW: Address physics domain warnings

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   (2.7055237*angle**gravity - 2.7055237*initial_velocity + 11.3149186579164/angle)*log(gravity/initial_velocity) + 11.359551

📊 Model Performance:
   • R² Score:    0.948906
   • Complexity:  18

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

❌ FAIL Overall Valid: False
📊 Total Score: 76.40/100

📋 Layer Performance:
   ⚠ Symbolic      :  69.00/100
   ✅ Dimensional   :  72.00/100
   ✅ Domain        :  97.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9489
❌ Validation: Score = 76.40/100

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
✅ Found: mass*velocity*velocity*0.49964887
   R² Score: 0.9998
   Complexity: 7

[2/3] ✓ Validating expression across 4 layers...
✓ Overall Score: 97.9/100
   Layer Scores:
     ✓ Symbolic: 100.0
     ✓ Dimensional: 98.0
     ✓ Domain: 95.0
     ✓ Numerical: 100.0

   ℹ Warnings: 1

[3/3] 🤖 Interpreting with real LLM API...
✅ Interpretation complete via ANTHROPIC
   Summary: This expression calculates approximately half the kinetic energy of an object, representing the average kinetic energy or energy transfer in collision...
   Suggested name: Modified Kinetic Energy (Half-Energy Formula)

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   mass*velocity*velocity*0.49964887

📊 Model Performance:
   • R² Score:    0.999809
   • Complexity:  7

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

✅ PASS Overall Valid: True
📊 Total Score: 97.90/100

📋 Layer Performance:
   ✅ Symbolic      : 100.00/100
   ✅ Dimensional   :  98.00/100
   ✅ Domain        :  95.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9998
✅ Validation: Score = 97.90/100

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
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 20:05:20,033 - hypatiax.tools.symbolic.hybrid_system - INFO - 🤖 Interpreting with ANTHROPIC...
2025-12-26 20:05:34,448 - httpx - INFO - HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2025-12-26 20:05:34,450 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Interpretation completed via ANTHROPIC in 14.42s
2025-12-26 20:05:34,452 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing HybridDiscoverySystem v3.0
2025-12-26 20:05:34,452 - hypatiax.tools.symbolic.hybrid_system - INFO - Domain: physics | Primary LLM: anthropic | Fallback: True
2025-12-26 20:05:34,452 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing symbolic engine...
2025-12-26 20:05:34,452 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing ensemble validator (domain=physics)...
2025-12-26 20:05:35,206 - pint.util - WARNING - Redefining 'molar' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 20:05:35,207 - pint.util - WARNING - Redefining 'M' (<class 'pint.delegates.txt_defparser.plain.UnitDefinition'>)
2025-12-26 20:05:35,216 - hypatiax.tools.symbolic.hybrid_system - INFO - Initializing LLM providers...
2025-12-26 20:05:35,241 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Anthropic Claude provider initialized
2025-12-26 20:05:35,352 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Google Gemini provider initialized
2025-12-26 20:05:35,352 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ HybridDiscoverySystem initialized successfully
/home/agagora/Downloads/py312/lib/python3.12/site-packages/pysr/sr.py:2858: UserWarning: The `multithreading: bool` parameter has been deprecated in favor of `parallelism: Literal['multithreading', 'serial', 'multiprocessing']`.
Previous usage of `multithreading=True` (default) is now `parallelism='multithreading'`; `multithreading=False, procs=0` is now `parallelism='serial'`; and `multithreading=True, procs={int}` is now `parallelism='multiprocessing', procs={int}`.
  warnings.warn(
2025-12-26 20:06:10,833 - hypatiax.tools.symbolic.hybrid_system - INFO - 🤖 Interpreting with ANTHROPIC...
2025-12-26 20:06:21,655 - httpx - INFO - HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
2025-12-26 20:06:21,657 - hypatiax.tools.symbolic.hybrid_system - INFO - ✅ Interpretation completed via ANTHROPIC in 10.82s
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
✅ Found: (-4.070759 + (moles + moles**1.0206165)/volume)*(4.2701807*temperature + (moles + 3.7527869)*log(volume) - 3.479323)
   R² Score: 1.0000
   Complexity: 22

[2/3] ✓ Validating expression across 4 layers...
✓ Overall Score: 85.9/100
   Layer Scores:
     ✓ Symbolic: 71.0
     ✓ Dimensional: 90.0
     ✓ Domain: 92.0
     ✓ Numerical: 100.0

   ℹ Warnings: 7

[3/3] 🤖 Interpreting with real LLM API...
✅ Interpretation complete via ANTHROPIC
   Summary: This expression appears to calculate a thermodynamic property (likely entropy or a related state function) for a gas system, combining pressure-volume...
   Suggested name: Modified Gas State Function

======================================================================
✅ Workflow complete. Result stored (1/100)
======================================================================


================================================================================
                                    RESULTS                                     
================================================================================

SYMBOLIC DISCOVERY
--------------------------------------------------------------------------------

🔍 Discovered Expression:
   (-4.070759 + (moles + moles**1.0206165)/volume)*(4.2701807*temperature + (moles + 3.7527869)*log(volume) - 3.479323)

📊 Model Performance:
   • R² Score:    0.999966
   • Complexity:  22

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

✅ PASS Overall Valid: True
📊 Total Score: 85.90/100

📋 Layer Performance:
   ✅ Symbolic      :  71.00/100
   ✅ Dimensional   :  90.00/100
   ✅ Domain        :  92.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 1.0000
✅ Validation: Score = 85.90/100

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
   R² Score: 0.9998
   Complexity: 3

[2/3] ✓ Validating expression across 4 layers...
✓ Overall Score: 99.4/100
   Layer Scores:
     ✓ Symbolic: 100.0
     ✓ Dimensional: 98.0
     ✓ Domain: 100.0
     ✓ Numerical: 100.0

   ℹ Warnings: 1

[3/3] 🤖 Interpreting with real LLM API...
✅ Interpretation complete via ANTHROPIC
   Summary: This expression calculates voltage (electric potential difference) across a resistive element by multiplying electric current by resistance, represent...
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
   • R² Score:    0.999768
   • Complexity:  3

VALIDATION BREAKDOWN
--------------------------------------------------------------------------------

✅ PASS Overall Valid: True
📊 Total Score: 99.40/100

📋 Layer Performance:
   ✅ Symbolic      : 100.00/100
   ✅ Dimensional   :  98.00/100
   ✅ Domain        : 100.00/100
   ✅ Numerical     : 100.00/100

SUCCESS METRICS
--------------------------------------------------------------------------------

✅ Discovery:   R² = 0.9998
✅ Validation: Score = 99.40/100

========================================
           OVERALL: ✅ SUCCESS           
========================================


================================================================================
                               BATCH TEST SUMMARY                               
================================================================================

📊 Overall Statistics:
   • Total Tests:     18
   • Successful:      15
   • Failed:          3
   • Success Rate:    83.3%

🏆 Domain Breakdown:
   Biology     : 3/3 (100%)
   Chemistry   : 2/3 (67%)
   Economics   : 2/2 (100%)
   Engineering : 2/3 (67%)
   Mathematics : 3/3 (100%)
   Physics     : 3/4 (75%)

📋 Individual Results:
   ✅ michaelis_menten              : R²=0.9997, Val=86.9/100
   ✅ logistic_growth               : R²=0.9980, Val=85.0/100
   ✅ allometric_scaling            : R²=0.9995, Val=100.0/100
   ❌ arrhenius_equation            : R²=0.9971, Val=77.0/100
   ✅ henderson_hasselbalch         : R²=0.9991, Val=85.0/100
   ✅ nernst_equation               : R²=0.9989, Val=96.1/100
   ✅ elasticity_demand             : R²=1.0000, Val=88.9/100
   ✅ cobb_douglas                  : R²=0.9995, Val=87.4/100
   ✅ reynolds_number               : R²=0.9999, Val=88.0/100
   ✅ hookes_law                    : R²=0.9997, Val=97.0/100
   ❌ bernoulli_equation            : R²=0.9893, Val=71.9/100
   ✅ pythagorean_theorem           : R²=0.9987, Val=99.1/100
   ✅ compound_interest             : R²=0.9995, Val=88.3/100
   ✅ quadratic_formula             : R²=0.9998, Val=99.4/100
   ❌ projectile_motion             : R²=0.9489, Val=76.4/100
   ✅ kinetic_energy                : R²=0.9998, Val=97.9/100
   ✅ ideal_gas_law                 : R²=1.0000, Val=85.9/100
   ✅ ohms_law                      : R²=0.9998, Val=99.4/100
✓ Completed: complete_hybrid_system_all_domains.py
[2025-12-26 20:06:25] SUCCESS: Hybrid System (All Domains)
⚠ Hybrid system completed but no new files created


╔══════════════════════════════════════════════════════════════════════╗                                                         
║  PHASE 2: UNIFIED ANALYSIS                                                                                                     
╚══════════════════════════════════════════════════════════════════════╝                                                         
                                                                                                                                 
▶ Running Master Analyzer
▶ Running: master_analyzer.py
[2025-12-26 20:06:25] Starting: Master Analyzer (All Modules)
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
[2025-12-26 20:06:25] FAILED: Master Analyzer (All Modules) (exit code: 1)
⚠ Master analyzer had issues but continuing...


╔══════════════════════════════════════════════════════════════════════╗                                                         
║  PHASE 3: COMPREHENSIVE REPORTS                                                                                                
╚══════════════════════════════════════════════════════════════════════╝                                                         
                                                                                                                                 
▶ Generating Comprehensive Reports
▶ Running: analyze_hybrid_results.py
[2025-12-26 20:06:25] Starting: Comprehensive Analysis Report
✓ Working directory: /home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab
❌ No comparison_results directory found
✗ ERROR: Failed: analyze_hybrid_results.py (exit code: 1)
[2025-12-26 20:06:31] FAILED: Comprehensive Analysis Report (exit code: 1)


╔══════════════════════════════════════════════════════════════════════╗                                                         
  Pipeline Execution Summary                                                                                                     
╚══════════════════════════════════════════════════════════════════════╝                                                         
                                                                                                                                 
Configuration:
  • Domain: All domains (biology, chemistry, economics, engineering, physics, mathematics)
  • Mode: Quick (baselines skipped)
  • LLM Interpretation: ENABLED ✓

Directories:
  • Results: /home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab/hypatiax/data/results
  • Analysis: /home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab/analysis
  • Visualization Scripts: /home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab/hypatiax/tools/visualization
  • Log File: /home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab/logs/pipeline_20251226_194230.log

Files Created in This Run:

Total new files: 0

Total Files in Results Directory:
  • JSON results: 13
  • CSV tables: 2
  • PNG figures: 3

⚠ WARNING: No new files were created!
  Check the log file: /home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab/logs/pipeline_20251226_194230.log

Next Steps:
  1. Review results in: /home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab/hypatiax/data/results
  2. Check analysis in: /home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab/analysis
  3. View visualization scripts in: /home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab/hypatiax/tools/visualization
  4. View full log: /home/agagora/Downloads/GITHUB/LLM-HypatiaX-Colab/logs/pipeline_20251226_194230.log


Total execution time: 24m 0s
Finished at: Fri Dec 26 08:06:31 PM GMT 2025


┌──(py312)(agagora㉿localhost)-[~/Downloads/GITHUB/LLM-HypatiaX-Colab/tests]
└─$                                                 
