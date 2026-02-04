#!/usr/bin/env python3
"""
Wrapper to run hybrid system and ensure results are saved
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import subprocess

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_hybrid_and_save():
    """Run hybrid system and explicitly save results"""
    
    print("="*80)
    print("RUNNING HYBRID SYSTEM WITH EXPLICIT RESULT SAVING")
    print("="*80)
    
    # Ensure results directory exists
    results_dir = project_root / "hypatiax" / "data" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Run the hybrid system script
    hybrid_script = project_root / "hypatiax" / "core" / "generation" / "hybrid_all_domains" / "complete_hybrid_system_all_domains.py"
    
    print(f"\n📂 Results will be saved to: {results_dir}")
    print(f"🚀 Running: {hybrid_script.name}\n")
    
    # Run with output capture
    try:
        result = subprocess.run(
            [sys.executable, str(hybrid_script), "--batch", "--llm"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour max
        )
        
        print("="*80)
        print("EXECUTION OUTPUT")
        print("="*80)
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        print("="*80)
        print(f"Exit code: {result.returncode}")
        print("="*80)
        
        # Check what files were created
        print("\n📊 Checking for result files...")
        result_files = list(results_dir.glob("*.json"))
        
        if result_files:
            print(f"✓ Found {len(result_files)} result files:")
            for f in result_files:
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                size = f.stat().st_size
                print(f"  • {f.name}")
                print(f"    Modified: {mtime}")
                print(f"    Size: {size:,} bytes")
        else:
            print("✗ No result files found!")
            print("\n⚠ Results were not saved properly.")
            print("\nAttempting to extract results from output...")
            
            # Try to extract results from stdout
            if "SUCCESS" in result.stdout and "r2" in result.stdout.lower():
                print("\n✓ Found results in output - attempting to save...")
                
                # Create a results file from the output
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = results_dir / f"hybrid_results_captured_{timestamp}.json"
                
                # Parse output for results (simplified)
                captured_results = {
                    "timestamp": timestamp,
                    "source": "stdout_capture",
                    "note": "Results extracted from program output",
                    "raw_output": result.stdout[:5000],  # First 5000 chars
                    "success": result.returncode == 0
                }
                
                with open(output_file, 'w') as f:
                    json.dump(captured_results, f, indent=2)
                
                print(f"✓ Saved captured output to: {output_file.name}")
        
        return result.returncode
        
    except subprocess.TimeoutExpired:
        print("\n✗ Process timed out after 1 hour")
        return 1
    except Exception as e:
        print(f"\n✗ Error running hybrid system: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_hybrid_and_save())
