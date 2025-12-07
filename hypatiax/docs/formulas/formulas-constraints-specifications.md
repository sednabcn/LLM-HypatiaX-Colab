# HypatiaX Formula Constraint Specifications

## Comprehensive Guide to Mathematical Constraints & Domain Rules

**Version:** 2.0
**Last Updated:** Week 2 Critical Updates
**Status:** Production Standard

---

## Table of Contents

1. [Overview](#overview)
2. [Constraint Types](#constraint-types)
3. [DeFi Domain Constraints](#defi-domain-constraints)
4. [Physics Domain Constraints](#physics-domain-constraints)
5. [Chemistry Domain Constraints](#chemistry-domain-constraints)
6. [Edge Case Constraints](#edge-case-constraints)
7. [Constraint Validation Rules](#constraint-validation-rules)
8. [Implementation Guide](#implementation-guide)

---

## Overview

### Purpose

This document defines **mandatory constraints** for all mathematical formulas in the HypatiaX system. Constraints ensure:

- ✅ Mathematical validity (no division by zero, domain errors)
- ✅ Physical/financial plausibility
- ✅ Numerical stability (no overflow/underflow)
- ✅ Edge case protection

### Constraint Enforcement Levels

| Level | Description | Action on Violation |
|-------|-------------|---------------------|
| **CRITICAL** | Safety violations (div/0, overflow) | Auto-reject, -15 points |
| **REQUIRED** | Domain rules (price > 0) | Auto-reject, -10 points |
| **RECOMMENDED** | Best practices (bounds) | Warning, -5 points |
| **OPTIONAL** | Optimization hints | No penalty |

---

## Constraint Types

### 1. Non-Zero Constraints

**Purpose:** Prevent division by zero and ensure non-degenerate cases

**Syntax:**

```python
'variable != 0'
'variable > 0'        # Strictly positive
'variable >= epsilon' # Positive with guard
```

**Examples:**

```python
# Division operations
{
    'expression': '1/x',
    'constraints': ['x != 0', 'x > 1e-10']  # Epsilon guard
}

# DeFi price ratios
{
    'expression': 'sqrt(r/(1+r))',
    'constraints': ['r > 0', 'r > 1e-10']  # CRITICAL
}

# Denominators in physics
{
    'expression': 'F = G*m1*m2/r^2',
    'constraints': ['r > 0', 'm1 > 0', 'm2 > 0']  # CRITICAL
}
```

**Enforcement Level:** CRITICAL
**Penalty:** -15 points (auto-fail below 85.0 threshold)

---

### 2. Positivity Constraints

**Purpose:** Ensure physically/financially meaningful positive quantities

**Syntax:**

```python
'variable > 0'      # Strict positivity
'variable >= 0'     # Non-negative
'0 < variable'      # Alternative syntax
```

**Examples:**

```python
# Prices (DeFi Tests 7, 9)
{
    'expression': '(Pt - P0) / P0',
    'constraints': [
        'Pt > 0',    # Current price positive
        'P0 > 0'     # Initial price positive
    ]
}

# Mass (physics)
{
    'expression': 'E = m*c^2',
    'constraints': ['m > 0']  # Mass always positive
}

# Concentration (chemistry)
{
    'expression': 'rate = k*[A]*[B]',
    'constraints': [
        '[A] > 0',   # Concentration positive
        '[B] > 0',
        'k > 0'      # Rate constant positive
    ]
}

# Volatility (DeFi)
{
    'expression': 'IL_adjusted = IL + sigma*weight',
    'constraints': ['sigma >= 0']  # Volatility non-negative
}
```

**Enforcement Level:** REQUIRED
**Penalty:** -10 points

---

### 3. Upper Bound Constraints

**Purpose:** Prevent unrealistic values and ensure normalized quantities

**Syntax:**

```python
'variable < upper'
'variable <= upper'
'lower <= variable <= upper'  # Range constraint
```

**Examples:**

```python
# Fees (DeFi Test 9)
{
    'expression': 'profit = volume * φ',
    'constraints': [
        'φ > 0',     # Fee positive
        'φ < 1'      # Fee less than 100%
    ]
}

# Correlation coefficients
{
    'expression': 'ρ*sigma1*sigma2',
    'constraints': [
        '-1 <= ρ <= 1'  # Correlation bounded
    ]
}

# Probability
{
    'expression': 'p*outcome1 + (1-p)*outcome2',
    'constraints': [
        '0 <= p <= 1'   # Probability range
    ]
}

# Pool weights (DeFi)
{
    'expression': 'w1*asset1 + w2*asset2',
    'constraints': [
        '0 < w1 < 1',
        '0 < w2 < 1',
        'w1 + w2 = 1'   # Weights sum to 1
    ]
}
```

**Enforcement Level:** REQUIRED
**Penalty:** -10 points

---

### 4. Domain Constraints

**Purpose:** Restrict variables to valid mathematical domains

**Syntax:**

```python
'variable in (a, b)'     # Open interval
'variable in [a, b]'     # Closed interval
'variable in (a, inf)'   # Unbounded above
'variable in (-inf, b)'  # Unbounded below
```

**Examples:**

```python
# Logarithm arguments
{
    'expression': 'ln(x)',
    'constraints': ['x in (0, inf)']  # Must be positive
}

# Square root arguments
{
    'expression': 'sqrt(x)',
    'constraints': ['x in [0, inf)']  # Non-negative
}

# Inverse trig functions
{
    'expression': 'asin(x)',
    'constraints': ['x in [-1, 1]']   # Restricted domain
}

# Exponential arguments (overflow prevention)
{
    'expression': 'exp(x)',
    'constraints': ['x in (-10, 10)']  # Prevent overflow
}
```

**Enforcement Level:** CRITICAL (for mathematical validity)
**Penalty:** -15 points

---

### 5. Relationship Constraints

**Purpose:** Enforce relationships between multiple variables

**Syntax:**

```python
'var1 + var2 = constant'
'var1 < var2'
'var1 = f(var2)'
```

**Examples:**

```python
# Portfolio weights
{
    'expression': 'w1*return1 + w2*return2',
    'constraints': [
        'w1 + w2 = 1',    # Weights sum to 1
        'w1 >= 0',
        'w2 >= 0'
    ]
}

# Temperature relationships
{
    'expression': 'heat_flow = k*(T_hot - T_cold)',
    'constraints': [
        'T_hot > T_cold',  # Heat flows hot to cold
        'T_hot > 0',       # Kelvin scale
        'T_cold > 0'
    ]
}

# Rate relationships
{
    'expression': 'net_rate = forward_rate - reverse_rate',
    'constraints': [
        'forward_rate > 0',
        'reverse_rate > 0',
        'forward_rate > reverse_rate'  # Net positive
    ]
}
```

**Enforcement Level:** REQUIRED
**Penalty:** -10 points

---

## DeFi Domain Constraints

### Standard DeFi Constraints

#### 1. Impermanent Loss Formulas (Tests 1, 2)

**Formula:** `IL = sqrt(2*sqrt(r/(1+r))) - 1`

**Required Constraints:**

```python
{
    'expression': 'sqrt(2*sqrt(r/(1+r))) - 1',
    'constraints': [
        'r > 0',           # CRITICAL: Price ratio must be positive
        'r > 1e-10',       # CRITICAL: Epsilon guard
        'r < 1e6'          # RECOMMENDED: Reasonable upper bound
    ],
    'variables': {
        'r': {
            'name': 'price_ratio',
            'type': 'continuous',
            'domain': '(1e-10, 1e6)',
            'units': 'dimensionless',
            'description': 'Ratio of final to initial price',
            'bounds': {'min': 1e-10, 'max': 1e6}
        }
    }
}
```

**Rationale:**

- `r > 0`: Division by zero protection in `r/(1+r)`
- `r > 1e-10`: Numerical stability near zero
- `r < 1e6`: Prevents unrealistic price ratios

---

#### 2. Weighted IL with Volatility (Test 2)

**Formula:** `IL_weighted = w1*sqrt(2*sqrt(r/(1+r))) + w2*sigma - 1`

**Required Constraints:**

```python
{
    'expression': 'w1*sqrt(2*sqrt(r/(1+r))) + w2*sigma - 1',
    'constraints': [
        'r > 0',           # Price ratio positive
        'r > 1e-10',       # Epsilon guard
        'w1 > 0',          # Weight 1 positive
        'w2 > 0',          # Weight 2 positive
        'w1 + w2 = 1',     # Weights sum to 1
        'sigma >= 0',      # Volatility non-negative
        'sigma < 10'       # Reasonable volatility cap
    ],
    'variables': {
        'r': {'domain': '(1e-10, inf)', 'bounds': {'min': 1e-10}},
        'w1': {'domain': '(0, 1)', 'bounds': {'min': 0, 'max': 1}},
        'w2': {'domain': '(0, 1)', 'bounds': {'min': 0, 'max': 1}},
        'sigma': {'domain': '[0, 10)', 'bounds': {'min': 0, 'max': 10}}
    }
}
```

---

#### 3. Price Change Formula (Test 7)

**Formula:** `price_change = (Pt - P0) / P0`

**Required Constraints:**

```python
{
    'expression': '(Pt - P0) / P0',
    'constraints': [
        'Pt > 0',          # CRITICAL: Current price positive
        'P0 > 0',          # CRITICAL: Initial price positive
        'Pt > 1e-10',      # Epsilon guard
        'P0 > 1e-10'       # Epsilon guard
    ],
    'variables': {
        'Pt': {
            'name': 'current_price',
            'domain': '(1e-10, inf)',
            'units': 'USD',
            'bounds': {'min': 1e-10}
        },
        'P0': {
            'name': 'initial_price',
            'domain': '(1e-10, inf)',
            'units': 'USD',
            'bounds': {'min': 1e-10}
        }
    }
}
```

---

#### 4. Fee-Adjusted Returns (Test 9)

**Formula:** `return_net = return_gross * (1 - φ)`

**Required Constraints:**

```python
{
    'expression': 'return_gross * (1 - φ)',
    'constraints': [
        'φ > 0',           # CRITICAL: Fee positive
        'φ < 1',           # CRITICAL: Fee less than 100%
        '0 < φ < 0.1'      # RECOMMENDED: Realistic fee range (0-10%)
    ],
    'variables': {
        'φ': {
            'name': 'fee_rate',
            'domain': '(0, 1)',
            'units': 'dimensionless',
            'description': 'Trading fee as decimal (0.003 = 0.3%)',
            'bounds': {'min': 0, 'max': 1},
            'typical_range': [0.0001, 0.01]  # 0.01% to 1%
        }
    }
}
```

---

#### 5. Quality Score (QS) Metric

**Formula:** `QS = (return_mean / volatility) * sqrt(sharpe_ratio)`

**Required Constraints:**

```python
{
    'expression': '(return_mean / volatility) * sqrt(sharpe_ratio)',
    'constraints': [
        'volatility > 0',       # CRITICAL: Avoid division by zero
        'volatility > 1e-10',   # Epsilon guard
        'sharpe_ratio >= 0',    # Sharpe typically positive
        'sharpe_ratio < 10'     # Reasonable upper bound
    ],
    'thresholds': {
        'excellent': 'QS > 2.0',    # USDT/USDC example
        'poor': 'QS < 0.5'          # SHIB/USDC example
    }
}
```

**Reference from Report:**

- USDT/USDC (QS > 2.0): +$2,700 profit, 100% win rate ✅
- SHIB/USDC (QS < 0.5): -$8,903 loss, 0% win rate ❌

---

## Physics Domain Constraints

### Standard Physics Constraints

#### 1. Kinematic Equations

**Formula:** `v^2 = v0^2 + 2*a*d`

**Required Constraints:**

```python
{
    'expression': 'v**2 = v0**2 + 2*a*d',
    'constraints': [
        'v >= 0',          # Speed non-negative
        'v0 >= 0',         # Initial speed non-negative
        'd >= 0',          # Distance non-negative
        'v < c'            # Below speed of light (3e8 m/s)
    ],
    'variables': {
        'v': {'units': 'm/s', 'bounds': {'min': 0, 'max': 3e8}},
        'v0': {'units': 'm/s', 'bounds': {'min': 0, 'max': 3e8}},
        'a': {'units': 'm/s^2', 'bounds': {'min': -100, 'max': 100}},
        'd': {'units': 'm', 'bounds': {'min': 0}}
    }
}
```

---

#### 2. Gravitational Force

**Formula:** `F = G*m1*m2/r^2`

**Required Constraints:**

```python
{
    'expression': 'G*m1*m2/r**2',
    'constraints': [
        'm1 > 0',          # CRITICAL: Mass 1 positive
        'm2 > 0',          # CRITICAL: Mass 2 positive
        'r > 0',           # CRITICAL: Distance positive
        'r > 1e-10',       # Epsilon guard
        'G = 6.674e-11'    # Gravitational constant (fixed)
    ],
    'variables': {
        'm1': {'units': 'kg', 'bounds': {'min': 1e-10}},
        'm2': {'units': 'kg', 'bounds': {'min': 1e-10}},
        'r': {'units': 'm', 'bounds': {'min': 1e-10}}
    }
}
```

---

#### 3. Ideal Gas Law

**Formula:** `PV = nRT`

**Required Constraints:**

```python
{
    'expression': 'P*V = n*R*T',
    'constraints': [
        'P > 0',           # CRITICAL: Pressure positive
        'V > 0',           # CRITICAL: Volume positive
        'n > 0',           # CRITICAL: Moles positive
        'T > 0',           # CRITICAL: Temperature positive (Kelvin)
        'T >= 0.01',       # Near absolute zero guard
        'R = 8.314'        # Gas constant (fixed)
    ],
    'variables': {
        'P': {'units': 'Pa', 'bounds': {'min': 0}},
        'V': {'units': 'm^3', 'bounds': {'min': 0}},
        'n': {'units': 'mol', 'bounds': {'min': 0}},
        'T': {'units': 'K', 'bounds': {'min': 0.01}}
    }
}
```

---

## Chemistry Domain Constraints

### Standard Chemistry Constraints

#### 1. Rate Equation (First Order)

**Formula:** `rate = k*[A]`

**Required Constraints:**

```python
{
    'expression': 'k*[A]',
    'constraints': [
        'k > 0',           # CRITICAL: Rate constant positive
        '[A] > 0',         # CRITICAL: Concentration positive
        '[A] < 100',       # RECOMMENDED: Reasonable molarity
        'k < 1e10'         # Prevent overflow
    ],
    'variables': {
        'k': {
            'units': 's^-1',
            'bounds': {'min': 1e-10, 'max': 1e10},
            'temperature_dependent': True
        },
        '[A]': {
            'units': 'M (mol/L)',
            'bounds': {'min': 1e-10, 'max': 100}
        }
    }
}
```

---

#### 2. Arrhenius Equation

**Formula:** `k = A*exp(-Ea/(R*T))`

**Required Constraints:**

```python
{
    'expression': 'A*exp(-Ea/(R*T))',
    'constraints': [
        'A > 0',           # Frequency factor positive
        'Ea > 0',          # Activation energy positive
        'T > 0',           # CRITICAL: Temperature positive
        'T > 1e-3',        # Kelvin guard
        'R = 8.314',       # Gas constant
        '-Ea/(R*T) > -50', # CRITICAL: Prevent underflow
        '-Ea/(R*T) < 10'   # CRITICAL: Prevent overflow
    ],
    'variables': {
        'A': {'units': 's^-1', 'bounds': {'min': 0}},
        'Ea': {'units': 'J/mol', 'bounds': {'min': 0, 'max': 500000}},
        'T': {'units': 'K', 'bounds': {'min': 0.001, 'max': 5000}}
    }
}
```

---

## Edge Case Constraints

### Critical Edge Cases (Week 2 Fixes)

#### 1. Empty Expression Detection

**Rule:** Expression must contain valid symbolic content

**Implementation:**

```python
def validate_expression(expr: str) -> bool:
    """Validate expression is not empty"""
    if not expr or expr.strip() == '':
        raise ValidationError("Empty expression detected")

    if len(expr.strip()) < 3:
        raise ValidationError("Expression too short (min 3 chars)")

    return True
```

**Penalty:** -15 points (auto-fail)

---

#### 2. Division by Zero Protection

**Rule:** All denominators must have non-zero constraints

**Detection Patterns:**

```python
DIVISION_PATTERNS = [
    r'1/(\w+)',           # Direct: 1/x
    r'(\w+)/(\w+)',       # Variable: a/b
    r'/\(([^)]+)\)'       # Expression: 1/(x+y)
]

def check_division_by_zero(expr: str, constraints: List[str]) -> bool:
    """Check all divisions have non-zero constraints"""
    for pattern in DIVISION_PATTERNS:
        matches = re.findall(pattern, expr)
        for var in matches:
            if not any(f'{var} != 0' in c or f'{var} > 0' in c
                      for c in constraints):
                raise ValidationError(f"Division by {var} without non-zero constraint")
    return True
```

**Penalty:** -15 points (critical safety)

---

#### 3. Numerical Overflow Protection

**Rule:** Exponential operations must be bounded

**Detection:**

```python
def check_overflow_risk(expr: str, constraints: List[str]) -> bool:
    """Check for overflow risks"""

    # Check for unbounded exponentials
    if 'exp(' in expr:
        # Extract exp argument
        arg = extract_exp_argument(expr)
        if not has_bounds(arg, constraints):
            raise ValidationError(f"Unbounded exponential: exp({arg})")

    # Check for large exponents
    if '**' in expr:
        base, exp = extract_power(expr)
        if exp > 10 and not has_bounds(base, constraints):
            raise ValidationError(f"Large exponent without bounds: {base}**{exp}")

    return True
```

**Recommended Bounds:**

```python
SAFE_EXPONENTIAL_BOUNDS = {
    'exp(x)': '-10 < x < 10',
    'x**n': 'n <= 10 or bounds on x',
    'log(x)': 'x > epsilon',
    'sqrt(x)': 'x >= 0'
}
```

**Penalty:** -10 points (warning) to -15 points (critical)

---

## Constraint Validation Rules

### Validation Hierarchy

```
1. Parse Expression
   ↓
2. Extract Variables
   ↓
3. Identify Operations (division, exp, log, sqrt)
   ↓
4. Check CRITICAL constraints (div/0, overflow)
   ↓
5. Check REQUIRED constraints (domain rules)
   ↓
6. Check RECOMMENDED constraints (bounds)
   ↓
7. Generate Validation Report
```

### Validation Checklist

```python
VALIDATION_CHECKLIST = {
    'critical': [
        'no_empty_expression',
        'no_division_by_zero',
        'no_unbounded_exponentials',
        'valid_mathematical_domains'
    ],
    'required': [
        'positivity_constraints',
        'domain_constraints',
        'relationship_constraints'
    ],
    'recommended': [
        'upper_bounds',
        'epsilon_guards',
        'typical_ranges'
    ]
}
```

---

## Implementation Guide

### Step 1: Define Formula with Constraints

```python
formula = {
    'name': 'Impermanent Loss',
    'expression': 'sqrt(2*sqrt(r/(1+r))) - 1',
    'description': 'IL for AMM liquidity providers',

    # CRITICAL constraints
    'constraints': [
        'r > 0',          # Price ratio positive
        'r > 1e-10',      # Epsilon guard
        'r < 1e6'         # Upper bound
    ],

    # Variable specifications
    'variables': {
        'r': {
            'name': 'price_ratio',
            'type': 'continuous',
            'domain': '(1e-10, 1e6)',
            'units': 'dimensionless',
            'description': 'Final price / Initial price',
            'bounds': {'min': 1e-10, 'max': 1e6},
            'typical_range': [0.5, 2.0]
        }
    },

    # Domain metadata
    'domain': 'defi',
    'subdomain': 'amm',
    'complexity': 'medium',
    'validation_level': 'critical'
}
```

### Step 2: Validate Constraints

```python
from hypatiax.tools.validation.ensemble_validator import EnsembleValidator

validator = EnsembleValidator(domain='defi')
result = validator.validate(formula)

print(f"Score: {result['total_score']}")
print(f"Edge Cases: {result['edge_cases_detected']}")
print(f"Status: {result['status']}")
```

### Step 3: Handle Validation Results

```python
if result['status'] == 'passed':
    print("✅ Formula validated successfully")
    print(f"Acceptance criteria: {result['acceptance_criteria']}")
else:
    print("❌ Validation failed")
    print(f"Reasons: {result['edge_cases_detected']}")
    print(f"Score: {result['total_score']} (threshold: 85.0)")

    # Fix constraints based on feedback
    for edge_case in result['edge_cases_detected']:
        if edge_case == 'division_by_zero_risk':
            print("→ Add: constraints ['denominator > 0']")
        elif edge_case == 'overflow_risk':
            print("→ Add: bounds on exponential arguments")
```

---

## Quick Reference Table

| Formula Type | Critical Constraints | Required Constraints | Recommended |
|-------------|---------------------|---------------------|-------------|
| DeFi IL | r > 0, r > ε | r < 1e6 | Typical: 0.5-2.0 |
| DeFi Prices | P > 0, P > ε | P < 1e12 | Reasonable bounds |
| DeFi Fees | 0 < φ < 1 | 0 < φ < 0.1 | Typical: 0.0003-0.003 |
| Physics Mass | m > 0 | m < 1e30 | Realistic bounds |
| Physics Velocity | v >= 0 | v < c (3e8) | Practical limits |
| Chem Concentration | [A] > 0 | [A] < 100M | Typical: 0.001-10M |
| Chem Temperature | T > 0 | 273 < T < 500 | Lab conditions |

---

**Version:** 2.0
**Compliance:** All formulas must meet constraint specifications to pass validation (score >= 85.0)
**Status:** Production Standard ✅
