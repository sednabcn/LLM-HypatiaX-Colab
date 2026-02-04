#!/usr/bin/env python3
"""
JMLR Submission Checklist Verifier
===================================
Verifies all components are ready for submission

Usage:
    python verify_submission_ready.py
"""

import re
from pathlib import Path
import subprocess

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def check_mark(passed):
    return f"{Colors.GREEN}✓{Colors.END}" if passed else f"{Colors.RED}✗{Colors.END}"

def warning_mark():
    return f"{Colors.YELLOW}⚠{Colors.END}"


class SubmissionChecker:
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = 0
        
    def check(self, name, passed, details=""):
        status = check_mark(passed)
        print(f"  {status} {name}")
        if details:
            print(f"      {details}")
        if passed:
            self.checks_passed += 1
        else:
            self.checks_failed += 1
            
    def warn(self, message):
        print(f"  {warning_mark()} {message}")
        self.warnings += 1
    
    def section(self, title):
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")


def check_figures():
    """Verify all figures exist and are high quality"""
    checker = SubmissionChecker()
    checker.section("📊 FIGURE VERIFICATION")
    
    figures = {
        'figure0_architecture': ['png', 'pdf'],
        'figure1_arrhenius_extrapolation': ['png', 'pdf'],
        'figure2_domain_comparison': ['png', 'pdf'],
        'figure3_validation_layers': ['png', 'pdf'],
        'figure4_r2_complexity': ['png', 'pdf'],
        'figure5_method_comparison': ['png', 'pdf'],
    }
    
    for fig_name, formats in figures.items():
        for fmt in formats:
            fig_path = Path(f'figures/{fig_name}.{fmt}')
            exists = fig_path.exists()
            
            if exists:
                size = fig_path.stat().st_size / 1024  # KB
                if size < 10:
                    checker.check(f'{fig_name}.{fmt}', False, 
                                f"File too small ({size:.1f} KB), likely corrupt")
                elif size > 5000:
                    checker.warn(f'{fig_name}.{fmt} is large ({size:.0f} KB)')
                    checker.check(f'{fig_name}.{fmt}', True, f"{size:.0f} KB")
                else:
                    checker.check(f'{fig_name}.{fmt}', True, f"{size:.0f} KB")
            else:
                checker.check(f'{fig_name}.{fmt}', False, "File not found")
    
    return checker


