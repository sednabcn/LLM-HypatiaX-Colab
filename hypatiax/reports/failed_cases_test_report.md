─$ python tests/test_failed_cases_only.py                                                                                       


╔══════════════════════════════════════════════════════════════════════════════╗
║                    FAILED CASES RETEST SUITE                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

Testing 11 failed cases from original run
Threshold: 85.0/100 to pass

================================================================================
TEST: michaelis_menten
================================================================================
Domain: biology
Expression: (Vmax * substrate_concentration) / (km + substrate_concentration)
Previous Score: 52.5/100
Main Issue: Dimensional inconsistencies in addition

✓ NEW SCORE: 97.0/100
  Valid: True
  Base Score: 97.0

Layer Scores:
  ✓ symbolic: 100.0/100
  ✓ dimensional: 98.0/100
  ✓ domain: 92.0/100
  ✓ numerical: 100.0/100

Acceptance Criteria:
  ✓ minimum_score_met: True
  ✓ symbolic_valid: True
  ✓ dimensional_valid: True
  ✓ domain_valid: True
  ✓ no_critical_edge_cases: True
  ✓ threshold_used: 85.0
  ✓ all_layers_above_critical: True

WARNINGS:
  • Multiplication of variables: verify dimensional consistency
  • Michaelis-Menten pattern detected. Ensure Km > 0 and substrate S >= 0
  • Found 1 division(s). Consider epsilon protection: (denominator + ε) where ε = 1e-10

TOP RECOMMENDATIONS:
  • 🟡 VERIFY: Check dimensional analysis warnings
  • 🟡 REVIEW: Address biology domain warnings

================================================================================
TEST: logistic_growth
================================================================================
Domain: biology
Expression: growth_rate * population * (1 - population / carrying_capacity)
Previous Score: 76.1/100
Main Issue: Dimensional warnings

✓ NEW SCORE: 97.0/100
  Valid: True
  Base Score: 97.0

Layer Scores:
  ✓ symbolic: 98.0/100
  ✓ dimensional: 95.0/100
  ✓ domain: 97.0/100
  ✓ numerical: 100.0/100

Acceptance Criteria:
  ✓ minimum_score_met: True
  ✓ symbolic_valid: True
  ✓ dimensional_valid: True
  ✓ domain_valid: True
  ✓ no_critical_edge_cases: True
  ✓ threshold_used: 85.0
  ✓ all_layers_above_critical: True

WARNINGS:
  • Can be simplified to: growth_rate*population*(carrying_capacity - population)/carrying_capacity
  • Division by 'carrying_capacity' - ensure carrying_capacity ≠ 0
  • Multiplication of variables: verify dimensional consistency
  ... and 2 more

TOP RECOMMENDATIONS:
  • 🟡 VERIFY: Check dimensional analysis warnings
  • 🟡 REVIEW: Address biology domain warnings

================================================================================
TEST: allometric_scaling
================================================================================
Domain: biology
Expression: coefficient * mass**exponent
Previous Score: 81.4/100
Main Issue: Unit attribute errors

✓ NEW SCORE: 89.8/100
  Valid: True
  Base Score: 89.8

Layer Scores:
  ✓ symbolic: 73.0/100
  ✓ dimensional: 93.0/100
  ✓ domain: 100.0/100
  ✓ numerical: 100.0/100

Acceptance Criteria:
  ✓ minimum_score_met: True
  ✓ symbolic_valid: True
  ✓ dimensional_valid: True
  ✓ domain_valid: True
  ✓ no_critical_edge_cases: True
  ✓ threshold_used: 85.0
  ✓ all_layers_above_critical: True

WARNINGS:
  • Power overflow risk: (mass)^(exponent). Verify bounds on base and exponent
  • Exponent contains dimensional variables: exponent. Exponents must be dimensionless.
  • Variable exponent: mass^exponent - verify bounds carefully
  ... and 1 more

