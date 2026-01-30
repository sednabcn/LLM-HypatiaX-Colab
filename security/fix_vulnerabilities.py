#!/usr/bin/env python3
"""
Script to fix security vulnerabilities in Python dependencies
Addresses:
- AIOHTTP unicode processing vulnerability
- PyTorch local DoS vulnerability
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command and return the result"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors/Warnings:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error: {e}")
        return False

def update_requirements_file(file_path, package_updates):
    """Update package versions in a requirements file"""
    if not Path(file_path).exists():
        print(f"Warning: {file_path} not found, skipping...")
        return False
    
    print(f"\nUpdating {file_path}...")
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    updated_lines = []
    updated_packages = []
    
    for line in lines:
        line_updated = False
        for package, new_version in package_updates.items():
            if line.strip().startswith(package):
                # Update the version
                updated_lines.append(f"{package}>={new_version}\n")
                updated_packages.append(package)
                line_updated = True
                print(f"  ✓ Updated {package} to >={new_version}")
                break
        
        if not line_updated:
            updated_lines.append(line)
    
    # Write back
    with open(file_path, 'w') as f:
        f.writelines(updated_lines)
    
    return True

def main():
    print("🔒 Security Vulnerability Fix Script")
    print("=" * 60)
    
    # Define the minimum safe versions
    vulnerabilities = {
        'requirements/requirements.txt': {
            'aiohttp': '3.10.11'  # Fix for unicode processing vulnerability
        },
        'requirements/requirements-py311.txt': {
            'torch': '2.5.0'  # Fix for local DoS vulnerability
        }
    }
    
    # Update requirements files
    for req_file, updates in vulnerabilities.items():
        if update_requirements_file(req_file, updates):
            print(f"✓ Successfully updated {req_file}")
        else:
            print(f"✗ Failed to update {req_file}")
    
    # Option 1: Update packages directly (if you want to apply immediately)
    print("\n" + "="*60)
    print("OPTION 1: Direct Package Update")
    print("="*60)
    print("\nTo apply these fixes immediately, run:")
    print("  pip install --upgrade aiohttp>=3.10.11")
    print("  pip install --upgrade torch>=2.5.0")
    
    # Option 2: Reinstall from updated requirements
    print("\n" + "="*60)
    print("OPTION 2: Reinstall from Requirements Files")
    print("="*60)
    print("\nAfter updating requirements files, run:")
    print("  pip install -r requirements/requirements.txt --upgrade")
    print("  pip install -r requirements/requirements-py311.txt --upgrade")
    
    # Generate a security report
    print("\n" + "="*60)
    print("SECURITY AUDIT")
    print("="*60)
    print("\nRunning pip security check (if available)...")
    
    # Try to use pip-audit if available
    run_command("pip install pip-audit 2>/dev/null", "Installing pip-audit...")
    run_command("pip-audit", "Running security audit...")
    
    print("\n✅ Vulnerability fix script completed!")
    print("\nNext steps:")
    print("1. Review the updated requirements files")
    print("2. Test your application with the new versions")
    print("3. Update your dependencies: pip install -r requirements/requirements.txt --upgrade")
    print("4. Commit the changes to version control")

if __name__ == "__main__":
    main()
