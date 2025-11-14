cat > demos/README.md << 'EOF'
# HypatiaX Demo Framework

This directory contains demo scripts, strategies, and workspaces for testing and documenting HypatiaX functionality.

## Directory Structure
```
demos/
├── scripts/           # Executable demo scripts
│   ├── thursday_demo.py
│   └── test_thursday_demo.py
├── strategies/        # Different implementation strategies
│   ├── strategy01.py  # Sequential pipeline
│   ├── strategy02.py  # Joint training
│   └── strategy1-1.2.py  # Entity mapping
├── workspaces/        # HTML demo workspaces
│   ├── demo_workspace.html
│   └── demo-interactive.html
└── documentation/     # Usage guides and docs
    ├── usage_demo.md
    ├── usage_strategy.md
    └── usage-strategy1-1.2.md
```

## Quick Start

### Run Thursday Demo
```bash
python demos/scripts/thursday_demo.py
```

### Test Strategy 1 (Sequential Pipeline)
```bash
python demos/strategies/strategy01.py
```

### Test Strategy 2 (Joint Training)
```bash
python demos/strategies/strategy02.py
```

### Use Demo Workspace
Open `demos/workspaces/demo_workspace.html` in your browser.

## Existing HypatiaX Demo Integration

Your existing demo structure:
```
hypatiax/demo/
├── raw_sentences/
├── training_cases/
├── demo_runner.py
└── utils/
```

These demos/ files complement (not replace) your existing structure.
- `hypatiax/demo/` = Core demo functionality (keep as-is)
- `demos/` = Testing, strategies, and documentation (new organization)

## Usage Patterns

### For Quick Tests
Use files in `demos/scripts/`

### For Strategy Comparison
Use files in `demos/strategies/`

### For Documentation & Tracking
Use HTML workspaces in `demos/workspaces/`

### For Learning & Reference
Read guides in `demos/documentation/`

## Integration with Existing Code

The demo files work with your existing structure:
```python
# In demos/scripts/thursday_demo.py
from hypatiax.demo.demo_runner import DemoRunner  # Your existing code
from hypatiax.config import paths, ModelConfig     # New config system

# Run demo
runner = DemoRunner()
result = runner.run("calculate area of circle")
```

## Next Steps

1. Run `python demos/scripts/thursday_demo.py` to test one example
2. Document results in HTML workspace
3. Try different strategies to compare approaches
4. Use existing `hypatiax/demo/` for core functionality
EOF