TOP RECOMMENDATIONS:
  • 🟡 VERIFY: Check dimensional analysis warnings
  • 🟡 IMPROVE: Simplify to: coefficient*mass**exponent

================================================================================
TEST: arrhenius_equation
================================================================================
Domain: chemistry
Expression: pre_exponential * exp(-activation_energy / (gas_constant * temperature))
Previous Score: 78.7/100
Main Issue: Complex expression warnings

✓ NEW SCORE: 86.8/100
  Valid: True
  Base Score: 86.8

Layer Scores:
  ✓ symbolic: 73.0/100
  ✓ dimensional: 96.0/100
  ✓ domain: 87.0/100
  ✓ numerical: 100.0/100

Acceptance Criteria:
  ✓ minimum_score_met: True
  ✓ symbolic_valid: True
  ✓ dimensional_valid: True
  ✓ domain_valid: True
  ✓ no_critical_edge_cases: True
  ✓ threshold_used: 85.0
  ✓ all_layers_above_critical: True

WARNINGS:
  • Exponential overflow risk: exp(-activation_energy/(gas_constant*temperature)). Recommend capping argument or using safe_exp
  • Function exp((-activation_energy)/((gas_constant*temperature))) has dimensional argument. Should be dimensionless ratio.
  • Multiplication of variables: verify dimensional consistency
  ... and 1 more

TOP RECOMMENDATIONS:
  • 🟡 VERIFY: Check dimensional analysis warnings
  • 🟡 IMPROVE: Simplify to: pre_exponential*exp(-activation_energy/(gas_constant*temperature))
  • 🟡 REVIEW: Address chemistry domain warnings

================================================================================
TEST: henderson_hasselbalch
================================================================================
Domain: chemistry
Expression: pKa + log10(base_concentration / (acid_concentration + 1e-10))
Previous Score: 71.9/100
Main Issue: Unit attribute error for pKa

✓ NEW SCORE: 93.4/100
  Valid: True
  Base Score: 93.4

Layer Scores:
  ✓ symbolic: 100.0/100
  ✓ dimensional: 98.0/100
  ✓ domain: 90.0/100
  ✓ numerical: 70.0/100

Acceptance Criteria:
  ✓ minimum_score_met: True
  ✓ symbolic_valid: True
  ✓ dimensional_valid: True
  ✓ domain_valid: True
  ✓ no_critical_edge_cases: True
  ✓ threshold_used: 85.0
  ✓ all_layers_above_critical: True

ERRORS:
  • Evaluation error at sample 0: Cannot convert expression to float
  • Evaluation error at sample 1: Cannot convert expression to float
  • Evaluation error at sample 2: Cannot convert expression to float

WARNINGS:
  • Multiplication of variables: verify dimensional consistency

TOP RECOMMENDATIONS:
  • 🟡 VERIFY: Check dimensional analysis warnings
  • 🔴 FIX: Resolve numerical stability issues

================================================================================
TEST: nernst_equation
================================================================================
Domain: chemistry
Expression: standard_potential - (gas_constant * temperature / (charge * faraday_constant)) * log(reaction_quotient)
Previous Score: 67.2/100
Main Issue: Multiple unit attribute errors

✓ NEW SCORE: 85.3/100
  Valid: True
  Base Score: 85.3

Layer Scores:
  ✓ symbolic: 71.0/100
  ✓ dimensional: 93.0/100
  ✓ domain: 87.0/100
  ✓ numerical: 100.0/100

Acceptance Criteria:
  ✓ minimum_score_met: True
  ✓ symbolic_valid: True
  ✓ dimensional_valid: True
  ✓ domain_valid: True
  ✓ no_critical_edge_cases: True
  ✓ threshold_used: 85.0
  ✓ all_layers_above_critical: True

WARNINGS:
  • Multiple multiplications (6 terms) - check for overflow. Consider: -1 * gas_constant * temperature...
  • Logarithm of non-positive value risk: log(reaction_quotient). Ensure reaction_quotient > 0
  • Function log(reaction_quotient) has dimensional argument. Should be dimensionless ratio.
  ... and 3 more

