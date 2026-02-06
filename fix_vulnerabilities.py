#!/usr/bin/env python3
"""
Security Vulnerability Remediation Script
Automatically updates vulnerable packages identified in the security scan.
Includes backup, rollback capabilities, and testing validation.

Usage:
    python fix_vulnerabilities.py [options]

Options:
    --dry-run         Show what would be updated without making changes
    --priority        Update only CRITICAL and HIGH severity packages
    --backup          Create backup of current environment before updating
    --test            Run tests after each update (requires pytest)
    --skip-major      Skip major version upgrades (safer option)
    --interactive     Prompt before each update
"""

import subprocess
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path


class VulnerabilityFixer:
    """Handles the remediation of security vulnerabilities in Python packages."""
    
    # Package updates organized by severity
    CRITICAL_UPDATES = [
        ("fonttools", "4.61.0", "CVE-2025-66034: Path traversal (CVSS 9.8)"),
    ]
    
    HIGH_UPDATES = [
        ("urllib3", "2.6.3", "3 DoS vulnerabilities"),
        ("pyasn1", "0.6.2", "CVE-2026-23490: DoS (CVSS 7.5)"),
        ("nbconvert", "7.17.0", "CVE-2025-53000: Search path issue (CVSS 7.8)"),
        ("marshmallow", "4.1.2", "CVE-2025-68480: DoS (CVSS 7.5)"),
        ("django", "5.2.11", "8 vulnerabilities including SQL injection"),
        ("aiohttp", "3.13.3", "8 vulnerabilities including DoS and request smuggling"),
    ]
    
    MEDIUM_UPDATES = [
        ("werkzeug", "3.1.5", "2 DoS vulnerabilities"),
        ("filelock", "3.20.3", "3 TOCTOU race conditions"),
        ("virtualenv", "20.36.1", "Race condition vulnerability"),
        ("authlib", "1.6.6", "CSRF vulnerability"),
    ]
    
    STANDARD_UPDATES = [
        ("wheel", "0.46.2", "Path traversal vulnerability"),
        ("sqlparse", "0.5.4", "Algorithmic complexity DoS"),
    ]
    
    # Major version upgrades (may have breaking changes)
    MAJOR_VERSION_UPDATES = [
        ("transformers", "5.0.0", "Insecure deserialization", "4.x → 5.0.0"),
        ("protobuf", "6.33.5", "DoS via recursion depth bypass", "5.x → 6.x"),
        ("pip", "26.0", "Path traversal vulnerability", "25.x → 26.0"),
    ]
    
    def __init__(self, args):
        self.args = args
        self.backup_file = None
        self.updated_packages = []
        self.failed_packages = []
        self.log_file = Path(f"vulnerability_fix_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
    def log(self, message, level="INFO"):
        """Log message to console and file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        with open(self.log_file, "a") as f:
            f.write(log_entry + "\n")
    
    def run_command(self, command, check=True):
        """Execute a shell command and return the result."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {command}", "ERROR")
            self.log(f"Error output: {e.stderr}", "ERROR")
            return None
    
    def get_installed_version(self, package_name):
        """Get the currently installed version of a package."""
        result = self.run_command(f"pip show {package_name}", check=False)
        if result and result.returncode == 0:
            for line in result.stdout.split("\n"):
                if line.startswith("Version:"):
                    return line.split(":")[1].strip()
        return None
    
    def create_backup(self):
        """Create a backup of currently installed packages."""
        if not self.args.backup:
            return True
        
        self.log("Creating backup of current environment...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_file = Path(f"requirements_backup_{timestamp}.txt")
        
        result = self.run_command(f"pip freeze > {self.backup_file}")
        if result and result.returncode == 0:
            self.log(f"Backup created: {self.backup_file}", "SUCCESS")
            return True
        else:
            self.log("Failed to create backup", "ERROR")
            return False
    
    def update_package(self, package_name, version, description):
        """Update a single package to the specified version."""
        current_version = self.get_installed_version(package_name)
        
        if not current_version:
            self.log(f"Package {package_name} is not installed. Skipping.", "WARNING")
            return False
        
        self.log(f"\n{'='*70}")
        self.log(f"Package: {package_name}")
        self.log(f"Current version: {current_version}")
        self.log(f"Target version: {version}")
        self.log(f"Reason: {description}")
        self.log(f"{'='*70}")
        
        if self.args.interactive:
            response = input(f"Update {package_name} {current_version} → {version}? [y/N]: ")
            if response.lower() != 'y':
                self.log(f"Skipped by user: {package_name}", "INFO")
                return False
        
        if self.args.dry_run:
            self.log(f"[DRY RUN] Would update {package_name} to {version}", "INFO")
            return True
        
        # Perform the update
        self.log(f"Updating {package_name} to {version}...", "INFO")
        result = self.run_command(
            f"pip install --upgrade {package_name}=={version}",
            check=False
        )
        
        if result and result.returncode == 0:
            new_version = self.get_installed_version(package_name)
            self.log(f"Successfully updated {package_name} to {new_version}", "SUCCESS")
            self.updated_packages.append((package_name, current_version, new_version))
            
            # Run tests if requested
            if self.args.test:
                self.run_tests(package_name)
            
            return True
        else:
            self.log(f"Failed to update {package_name}", "ERROR")
            self.failed_packages.append((package_name, description))
            return False
    
    def run_tests(self, package_name):
        """Run tests after updating a package."""
        self.log(f"Running tests after updating {package_name}...", "INFO")
        result = self.run_command("pytest --tb=short -q", check=False)
        
        if result and result.returncode == 0:
            self.log("Tests passed", "SUCCESS")
        else:
            self.log("Tests failed or not available", "WARNING")
    
    def process_updates(self, updates, category_name):
        """Process a list of package updates."""
        self.log(f"\n{'#'*70}")
        self.log(f"# {category_name}")
        self.log(f"{'#'*70}\n")
        
        for package_name, version, description, *extra in updates:
            # Check if this is a major version update
            is_major = len(extra) > 0
            if is_major and self.args.skip_major:
                self.log(f"Skipping major version update: {package_name} ({extra[0]})", "WARNING")
                continue
            
            self.update_package(package_name, version, description)
    
    def print_summary(self):
        """Print a summary of all updates performed."""
        self.log("\n" + "="*70)
        self.log("REMEDIATION SUMMARY")
        self.log("="*70 + "\n")
        
        if self.args.dry_run:
            self.log("DRY RUN MODE - No changes were made", "INFO")
        
        self.log(f"Successfully updated: {len(self.updated_packages)} packages")
        for package_name, old_version, new_version in self.updated_packages:
            self.log(f"  ✓ {package_name}: {old_version} → {new_version}")
        
        if self.failed_packages:
            self.log(f"\nFailed to update: {len(self.failed_packages)} packages", "WARNING")
            for package_name, description in self.failed_packages:
                self.log(f"  ✗ {package_name}: {description}")
        
        if self.backup_file:
            self.log(f"\nBackup file: {self.backup_file}")
            self.log(f"To rollback: pip install -r {self.backup_file}")
        
        self.log(f"\nLog file: {self.log_file}")
        
        if not self.args.dry_run:
            self.log("\n⚠️  IMPORTANT: Run your test suite to verify everything works correctly!")
            self.log("If issues occur, rollback using the backup file.")
    
    def run(self):
        """Main execution method."""
        self.log("="*70)
        self.log("Security Vulnerability Remediation Script")
        self.log("="*70)
        self.log(f"Mode: {'DRY RUN' if self.args.dry_run else 'LIVE UPDATE'}")
        self.log(f"Priority only: {self.args.priority}")
        self.log(f"Skip major versions: {self.args.skip_major}")
        self.log(f"Interactive: {self.args.interactive}")
        self.log(f"Backup: {self.args.backup}")
        self.log(f"Test: {self.args.test}")
        self.log("")
        
        # Create backup if requested
        if self.args.backup and not self.args.dry_run:
            if not self.create_backup():
                self.log("Aborting due to backup failure", "ERROR")
                return 1
        
        # Process updates by priority
        self.process_updates(self.CRITICAL_UPDATES, "CRITICAL UPDATES")
        self.process_updates(self.HIGH_UPDATES, "HIGH PRIORITY UPDATES")
        
        if not self.args.priority:
            self.process_updates(self.MEDIUM_UPDATES, "MEDIUM PRIORITY UPDATES")
            self.process_updates(self.STANDARD_UPDATES, "STANDARD UPDATES")
            self.process_updates(self.MAJOR_VERSION_UPDATES, "MAJOR VERSION UPDATES (Breaking Changes Possible)")
        
        # Print summary
        self.print_summary()
        
        return 0 if not self.failed_packages else 1


def main():
    parser = argparse.ArgumentParser(
        description="Automatically fix security vulnerabilities in Python packages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview changes without making them
  python fix_vulnerabilities.py --dry-run
  
  # Update only critical and high priority packages
  python fix_vulnerabilities.py --priority --backup
  
  # Interactive mode with testing
  python fix_vulnerabilities.py --interactive --test --backup
  
  # Safe mode: skip major version upgrades
  python fix_vulnerabilities.py --skip-major --backup
  
  # Full update with backup
  python fix_vulnerabilities.py --backup
        """
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes"
    )
    
    parser.add_argument(
        "--priority",
        action="store_true",
        help="Update only CRITICAL and HIGH severity packages"
    )
    
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create backup of current environment before updating"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run tests after each update (requires pytest)"
    )
    
    parser.add_argument(
        "--skip-major",
        action="store_true",
        help="Skip major version upgrades (safer option)"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Prompt before each update"
    )
    
    args = parser.parse_args()
    
    # Verify pip is available
    try:
        subprocess.run(["pip", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: pip is not available. Please ensure pip is installed.")
        return 1
    
    fixer = VulnerabilityFixer(args)
    return fixer.run()


if __name__ == "__main__":
    sys.exit(main())
