#!/usr/bin/env python3
"""
Script to extend the datasets structure with new operational scripts and domains.
Maintains compatibility with the original hypatiax/datasets structure.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional


class DatasetExtender:
    """Extends the datasets structure following the original pattern."""
    
    # Standard operational script directories
    OPERATIONAL_SCRIPTS = [
        'combined',
        'normalize',
        'analytics',
        'llm',
        'transformer',
        'agent'
    ]
    
    # Standard data storage subdirectories
    DATA_SUBDIRS = [
        'testing',
        'testing_spacy',
        'training',
        'training_spacy',
        'validation',
        'validation_spacy'
    ]
    
    def __init__(self, base_path: str = '.'):
        """
        Initialize the dataset extender.
        
        Args:
            base_path: Base path where datasets/ directory exists or will be created
        """
        self.base_path = Path(base_path).resolve()
        self.datasets_path = self.base_path / 'datasets'
        
        # Auto-detect if we're already in a directory containing datasets/
        if not self.datasets_path.exists() and (self.base_path.parent / 'datasets').exists():
            self.datasets_path = self.base_path.parent / 'datasets'
            self.base_path = self.base_path.parent
    
    def create_init_file(self, directory: Path):
        """Create an __init__.py file in the specified directory."""
        init_file = directory / '__init__.py'
        if not init_file.exists():
            init_file.write_text('"""Auto-generated __init__.py"""\n')
            print(f"  Created: {init_file.relative_to(self.base_path)}")
    
    def create_test_file(self, directory: Path):
        """Create a test.py template in the specified directory."""
        test_file = directory / 'test.py'
        if not test_file.exists():
            content = '''"""Test module for data processing."""

def test():
    """Run tests."""
    print("Running tests...")
    pass


if __name__ == "__main__":
    test()
'''
            test_file.write_text(content)
            print(f"  Created: {test_file.relative_to(self.base_path)}")
    
    def extend_existing_domain(self, domain_name: str, 
                              add_scripts: Optional[List[str]] = None):
        """
        Extend an existing domain with new operational scripts.
        
        Args:
            domain_name: Name of the domain (e.g., 'queries')
            add_scripts: List of script types to add (defaults to ['analytics', 'llm', 'transformer', 'agent'])
        """
        if add_scripts is None:
            add_scripts = ['analytics', 'llm', 'transformer', 'agent']
        
        domain_path = self.datasets_path / domain_name
        
        if not domain_path.exists():
            print(f"❌ Domain '{domain_name}' does not exist. Use create_new_domain() instead.")
            return False
        
        print(f"\n📦 Extending domain: {domain_name}")
        
        for script_type in add_scripts:
            script_path = domain_path / script_type
            script_path.mkdir(parents=True, exist_ok=True)
            print(f"  📁 {script_type}/")
            
            # Create __init__.py
            self.create_init_file(script_path)
            
            # Create test.py
            self.create_test_file(script_path)
            
            # Create main processing script based on type
            if script_type == 'analytics':
                main_script = script_path / f'analytics_data.py'
                content = f'''"""