TOP RECOMMENDATIONS:
  • 🟡 VERIFY: Check dimensional analysis warnings
  • 🟡 IMPROVE: Simplify to: standard_potential - gas_constant*temperature*log(reaction_quotient)/(charge*faraday_constant)
  • 🟡 REVIEW: Address chemistry domain warnings

================================================================================
TEST: cobb_douglas
================================================================================
Domain: economics
Expression: productivity * capital**capital_share * labor**labor_share
Previous Score: 78.5/100
Main Issue: Unit attribute errors for shares

✓ NEW SCORE: 87.7/100
  Valid: True
  Base Score: 87.7

Layer Scores:
  ✓ symbolic: 71.0/100
  ✓ dimensional: 88.0/100
  ✓ domain: 100.0/100
  ✓ numerical: 100.0/100

Acceptance Criteria:
  ✓ minimum_score_met: True
  ✓ symbolic_valid: True
  ✓ dimensional_valid: True
  ✓ domain_valid: True
  ✓ no_critical_edge_cases: True
  ✓ threshold_used: 85.0
  ✓ all_layers_above_critical: True

WARNINGS:
  • Power overflow risk: (capital)^(capital_share). Verify bounds on base and exponent
  • Power overflow risk: (labor)^(labor_share). Verify bounds on base and exponent
  • Exponent contains dimensional variables: capital_share. Exponents must be dimensionless.
  ... and 4 more

TOP RECOMMENDATIONS:
  • 🟡 VERIFY: Check dimensional analysis warnings
  • 🟡 IMPROVE: Simplify to: capital**capital_share*labor**labor_share*productivity

================================================================================
TEST: bernoulli_equation
================================================================================
Domain: engineering
Expression: pressure + 0.5 * density * velocity**2 + density * gravity * height
Previous Score: 71.0/100
Main Issue: Incompatible units in addition

✓ NEW SCORE: 89.8/100
  Valid: True
  Base Score: 89.8

Layer Scores:
  ✓ symbolic: 73.0/100
  ✓ dimensional: 98.0/100
  ✓ domain: 95.0/100
  ✓ numerical: 100.0/100

Acceptance Criteria:
  ✓ minimum_score_met: True
  ✓ symbolic_valid: True
  ✓ dimensional_valid: True
  ✓ domain_valid: True
  ✓ no_critical_edge_cases: True
  ✓ threshold_used: 85.0
  ✓ all_layers_above_critical: True

WARNINGS:
  • Multiple multiplications (6 terms) - check for overflow. Consider: 0.500000000000000 * density * velocity**2...
  • Multiplication of variables: verify dimensional consistency

TOP RECOMMENDATIONS:
  • 🟡 VERIFY: Check dimensional analysis warnings
  • 🟡 IMPROVE: Simplify to: density*gravity*height + 0.5*density*velocity**2 + pressure

================================================================================
TEST: compound_interest
================================================================================
Domain: mathematics
Expression: principal * (1 + rate / compounds_per_year)**(compounds_per_year * time)
Previous Score: 84.4/100
Main Issue: Just below 85.0 threshold, unit attribute error

✓ NEW SCORE: 87.4/100
  Valid: True
  Base Score: 87.4

Layer Scores:
  ✓ symbolic: 71.0/100
  ✓ dimensional: 90.0/100
  ✓ domain: 97.0/100
  ✓ numerical: 100.0/100

Acceptance Criteria:
  ✓ minimum_score_met: True
  ✓ symbolic_valid: True
  ✓ dimensional_valid: True
  ✓ domain_valid: True
  ✓ no_critical_edge_cases: True
  ✓ threshold_used: 85.0
  ✓ all_layers_above_critical: True

WARNINGS:
  • Can be simplified to: principal*((compounds_per_year + rate)/compounds_per_year)**(compounds_per_year*time)
  • Power overflow risk: (1 + rate/compounds_per_year)^(compounds_per_year*time). Verify bounds on base and exponent
  • Exponent contains dimensional variables: compounds_per_year*time. Exponents must be dimensionless.
  ... and 4 more