def check_latex():
    """Verify LaTeX file structure"""
    checker = SubmissionChecker()
    checker.section("📝 LATEX FILE VERIFICATION")
    
    tex_file = Path('jmlr_paper.tex')
    if not tex_file.exists():
        checker.check("jmlr_paper.tex exists", False)
        return checker
    
    with open(tex_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for placeholders
    cat_count = len(re.findall(r'figures/cat\.png', content))
    checker.check("No cat.png placeholders", cat_count == 0, 
                 f"Found {cat_count} cat.png references" if cat_count > 0 else "")
    
    # Check for TODOs
    todo_count = len(re.findall(r'\[TODO\]|\[CITE\]|TODO:|FIXME:', content, re.IGNORECASE))
    checker.check("No TODO/FIXME markers", todo_count == 0,
                 f"Found {todo_count} TODO markers" if todo_count > 0 else "")
    
    # Check key sections exist
    required_sections = [
        r'\\section{Introduction}',
        r'\\section{Related Work}',
        r'\\section.*{Methodology}|\\section.*{Methods}',
        r'\\section.*{Experiments}',
        r'\\section.*{Results}',
        r'\\section.*{Discussion}',
        r'\\section.*{Conclusion}',
    ]
    
    for section in required_sections:
        found = bool(re.search(section, content))
        section_name = section.replace(r'\\section', '').replace('{', '').replace('}', '').strip()
        checker.check(f"Section: {section_name}", found)
    
    # Check figure references
    fig_refs = re.findall(r'\\ref{fig:(\w+)}', content)
    checker.check("Figure references found", len(fig_refs) > 0, 
                 f"Found {len(fig_refs)} figure references")
    
    # Check bibliography
    has_bibliography = bool(re.search(r'\\bibliography{', content))
    checker.check("Bibliography included", has_bibliography)
    
    # Word count estimate
    text_content = re.sub(r'\\[a-zA-Z]+(\[.*?\])?{.*?}', '', content)
    text_content = re.sub(r'%.*', '', text_content)
    words = len(text_content.split())
    in_range = 6000 <= words <= 10000
    checker.check("Word count in range (6k-10k)", in_range, 
                 f"Approximately {words:,} words")
    
    return checker


def check_data_files():
    """Verify experimental data files exist"""
    checker = SubmissionChecker()
    checker.section("💾 DATA FILES VERIFICATION")
    
    key_dirs = [
        'comparison_llM_nn_generation',
        'comparison_llM_nn_generation/comparison_analysis_all_domains',
        'comparison_llM_nn_generation/json_reports',
    ]
    
    for dir_path in key_dirs:
        exists = Path(dir_path).exists()
        checker.check(f"Directory: {dir_path}", exists)
    
    # Check for JSON files
    json_files = list(Path('comparison_llM_nn_generation').rglob('*.json'))
    checker.check("Experimental JSON files found", len(json_files) > 0,
                 f"Found {len(json_files)} JSON files")
    
    return checker


def check_compilation():
    """Try to compile LaTeX"""
    checker = SubmissionChecker()
    checker.section("🔧 LATEX COMPILATION CHECK")
    
    try:
        result = subprocess.run(['pdflatex', '--version'], 
                              capture_output=True, text=True, timeout=5)
        has_pdflatex = result.returncode == 0
        checker.check("pdflatex installed", has_pdflatex)
    except:
        checker.check("pdflatex installed", False, "Cannot find pdflatex")
        return checker
    
    # Try compilation (dry run)
    print("\n  Attempting to compile (may take 30 seconds)...")
    try:
        result = subprocess.run(['pdflatex', '-interaction=nonstopmode', 'jmlr_paper.tex'],
                              capture_output=True, text=True, timeout=60)
        
        if 'Error' in result.stdout or result.returncode != 0:
            checker.check("LaTeX compiles without errors", False,
                         "Check jmlr_paper.log for details")
        else:
            checker.check("LaTeX compiles without errors", True)
            
            # Check if PDF was created
            pdf_exists = Path('jmlr_paper.pdf').exists()
            if pdf_exists:
                size_mb = Path('jmlr_paper.pdf').stat().st_size / (1024*1024)
                checker.check("PDF generated", True, f"{size_mb:.1f} MB")
                
                if size_mb > 10:
                    checker.warn(f"PDF is large ({size_mb:.1f} MB), consider compressing")
            else:
                checker.check("PDF generated", False)
                
    except subprocess.TimeoutExpired:
        checker.check("LaTeX compiles without errors", False, "Compilation timed out")
    except Exception as e:
        checker.check("LaTeX compiles without errors", False, str(e))
    
    return checker


def check_submission_package():
    """Verify submission package components"""
    checker = SubmissionChecker()
    checker.section("📦 SUBMISSION PACKAGE")
    
    required_files = {
        'jmlr_paper.tex': 'Main LaTeX file',
        'bibliography.bib': 'References (or embedded in .tex)',
        'figures/': 'Figures directory',
        'README.md': 'Repository README',
    }
    
    for file, description in required_files.items():
        exists = Path(file).exists()
        checker.check(f"{file}", exists, description)
    
    # Check for supplementary materials
    supp_files = [
        'comparison_llM_nn_generation/',
        'experiments/',
    ]
    
    has_supp = any(Path(f).exists() for f in supp_files)
    if has_supp:
        checker.check("Supplementary materials available", True)
    else:
        checker.warn("No supplementary materials found")
    
    return checker


def final_summary(all_checkers):
    """Print final summary"""
    total_passed = sum(c.checks_passed for c in all_checkers)
    total_failed = sum(c.checks_failed for c in all_checkers)
    total_warnings = sum(c.warnings for c in all_checkers)
    
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}FINAL SUMMARY{Colors.END}")
    print(f"{'='*60}")
    print(f"\n  ✓ Checks passed:  {Colors.GREEN}{total_passed}{Colors.END}")
    print(f"  ✗ Checks failed:  {Colors.RED}{total_failed}{Colors.END}")
    print(f"  ⚠ Warnings:       {Colors.YELLOW}{total_warnings}{Colors.END}")
    
    if total_failed == 0:
        print(f"\n  {Colors.GREEN}{Colors.BOLD}✅ READY FOR SUBMISSION!{Colors.END}")
        print(f"\n  Next steps:")
        print(f"    1. Review generated PDF one final time")
        print(f"    2. Prepare cover letter")
        print(f"    3. Submit to JMLR: http://jmlr.org/author-info.html")
        print(f"    4. Celebrate! 🎉")
    else:
        print(f"\n  {Colors.RED}{Colors.BOLD}⚠️  NOT READY - Fix failed checks first{Colors.END}")
        print(f"\n  Priority fixes:")
        if total_failed > 0:
            print(f"    • Address all {total_failed} failed checks above")
        print(f"    • Run generate_all_figures.py if figures are missing")
        print(f"    • Run update_latex_figures.py to fix cat.png placeholders")
        print(f"    • Fix any LaTeX compilation errors")
    
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔" + "═"*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "   JMLR SUBMISSION READINESS VERIFICATION   ".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "═"*58 + "╝")
    print(f"{Colors.END}\n")
    
    checkers = [
        check_figures(),
        check_latex(),
        check_data_files(),
        check_compilation(),
        check_submission_package(),
    ]
    
    final_summary(checkers)
