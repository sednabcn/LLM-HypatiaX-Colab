#!/usr/bin/env python3
"""
Script to migrate hard-coded paths and configs to use hypatiax.config system.
Usage: python migrate_to_config.py [--dry-run] [--path /path/to/project]
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict
import argparse


class ConfigMigrator:
    def __init__(self, project_root: str, dry_run: bool = False):
        self.project_root = Path(project_root)
        self.dry_run = dry_run
        self.changes_made = 0
        self.files_modified = 0
        
        # Patterns to find and replace
        self.path_patterns = [
            # Dataset paths
            (r"['\"]hypatiax/datasets/queries/tableau/training/([^'\"]+)['\"]",
             r"paths.training_data / '\1'"),
            (r"['\"]hypatiax/datasets/queries/tableau/testing/([^'\"]+)['\"]",
             r"paths.testing_data / '\1'"),
            (r"['\"]hypatiax/datasets/queries/tableau/training_spacy/([^'\"]+)['\"]",
             r"paths.training_spacy / '\1'"),
            (r"['\"]hypatiax/datasets/queries/tableau/testing_spacy/([^'\"]+)['\"]",
             r"paths.testing_spacy / '\1'"),
            
            # Output paths
            (r"['\"]outputs/models/([^'\"]+)['\"]",
             r"paths.get_output_path('models', '\1')"),
            (r"['\"]outputs/([^'\"]+)['\"]",
             r"paths.outputs / '\1'"),
            
            # Data spacy paths
            (r"['\"]hypatiax/data_spacy/queries/tableau/([^'\"]+)['\"]",
             r"paths.models / '\1'"),
            
            # Custom NER paths
            (r"['\"]hypatiax/custom_ner/queries/tableau/rules/([^'\"]+)['\"]",
             r"paths.custom_rules / '\1'"),
        ]
        
        # Config dictionary patterns
        self.config_patterns = [
            # Training configs
            (r"config\s*=\s*\{\s*['\"]niter['\"]\s*:\s*(\d+)\s*,\s*['\"]batchsize['\"]\s*:\s*(\d+)\s*,\s*['\"]drop['\"]\s*:\s*([\d.]+)\s*,\s*['\"]dtype['\"]\s*:\s*['\"]desc['\"]\s*\}",
             r"config = ModelConfig.training_desc(niter=\1, batchsize=\2, drop=\3)"),
            (r"config\s*=\s*\{\s*['\"]niter['\"]\s*:\s*(\d+)\s*,\s*['\"]batchsize['\"]\s*:\s*(\d+)\s*,\s*['\"]drop['\"]\s*:\s*([\d.]+)\s*,\s*['\"]dtype['\"]\s*:\s*['\"]formulas['\"]\s*\}",
             r"config = ModelConfig.training_formulas(niter=\1, batchsize=\2, drop=\3)"),
        ]

    def should_skip_file(self, filepath: Path) -> bool:
        """Check if file should be skipped."""
        skip_patterns = [
            '__pycache__',
            '.git',
            'venv',
            'build',
            'dist',
            '.egg-info',
            'hypatiax/config',  # Don't modify config files themselves
            'migrate_to_config.py',  # Don't modify this script
        ]
        
        str_path = str(filepath)
        return any(pattern in str_path for pattern in skip_patterns)

    def find_python_files(self) -> List[Path]:
        """Find all Python files in the project."""
        python_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Remove directories to skip from dirs list
            dirs[:] = [d for d in dirs if not any(skip in d for skip in 
                      ['__pycache__', '.git', 'venv', 'build', 'dist'])]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = Path(root) / file
                    if not self.should_skip_file(filepath):
                        python_files.append(filepath)
        
        return python_files

    def needs_config_import(self, content: str) -> Tuple[bool, bool]:
        """Check if file needs config imports."""
        needs_paths = bool(re.search(r'\bpaths\.[a-z_]+', content))
        needs_model_config = bool(re.search(r'\bModelConfig\.[a-z_]+', content))
        return needs_paths, needs_model_config

    def add_imports(self, content: str) -> str:
        """Add necessary imports to the file."""
        needs_paths, needs_model_config = self.needs_config_import(content)
        
        if not (needs_paths or needs_model_config):
            return content
        
        # Build import statement
        imports_needed = []
        if needs_paths:
            imports_needed.append('paths')
        if needs_model_config:
            imports_needed.append('ModelConfig')
        
        import_line = f"from hypatiax.config import {', '.join(imports_needed)}\n"
        
        # Check if import already exists
        if 'from hypatiax.config import' in content:
            # Update existing import
            content = re.sub(
                r'from hypatiax\.config import [^\n]+\n',
                import_line,
                content
            )
        else:
            # Add new import after other imports
            import_section_match = re.search(r'((?:from|import)[^\n]+\n)+', content)
            if import_section_match:
                # Add after last import
                insert_pos = import_section_match.end()
                content = content[:insert_pos] + import_line + content[insert_pos:]
            else:
                # Add at the beginning (after shebang and docstring if present)
                lines = content.split('\n')
                insert_idx = 0
                
                # Skip shebang
                if lines[0].startswith('#!'):
                    insert_idx = 1
                
                # Skip docstring
                if insert_idx < len(lines) and (lines[insert_idx].startswith('"""') or lines[insert_idx].startswith("'''")):
                    quote = '"""' if '"""' in lines[insert_idx] else "'''"
                    insert_idx += 1
                    while insert_idx < len(lines) and quote not in lines[insert_idx]:
                        insert_idx += 1
                    insert_idx += 1
                
                lines.insert(insert_idx, import_line)
                content = '\n'.join(lines)
        
        return content

    def migrate_file(self, filepath: Path) -> bool:
        """Migrate a single file. Returns True if file was modified."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                original_content = f.read()
        except Exception as e:
            print(f"❌ Error reading {filepath}: {e}")
            return False
        
        content = original_content
        file_changes = 0
        
        # Apply path replacements
        for pattern, replacement in self.path_patterns:
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                file_changes += len(matches)
        
        # Apply config replacements
        for pattern, replacement in self.config_patterns:
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                file_changes += len(matches)
        
        # Add imports if needed
        if file_changes > 0:
            content = self.add_imports(content)
        
        # Check if file was modified
        if content != original_content:
            if self.dry_run:
                print(f"🔍 Would modify: {filepath.relative_to(self.project_root)} ({file_changes} changes)")
                # Show diff preview
                self._show_diff_preview(original_content, content, filepath)
            else:
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ Modified: {filepath.relative_to(self.project_root)} ({file_changes} changes)")
                except Exception as e:
                    print(f"❌ Error writing {filepath}: {e}")
                    return False
            
            self.changes_made += file_changes
            self.files_modified += 1
            return True
        
        return False

    def _show_diff_preview(self, original: str, modified: str, filepath: Path):
        """Show a preview of changes."""
        orig_lines = original.split('\n')
        mod_lines = modified.split('\n')
        
        print(f"  Preview of changes in {filepath.name}:")
        for i, (orig, mod) in enumerate(zip(orig_lines, mod_lines), 1):
            if orig != mod:
                print(f"    Line {i}:")
                print(f"      - {orig[:80]}...")
                print(f"      + {mod[:80]}...")
                if i > 3:  # Show only first 3 changes
                    print(f"    ... and more")
                    break
        print()

    def run(self):
        """Run the migration."""
        print(f"🔍 Scanning project at: {self.project_root}")
        print(f"{'🧪 DRY RUN MODE - No files will be modified' if self.dry_run else '✏️  LIVE MODE - Files will be modified'}")
        print("=" * 70)
        
        python_files = self.find_python_files()
        print(f"Found {len(python_files)} Python files to check\n")
        
        for filepath in python_files:
            self.migrate_file(filepath)
        
        print("\n" + "=" * 70)
        print(f"📊 Summary:")
        print(f"   Files modified: {self.files_modified}")
        print(f"   Total changes: {self.changes_made}")
        
        if self.dry_run:
            print("\n💡 Run without --dry-run to apply these changes")
        else:
            print("\n✅ Migration complete!")
            print("\n🧪 Next steps:")
            print("   1. Run tests to verify: python -m pytest tests/")
            print("   2. Check git diff to review changes: git diff")
            print("   3. Test imports: python -c 'from hypatiax.config import paths, ModelConfig'")


def main():
    parser = argparse.ArgumentParser(
        description='Migrate HypatiaX project to use centralized config system'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    parser.add_argument(
        '--path',
        type=str,
        default='.',
        help='Path to project root (default: current directory)'
    )
    
    args = parser.parse_args()
    
    project_root = Path(args.path).resolve()
    
    if not project_root.exists():
        print(f"❌ Error: Path does not exist: {project_root}")
        sys.exit(1)
    
    if not (project_root / 'hypatiax').exists():
        print(f"❌ Error: Not a HypatiaX project (hypatiax directory not found)")
        sys.exit(1)
    
    migrator = ConfigMigrator(project_root, dry_run=args.dry_run)
    migrator.run()


if __name__ == '__main__':
    main()