TOP RECOMMENDATIONS:
  • 🟡 VERIFY: Check dimensional analysis warnings
  • 🟡 IMPROVE: Simplify to: principal*((compounds_per_year + rate)/compounds_per_year)**(compounds_per_year*time)
  • 🟡 REVIEW: Address mathematics domain warnings

================================================================================
TEST: quadratic_formula
================================================================================
Domain: mathematics
Expression: coefficient_b**2 - 4 * coefficient_a * coefficient_c
Previous Score: 89.5/100
Main Issue: Just below threshold, unit attribute errors

✓ NEW SCORE: 99.4/100
  Valid: True
  Base Score: 99.4

Layer Scores:
  ✓ symbolic: 100.0/100
  ✓ dimensional: 98.0/100
  ✓ domain: 100.0/100
  ✓ numerical: 100.0/100

Acceptance Criteria:
  ✓ minimum_score_met: True
  ✓ symbolic_valid: True
  ✓ dimensional_valid: True
  ✓ domain_valid: True
  ✓ no_critical_edge_cases: True
  ✓ threshold_used: 85.0
  ✓ all_layers_above_critical: True

WARNINGS:
  • Multiplication of variables: verify dimensional consistency

TOP RECOMMENDATIONS:
  • 🟡 VERIFY: Check dimensional analysis warnings

================================================================================
TEST: projectile_motion
================================================================================
Domain: physics
Expression: (initial_velocity**2 * sin(2 * angle)) / gravity
Previous Score: 78.2/100
Main Issue: Complex expression warnings

✓ NEW SCORE: 88.9/100
  Valid: True
  Base Score: 88.9

Layer Scores:
  ✓ symbolic: 73.0/100
  ✓ dimensional: 93.0/100
  ✓ domain: 97.0/100
  ✓ numerical: 100.0/100

Acceptance Criteria:
  ✓ minimum_score_met: True
  ✓ symbolic_valid: True
  ✓ dimensional_valid: True
  ✓ domain_valid: True
  ✓ no_critical_edge_cases: True
  ✓ threshold_used: 85.0
  ✓ all_layers_above_critical: True

WARNINGS:
  • Trigonometric functions - verify input ranges
  • Trigonometric function sin(2*angle) requires angle (dimensionless in radians)
  • Division by 'gravity' - ensure gravity ≠ 0
  ... and 2 more

TOP RECOMMENDATIONS:
  • 🟡 VERIFY: Check dimensional analysis warnings
  • 🟡 IMPROVE: Simplify to: initial_velocity**2*sin(2*angle)/gravity
  • 🟡 REVIEW: Address physics domain warnings



╔══════════════════════════════════════════════════════════════════════════════╗
║                              SUMMARY REPORT                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

Total Tests: 11
Now Passing: 11 (100.0%)
Still Failing: 0 (0.0%)

Average Score Before: 75.4/100
Average Score After:  91.1/100
Average Improvement:  +15.7

BY DOMAIN:
  biology        : 3/3 passing (100%)
  chemistry      : 3/3 passing (100%)
  economics      : 1/1 passing (100%)
  engineering    : 1/1 passing (100%)
  mathematics    : 2/2 passing (100%)
  physics        : 1/1 passing (100%)

TOP 5 IMPROVEMENTS:
  ✓ PASS michaelis_menten         :  52.5 →  97.0 (+44.5)
  ✓ PASS henderson_hasselbalch    :  71.9 →  93.4 (+21.5)
  ✓ PASS logistic_growth          :  76.1 →  97.0 (+20.9)
  ✓ PASS bernoulli_equation       :  71.0 →  89.8 (+18.8)
  ✓ PASS nernst_equation          :  67.2 →  85.3 (+18.1)


