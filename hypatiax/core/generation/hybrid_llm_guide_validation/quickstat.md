# LLM-Guided Symbolic Discovery - Quick Start Guide

## 🚀 Quick Setup (3 Steps)

### Step 1: Run Setup Script

```bash
# Navigate to the discovery system directory
cd hypatiax/core/generation/hybrid_llm_guide_validation

# Run the setup script
python setup_llm_discovery.py
```

This will automatically find and copy the protocol files to the correct location.

### Step 2: Set API Key

Choose one of these methods:

**Option A: Environment Variable**
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Option B: .env File**
```bash
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" > .env
```

**Option C: Command Line Argument**
```bash
python llm_guided_symbolic_discovery.py --api-key sk-ant-your-key-here --protocol B --batch
```

### Step 3: Run Discovery

```bash
# Run Protocol B (20 multi-domain tests)
python llm_guided_symbolic_discovery.py --protocol B --batch

# Or run Protocol ALL (30 tests across all domains)
python llm_guided_symbolic_discovery.py --protocol ALL --batch

# Or run Protocol DEFI (20 DeFi-specific tests)
python llm_guided_symbolic_discovery.py --protocol DEFI --batch
```

---

## 📋 Available Protocols

| Protocol | Tests | Domains | Description |
|----------|-------|---------|-------------|
| **B** | 20 | Physics, Chemistry, Biology, Engineering, Math, Economics | Multi-domain scientific equations |
| **ALL** | 30 | All above + expanded physics | Comprehensive protocol combining A+B |
| **DEFI** | 20 | AMM, Risk/VaR, Liquidity, Liquidation, Staking | DeFi-specific equations |

---

## ⚙️ Configuration Options

### Basic Usage
```bash
# Default settings (5 hypothesis candidates)
python llm_guided_symbolic_discovery.py --protocol B --batch

# More hypothesis candidates for better coverage
python llm_guided_symbolic_discovery.py --protocol B --batch --niterations 20

# Higher temperature for more creative hypotheses
python llm_guided_symbolic_discovery.py --protocol B --batch --temperature 0.7

# More tokens for complex equations
python llm_guided_symbolic_discovery.py --protocol B --batch --max-tokens 3000
```

### Advanced Usage
```bash
# Resume interrupted run
python llm_guided_symbolic_discovery.py --protocol ALL --batch --resume

# Quiet mode (less output)
python llm_guided_symbolic_discovery.py --protocol B --batch --quiet

# Custom model
python llm_guided_symbolic_discovery.py --protocol B --batch --model claude-opus-4-20250514
```

---

## 🔧 Troubleshooting

### Error: "Protocol loader not available"

**Solution:** Run the setup script:
```bash
python setup_llm_discovery.py
```

This will locate and copy the required protocol files.

### Error: "ANTHROPIC_API_KEY not found"

**Solution:** Set your API key using one of these methods:

```bash
# Method 1: Environment variable
export ANTHROPIC_API_KEY=your_key

# Method 2: .env file
echo "ANTHROPIC_API_KEY=your_key" > .env

# Method 3: Command line
python llm_guided_symbolic_discovery.py --api-key your_key --protocol B --batch
```

Get your API key at: https://console.anthropic.com/

### Manual Protocol File Setup

If the setup script doesn't work, manually copy files:

```bash
# Find where your protocol files are
find . -name "experiment_protocol_*.py"

# Copy them to the discovery directory
cp /path/to/experiment_protocol_all_30.py hypatiax/core/generation/hybrid_llm_guide_validation/
cp /path/to/experiment_protocol_all_20.py hypatiax/core/generation/hybrid_llm_guide_validation/
cp /path/to/experiment_protocol_defi_20.py hypatiax/core/generation/hybrid_llm_guide_validation/
```

---

## 📊 Understanding Results

After running, you'll see a results table:

```
================================================================================
                    LLM-GUIDED DISCOVERY RESULTS
================================================================================
Test Name                          R²       Val   Time  Status  Observation
----------------------------------------------------------------------------
PHYSICS
----------------------------------------------------------------------------
kinetic_energy                   0.9987   95.2   8.2s  ✅ PASS  LLM hypothesis successful
ohms_law                        0.9995   98.1   6.5s  ✅ PASS  LLM hypothesis successful
...
================================================================================
```

**Key Metrics:**
- **R²**: Goodness of fit (>0.95 is excellent)
- **Val**: Validation score from dimensional analysis (>70 is good)
- **Time**: Time taken for this test
- **Status**: ✅ PASS or ❌ FAIL
- **Observation**: What happened

---

## 💡 Tips for Best Results

### 1. Start with More Iterations
```bash
# Generate 20 hypothesis candidates instead of default 5
python llm_guided_symbolic_discovery.py --protocol B --batch --niterations 20
```

### 2. Use Protocol B for General Testing
Protocol B has the most diverse set of equations across different domains.

### 3. Check Results in Real-Time
Results are saved incrementally in `hypatiax/data/results/llm_guided/SESSION_ID/`

### 4. Resume Long Runs
If interrupted, use `--resume` to continue:
```bash
python llm_guided_symbolic_discovery.py --protocol ALL --batch --resume
```

---

## 📁 Output Files

Results are saved in: `hypatiax/data/results/llm_guided/SESSION_ID/`

```
llm_guided/
└── llm_20260108_143022/
    ├── checkpoint.json          # Progress tracking
    ├── kinetic_energy.json      # Individual test results
    ├── ohms_law.json
    ├── ...
    └── summary.json             # Final summary (if generated)
```

Each test result includes:
- Best equation found
- R² score
- Validation score
- All hypothesis candidates
- Timing information
- Metadata

---

## 🎯 Example Workflows

### Workflow 1: Quick Test
```bash
# Test Protocol B with default settings
python llm_guided_symbolic_discovery.py --protocol B --batch
```

### Workflow 2: Comprehensive Discovery
```bash
# Test Protocol ALL with many candidates
python llm_guided_symbolic_discovery.py --protocol ALL --batch --niterations 30
```

### Workflow 3: DeFi-Specific
```bash
# Run DeFi protocol for finance applications
python llm_guided_symbolic_discovery.py --protocol DEFI --batch --niterations 15
```

### Workflow 4: Custom Configuration
```bash
# High creativity, more tokens, many iterations
python llm_guided_symbolic_discovery.py --protocol B --batch \
  --temperature 0.8 \
  --max-tokens 4000 \
  --niterations 50
```

---

## 📞 Need Help?

1. **Run setup script:** `python setup_llm_discovery.py`
2. **Check protocol files are in place:** `ls experiment_protocol_*.py`
3. **Verify API key:** `echo $ANTHROPIC_API_KEY`
4. **Start with Protocol B:** Smallest, most tested protocol

---

## 🔬 How It Works

1. **Pattern Analysis** (0.5s): Analyze data patterns (linearity, power laws, etc.)
2. **LLM Hypothesis Generation** (5s): Generate N candidate equations using Claude
3. **Rapid Verification** (2-3s): Fit coefficients, compute R², validate dimensions
4. **Results**: Best hypothesis with full metrics

**Expected Performance:**
- 80% cases: Direct LLM hit (8s total)
- 15% cases: LLM + refinement (20s total)  
- 5% cases: Complex equations (30s total)
- **Average: 12s** (vs traditional 60-180s) → **10x speedup**

---

## 🎉 Ready to Go!

```bash
# 1. Setup
python setup_llm_discovery.py

# 2. Set API key
export ANTHROPIC_API_KEY=your_key

# 3. Run
python llm_guided_symbolic_discovery.py --protocol B --batch

# 🚀 Done!
```
