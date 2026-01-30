#!/usr/bin/env python3
"""
HypatiaX Quick Start Guide Generator
=====================================
Generates a comprehensive quick start guide based on the actual project structure,
identifying entry points, example usage, and common workflows.
"""

import os
import ast
from pathlib import Path
from typing import List, Dict
import json


class QuickStartGenerator:
    """Generates quick start documentation and example scripts."""
    
    def __init__(self, root_path: str = "./hypatiax"):
        self.root_path = Path(root_path)
        self.entry_points = []
        self.examples = []
        self.test_files = []
        self.config_files = []
    
    def find_entry_points(self) -> None:
        """Find main entry points and CLI scripts."""
        print("🔍 Finding entry points...\n")
        
        # Look for files with if __name__ == "__main__"
        for py_file in self.root_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if '__main__' in content:
                        self.entry_points.append({
                            'path': str(py_file.relative_to(self.root_path)),
                            'type': 'script',
                            'docstring': self.extract_docstring(py_file)
                        })
            except Exception as e:
                continue
        
        # Look for setup.py entry points
        setup_py = self.root_path.parent / "setup.py"
        if setup_py.exists():
            try:
                with open(setup_py, 'r') as f:
                    content = f.read()
                    if 'entry_points' in content or 'console_scripts' in content:
                        self.entry_points.append({
                            'path': 'setup.py',
                            'type': 'package_entry',
                            'docstring': 'Package entry points defined in setup.py'
                        })
            except:
                pass
    
    def extract_docstring(self, file_path: Path) -> str:
        """Extract module docstring."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
                return ast.get_docstring(tree) or "No description available"
        except:
            return "No description available"
    
    def find_test_files(self) -> None:
        """Find test files to understand usage patterns."""
        print("🧪 Finding test files...\n")
        
        test_dirs = ['tests', 'test']
        for test_dir in test_dirs:
            test_path = self.root_path.parent / test_dir
            if test_path.exists():
                for test_file in test_path.rglob("test_*.py"):
                    self.test_files.append({
                        'path': str(test_file.relative_to(self.root_path.parent)),
                        'name': test_file.stem,
                        'docstring': self.extract_docstring(test_file)
                    })
    
    def find_examples(self) -> None:
        """Find example files."""
        print("📚 Finding examples...\n")
        
        for example_file in self.root_path.rglob("*example*.py"):
            self.examples.append({
                'path': str(example_file.relative_to(self.root_path)),
                'docstring': self.extract_docstring(example_file)
            })
    
    def analyze_core_components(self) -> Dict:
        """Analyze core components of the project."""
        components = {
            'ner': [],
            'training': [],
            'evaluation': [],
            'preprocessing': [],
            'deployment': []
        }
        
        # Map directory names to component types
        component_mapping = {
            'custom_ner': 'ner',
            'training': 'training',
            'evaluation': 'evaluation',
            'preprocessing': 'preprocessing',
            'deployment': 'deployment'
        }
        
        for py_file in self.root_path.rglob("*.py"):
            if '__init__.py' in py_file.name:
                continue
            
            rel_path = py_file.relative_to(self.root_path)
            for part in rel_path.parts:
                if part in component_mapping:
                    components[component_mapping[part]].append(str(rel_path))
                    break
        
        return components
    
    def generate_quick_start_md(self) -> str:
        """Generate Quick Start guide in Markdown."""
        md = []
        
        md.append("# HypatiaX Quick Start Guide")
        md.append("\n**Generated automatically from project structure**\n")
        md.append("---\n")
        
        # Installation
        md.append("## 🚀 Installation\n")
        md.append("```bash")
        md.append("# Clone the repository")
        md.append("git clone <repository-url>")
        md.append("cd LLM-HypatiaX")
        md.append("")
        md.append("# Create virtual environment")
        md.append("python -m venv venv")
        md.append("source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        md.append("")
        md.append("# Install package")
        md.append("pip install -e .")
        md.append("")
        md.append("# Download spaCy model")
        md.append("python -m spacy download en_core_web_sm")
        md.append("```\n")
        
        # Fix known issues
        md.append("## 🔧 Fix Known Issues\n")
        md.append("Before running, fix the rule file naming issue:")
        md.append("```bash")
        md.append("python rule_file_analyzer.py")
        md.append("./fix_rules.sh")
        md.append("```\n")
        
        # Core Components
        md.append("## 📦 Core Components\n")
        components = self.analyze_core_components()
        
        for comp_name, files in components.items():
            if files:
                md.append(f"### {comp_name.upper()}")
                md.append(f"Located in: `hypatiax/{comp_name}/`")
                md.append(f"Files: {len(files)}\n")
        
        # Entry Points
        if self.entry_points:
            md.append("## 🎯 Entry Points\n")
            for entry in self.entry_points:
                md.append(f"### `{entry['path']}`")
                md.append(f"{entry['docstring']}\n")
                if entry['type'] == 'script':
                    md.append("```bash")
                    md.append(f"python {entry['path']}")
                    md.append("```\n")
        
        # Testing
        if self.test_files:
            md.append("## 🧪 Running Tests\n")
            md.append("```bash")
            md.append("# Run all tests")
            md.append("pytest tests/")
            md.append("")
            md.append("# Run specific test")
            for test in self.test_files[:3]:  # Show first 3
                md.append(f"pytest {test['path']}")
            md.append("```\n")
        
        # Examples
        if self.examples:
            md.append("## 📚 Examples\n")
            for example in self.examples:
                md.append(f"- `{example['path']}`")
                if example['docstring']:
                    md.append(f"  {example['docstring'][:100]}...")
            md.append("")
        
        # Common Workflows
        md.append("## 🔄 Common Workflows\n")
        
        md.append("### 1. Training a New Model")
        md.append("```python")
        md.append("from hypatiax.core.training import training_spacy")
        md.append("")
        md.append("# Configure and train model")
        md.append("# See hypatiax/core/training/ for details")
        md.append("```\n")
        
        md.append("### 2. Using Custom NER")
        md.append("```python")
        md.append("from hypatiax.custom_ner.queries.tableau import custom_tableau_components")
        md.append("")
        md.append("# Load and use NER model")
        md.append("# See tests/ for usage examples")
        md.append("```\n")
        
        md.append("### 3. Evaluating Models")
        md.append("```python")
        md.append("from hypatiax.core.evaluation import testing_model")
        md.append("")
        md.append("# Evaluate model performance")
        md.append("```\n")
        
        # Troubleshooting
        md.append("## ⚠️ Troubleshooting\n")
        md.append("### Rule File Not Found Error")
        md.append("Run the fix script:")
        md.append("```bash")
        md.append("python rule_file_analyzer.py")
        md.append("./fix_rules.sh")
        md.append("```\n")
        
        md.append("### NLTK Not Found")
        md.append("```bash")
        md.append("pip install nltk")
        md.append("```\n")
        
        md.append("### Import Errors")
        md.append("Make sure you installed the package:")
        md.append("```bash")
        md.append("pip install -e .")
        md.append("```\n")
        
        # Resources
        md.append("## 📖 Additional Resources\n")
        md.append("- Full documentation: See `docs_generated/`")
        md.append("- API reference: See `docs_generated/modules/`")
        md.append("- Test examples: See `tests/`")
        md.append("- Training data: See `hypatiax/datasets/queries/tableau/`\n")
        
        # Architecture
        md.append("## 🏗️ Architecture Overview\n")
        md.append("```")
        md.append("hypatiax/")
        md.append("├── core/              # Core functionality")
        md.append("│   ├── training/      # Model training")
        md.append("│   ├── evaluation/    # Model evaluation")
        md.append("│   └── preprocessing/ # Data preprocessing")
        md.append("├── custom_ner/        # Custom NER components")
        md.append("│   └── queries/       # Query-specific NER")
        md.append("│       └── tableau/   # Tableau query NER")
        md.append("├── datasets/          # Training/test datasets")
        md.append("├── data_spacy/        # spaCy models and data")
        md.append("└── models/            # Trained models")
        md.append("```\n")
        
        return "\n".join(md)
    
    def generate_example_usage(self) -> str:
        """Generate example usage script."""
        script = []
        
        script.append("#!/usr/bin/env python3")
        script.append('"""')
        script.append("HypatiaX Example Usage")
        script.append("======================")
        script.append("Basic example showing how to use HypatiaX for NER on Tableau queries.")
        script.append('"""')
        script.append("")
        script.append("import spacy")
        script.append("from pathlib import Path")
        script.append("")
        script.append("def main():")
        script.append('    """Run basic NER example."""')
        script.append('    print("🚀 HypatiaX Example Usage\\n")')
        script.append("    ")
        script.append("    # Load base spaCy model")
        script.append('    print("Loading spaCy model...")')
        script.append("    nlp = spacy.load('en_core_web_sm')")
        script.append("    ")
        script.append("    # Example Tableau query")
        script.append('    query = "SELECT SUM(Sales) FROM Orders WHERE Region = \'West\'"')
        script.append("    ")
        script.append("    # Process with spaCy")
        script.append("    doc = nlp(query)")
        script.append("    ")
        script.append('    print(f"\\nQuery: {query}")')
        script.append('    print(f"\\nTokens:")')
        script.append("    for token in doc:")
        script.append('        print(f"  - {token.text:15} {token.pos_:10} {token.tag_:10}")')
        script.append("    ")
        script.append('    print("\\n✅ Example complete!")')
        script.append('    print("\\n💡 Next steps:")')
        script.append('    print("  1. Load custom Tableau NER model")')
        script.append('    print("  2. Try with your own Tableau queries")')
        script.append('    print("  3. Train custom models on your data")')
        script.append("")
        script.append("")
        script.append('if __name__ == "__main__":')
        script.append("    main()")
        
        return "\n".join(script)
    
    def run_full_generation(self) -> None:
        """Run complete quick start generation."""
        self.find_entry_points()
        self.find_test_files()
        self.find_examples()
        
        # Generate Quick Start
        quick_start = self.generate_quick_start_md()
        with open("QUICKSTART.md", 'w') as f:
            f.write(quick_start)
        print("✅ Generated: QUICKSTART.md\n")
        
        # Generate example script
        example_script = self.generate_example_usage()
        with open("example_usage.py", 'w') as f:
            f.write(example_script)
        os.chmod("example_usage.py", 0o755)
        print("✅ Generated: example_usage.py\n")
        
        # Generate metadata
        metadata = {
            'entry_points': self.entry_points,
            'test_files': self.test_files,
            'examples': self.examples,
            'components': self.analyze_core_components()
        }
        
        with open("project_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        print("✅ Generated: project_metadata.json\n")
        
        print("=" * 70)
        print("Quick Start generation complete!")
        print("=" * 70)
        print("\n📖 Read: QUICKSTART.md")
        print("🚀 Try: python example_usage.py")
        print("📊 View: project_metadata.json")


def main():
    print("=" * 70)
    print("HypatiaX Quick Start Guide Generator")
    print("=" * 70)
    print("")
    
    generator = QuickStartGenerator()
    generator.run_full_generation()


if __name__ == "__main__":
    main()