================================================================================
┌──(py312)(agagora㉿localhost)-[~/Downloads/GITHUB/LLM-HypatiaX-Colab]
└─$ python tests/test_failed_cases_only.py                                                                                       


╔══════════════════════════════════════════════════════════════════════════════╗
║                    FAILED CASES RETEST SUITE                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

Testing 11 failed cases from original run
Threshold: 85.0/100 to pass

================================================================================
TEST: michaelis_menten
================================================================================
Domain: biology
Expression: (Vmax * substrate_concentration) / (km + substrate_concentration)
Previous Score: 52.5/100
Main Issue: Dimensional inconsistencies in addition

✓ NEW SCORE: 97.0/100
  Valid: True
  Base Score: 97.0

Layer Scores:
  ✓ symbolic: 100.0/100
  ✓ dimensional: 98.0/100
  ✓ domain: 92.0/100
  ✓ numerical: 100.0/100

Acceptance Criteria:
  ✓ minimum_score_met: True
  ✓ symbolic_valid: True
  ✓ dimensional_valid: True
  ✓ domain_valid: True
  ✓ no_critical_edge_cases: True
  ✓ threshold_used: 85.0
  ✓ all_layers_above_critical: True

WARNINGS:
  • Multiplication of variables: verify dimensional consistency
  • Michaelis-Menten pattern detected. Ensure Km > 0 and substrate S >= 0
  • Found 1 division(s). Consider epsilon protection: (denominator + ε) where ε = 1e-10

TOP RECOMMENDATIONS:
  • 🟡 VERIFY: Check dimensional analysis warnings
  • 🟡 REVIEW: Address biology domain warnings

================================================================================
TEST: logistic_growth
================================================================================
Domain: biology
Expression: growth_rate * population * (1 - population / carrying_capacity)
Previous Score: 76.1/100
Main Issue: Dimensional warnings

✓ NEW SCORE: 97.0/100
  Valid: True
  Base Score: 97.0

Layer Scores:
  ✓ symbolic: 98.0/100
  ✓ dimensional: 95.0/100
  ✓ domain: 97.0/100
  ✓ numerical: 100.0/100

Acceptance Criteria:
  ✓ minimum_score_met: True
  ✓ symbolic_valid: True
  ✓ dimensional_valid: True
  ✓ domain_valid: True
  ✓ no_critical_edge_cases: True
  ✓ threshold_used: 85.0
  ✓ all_layers_above_critical: True

WARNINGS:
  • Can be simplified to: growth_rate*population*(carrying_capacity - population)/carrying_capacity
  • Division by 'carrying_capacity' - ensure carrying_capacity ≠ 0
  • Multiplication of variables: verify dimensional consistency
  ... and 2 more

TOP RECOMMENDATIONS:
  • 🟡 VERIFY: Check dimensional analysis warnings
  • 🟡 REVIEW: Address biology domain warnings

================================================================================
TEST: allometric_scaling
================================================================================
Domain: biology
Expression: coefficient * mass**exponent
Previous Score: 81.4/100
Main Issue: Unit attribute errors

✓ NEW SCORE: 89.8/100
  Valid: True
  Base Score: 89.8

Layer Scores:
  ✓ symbolic: 73.0/100
  ✓ dimensional: 93.0/100
  ✓ domain: 100.0/100
  ✓ numerical: 100.0/100

Acceptance Criteria:
  ✓ minimum_score_met: True
  ✓ symbolic_valid: True
  ✓ dimensional_valid: True
  ✓ domain_valid: True
  ✓ no_critical_edge_cases: True
  ✓ threshold_used: 85.0
  ✓ all_layers_above_critical: True

WARNINGS:
  • Power overflow risk: (mass)^(exponent). Verify bounds on base and exponent
  • Exponent contains dimensional variables: exponent. Exponents must be dimensionless.
  • Variable exponent: mass^exponent - verify bounds carefully
  ... and 1 more

TOP RECOMMENDATIONS:
  • 🟡 VERIFY: Check dimensional analysis warnings
  • 🟡 IMPROVE: Simplify to: coefficient*mass**exponent

