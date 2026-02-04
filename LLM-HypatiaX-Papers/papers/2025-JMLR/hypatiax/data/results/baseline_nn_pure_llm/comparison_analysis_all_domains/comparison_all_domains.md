─$ python results/comparison_analysis_improved.py results/baseline_llm_PARSED.json results/baseline_nn_PARSED.json
✅ Loaded LLM results from: results/baseline_llm_PARSED.json
✅ Loaded NN results from: results/baseline_nn_PARSED.json
====================================================================================================
                            GENERATING COMPREHENSIVE COMPARISON ANALYSIS
====================================================================================================

📊 Creating comparison tables...
✅ Saved: results/comparison_analysis/detailed_comparison.csv

📈 Generating visualizations...
✅ Saved: results/comparison_analysis/overall_comparison.png
✅ Saved: results/comparison_analysis/domain_comparison.png
✅ Saved: results/comparison_analysis/formula_type_comparison.png
⚠ No extrapolation test cases found

📝 Creating summary tables...
✅ Saved: results/comparison_analysis/summary_tables.txt

====================================================================================================
                                         SUMMARY STATISTICS
====================================================================================================

Overall Performance:
  LLM Mean R²: 0.8000 (±0.8945)
  NN Mean R²:  0.9892 (±0.0238)
  LLM Advantage: -0.1892

Win Rates:
  LLM: 10/20 (50.0%)
  NN:  1/20 (5.0%)
  Tie: 9/20 (45.0%)

Performance by Quality:
  Excellent (R² > 0.99):
    LLM: 19/20 (95.0%)
    NN:  14/20 (70.0%)

  Good (R² > 0.95):
    LLM: 19/20 (95.0%)
    NN:  19/20 (95.0%)

====================================================================================================
                                      DOMAIN-SPECIFIC ANALYSIS
====================================================================================================

CHEMISTRY:
  Cases: 4
  LLM Mean R²: -0.0001
  NN Mean R²:  0.9990
  Advantage:   -0.9991 (NN wins)

FLUIDS:
  Cases: 4
  LLM Mean R²: 1.0000
  NN Mean R²:  0.9641
  Advantage:   +0.0359 (LLM wins)

MATERIALS:
  Cases: 4
  LLM Mean R²: 1.0000
  NN Mean R²:  0.9985
  Advantage:   +0.0015 (LLM wins)

MECHANICS:
  Cases: 4
  LLM Mean R²: 1.0000
  NN Mean R²:  0.9869
  Advantage:   +0.0131 (LLM wins)

THERMODYNAMICS:
  Cases: 4
  LLM Mean R²: 1.0000
  NN Mean R²:  0.9972
  Advantage:   +0.0028 (LLM wins)

====================================================================================================
                                         CRITICAL INSIGHTS
====================================================================================================

⚠  Cases where NN has advantage (R² diff < -0.1):
  • Henderson-Hasselbalch equation: pH of buffer solut
    NN: 0.9969 vs LLM: -3.0003 (Δ = -3.9972)

====================================================================================================
                                          FAILURE ANALYSIS
====================================================================================================

LLM Failures (R² < 0.80): 1/20
  • Henderson-Hasselbalch equation: pH of buffer solut
    R² = -3.0003, Domain: chemistry

NN Failures (R² < 0.80): 0/20

🚨 CATASTROPHIC FAILURES (R² < 0):

  LLM: 1 cases
    • Henderson-Hasselbalch equation: pH of buffer solut: R² = -3.0003

====================================================================================================
                                          RECOMMENDATIONS
====================================================================================================

💡 Based on the analysis:

✅ PREFER NN APPROACH for:
  • Overall superior performance across domains
  • 5.0% win rate vs 50.0%
  • Complex non-linear patterns
  • When interpretability is not required

📊 Domain-specific recommendations:
  • chemistry           : NN ✅            (LLM: -0.000, NN: 0.999)
  • fluids              : Either ⚖       (LLM: 1.000, NN: 0.964)
  • materials           : Either ⚖       (LLM: 1.000, NN: 0.999)
  • mechanics           : Either ⚖       (LLM: 1.000, NN: 0.987)
  • thermodynamics      : Either ⚖       (LLM: 1.000, NN: 0.997)

====================================================================================================
✅ All results saved to: results/comparison_analysis
====================================================================================================

Generated files:
  • detailed_comparison.csv
  • summary_tables.txt
  • comparison_summary.json
  • overall_comparison.png
  • domain_comparison.png
  • formula_type_comparison.png
  • extrapolation_analysis.png