Analytics operations for {domain_name} data.
Provides visualization and metrics computation.
"""


def visualize():
    """Generate visualizations from data."""
    print(f"Generating visualizations for {domain_name} data...")
    # Implementation: create charts, graphs, plots
    # Examples: matplotlib, plotly, seaborn visualizations
    pass


def compute_metrics():
    """Calculate metrics and statistics."""
    print(f"Computing metrics for {domain_name} data...")
    # Implementation: statistical analysis, KPIs, aggregations
    # Examples: mean, median, distributions, correlations
    pass


def generate_report():
    """Generate analytics report with visualizations and metrics."""
    print(f"Generating analytics report for {domain_name}...")
    visualize()
    compute_metrics()
    # Implementation: combine visualizations and metrics into report
    pass


if __name__ == "__main__":
    generate_report()
'''
            else:
                main_script = script_path / f'{script_type}_{domain_name}.py'
                content = f'''"""
{script_type.upper()} processing for {domain_name} domain.
"""


def process():
    """Main processing function."""
    print(f"Processing {domain_name} data with {script_type}...")
    # Implementation here
    pass


if __name__ == "__main__":
    process()
'''
            
            if not main_script.exists():
                main_script.write_text(content)
                print(f"  Created: {main_script.relative_to(self.base_path)}")
            
            # Create __pycache__ directory
            pycache = script_path / '__pycache__'
            pycache.mkdir(exist_ok=True)
        
        return True
    
    def create_new_domain(self, domain_name: str, 
                         data_dir_name: str = 'data',
                         include_scripts: Optional[List[str]] = None):
        """
        Create a complete new domain with all standard directories.
        
        Args:
            domain_name: Name of the new domain (e.g., 'finance', 'analytics')
            data_dir_name: Name for the data storage directory (default: 'data')
            include_scripts: List of operational scripts to include (default: all)
        """
        if include_scripts is None:
            include_scripts = self.OPERATIONAL_SCRIPTS
        
        domain_path = self.datasets_path / domain_name
        
        if domain_path.exists():
            print(f"⚠️  Domain '{domain_name}' already exists. Use extend_existing_domain() instead.")
            return False
        
        print(f"\n🆕 Creating new domain: {domain_name}")
        domain_path.mkdir(parents=True, exist_ok=True)
        
        # Create domain-level __init__.py
        self.create_init_file(domain_path)
        
        # Create operational script directories
        for script_type in include_scripts:
            script_path = domain_path / script_type
            script_path.mkdir(parents=True, exist_ok=True)
            print(f"  📁 {script_type}/")
            
            self.create_init_file(script_path)
            self.create_test_file(script_path)
            
            # Create main script
            if script_type == 'combined':
                main_script = script_path / f'combined_data.py'
                content = f'''"""Combine data from multiple sources for {domain_name}."""


def combine():
    """Combine data from various sources."""
    print(f"Combining {domain_name} data...")
    # Implementation here
    pass


if __name__ == "__main__":
    combine()
'''
            elif script_type == 'normalize':
                main_script = script_path / f'normalize_data.py'
                content = f'''"""Normalize {domain_name} data."""


def normalize():
    """Normalize data format."""
    print(f"Normalizing {domain_name} data...")
    # Implementation here
    pass


if __name__ == "__main__":
    normalize()
'''
            elif script_type == 'analytics':
                main_script = script_path / f'analytics_data.py'
                content = f'''"""