================================================================================
TEST: arrhenius_equation
================================================================================
Domain: chemistry
Expression: pre_exponential * exp(-activation_energy / (gas_constant * temperature))
Previous Score: 78.7/100
Main Issue: Complex expression warnings

✓ NEW SCORE: 86.8/100
  Valid: True
  Base Score: 86.8

Layer Scores:
  ✓ symbolic: 73.0/100
  ✓ dimensional: 96.0/100
  ✓ domain: 87.0/100
  ✓ numerical: 100.0/100

Acceptance Criteria:
  ✓ minimum_score_met: True
  ✓ symbolic_valid: True
  ✓ dimensional_valid: True
  ✓ domain_valid: True
  ✓ no_critical_edge_cases: True
  ✓ threshold_used: 85.0
  ✓ all_layers_above_critical: True

WARNINGS:
  • Exponential overflow risk: exp(-activation_energy/(gas_constant*temperature)). Recommend capping argument or using safe_exp
  • Function exp((-activation_energy)/((gas_constant*temperature))) has dimensional argument. Should be dimensionless ratio.
  • Multiplication of variables: verify dimensional consistency
  ... and 1 more

TOP RECOMMENDATIONS:
  • 🟡 VERIFY: Check dimensional analysis warnings
  • 🟡 IMPROVE: Simplify to: pre_exponential*exp(-activation_energy/(gas_constant*temperature))
  • 🟡 REVIEW: Address chemistry domain warnings

================================================================================
TEST: henderson_hasselbalch
================================================================================
Domain: chemistry
Expression: pKa + log10(base_concentration / (acid_concentration + 1e-10))
Previous Score: 71.9/100
Main Issue: Unit attribute error for pKa

✓ NEW SCORE: 95.5/100
  Valid: True
  Base Score: 95.5

Layer Scores:
  ✓ symbolic: 100.0/100
  ✓ dimensional: 98.0/100
  ✓ domain: 90.0/100
  ✓ numerical: 91.0/100

Acceptance Criteria:
  ✓ minimum_score_met: True
  ✓ symbolic_valid: True
  ✓ dimensional_valid: True
  ✓ domain_valid: True
  ✓ no_critical_edge_cases: True
  ✓ threshold_used: 85.0
  ✓ all_layers_above_critical: True

WARNINGS:
  • Multiplication of variables: verify dimensional consistency
  • Numerical evaluation skipped at sample 0: Cannot convert expression to float
  • Numerical evaluation skipped at sample 1: Cannot convert expression to float
  ... and 1 more

TOP RECOMMENDATIONS:
  • 🟡 VERIFY: Check dimensional analysis warnings
  • 🟡 OPTIMIZE: Improve numerical stability

================================================================================
TEST: nernst_equation
================================================================================
Domain: chemistry
Expression: standard_potential - (gas_constant * temperature / (charge * faraday_constant)) * log(reaction_quotient)
Previous Score: 67.2/100
Main Issue: Multiple unit attribute errors

✓ NEW SCORE: 85.3/100
  Valid: True
  Base Score: 85.3

Layer Scores:
  ✓ symbolic: 71.0/100
  ✓ dimensional: 93.0/100
  ✓ domain: 87.0/100
  ✓ numerical: 100.0/100

Acceptance Criteria:
  ✓ minimum_score_met: True
  ✓ symbolic_valid: True
  ✓ dimensional_valid: True
  ✓ domain_valid: True
  ✓ no_critical_edge_cases: True
  ✓ threshold_used: 85.0
  ✓ all_layers_above_critical: True

WARNINGS:
  • Multiple multiplications (6 terms) - check for overflow. Consider: -1 * gas_constant * temperature...
  • Logarithm of non-positive value risk: log(reaction_quotient). Ensure reaction_quotient > 0
  • Function log(reaction_quotient) has dimensional argument. Should be dimensionless ratio.
  ... and 3 more

