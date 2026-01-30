#!/usr/bin/env python3
"""
HypatiaX Documentation Generator
================================
Automatically generates comprehensive documentation for the LLM-HypatiaX project
by analyzing the codebase structure and extracting docstrings, type hints, and usage patterns.

Usage:
    python generate_docs.py [--output-dir docs] [--format markdown]
"""

import os
import ast
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re


class DocumentationGenerator:
    """Generates comprehensive documentation for Python codebases."""
    
    def __init__(self, root_path: str, output_dir: str = "docs"):
        self.root_path = Path(root_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Project structure storage
        self.modules = {}
        self.classes = {}
        self.functions = {}
        self.file_dependencies = {}
        
        # Patterns to ignore
        self.ignore_patterns = [
            '__pycache__', '.pyc', '.egg-info', 'build', 'dist',
            '.git', 'venv', 'node_modules', '.pytest_cache'
        ]
    
    def should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored."""
        return any(pattern in str(path) for pattern in self.ignore_patterns)
    
    def extract_module_info(self, file_path: Path) -> Dict:
        """Extract information from a Python module."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
            
            module_info = {
                'path': str(file_path.relative_to(self.root_path)),
                'docstring': ast.get_docstring(tree),
                'imports': [],
                'classes': [],
                'functions': [],
                'constants': [],
                'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_info['imports'].append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_info['imports'].append(node.module)
                
                elif isinstance(node, ast.ClassDef):
                    class_info = self.extract_class_info(node)
                    module_info['classes'].append(class_info)
                
                elif isinstance(node, ast.FunctionDef):
                    # Only top-level functions
                    if isinstance(node.parent if hasattr(node, 'parent') else None, ast.Module):
                        func_info = self.extract_function_info(node)
                        module_info['functions'].append(func_info)
                
                elif isinstance(node, ast.Assign):
                    # Extract module-level constants
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            module_info['constants'].append(target.id)
            
            return module_info
        
        except Exception as e:
            return {
                'path': str(file_path.relative_to(self.root_path)),
                'error': str(e),
                'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
    
    def extract_class_info(self, node: ast.ClassDef) -> Dict:
        """Extract information from a class definition."""
        return {
            'name': node.name,
            'docstring': ast.get_docstring(node),
            'bases': [self.get_name(base) for base in node.bases],
            'methods': [self.extract_function_info(n) for n in node.body 
                       if isinstance(n, ast.FunctionDef)],
            'decorators': [self.get_name(d) for d in node.decorator_list]
        }
    
    def extract_function_info(self, node: ast.FunctionDef) -> Dict:
        """Extract information from a function definition."""
        args = []
        if node.args:
            for arg in node.args.args:
                arg_info = {'name': arg.arg}
                if arg.annotation:
                    arg_info['type'] = self.get_annotation(arg.annotation)
                args.append(arg_info)
        
        return {
            'name': node.name,
            'docstring': ast.get_docstring(node),
            'args': args,
            'returns': self.get_annotation(node.returns) if node.returns else None,
            'decorators': [self.get_name(d) for d in node.decorator_list],
            'is_async': isinstance(node, ast.AsyncFunctionDef)
        }
    
    def get_name(self, node) -> str:
        """Get name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self.get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self.get_name(node.func)
        return str(node)
    
    def get_annotation(self, node) -> str:
        """Get type annotation as string."""
        if node is None:
            return None
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Subscript):
            return f"{self.get_annotation(node.value)}[{self.get_annotation(node.slice)}]"
        elif isinstance(node, ast.Attribute):
            return f"{self.get_annotation(node.value)}.{node.attr}"
        return str(node)
    
    def scan_directory(self) -> None:
        """Scan directory and extract all module information."""
        print(f"🔍 Scanning {self.root_path}...")
        
        for py_file in self.root_path.rglob("*.py"):
            if self.should_ignore(py_file):
                continue
            
            print(f"  📄 Processing: {py_file.relative_to(self.root_path)}")
            module_info = self.extract_module_info(py_file)
            self.modules[str(py_file.relative_to(self.root_path))] = module_info
    
    def generate_markdown_overview(self) -> str:
        """Generate overview documentation in Markdown."""
        md = [f"# HypatiaX Project Documentation"]
        md.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        md.append("---\n")
        
        md.append("## 📊 Project Statistics\n")
        total_modules = len(self.modules)
        total_classes = sum(len(m.get('classes', [])) for m in self.modules.values())
        total_functions = sum(len(m.get('functions', [])) for m in self.modules.values())
        
        md.append(f"- **Total Modules**: {total_modules}")
        md.append(f"- **Total Classes**: {total_classes}")
        md.append(f"- **Total Functions**: {total_functions}\n")
        
        return "\n".join(md)
    
    def generate_module_doc(self, module_path: str, module_info: Dict) -> str:
        """Generate documentation for a single module."""
        md = [f"# Module: `{module_path}`\n"]
        
        if 'error' in module_info:
            md.append(f"⚠️ **Error parsing module**: {module_info['error']}\n")
            return "\n".join(md)
        
        # Module docstring
        if module_info.get('docstring'):
            md.append(f"## Description\n\n{module_info['docstring']}\n")
        
        # Metadata
        md.append(f"**Last Modified**: {module_info.get('last_modified', 'Unknown')}\n")
        
        # Imports
        if module_info.get('imports'):
            md.append("## Dependencies\n")
            for imp in sorted(set(module_info['imports'])):
                md.append(f"- `{imp}`")
            md.append("")
        
        # Constants
        if module_info.get('constants'):
            md.append("## Constants\n")
            for const in module_info['constants']:
                md.append(f"- `{const}`")
            md.append("")
        
        # Classes
        if module_info.get('classes'):
            md.append("## Classes\n")
            for cls in module_info['classes']:
                md.append(f"### `{cls['name']}`\n")
                
                if cls.get('bases'):
                    md.append(f"**Inherits from**: {', '.join(f'`{b}`' for b in cls['bases'])}\n")
                
                if cls.get('docstring'):
                    md.append(f"{cls['docstring']}\n")
                
                if cls.get('decorators'):
                    md.append(f"**Decorators**: {', '.join(f'`{d}`' for d in cls['decorators'])}\n")
                
                # Methods
                if cls.get('methods'):
                    md.append("**Methods**:\n")
                    for method in cls['methods']:
                        sig = self.format_function_signature(method)
                        md.append(f"- `{sig}`")
                        if method.get('docstring'):
                            # First line of docstring only
                            first_line = method['docstring'].split('\n')[0].strip()
                            md.append(f"  - {first_line}")
                    md.append("")
        
        # Functions
        if module_info.get('functions'):
            md.append("## Functions\n")
            for func in module_info['functions']:
                sig = self.format_function_signature(func)
                md.append(f"### `{sig}`\n")
                
                if func.get('docstring'):
                    md.append(f"{func['docstring']}\n")
                
                if func.get('decorators'):
                    md.append(f"**Decorators**: {', '.join(f'`{d}`' for d in func['decorators'])}\n")
        
        return "\n".join(md)
    
    def format_function_signature(self, func: Dict) -> str:
        """Format function signature."""
        args_str = ", ".join(
            f"{arg['name']}: {arg.get('type', 'Any')}" if 'type' in arg else arg['name']
            for arg in func.get('args', [])
        )
        
        returns = f" -> {func['returns']}" if func.get('returns') else ""
        async_prefix = "async " if func.get('is_async') else ""
        
        return f"{async_prefix}{func['name']}({args_str}){returns}"
    
    def generate_structure_tree(self) -> str:
        """Generate directory structure documentation."""
        md = ["# Project Structure\n"]
        md.append("```")
        
        # Group by directory
        dirs = {}
        for module_path in sorted(self.modules.keys()):
            parts = Path(module_path).parts
            current = dirs
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            if parts:
                current[parts[-1]] = None
        
        def print_tree(d, prefix="", is_last=True):
            items = sorted(d.items())
            for i, (name, subdir) in enumerate(items):
                is_last_item = i == len(items) - 1
                connector = "└── " if is_last_item else "├── "
                md.append(f"{prefix}{connector}{name}")
                
                if subdir is not None:
                    extension = "    " if is_last_item else "│   "
                    print_tree(subdir, prefix + extension, is_last_item)
        
        print_tree(dirs)
        md.append("```\n")
        
        return "\n".join(md)
    
    def generate_all_docs(self) -> None:
        """Generate all documentation files."""
        print("\n📝 Generating documentation...\n")
        
        # Overview
        overview = self.generate_markdown_overview()
        overview += "\n" + self.generate_structure_tree()
        
        overview_path = self.output_dir / "README.md"
        with open(overview_path, 'w', encoding='utf-8') as f:
            f.write(overview)
        print(f"✅ Generated: {overview_path}")
        
        # Individual module docs
        modules_dir = self.output_dir / "modules"
        modules_dir.mkdir(exist_ok=True)
        
        for module_path, module_info in self.modules.items():
            # Create directory structure
            doc_path = modules_dir / module_path.replace('.py', '.md')
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            
            doc_content = self.generate_module_doc(module_path, module_info)
            
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(doc_content)
        
        print(f"✅ Generated module docs in: {modules_dir}")
        
        # Save raw JSON data
        json_path = self.output_dir / "project_structure.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.modules, f, indent=2)
        print(f"✅ Generated JSON data: {json_path}")
        
        print(f"\n🎉 Documentation generation complete!")
        print(f"📁 Output directory: {self.output_dir.absolute()}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate documentation for HypatiaX project"
    )
    parser.add_argument(
        "--root",
        default="./hypatiax",
        help="Root directory of the project (default: ./hypatiax)"
    )
    parser.add_argument(
        "--output",
        default="./docs_generated",
        help="Output directory for documentation (default: ./docs_generated)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("HypatiaX Documentation Generator")
    print("=" * 60)
    
    generator = DocumentationGenerator(args.root, args.output)
    generator.scan_directory()
    generator.generate_all_docs()


if __name__ == "__main__":
    main()
