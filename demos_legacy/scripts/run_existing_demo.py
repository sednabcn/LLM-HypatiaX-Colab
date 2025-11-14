cat > demos/scripts/run_existing_demo.py << 'EOF'
#!/usr/bin/env python3
"""
Bridge script to run existing HypatiaX demos with new config system
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import your existing demo runner
from hypatiax.demo.demo_runner import DemoRunner  # Adjust import as needed
from hypatiax.config import paths, ModelConfig

def run_existing_demo():
    """Run your existing demo with config system"""
    print("=" * 60)
    print("Running Existing HypatiaX Demo")
    print("=" * 60)
    
    # Use your existing demo structure
    # TODO: Replace with actual import/call based on your code
    
    # Example:
    # runner = DemoRunner()
    # result = runner.process("calculate area of circle")
    
    print("\nThis script bridges to your existing demo in:")
    print(f"  {paths.hypatiax / 'demo'}")
    print("\nUpdate this script with your actual demo runner code.")

if __name__ == "__main__":
    run_existing_demo()
EOF



# Users can import your package demo
# from hypatiax.demo import DemoRunner

# But they don't get your test strategies or migration scripts
# (demos/ and migrations/ are not installed)