TOP RECOMMENDATIONS:
  • 🟡 VERIFY: Check dimensional analysis warnings
  • 🟡 IMPROVE: Simplify to: standard_potential - gas_constant*temperature*log(reaction_quotient)/(charge*faraday_constant)
  • 🟡 REVIEW: Address chemistry domain warnings

================================================================================
TEST: cobb_douglas
================================================================================
Domain: economics
Expression: productivity * capital**capital_share * labor**labor_share
Previous Score: 78.5/100
Main Issue: Unit attribute errors for shares

✓ NEW SCORE: 87.7/100
  Valid: True
  Base Score: 87.7

Layer Scores:
  ✓ symbolic: 71.0/100
  ✓ dimensional: 88.0/100
  ✓ domain: 100.0/100
  ✓ numerical: 100.0/100

Acceptance Criteria:
  ✓ minimum_score_met: True
  ✓ symbolic_valid: True
  ✓ dimensional_valid: True
  ✓ domain_valid: True
  ✓ no_critical_edge_cases: True
  ✓ threshold_used: 85.0
  ✓ all_layers_above_critical: True

WARNINGS:
  • Power overflow risk: (capital)^(capital_share). Verify bounds on base and exponent
  • Power overflow risk: (labor)^(labor_share). Verify bounds on base and exponent
  • Exponent contains dimensional variables: capital_share. Exponents must be dimensionless.
  ... and 4 more

TOP RECOMMENDATIONS:
  • 🟡 VERIFY: Check dimensional analysis warnings
  • 🟡 IMPROVE: Simplify to: capital**capital_share*labor**labor_share*productivity

================================================================================
TEST: bernoulli_equation
================================================================================
Domain: engineering
Expression: pressure + 0.5 * density * velocity**2 + density * gravity * height
Previous Score: 71.0/100
Main Issue: Incompatible units in addition

✓ NEW SCORE: 89.8/100
  Valid: True
  Base Score: 89.8

Layer Scores:
  ✓ symbolic: 73.0/100
  ✓ dimensional: 98.0/100
  ✓ domain: 95.0/100
  ✓ numerical: 100.0/100

Acceptance Criteria:
  ✓ minimum_score_met: True
  ✓ symbolic_valid: True
  ✓ dimensional_valid: True
  ✓ domain_valid: True
  ✓ no_critical_edge_cases: True
  ✓ threshold_used: 85.0
  ✓ all_layers_above_critical: True

WARNINGS:
  • Multiple multiplications (6 terms) - check for overflow. Consider: 0.500000000000000 * density * velocity**2...
  • Multiplication of variables: verify dimensional consistency

TOP RECOMMENDATIONS:
  • 🟡 VERIFY: Check dimensional analysis warnings
  • 🟡 IMPROVE: Simplify to: density*gravity*height + 0.5*density*velocity**2 + pressure

================================================================================
TEST: compound_interest
================================================================================
Domain: mathematics
Expression: principal * (1 + rate / compounds_per_year)**(compounds_per_year * time)
Previous Score: 84.4/100
Main Issue: Just below 85.0 threshold, unit attribute error

✓ NEW SCORE: 87.4/100
  Valid: True
  Base Score: 87.4

Layer Scores:
  ✓ symbolic: 71.0/100
  ✓ dimensional: 90.0/100
  ✓ domain: 97.0/100
  ✓ numerical: 100.0/100

Acceptance Criteria:
  ✓ minimum_score_met: True
  ✓ symbolic_valid: True
  ✓ dimensional_valid: True
  ✓ domain_valid: True
  ✓ no_critical_edge_cases: True
  ✓ threshold_used: 85.0
  ✓ all_layers_above_critical: True

WARNINGS:
  • Can be simplified to: principal*((compounds_per_year + rate)/compounds_per_year)**(compounds_per_year*time)
  • Power overflow risk: (1 + rate/compounds_per_year)^(compounds_per_year*time). Verify bounds on base and exponent
  • Exponent contains dimensional variables: compounds_per_year*time. Exponents must be dimensionless.
  ... and 4 more

