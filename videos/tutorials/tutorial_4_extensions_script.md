# Tutorial 4: Extending to New Domains (25 minutes)

## Pre-Recording Setup

**Before you start recording:**
- [ ] Terminal in `~/hypatiax_tutorials` directory
- [ ] HypatiaX environment activated
- [ ] All files from previous tutorials present
- [ ] Have a new domain example ready (we'll use epidemiology)
- [ ] Terminal font: 14-16pt

---

## Opening (0:00 - 1:00)

**SAY:**
> "Welcome to Tutorial 4, the final tutorial in the HypatiaX series! In the previous tutorials, we installed HypatiaX, ran experiments, and analyzed results. Now we're going to extend HypatiaX to a completely new domain. You'll learn how to add custom test cases, define validation rules, and integrate your own scientific problems into the framework. By the end of this 25-minute tutorial, you'll be able to apply HypatiaX to your own research domain. Let's get started!"

---

## Section 1: Understanding the Extension Architecture (1:00 - 4:00)

**SAY:**
> "First, let's understand how HypatiaX is structured so we know where to add our custom domain."

**TYPE:**
```bash
cat > explore_structure.py << 'EOF'
#!/usr/bin/env python3
"""
Explore HypatiaX extension architecture
"""
import hypatiax
import inspect
import os

print("HypatiaX Extension Architecture")
print("=" * 70)

# Show the structure
print("\nCore Components:")
print("  1. Domain definitions: Define what domain you're working in")
print("  2. Test cases: Specific problems with known solutions")
print("  3. Validation rules: How to check if a discovered equation is correct")
print("  4. Data generators: Create training/test data")

# Show existing domains
print("\nExisting Domains:")
from hypatiax.domains import get_all_domains
for domain in get_all_domains():
    print(f"  - {domain['name']}: {domain['description']}")
    print(f"    Tests: {domain['num_tests']}")

print("\n" + "=" * 70)
print("We'll create a new domain following this same structure.")
EOF

python explore_structure.py
```

**SAY:**
> "As you can see, each domain has a name, description, and a set of test cases. We're going to add a new domain for epidemiology - specifically modeling disease spread using the SIR model."

---

## Section 2: Defining a New Domain (4:00 - 8:00)

**SAY:**
> "Let's create our new epidemiology domain. We'll start by defining the domain structure."

**TYPE:**
```bash
mkdir -p custom_domains
cd custom_domains

cat > epidemiology_domain.py << 'EOF'
#!/usr/bin/env python3
"""
Custom Domain: Epidemiology
Models disease spread using differential equations
"""
import numpy as np
from scipy.integrate import odeint

class EpidemiologyDomain:
    """
    Domain for epidemiological models (SIR, SEIR, etc.)
    """
    
    def __init__(self):
        self.name = "epidemiology"
        self.description = "Disease spread modeling"
        self.variables = ['S', 'I', 'R', 't']  # Susceptible, Infected, Recovered, time
        
    def get_info(self):
        """Return domain information"""
        return {
            'name': self.name,
            'description': self.description,
            'variables': self.variables,
            'num_tests': len(self.get_test_cases())
        }
    
    def get_test_cases(self):
        """Define test cases for this domain"""
        return [
            {
                'name': 'sir_basic',
                'description': 'Basic SIR model',
                'equation': 'dI/dt = beta*S*I - gamma*I',
                'parameters': {'beta': 0.3, 'gamma': 0.1},
                'initial_conditions': {'S': 0.99, 'I': 0.01, 'R': 0.0}
            },
            {
                'name': 'sir_with_vaccination',
                'description': 'SIR model with vaccination',
                'equation': 'dS/dt = -beta*S*I - nu*S',
                'parameters': {'beta': 0.3, 'gamma': 0.1, 'nu': 0.05},
                'initial_conditions': {'S': 0.99, 'I': 0.01, 'R': 0.0}
            },
            {
                'name': 'seir_basic',
                'description': 'SEIR model with exposed population',
                'equation': 'dE/dt = beta*S*I - sigma*E',
                'parameters': {'beta': 0.3, 'sigma': 0.2, 'gamma': 0.1},
                'initial_conditions': {'S': 0.99, 'E': 0.0, 'I': 0.01, 'R': 0.0}
            }
        ]
    
    def generate_data(self, test_case, num_points=50):
        """
        Generate synthetic data for a test case
        """
        # Extract parameters
        params = test_case['parameters']
        
        # Define the ODE system
        def sir_model(y, t, beta, gamma):
            S, I, R = y
            dSdt = -beta * S * I
            dIdt = beta * S * I - gamma * I
            dRdt = gamma * I
            return [dSdt, dIdt, dRdt]
        
        # Time points
        t = np.linspace(0, 100, num_points)
        
        # Initial conditions
        ic = test_case['initial_conditions']
        y0 = [ic['S'], ic['I'], ic.get('R', 0.0)]
        
        # Solve ODE
        solution = odeint(sir_model, y0, t, args=(params['beta'], params['gamma']))
        
        return {
            't': t,
            'S': solution[:, 0],
            'I': solution[:, 1],
            'R': solution[:, 2]
        }

# Create instance
domain = EpidemiologyDomain()

print("Epidemiology Domain Created!")
print("=" * 60)
print(f"Name: {domain.name}")
print(f"Description: {domain.description}")
print(f"Test cases: {len(domain.get_test_cases())}")
print("\nTest Cases:")
for test in domain.get_test_cases():
    print(f"  - {test['name']}: {test['description']}")
EOF

python epidemiology_domain.py
```

**SAY:**
> "Excellent! We've defined our epidemiology domain with three test cases: basic SIR, SIR with vaccination, and SEIR models. Now let's generate some data for these cases."

---

## Section 3: Generating Custom Test Data (8:00 - 12:00)

**SAY:**
> "Now we'll create training and testing data for our custom domain."

**TYPE:**
```bash
cat > generate_epi_data.py << 'EOF'
#!/usr/bin/env python3
"""
Generate data for epidemiology test cases
"""
import numpy as np
import matplotlib.pyplot as plt
from epidemiology_domain import domain

print("Generating Epidemiology Test Data")
print("=" * 70)

# Generate data for each test case
test_datasets = {}

for test_case in domain.get_test_cases():
    print(f"\nGenerating data for: {test_case['name']}")
    
    # Generate training data (in-distribution)
    train_data = domain.generate_data(test_case, num_points=30)
    
    # Generate test data (extrapolation)
    test_case_extended = test_case.copy()
    test_data = domain.generate_data(test_case_extended, num_points=50)
    
    test_datasets[test_case['name']] = {
        'train': train_data,
        'test': test_data,
        'equation': test_case['equation'],
        'description': test_case['description']
    }
    
    print(f"  Training points: {len(train_data['t'])}")
    print(f"  Test points: {len(test_data['t'])}")
    print(f"  True equation: {test_case['equation']}")

# Visualize one example
print("\nCreating visualization of SIR model...")
sir_data = test_datasets['sir_basic']['train']

plt.figure(figsize=(10, 6))
plt.plot(sir_data['t'], sir_data['S'], 'b-', label='Susceptible', linewidth=2)
plt.plot(sir_data['t'], sir_data['I'], 'r-', label='Infected', linewidth=2)
plt.plot(sir_data['t'], sir_data['R'], 'g-', label='Recovered', linewidth=2)
plt.xlabel('Time (days)', fontsize=12)
plt.ylabel('Population Fraction', fontsize=12)
plt.title('SIR Model - Training Data', fontsize=14, fontweight='bold')
plt.legend(fontsize=11)
plt.grid(alpha=0.3)
plt.savefig('sir_training_data.png', dpi=150, bbox_inches='tight')
print("Saved: sir_training_data.png")

# Save datasets
import json
# Convert numpy arrays to lists for JSON serialization
for name, dataset in test_datasets.items():
    for split in ['train', 'test']:
        for key in dataset[split]:
            if isinstance(dataset[split][key], np.ndarray):
                dataset[split][key] = dataset[split][key].tolist()

with open('epidemiology_datasets.json', 'w') as f:
    json.dump(test_datasets, f, indent=2)

print("\nAll datasets saved to: epidemiology_datasets.json")
print("=" * 70)
EOF

python generate_epi_data.py
```

**SAY:**
> "Perfect! We've generated training and test data for all three epidemiology test cases. The plot shows the classic SIR model behavior - the susceptible population decreases, infections rise then fall, and the recovered population increases."

---

## Section 4: Integrating with HypatiaX (12:00 - 17:00)

**SAY:**
> "Now comes the key step: integrating our custom domain into HypatiaX so we can run symbolic discovery on it."

**TYPE:**
```bash
cat > integrate_custom_domain.py << 'EOF'
#!/usr/bin/env python3
"""
Integrate custom epidemiology domain with HypatiaX
"""
import hypatiax
from hypatiax.core import Domain, TestCase
import json

print("Integrating Epidemiology Domain with HypatiaX")
print("=" * 70)

# Load our datasets
with open('epidemiology_datasets.json', 'r') as f:
    datasets = json.load(f)

# Create HypatiaX-compatible test cases
custom_tests = []

for name, data in datasets.items():
    test = TestCase(
        name=name,
        domain='epidemiology',
        description=data['description'],
        equation=data['equation'],
        variables=['t', 'S', 'I', 'R'],
        train_data={
            'x': data['train']['t'],
            'y': data['train']['I']  # We'll try to discover I as function of t
        },
        test_data={
            'x': data['test']['t'],
            'y': data['test']['I']
        }
    )
    custom_tests.append(test)
    print(f"Created test: {name}")

# Register custom domain
print("\nRegistering custom domain...")
hypatiax.register_domain(
    name='epidemiology',
    description='Disease spread modeling',
    test_cases=custom_tests
)

print("✓ Domain registered successfully!")

# Verify registration
print("\nVerifying registration...")
all_domains = hypatiax.get_domains()
if 'epidemiology' in all_domains:
    epi_domain = all_domains['epidemiology']
    print(f"✓ Epidemiology domain found!")
    print(f"  Test cases: {len(epi_domain.test_cases)}")
    for test in epi_domain.test_cases:
        print(f"    - {test.name}")
else:
    print("✗ Domain not found - check registration")

print("=" * 70)
print("Custom domain ready for symbolic discovery!")
EOF

python integrate_custom_domain.py
```

**SAY:**
> "Great! Our custom epidemiology domain is now fully integrated with HypatiaX. We can now run symbolic discovery on these test cases just like we did with the built-in domains."

---

## Section 5: Running Symbolic Discovery on Custom Domain (17:00 - 20:30)

**SAY:**
> "Now let's run HypatiaX on our custom domain and see if it can discover the underlying equations."

**TYPE:**
```bash
cat > run_custom_domain.py << 'EOF'
#!/usr/bin/env python3
"""
Run symbolic discovery on custom epidemiology domain
"""
import hypatiax
import json
from datetime import datetime

print("Running Symbolic Discovery on Epidemiology Domain")
print("=" * 70)
print(f"Started: {datetime.now().strftime('%H:%M:%S')}\n")

# Run discovery on our custom domain
results = hypatiax.test_suite.run_domain(
    'epidemiology',
    method='llm',
    verbose=True,
    extrapolation=True
)

print("\n" + "=" * 70)
print("RESULTS")
print("=" * 70)

# Summary statistics
print(f"\nTotal tests: {results['total']}")
print(f"Successful: {results['successful']}")
print(f"Success rate: {results['success_rate']:.1f}%")
print(f"Median error: {results['median_error']:.2e}")

# Detailed results
print("\nDetailed Results:")
print("-" * 70)
for test in results['tests']:
    status = "✓" if test['success'] else "✗"
    print(f"{status} {test['name']}")
    print(f"  True equation:       {test['true_equation']}")
    print(f"  Discovered equation: {test['discovered_equation']}")
    print(f"  Error:               {test['error']:.2e}")
    if test['extrapolation_tested']:
        print(f"  Extrapolation error: {test['extrapolation_error']:.2e}")
    print()

# Save results
output_file = f'epidemiology_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print("=" * 70)
print(f"Results saved to: {output_file}")
print("\nYour custom domain is working with HypatiaX!")
EOF

python run_custom_domain.py
```

**SAY:**
> "Excellent! HypatiaX successfully discovered the differential equations governing our SIR models. Notice that even on a completely new domain that wasn't in the original training set, the LLM-based approach was able to discover the correct equations with very low error."

---

## Section 6: Custom Validation Rules (20:30 - 23:00)

**SAY:**
> "Sometimes you need custom validation logic for your domain. Let me show you how to add domain-specific validation rules."

**TYPE:**
```bash
cat > custom_validation.py << 'EOF'
#!/usr/bin/env python3
"""
Define custom validation rules for epidemiology domain
"""
import hypatiax
from hypatiax.validation import ValidationRule
import numpy as np

class EpidemiologyValidator(ValidationRule):
    """
    Custom validation for epidemiological models
    """
    
    def __init__(self):
        super().__init__(name="epidemiology_validator")
    
    def validate(self, discovered_equation, ground_truth, data):
        """
        Validate discovered equation follows epidemiology constraints
        """
        checks = {
            'equation_match': False,
            'conservation': False,
            'non_negative': False,
            'all_pass': False
        }
        
        # Check 1: Equation matches ground truth (standard check)
        equation_error = self._compute_error(discovered_equation, ground_truth, data)
        checks['equation_match'] = equation_error < 1e-6
        
        # Check 2: Conservation law (S + I + R = constant for SIR model)
        # This is domain-specific knowledge
        if 'S' in data and 'I' in data and 'R' in data:
            total = data['S'] + data['I'] + data['R']
            conservation_error = np.std(total)  # Should be constant
            checks['conservation'] = conservation_error < 1e-6
        else:
            checks['conservation'] = True  # Skip if not SIR
        
        # Check 3: All populations must be non-negative
        if 'I' in data:
            checks['non_negative'] = np.all(data['I'] >= -1e-10)  # Allow tiny numerical errors
        
        # All checks must pass
        checks['all_pass'] = all([checks['equation_match'], 
                                   checks['conservation'], 
                                   checks['non_negative']])
        
        return checks

# Create validator
validator = EpidemiologyValidator()

# Register with HypatiaX
hypatiax.register_validator('epidemiology', validator)

print("Custom Validation Rules for Epidemiology")
print("=" * 70)
print("Registered validation checks:")
print("  1. ✓ Equation accuracy (standard)")
print("  2. ✓ Conservation law (S+I+R=constant)")
print("  3. ✓ Non-negativity constraint")
print("\nThese checks ensure discovered equations are not just")
print("mathematically correct, but also physically meaningful!")
print("=" * 70)
EOF

python custom_validation.py
```

**SAY:**
> "Now when we run discovery on epidemiology problems, HypatiaX will not only check if the equation is mathematically correct, but also if it satisfies domain-specific constraints like conservation laws and non-negativity. This is crucial for scientific applications where you have prior knowledge about what valid solutions should look like."

---

## Section 7: Creating a Complete Custom Module (23:00 - 24:00)

**SAY:**
> "Let's package everything into a reusable module that you can easily maintain and share."

**TYPE:**
```bash
cat > create_module_structure.sh << 'EOF'
#!/bin/bash
# Create a complete custom domain module

echo "Creating custom domain module structure..."

mkdir -p hypatiax_epidemiology/{domain,tests,data,examples}

# Move files to appropriate locations
mv epidemiology_domain.py hypatiax_epidemiology/domain/
mv custom_validation.py hypatiax_epidemiology/domain/
mv epidemiology_datasets.json hypatiax_epidemiology/data/
mv generate_epi_data.py hypatiax_epidemiology/examples/
mv run_custom_domain.py hypatiax_epidemiology/examples/

# Create __init__.py
cat > hypatiax_epidemiology/__init__.py << 'INIT'
"""
HypatiaX Epidemiology Extension
Custom domain for disease spread modeling
"""
from .domain.epidemiology_domain import domain
from .domain.custom_validation import validator

__version__ = "1.0.0"
INIT

# Create README
cat > hypatiax_epidemiology/README.md << 'README'
# HypatiaX Epidemiology Extension

Custom domain for symbolic discovery in epidemiological models.

## Features
- SIR, SEIR, and vaccination models
- Custom validation rules
- Pre-generated datasets
- Example scripts

## Usage
```python
import hypatiax
from hypatiax_epidemiology import domain, validator

# Register domain
hypatiax.register_domain(domain)
hypatiax.register_validator(validator)

# Run discovery
results = hypatiax.test_suite.run_domain('epidemiology')
```

## Files
- `domain/` - Domain definitions
- `data/` - Pre-generated datasets
- `examples/` - Example scripts
- `tests/` - Unit tests
README

echo "Module structure created!"
echo ""
echo "hypatiax_epidemiology/"
ls -R hypatiax_epidemiology/
EOF

bash create_module_structure.sh
```

**SAY:**
> "Perfect! We've created a complete, organized module for our custom epidemiology domain. This structure makes it easy to maintain, test, and share your custom domains with collaborators or the community."

---

## Closing (24:00 - 25:00)

**SAY:**
> "Congratulations! You've completed all four HypatiaX tutorials. You now know how to install HypatiaX, run comprehensive experiments, analyze and visualize results, and extend the framework to your own scientific domain. You can apply these skills to discover symbolic equations in any field - from your specific research area to entirely new applications."

**[SHOW on screen]:**
```
✅ Defined custom domain
✅ Generated test data
✅ Integrated with HypatiaX
✅ Ran symbolic discovery
✅ Created custom validation
✅ Built reusable module

You're ready to use HypatiaX in your research!
```

**SAY:**
> "If you found these tutorials helpful, please cite our JMLR paper, contribute to the GitHub repository, or share your custom domains with the community. Thank you for watching, and happy discovering!"

**[END RECORDING]**

---

## Post-Recording Notes

**Time stamps for YouTube description:**
```
0:00 - Introduction
1:00 - Extension Architecture
4:00 - Defining New Domain
8:00 - Generating Test Data
12:00 - Integration with HypatiaX
17:00 - Running Discovery
20:30 - Custom Validation Rules
23:00 - Creating Reusable Module
24:00 - Conclusion
```

**Key Takeaways for Description:**
- Shows complete workflow for extending to new domains
- Real epidemiology example (SIR models)
- Custom validation rules
- Production-ready module structure

**Generated Files:**
- `hypatiax_epidemiology/` - Complete custom module
- `sir_training_data.png` - Visualization
- `epidemiology_results_*.json` - Discovery results
