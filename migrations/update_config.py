#!/usr/bin/env python3
"""
Script to scan HypatiaX directory structure and automatically update
pyproject.toml and setup.py with all discovered packages and data files.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Set
import tomllib
import re


class HypatiaXScanner:
    """Scans HypatiaX structure and updates configuration files."""
    
    # File extensions to include in package_data
    DATA_EXTENSIONS = {
        '.xlsx', '.json', '.spacy', '.cfg', '.txt', '.bin',
        '.csv', '.xml', '.yaml', '.yml', '.md', '.rst'
    }
    
    # Directories to exclude from scanning
    EXCLUDE_DIRS = {
        '__pycache__', '.git', '.pytest_cache', '.venv', 'venv',
        'build', 'dist', '*.egg-info', '.tox', '.mypy_cache',
        'node_modules', '.ipynb_checkpoints'
    }
    
    def __init__(self, base_path: str = '.'):
        """
        Initialize scanner.
        
        Args:
            base_path: Base path of HypatiaX project
        """
        self.base_path = Path(base_path).resolve()
        self.hypatiax_path = self.base_path / 'hypatiax'
        
        if not self.hypatiax_path.exists():
            # Check if we're already in hypatiax
            if (self.base_path / 'datasets').exists():
                self.hypatiax_path = self.base_path
            else:
                raise ValueError(f"Cannot find hypatiax directory at {self.base_path}")
        
        self.packages = set()
        self.package_data = {}
        self.scripts = []
        
    def should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded."""
        return any(exclude in str(path) for exclude in self.EXCLUDE_DIRS)
    
    def scan_packages(self) -> Set[str]:
        """
        Scan for all Python packages (directories with __init__.py).
        
        Returns:
            Set of package names
        """
        packages = set()
        
        for root, dirs, files in os.walk(self.hypatiax_path):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if not self.should_exclude(Path(root) / d)]
            
            if '__init__.py' in files:
                # Convert path to package name
                rel_path = Path(root).relative_to(self.base_path)
                package_name = str(rel_path).replace(os.sep, '.')
                packages.add(package_name)
        
        self.packages = packages
        return packages
    
    def scan_data_files(self) -> Dict[str, List[str]]:
        """
        Scan for data files in each package.
        
        Returns:
            Dictionary mapping package names to data file patterns
        """
        package_data = {}
        
        for root, dirs, files in os.walk(self.hypatiax_path):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if not self.should_exclude(Path(root) / d)]
            
            root_path = Path(root)
            
            # Check if this is a package
            if not (root_path / '__init__.py').exists():
                continue
            
            # Get package name
            rel_path = root_path.relative_to(self.base_path)
            package_name = str(rel_path).replace(os.sep, '.')
            
            # Find data files
            data_patterns = set()
            
            # Check for data files in this directory
            has_data = any(Path(f).suffix in self.DATA_EXTENSIONS for f in files)
            if has_data:
                for ext in self.DATA_EXTENSIONS:
                    if any(f.endswith(ext) for f in files):
                        data_patterns.add(f"*{ext}")
            
            # Check subdirectories for data
            for dirpath, _, subfiles in os.walk(root_path):
                if self.should_exclude(Path(dirpath)):
                    continue
                    
                subdir_rel = Path(dirpath).relative_to(root_path)
                if subdir_rel != Path('.'):
                    # Check if subdirectory has data files
                    if any(Path(f).suffix in self.DATA_EXTENSIONS for f in subfiles):
                        data_patterns.add(f"{subdir_rel}/*")
            
            if data_patterns:
                package_data[package_name] = sorted(data_patterns)
        
        self.package_data = package_data
        return package_data
    
    def scan_scripts(self) -> List[str]:
        """
        Scan for executable scripts.
        
        Returns:
            List of script paths
        """
        scripts = []
        scripts_dir = self.hypatiax_path / 'scripts_'
        
        if scripts_dir.exists():
            for file in scripts_dir.glob('script_*.py'):
                scripts.append(str(file.relative_to(self.base_path)))
        
        self.scripts = scripts
        return scripts
    
    def generate_pyproject_toml(self) -> str:
        """
        Generate updated pyproject.toml content.
        
        Returns:
            Updated TOML content as string
        """
        # Read existing pyproject.toml
        pyproject_path = self.base_path / 'pyproject.toml'
        
        with open(pyproject_path, 'rb') as f:
            config = tomllib.load(f)
        
        # Generate package data section
        package_data_lines = []
        package_data_lines.append('[tool.setuptools.package-data]')
        
        # Add wildcard for all common extensions
        all_extensions = ' '.join([f'"*{ext}"' for ext in sorted(self.DATA_EXTENSIONS)])
        package_data_lines.append(f'"*" = [{all_extensions}]')
        
        # Add specific package data
        for package, patterns in sorted(self.package_data.items()):
            patterns_str = ', '.join([f'"{p}"' for p in patterns])
            package_data_lines.append(f'"{package}" = [{patterns_str}]')
        
        return '\n'.join(package_data_lines)
    
    def generate_setup_py_sections(self) -> Dict[str, str]:
        """
        Generate sections for setup.py.
        
        Returns:
            Dictionary with setup.py sections
        """
        sections = {}
        
        # Generate package_data section
        package_data_lines = ['{']
        package_data_lines.append('    "": [' + ', '.join([f'"{ext}"' for ext in sorted(self.DATA_EXTENSIONS)]) + '],')
        
        for package, patterns in sorted(self.package_data.items()):
            patterns_str = ', '.join([f'"{p}"' for p in patterns])
            package_data_lines.append(f'    "{package}": [{patterns_str}],')
        
        package_data_lines.append('}')
        sections['package_data'] = '\n'.join(package_data_lines)
        
        # Generate scripts section
        if self.scripts:
            scripts_str = ',\n        '.join([f'"{s}"' for s in self.scripts])
            sections['scripts'] = f'[\n        {scripts_str}\n    ]'
        else:
            sections['scripts'] = '[]'
        
        return sections
    
    def update_pyproject_toml(self, backup: bool = True):
        """
        Update pyproject.toml file.
        
        Args:
            backup: Whether to create backup of original file
        """
        pyproject_path = self.base_path / 'pyproject.toml'
        
        if backup and pyproject_path.exists():
            backup_path = self.base_path / 'pyproject.toml.backup'
            import shutil
            shutil.copy2(pyproject_path, backup_path)
            print(f"✅ Backed up pyproject.toml to {backup_path}")
        
        # Read original file
        with open(pyproject_path, 'r') as f:
            content = f.read()
        
        # Find and replace [tool.setuptools.package-data] section
        package_data_section = self.generate_pyproject_toml()
        
        # Remove old package-data section
        pattern = r'\[tool\.setuptools\.package-data\].*?(?=\n\[|\Z)'
        content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        # Add new section at the end
        content = content.rstrip() + '\n\n' + package_data_section + '\n'
        
        with open(pyproject_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated {pyproject_path}")
    
    def update_setup_py(self, backup: bool = True):
        """
        Update setup.py file.
        
        Args:
            backup: Whether to create backup of original file
        """
        setup_path = self.base_path / 'setup.py'
        
        if not setup_path.exists():
            print("⚠️  setup.py not found")
            return
        
        if backup:
            backup_path = self.base_path / 'setup.py.backup'
            import shutil
            shutil.copy2(setup_path, backup_path)
            print(f"✅ Backed up setup.py to {backup_path}")
        
        with open(setup_path, 'r') as f:
            content = f.read()
        
        sections = self.generate_setup_py_sections()
        
        # Update package_data
        pattern = r'package_data\s*=\s*\{[^}]+\}'
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(
                pattern,
                f'package_data={sections["package_data"]}',
                content,
                flags=re.DOTALL
            )
        
        # Update scripts
        pattern = r'scripts\s*=\s*\[[^\]]*\]'
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(
                pattern,
                f'scripts={sections["scripts"]}',
                content,
                flags=re.DOTALL
            )
        
        with open(setup_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated {setup_path}")
    
    def generate_report(self) -> str:
        """
        Generate a report of discovered packages and data.
        
        Returns:
            Report as string
        """
        lines = []
        lines.append("=" * 60)
        lines.append("HypatiaX Structure Scan Report")
        lines.append("=" * 60)
        lines.append(f"\nBase path: {self.base_path}")
        lines.append(f"HypatiaX path: {self.hypatiax_path}")
        
        lines.append(f"\n📦 Discovered {len(self.packages)} packages:")
        for package in sorted(self.packages):
            lines.append(f"  - {package}")
        
        lines.append(f"\n📄 Package data in {len(self.package_data)} packages:")
        for package, patterns in sorted(self.package_data.items()):
            lines.append(f"  {package}:")
            for pattern in patterns:
                lines.append(f"    - {pattern}")
        
        if self.scripts:
            lines.append(f"\n📜 Found {len(self.scripts)} scripts:")
            for script in self.scripts:
                lines.append(f"  - {script}")
        
        return '\n'.join(lines)


def main():
    """Main execution function."""
    print("=" * 60)
    print("  HypatiaX Configuration Updater")
    print("=" * 60)
    
    # Get base path
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = "."
    
    try:
        scanner = HypatiaXScanner(base_path)
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        return
    
    print(f"\n📁 Scanning: {scanner.hypatiax_path}")
    
    # Scan structure
    print("\n🔍 Scanning packages...")
    packages = scanner.scan_packages()
    print(f"   Found {len(packages)} packages")
    
    print("\n🔍 Scanning data files...")
    package_data = scanner.scan_data_files()
    print(f"   Found data in {len(package_data)} packages")
    
    print("\n🔍 Scanning scripts...")
    scripts = scanner.scan_scripts()
    print(f"   Found {len(scripts)} scripts")
    
    # Generate report
    print("\n" + scanner.generate_report())
    
    # Ask for confirmation
    print("\n" + "=" * 60)
    response = input("\nUpdate configuration files? (y/n): ").strip().lower()
    
    if response == 'y':
        print("\n📝 Updating configuration files...")
        
        # Update pyproject.toml
        try:
            scanner.update_pyproject_toml(backup=True)
        except Exception as e:
            print(f"❌ Error updating pyproject.toml: {e}")
        
        # Update setup.py
        try:
            scanner.update_setup_py(backup=True)
        except Exception as e:
            print(f"❌ Error updating setup.py: {e}")
        
        print("\n✅ Configuration files updated!")
        print("\nBackup files created:")
        print("  - pyproject.toml.backup")
        print("  - setup.py.backup")
        
        # Save report
        report_path = scanner.base_path / 'scan_report.txt'
        with open(report_path, 'w') as f:
            f.write(scanner.generate_report())
        print(f"\n📊 Report saved to: {report_path}")
        
    else:
        print("\n❌ Update cancelled")


if __name__ == "__main__":
    main()