TOP RECOMMENDATIONS:
  • 🟡 VERIFY: Check dimensional analysis warnings
  • 🟡 IMPROVE: Simplify to: principal*((compounds_per_year + rate)/compounds_per_year)**(compounds_per_year*time)
  • 🟡 REVIEW: Address mathematics domain warnings

================================================================================
TEST: quadratic_formula
================================================================================
Domain: mathematics
Expression: coefficient_b**2 - 4 * coefficient_a * coefficient_c
Previous Score: 89.5/100
Main Issue: Just below threshold, unit attribute errors

✓ NEW SCORE: 99.4/100
  Valid: True
  Base Score: 99.4

Layer Scores:
  ✓ symbolic: 100.0/100
  ✓ dimensional: 98.0/100
  ✓ domain: 100.0/100
  ✓ numerical: 100.0/100

Acceptance Criteria:
  ✓ minimum_score_met: True
  ✓ symbolic_valid: True
  ✓ dimensional_valid: True
  ✓ domain_valid: True
  ✓ no_critical_edge_cases: True
  ✓ threshold_used: 85.0
  ✓ all_layers_above_critical: True

WARNINGS:
  • Multiplication of variables: verify dimensional consistency

TOP RECOMMENDATIONS:
  • 🟡 VERIFY: Check dimensional analysis warnings

================================================================================
TEST: projectile_motion
================================================================================
Domain: physics
Expression: (initial_velocity**2 * sin(2 * angle)) / gravity
Previous Score: 78.2/100
Main Issue: Complex expression warnings

✓ NEW SCORE: 88.9/100
  Valid: True
  Base Score: 88.9

Layer Scores:
  ✓ symbolic: 73.0/100
  ✓ dimensional: 93.0/100
  ✓ domain: 97.0/100
  ✓ numerical: 100.0/100

Acceptance Criteria:
  ✓ minimum_score_met: True
  ✓ symbolic_valid: True
  ✓ dimensional_valid: True
  ✓ domain_valid: True
  ✓ no_critical_edge_cases: True
  ✓ threshold_used: 85.0
  ✓ all_layers_above_critical: True

WARNINGS:
  • Trigonometric functions - verify input ranges
  • Trigonometric function sin(2*angle) requires angle (dimensionless in radians)
  • Division by 'gravity' - ensure gravity ≠ 0
  ... and 2 more

TOP RECOMMENDATIONS:
  • 🟡 VERIFY: Check dimensional analysis warnings
  • 🟡 IMPROVE: Simplify to: initial_velocity**2*sin(2*angle)/gravity
  • 🟡 REVIEW: Address physics domain warnings



╔══════════════════════════════════════════════════════════════════════════════╗
║                              SUMMARY REPORT                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

Total Tests: 11
Now Passing: 11 (100.0%)
Still Failing: 0 (0.0%)

Average Score Before: 75.4/100
Average Score After:  91.3/100
Average Improvement:  +15.9

BY DOMAIN:
  biology        : 3/3 passing (100%)
  chemistry      : 3/3 passing (100%)
  economics      : 1/1 passing (100%)
  engineering    : 1/1 passing (100%)
  mathematics    : 2/2 passing (100%)
  physics        : 1/1 passing (100%)

TOP 5 IMPROVEMENTS:
  ✓ PASS michaelis_menten         :  52.5 →  97.0 (+44.5)
  ✓ PASS henderson_hasselbalch    :  71.9 →  95.5 (+23.6)
  ✓ PASS logistic_growth          :  76.1 →  97.0 (+20.9)
  ✓ PASS bernoulli_equation       :  71.0 →  89.8 (+18.8)
  ✓ PASS nernst_equation          :  67.2 →  85.3 (+18.1)


================================================================================

┌──(py312)(agagora㉿localhost)-[~/Downloads/GITHUB/LLM-HypatiaX-Colab]
