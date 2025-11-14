#!/usr/bin/env python3
"""
Script to migrate test files from subdirectories to centralized tests/ directory.

Usage:
    python migrate_tests.py --dry-run    # Preview changes
    python migrate_tests.py              # Execute migration
"""

import os
import shutil
import re
from pathlib import Path
from typing import List, Tuple, Dict
import argparse


# ============================================================================
# CONFIGURATION
# ============================================================================

TEST_FILE_PATTERNS = [
    r'^test_.*\.py$',           # test_*.py
    r'^.*_test\.py$',           # *_test.py
    r'^test.*\.py$',            # Anything starting with test
]

SOURCE_DIRS = [
    'core/preprocessing',
    'core/training',
    'core/evaluation',
    'core/deployment',
    'mappings',
    'utils',
    'custom_entities',
]

# Mapping from source directory to test category
DIR_TO_CATEGORY = {
    'core/preprocessing': 'unit',
    'core/training': 'unit',
    'core/evaluation': 'unit',
    'core/deployment': 'integration',
    'mappings': 'unit',
    'utils': 'unit',
    'custom_entities': 'unit',
}

# Special mappings for specific test types
SPECIAL_MAPPINGS = {
    'test_pipeline': 'integration',
    'test_api': 'integration',
    'test_e2e': 'integration',
    'test_end_to_end': 'integration',
    'benchmark': 'benchmark',
    'test_performance': 'benchmark',
    'test_load': 'benchmark',
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def is_test_file(filename: str) -> bool:
    """Check if a file is a test file based on naming patterns."""
    for pattern in TEST_FILE_PATTERNS:
        if re.match(pattern, filename, re.IGNORECASE):
            return True
    return False


def determine_test_category(filepath: Path, source_dir: str) -> str:
    """
    Determine the test category (unit/integration/benchmark).
    
    Args:
        filepath: Path to the test file
        source_dir: Source directory it came from
        
    Returns:
        Test category: 'unit', 'integration', or 'benchmark'
    """
    filename = filepath.name.lower()
    
    # Check special mappings first
    for keyword, category in SPECIAL_MAPPINGS.items():
        if keyword in filename:
            return category
    
    # Use directory mapping
    return DIR_TO_CATEGORY.get(source_dir, 'unit')


def find_test_files(base_dir: Path) -> List[Tuple[Path, str]]:
    """
    Find all test files in source directories.
    
    Returns:
        List of (filepath, source_dir) tuples
    """
    test_files = []
    
    for source_dir in SOURCE_DIRS:
        dir_path = base_dir / source_dir
        if not dir_path.exists():
            print(f"⚠️  Directory not found: {source_dir}")
            continue
        
        for file in dir_path.rglob('*.py'):
            if is_test_file(file.name):
                test_files.append((file, source_dir))
    
    return test_files


def create_test_structure(base_dir: Path, dry_run: bool = False):
    """Create the tests/ directory structure."""
    test_dirs = [
        'tests',
        'tests/unit',
        'tests/integration',
        'tests/benchmark',
        'tests/fixtures',
        'tests/data',
    ]
    
    for dir_path in test_dirs:
        full_path = base_dir / dir_path
        if not full_path.exists():
            if dry_run:
                print(f"[DRY RUN] Would create: {dir_path}/")
            else:
                full_path.mkdir(parents=True, exist_ok=True)
                print(f"✓ Created: {dir_path}/")
                
                # Create __init__.py
                init_file = full_path / '__init__.py'
                if not init_file.exists():
                    init_file.touch()
                    print(f"  ✓ Created: {dir_path}/__init__.py")


def generate_conftest(base_dir: Path, dry_run: bool = False):
    """Generate a conftest.py with common fixtures."""
    conftest_content = '''"""
Pytest configuration and shared fixtures for hypatiax tests.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_train_data():
    """Load sample training data."""
    # TODO: Implement based on your data format
    return []


@pytest.fixture
def sample_test_data():
    """Load sample test data."""
    # TODO: Implement based on your data format
    return []


@pytest.fixture
def mock_config():
    """Provide a mock configuration for testing."""
    return {
        'modules': 'datasets',
        'domain': 'queries',
        'sub_domain': 'tableau',
        'dtype': 'desc',
        'sizefile': 'sm',
        'test_size': 0.2,
    }


@pytest.fixture
def temp_output_dir(tmp_path):
    """Provide a temporary directory for test outputs."""
    output_dir = tmp_path / "test_outputs"
    output_dir.mkdir()
    return output_dir


# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "benchmark: marks tests as benchmark tests"
    )
'''
    
    conftest_path = base_dir / 'tests' / 'conftest.py'
    
    if dry_run:
        print(f"[DRY RUN] Would create: tests/conftest.py")
    else:
        if not conftest_path.exists():
            conftest_path.write_text(conftest_content)
            print(f"✓ Created: tests/conftest.py")
        else:
            print(f"⚠️  Already exists: tests/conftest.py")


def update_imports_in_file(filepath: Path, dry_run: bool = False) -> bool:
    """
    Update imports in test file to work from new location.
    
    Returns:
        True if changes were made
    """
    try:
        content = filepath.read_text()
        original_content = content
        
        # Common import patterns to fix
        import_replacements = [
            # Relative imports to absolute
            (r'from \.\. import', 'from hypatiax.core import'),
            (r'from \.\.\.', 'from hypatiax.'),
            (r'from \.', 'from hypatiax.core.'),
            
            # Add sys.path manipulation if needed
        ]
        
        for pattern, replacement in import_replacements:
            content = re.sub(pattern, replacement, content)
        
        if content != original_content:
            if not dry_run:
                filepath.write_text(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"⚠️  Error updating imports in {filepath}: {e}")
        return False


def migrate_test_file(
    source_file: Path,
    target_dir: Path,
    dry_run: bool = False
) -> bool:
    """
    Migrate a single test file.
    
    Returns:
        True if successful
    """
    try:
        target_file = target_dir / source_file.name
        
        # Check for naming conflicts
        if target_file.exists():
            print(f"⚠️  File already exists: {target_file.relative_to(target_dir.parent.parent)}")
            # Generate unique name
            counter = 1
            stem = source_file.stem
            while target_file.exists():
                target_file = target_dir / f"{stem}_{counter}.py"
                counter += 1
            print(f"   Renaming to: {target_file.name}")
        
        if dry_run:
            print(f"[DRY RUN] Would move:")
            print(f"  {source_file.relative_to(source_file.parent.parent.parent)} → {target_file.relative_to(target_file.parent.parent)}")
        else:
            shutil.copy2(source_file, target_file)
            print(f"✓ Migrated: {source_file.name} → {target_file.relative_to(target_file.parent.parent)}")
            
            # Update imports
            if update_imports_in_file(target_file):
                print(f"  ✓ Updated imports")
        
        return True
        
    except Exception as e:
        print(f"✗ Error migrating {source_file}: {e}")
        return False


def generate_migration_report(
    test_files: List[Tuple[Path, str]],
    base_dir: Path
) -> Dict:
    """Generate a report of what will be migrated."""
    report = {
        'unit': [],
        'integration': [],
        'benchmark': [],
    }
    
    for filepath, source_dir in test_files:
        category = determine_test_category(filepath, source_dir)
        report[category].append({
            'source': str(filepath.relative_to(base_dir)),
            'target': f"tests/{category}/{filepath.name}",
        })
    
    return report


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main migration function."""
    parser = argparse.ArgumentParser(
        description='Migrate test files to centralized tests/ directory'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without executing'
    )
    parser.add_argument(
        '--base-dir',
        type=str,
        default='.',
        help='Base directory of the project (default: current directory)'
    )
    parser.add_argument(
        '--keep-originals',
        action='store_true',
        help='Keep original test files (copy instead of move)'
    )
    
    args = parser.parse_args()
    
    base_dir = Path(args.base_dir).resolve()
    
    print("="*70)
    print("TEST FILE MIGRATION")
    print("="*70)
    print(f"Base directory: {base_dir}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'EXECUTE'}")
    print("="*70)
    
    # Step 1: Find all test files
    print("\n[1/5] Scanning for test files...")
    test_files = find_test_files(base_dir)
    
    if not test_files:
        print("✓ No test files found to migrate")
        return
    
    print(f"✓ Found {len(test_files)} test file(s)")
    
    # Step 2: Generate report
    print("\n[2/5] Generating migration report...")
    report = generate_migration_report(test_files, base_dir)
    
    print(f"\nMigration Plan:")
    print(f"  Unit tests:        {len(report['unit'])}")
    print(f"  Integration tests: {len(report['integration'])}")
    print(f"  Benchmark tests:   {len(report['benchmark'])}")
    
    if args.dry_run:
        print("\nDetailed Plan:")
        for category, files in report.items():
            if files:
                print(f"\n  {category.upper()}:")
                for file in files:
                    print(f"    {file['source']} → {file['target']}")
    
    # Step 3: Create test structure
    print("\n[3/5] Creating test directory structure...")
    create_test_structure(base_dir, args.dry_run)
    
    # Step 4: Generate conftest.py
    print("\n[4/5] Generating conftest.py...")
    generate_conftest(base_dir, args.dry_run)
    
    # Step 5: Migrate files
    print("\n[5/5] Migrating test files...")
    
    success_count = 0
    fail_count = 0
    
    for filepath, source_dir in test_files:
        category = determine_test_category(filepath, source_dir)
        target_dir = base_dir / 'tests' / category
        
        if migrate_test_file(filepath, target_dir, args.dry_run):
            success_count += 1
            
            # Remove original if not keeping and not dry run
            if not args.keep_originals and not args.dry_run:
                try:
                    filepath.unlink()
                    print(f"  ✓ Removed original: {filepath.name}")
                except Exception as e:
                    print(f"  ⚠️  Could not remove original: {e}")
        else:
            fail_count += 1
    
    # Summary
    print("\n" + "="*70)
    print("MIGRATION SUMMARY")
    print("="*70)
    print(f"Total files:     {len(test_files)}")
    print(f"Successful:      {success_count}")
    print(f"Failed:          {fail_count}")
    
    if args.dry_run:
        print("\n⚠️  DRY RUN MODE - No changes were made")
        print("Run without --dry-run to execute migration")
    else:
        print("\n✓ Migration completed!")
        print("\nNext steps:")
        print("  1. Review migrated test files")
        print("  2. Update import statements if needed")
        print("  3. Run: pytest tests/")
        print("  4. Update CI/CD configuration")
    
    print("="*70)


if __name__ == "__main__":
    main()
