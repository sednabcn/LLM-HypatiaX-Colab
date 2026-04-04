# Tutorial 1: Environment Setup (10 minutes)

## Pre-Recording Setup

**Before you start recording:**
- [ ] Fresh terminal window (clear history)
- [ ] Terminal font size: 14-16pt
- [ ] Close all unnecessary applications
- [ ] Have this script visible (second monitor or printed)
- [ ] Test microphone
- [ ] Start with clean Python environment (optional: fresh virtual environment)

---

## Opening (0:00 - 0:30)

**[SHOW: Your desktop/terminal]**

**SAY:**
> "Hello! Welcome to the HypatiaX tutorial series. I'm going to show you how to set up the HypatiaX framework on your system. HypatiaX is a tool that uses large language models as interfaces to symbolic discovery, and this is the companion software for our JMLR paper. By the end of this 10-minute tutorial, you'll have HypatiaX installed and running on your machine. Let's get started!"

---

## Section 1: Prerequisites Check (0:30 - 2:00)

**SAY:**
> "First, let's make sure you have the prerequisites. You'll need Python 3.8 or higher. Let's check your Python version."

**TYPE:**
```bash
python --version
```

**SAY:**
> "Great! I have Python [YOUR_VERSION]. If you see Python 3.8 or higher, you're good to go. If not, you'll need to install or update Python first - I'll put links in the description."

**SAY:**
> "Next, let's check that pip is installed. Pip is Python's package manager."

**TYPE:**
```bash
pip --version
```

**SAY:**
> "Perfect. Now let's create a fresh virtual environment. This keeps HypatiaX's dependencies separate from your other Python projects. This step is optional, but I recommend it."

**TYPE:**
```bash
python -m venv hypatiax_env
source hypatiax_env/bin/activate  # On Windows: hypatiax_env\Scripts\activate
```

**SAY:**
> "You'll see the environment name in parentheses in your prompt. On Windows, the activation command is slightly different - use backslash instead of forward slash. The command is shown on screen now."

---

## Section 2: Install HypatiaX (2:00 - 4:00)

**SAY:**
> "Now we're ready to install HypatiaX. We'll install it directly from the GitHub repository."

**TYPE:**
```bash
pip install git+https://github.com/[YOUR_USERNAME]/hypatiax.git
```

**SAY:**
> "This will download and install HypatiaX along with all its dependencies. This might take a minute or two."

**[WAIT for installation to complete - you can speed up the video here in editing, or just let it run]**

**SAY:**
> "Great! Installation is complete. You should see 'Successfully installed hypatiax' along with version information. Now let's verify the installation."

---

## Section 3: Verify Installation (4:00 - 6:00)

**SAY:**
> "Let's verify that HypatiaX is properly installed by importing it in Python."

**TYPE:**
```bash
python -c "import hypatiax; print('HypatiaX version:', hypatiax.__version__)"
```

**SAY:**
> "Perfect! HypatiaX imported successfully. Now let's check what modules are available."

**TYPE:**
```bash
python
```

**SAY:**
> "I'm opening an interactive Python session."

**TYPE (in Python):**
```python
import hypatiax
dir(hypatiax)
```

**SAY:**
> "Here we can see all the available modules and functions in HypatiaX. The main ones you'll use are the test suite runners and the analysis tools."

**TYPE:**
```python
exit()
```

---

## Section 4: Quick Test (6:00 - 8:30)

**SAY:**
> "Now let's run a quick test to make sure everything works. We'll run a simple symbolic regression problem - finding the equation for a parabola."

**TYPE:**
```bash
cd ~
mkdir hypatiax_tutorials
cd hypatiax_tutorials
```

**SAY:**
> "I've created a tutorials directory. Now let's create a simple test script."

**TYPE:**
```bash
cat > test_hypatiax.py << 'EOF'
#!/usr/bin/env python3
"""
Quick HypatiaX test - Parabola discovery
"""
import numpy as np
import hypatiax

# Generate simple parabola data
x = np.linspace(-2, 2, 20)
y = x**2 + 1

# Run symbolic regression
print("Testing HypatiaX with simple parabola: y = x^2 + 1")
print("Running symbolic discovery...")

result = hypatiax.discover(x, y, method='llm')

print(f"Discovered equation: {result['equation']}")
print(f"Error: {result['error']:.6f}")
print("\nSuccess! HypatiaX is working correctly.")
EOF
```

**SAY:**
> "I've created a simple test script. Let me show you what's in it."

**TYPE:**
```bash
cat test_hypatiax.py
```

**SAY:**
> "This script creates data for a simple parabola - y equals x squared plus one - and asks HypatiaX to discover the equation. Let's run it."

**TYPE:**
```bash
python test_hypatiax.py
```

**SAY:**
> "Perfect! HypatiaX successfully discovered the equation. The error is very small, showing the discovered equation accurately fits our data."

---

## Section 5: What's Next (8:30 - 9:30)

**SAY:**
> "Excellent! You now have HypatiaX installed and working. Let me quickly show you where to find the important files and documentation."

**TYPE:**
```bash
ls -la
```

**SAY:**
> "In future tutorials, we'll work from this directory. Here's what we'll cover:"

**[SHOW on screen - you can type this or prepare a simple text file to display]:**

```
Tutorial 2: Running the full test suite on 131 benchmarks
Tutorial 3: Analyzing results and generating publication plots
Tutorial 4: Extending HypatiaX to your own domain
```

**SAY:**
> "If you run into any issues, check the troubleshooting section in the GitHub repository. Common issues include missing dependencies or Python version incompatibilities."

---

## Closing (9:30 - 10:00)

**SAY:**
> "That's it for Tutorial 1! You now have HypatiaX installed and verified. In the next tutorial, we'll run the full experimental test suite with 131 test cases across multiple domains. Thanks for watching, and I'll see you in Tutorial 2!"

**[SHOW on screen]:**
```
✅ HypatiaX Installed
✅ Environment Verified  
✅ Test Passed

Next: Tutorial 2 - Running Experiments
```

**[END RECORDING]**

---

## Post-Recording Notes

**Good places to edit/cut:**
- Installation waiting time (speed up or cut)
- If you made mistakes, cut them out at the 3-second pauses
- Keep the actual commands and outputs visible

**What viewers need to see clearly:**
- Your Python version check
- The installation success message
- The test script contents
- The successful test output

**Files created in this tutorial:**
- `test_hypatiax.py` - keep this for Tutorial 2

**Time stamps for YouTube description:**
```
0:00 - Introduction
0:30 - Prerequisites Check
2:00 - Installing HypatiaX
4:00 - Verifying Installation
6:00 - Running Quick Test
8:30 - What's Next
9:30 - Conclusion
```