Analytics operations for {domain_name} data.
Provides visualization and metrics computation.
"""


def visualize():
    """Generate visualizations from data."""
    print(f"Generating visualizations for {domain_name} data...")
    # Implementation: create charts, graphs, plots
    # Examples: matplotlib, plotly, seaborn visualizations
    pass


def compute_metrics():
    """Calculate metrics and statistics."""
    print(f"Computing metrics for {domain_name} data...")
    # Implementation: statistical analysis, KPIs, aggregations
    # Examples: mean, median, distributions, correlations
    pass


def generate_report():
    """Generate analytics report with visualizations and metrics."""
    print(f"Generating analytics report for {domain_name}...")
    visualize()
    compute_metrics()
    # Implementation: combine visualizations and metrics into report
    pass


if __name__ == "__main__":
    generate_report()
'''
            else:
                main_script = script_path / f'{script_type}_{domain_name}.py'
                content = f'''"""
{script_type.upper()} processing for {domain_name} domain.
"""


def process():
    """Main processing function."""
    print(f"Processing {domain_name} data with {script_type}...")
    # Implementation here
    pass


if __name__ == "__main__":
    process()
'''
            
            main_script.write_text(content)
            print(f"    - {main_script.name}")
            
            # Create __pycache__
            (script_path / '__pycache__').mkdir(exist_ok=True)
        
        # Create data storage directory structure
        data_path = domain_path / data_dir_name
        data_path.mkdir(parents=True, exist_ok=True)
        print(f"  📁 {data_dir_name}/")
        
        self.create_init_file(data_path)
        
        # Create standard data subdirectories
        for subdir in self.DATA_SUBDIRS:
            subdir_path = data_path / subdir
            subdir_path.mkdir(parents=True, exist_ok=True)
            print(f"    📂 {subdir}/")
            
            self.create_init_file(subdir_path)
            self.create_test_file(subdir_path)
            
            # Create __pycache__
            (subdir_path / '__pycache__').mkdir(exist_ok=True)
        
        # Create a raw data subdirectory (optional)
        raw_path = data_path / 'raw'
        raw_path.mkdir(exist_ok=True)
        self.create_init_file(raw_path)
        self.create_test_file(raw_path)
        print(f"    📂 raw/")
        
        return True
    
    def show_structure(self, domain_name: Optional[str] = None):
        """
        Display the current structure of datasets.
        
        Args:
            domain_name: If provided, show only this domain's structure
        """
        if not self.datasets_path.exists():
            print("❌ datasets/ directory does not exist")
            return
        
        print("\n📊 Current Dataset Structure:")
        print("=" * 60)
        
        if domain_name:
            domain_path = self.datasets_path / domain_name
            if domain_path.exists():
                self._print_tree(domain_path, prefix="")
            else:
                print(f"❌ Domain '{domain_name}' not found")
        else:
            self._print_tree(self.datasets_path, prefix="", max_depth=3)
    
    def _print_tree(self, directory: Path, prefix: str = "", max_depth: int = 3, 
                   current_depth: int = 0):
        """Recursively print directory tree."""
        if current_depth > max_depth:
            return
        
        try:
            items = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name))
            dirs = [item for item in items if item.is_dir() and item.name != '__pycache__']
            files = [item for item in items if item.is_file() and item.suffix in ['.py', '.csv', '.json', '.xlsx']]
            
            for i, item in enumerate(dirs + files):
                is_last = i == len(dirs + files) - 1
                current = "└── " if is_last else "├── "
                extension = "    " if is_last else "│   "
                
                if item.is_dir():
                    print(f"{prefix}{current}{item.name}/")
                    self._print_tree(item, prefix + extension, max_depth, current_depth + 1)
                else:
                    print(f"{prefix}{current}{item.name}")
        except PermissionError:
            pass


def main():
    """Main execution function with interactive menu."""
    print("=" * 60)
    print("  HypatiaX Dataset Structure Extender")
    print("=" * 60)
    
    # Get base path - default to current directory
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = "."
    
    extender = DatasetExtender(base_path)
    
    print(f"\n📁 Working directory: {extender.base_path}")
    print(f"📁 Datasets path: {extender.datasets_path}")
    
    # Ensure datasets directory exists
    if not extender.datasets_path.exists():
        print(f"\n❌ datasets/ directory not found")
        create = input("Create datasets/ directory? (y/n): ").strip().lower()
        if create == 'y':
            extender.datasets_path.mkdir(parents=True, exist_ok=True)
            extender.create_init_file(extender.datasets_path)
            print("✅ Created datasets/ directory")
        else:
            print("Exiting...")
            return
    else:
        print("✅ datasets/ directory found")
    
    while True:
        print("\n" + "=" * 60)
        print("Options:")
        print("  1. Extend existing domain (add analytics/llm/transformer/agent)")
        print("  2. Create new domain")
        print("  3. Show current structure")
        print("  4. Quick setup: Extend 'queries' domain (all scripts)")
        print("  5. Quick setup: Add only 'analytics' to 'queries'")
        print("  6. Exit")
        print("=" * 60)
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            domain = input("Enter domain name (e.g., 'queries'): ").strip()
            if domain:
                scripts = input("Scripts to add (comma-separated, default: analytics,llm,transformer,agent): ").strip()
                if scripts:
                    scripts = [s.strip() for s in scripts.split(',')]
                else:
                    scripts = None
                extender.extend_existing_domain(domain, scripts)
        
        elif choice == '2':
            domain = input("Enter new domain name (e.g., 'finance'): ").strip()
            if domain:
                data_dir = input("Data directory name (default: 'data'): ").strip() or 'data'
                extender.create_new_domain(domain, data_dir)
        
        elif choice == '3':
            domain = input("Show specific domain (press Enter for all): ").strip()
            extender.show_structure(domain if domain else None)
        
        elif choice == '4':
            print("\n🚀 Quick Setup: Extending 'queries' domain with all scripts...")
            extender.extend_existing_domain('queries')
            extender.show_structure('queries')
        
        elif choice == '5':
            print("\n📊 Quick Setup: Adding 'analytics' to 'queries' domain...")
            extender.extend_existing_domain('queries', ['analytics'])
            extender.show_structure('queries')
        
        elif choice == '6':
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option")


if __name__ == "__main__":
    main()
