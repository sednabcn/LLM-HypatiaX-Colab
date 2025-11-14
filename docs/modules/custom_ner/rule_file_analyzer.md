# Module: `custom_ner/rule_file_analyzer.py`

## Description

HypatiaX Rule File Analyzer
============================
Analyzes the rule file versioning system and identifies the disconnect
between expected and actual rule file naming conventions.

This script helps solve the BLOCKER identified in the morning assessment.

**Last Modified**: 2025-11-04T16:01:31.033739

## Dependencies

- `json`
- `os`
- `pathlib`
- `shutil`
- `typing`

## Classes

### `RuleFileAnalyzer`

Analyzes and documents rule file structure.

**Methods**:

- `__init__(self, root_path: str)`
- `scan_rule_files(self) -> <ast.Constant object at 0x7fa6f8880f10>`
  - Scan for all rule-related files.
- `analyze_code_expectations(self) -> <ast.Constant object at 0x7fa6f8882450>`
  - Analyze what the code expects.
- `identify_gaps(self) -> <ast.Constant object at 0x7fa6f8880850>`
  - Identify what's missing.
- `generate_report(self) -> str`
  - Generate analysis report.
- `suggest_fix(self) -> Dict`
  - Suggest fix options.
- `generate_fix_script(self, fixes: Dict, output_path: str) -> <ast.Constant object at 0x7fa6f888ed90>`
  - Generate shell script to fix the issue.
- `run_full_analysis(self) -> <ast.Constant object at 0x7fa6f88d8e90>`
  - Run complete analysis.
