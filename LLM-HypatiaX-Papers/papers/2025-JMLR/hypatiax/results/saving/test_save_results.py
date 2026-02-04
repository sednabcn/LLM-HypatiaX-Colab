#!/usr/bin/env python3
"""Test if we can save results"""

import json
from pathlib import Path
from datetime import datetime

def test_save():
    results_dir = Path("hypatiax/data/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    test_data = {
        "timestamp": datetime.now().isoformat(),
        "test": "save_verification",
        "status": "success"
    }
    
    filename = f"test_save_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = results_dir / filename
    
    with open(filepath, 'w') as f:
        json.dump(test_data, f, indent=2)
    
    print(f"✓ Test file saved: {filepath}")
    print(f"  Size: {filepath.stat().st_size} bytes")
    
    # Verify we can read it back
    with open(filepath, 'r') as f:
        loaded = json.load(f)
    
    print(f"✓ Successfully loaded: {loaded['test']}")
    print("\n✓ Save/load test PASSED")
    
    return True

if __name__ == "__main__":
    test_save()
