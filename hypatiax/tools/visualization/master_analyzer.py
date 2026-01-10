#!/usr/bin/env python3
"""
HypatiaX Master Analysis Orchestrator v2.0
Domain-aware orchestration of all visualization scripts
Place in: hypatiax/tools/visualization/master_analyzer.py
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class MasterAnalyzer:
    """Orchestrates all HypatiaX analysis scripts with domain awareness."""

    DOMAINS = ["all_domains", "defi", "lending", "trading", "physics"]

    def __init__(self, results_dir: str = "hypatiax/data/results"):
        self.results_dir = Path(results_dir)
        self.comparison_dir = self.results_dir / "comparison_results"
        self.analysis_dir = self.results_dir / "analysis_outputs"

        for domain in self.DOMAINS:
            (self.comparison_dir / domain).mkdir(parents=True, exist_ok=True)
            (self.analysis_dir / domain).mkdir(parents=True, exist_ok=True)

        self.modules = {
            "tables": {
                "script": "generate_tables.py",
                "name": "Publication Tables",
                "outputs": ["CSV", "Markdown", "LaTeX"],
                "priority": 1,
                "domain_aware": True,
            },
            "figures": {
                "script": "generate_figures.py",
                "name": "Publication Figures",
                "outputs": ["PNG (6 figures)"],
                "priority": 2,
                "domain_aware": True,
            },
            "hybrid_viz": {
                "script": "hypatiax_hybrid_system_visualization.py",
                "name": "Hybrid System Comparison",
                "outputs": ["Statistical plots", "JSON reports"],
                "priority": 3,
                "domain_aware": True,
            },
            "defi_viz": {
                "script": "hypatiax_visualizer.py",
                "name": "DeFi Visualizations",
                "outputs": ["DeFi-specific plots"],
                "priority": 4,
                "domain_aware": False,
            },
        }

        print(f"📊 Master Analyzer initialized")
        print(f"   Results dir: {self.results_dir}")
        print(f"   Domains: {', '.join(self.DOMAINS)}")

    def detect_latest_results(self, domain: str = "all_domains") -> Dict[str, Path]:
        """Detect latest result files for a specific domain."""
        domain_dir = self.comparison_dir / domain

        if not domain_dir.exists():
            print(f"⚠️  Domain directory not found: {domain_dir}")
            return {}

        result_files = {}
        latest_link = domain_dir / "comparison_results_latest.json"

        if latest_link.exists():
            result_files["latest"] = latest_link
            print(f"   ✅ {domain}: Found latest link")
        else:
            files = sorted(domain_dir.glob("comparison_results_*.json"))
            if files:
                result_files["latest"] = files[-1]
                print(f"   ✅ {domain}: {files[-1].name}")
            else:
                print(f"   ⊘ {domain}: No results found")

        return result_files

    def get_all_domains_with_results(self) -> List[str]:
        """Get list of all domains that have result files."""
        domains_with_results = []
        for domain in self.DOMAINS:
            results = self.detect_latest_results(domain)
            if results:
                domains_with_results.append(domain)
        return domains_with_results

    def run_module(
        self,
        module_name: str,
        domain: str = "all_domains",
        input_file: Optional[Path] = None,
        verbose: bool = False,
    ) -> Dict:
        """Run a single analysis module for a specific domain."""
        module = self.modules.get(module_name)
        if not module:
            return {"success": False, "error": f"Unknown module: {module_name}"}

        if not module["domain_aware"] and domain != "defi":
            return {
                "success": False,
                "error": f"{module['name']} only supports 'defi' domain",
                "skipped": True,
            }

        viz_dir = Path(__file__).parent
        script_path = viz_dir / module["script"]

        if not script_path.exists():
            alt_paths = [
                Path("hypatiax/tools/visualization") / module["script"],
                Path("hypatiax/scripts") / module["script"],
                Path(module["script"]),
            ]
            script_path = next((p for p in alt_paths if p.exists()), None)

            if not script_path:
                return {
                    "success": False,
                    "error": f"Script not found: {module['script']}",
                }

        print(f"\n▶️  Running: {module['name']} ({domain})")
        print(f"   Script: {script_path}")

        cmd = [sys.executable, str(script_path)]
        output_dir = (
            self.analysis_dir / domain / datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        output_dir.mkdir(parents=True, exist_ok=True)

        if module_name == "tables":
            cmd.extend(["--domain", domain, "--output-dir", str(output_dir)])
        elif module_name == "figures":
            cmd.extend(["--domain", domain, "--output-dir", str(output_dir)])
        elif module_name == "hybrid_viz":
            if input_file:
                cmd.extend(["--input", str(input_file)])
            cmd.extend(["--output-dir", str(output_dir), "--domain", domain, "--all"])
        elif module_name == "defi_viz":
            cmd.extend(["--output-dir", str(output_dir)])

        if verbose:
            cmd.append("--verbose")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                print(f"   ✅ Success")
                return {
                    "success": True,
                    "domain": domain,
                    "output_dir": str(output_dir),
                    "stdout": result.stdout[-500:]
                    if len(result.stdout) > 500
                    else result.stdout,
                    "outputs": module["outputs"],
                }
            else:
                print(f"   ❌ Failed (exit code {result.returncode})")
                if verbose:
                    print(f"   Error: {result.stderr[-500:]}")
                return {
                    "success": False,
                    "domain": domain,
                    "error": result.stderr[-500:],
                    "exit_code": result.returncode,
                }

        except subprocess.TimeoutExpired:
            print(f"   ⏱️  Timeout (>5 min)")
            return {"success": False, "domain": domain, "error": "Timeout"}
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            return {"success": False, "domain": domain, "error": str(e)}

    def generate_master_report(self, results: Dict) -> Dict:
        """Generate comprehensive master report with domain breakdown."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "modules_executed": len(results),
            "by_domain": {},
            "summary": {
                "total_executions": 0,
                "successful": 0,
                "failed": 0,
                "skipped": 0,
            },
        }

        for key, result in results.items():
            module_name, domain = key

            if domain not in report["by_domain"]:
                report["by_domain"][domain] = {
                    "modules": {},
                    "successful": 0,
                    "failed": 0,
                }

            module_info = self.modules[module_name]
            report["by_domain"][domain]["modules"][module_name] = {
                "name": module_info["name"],
                "success": result["success"],
                "outputs": module_info["outputs"] if result["success"] else [],
                "error": result.get("error") if not result["success"] else None,
                "output_dir": result.get("output_dir"),
            }

            report["summary"]["total_executions"] += 1
            if result.get("skipped"):
                report["summary"]["skipped"] += 1
            elif result["success"]:
                report["summary"]["successful"] += 1
                report["by_domain"][domain]["successful"] += 1
            else:
                report["summary"]["failed"] += 1
                report["by_domain"][domain]["failed"] += 1

        return report

    def save_report(self, report: Dict):
        """Save master report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = (
            self.analysis_dir / "all_domains" / f"master_report_{timestamp}.json"
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Master report saved: {report_path}")

    def print_summary(self, report: Dict):
        """Print execution summary."""
        print("\n" + "=" * 80)
        print("MASTER ANALYSIS SUMMARY".center(80))
        print("=" * 80)

        print(f"\n📊 Overall:")
        print(f"   Total executions: {report['summary']['total_executions']}")
        print(f"   Successful:       {report['summary']['successful']}")
        print(f"   Failed:           {report['summary']['failed']}")
        print(f"   Skipped:          {report['summary']['skipped']}")

        print(f"\n📋 Results by Domain:")
        for domain, data in report["by_domain"].items():
            print(f"\n   {domain.upper()}:")
            for module_name, details in data["modules"].items():
                status = "✅" if details["success"] else "❌"
                print(f"      {status} {details['name']}")
                if details["success"] and details.get("output_dir"):
                    print(f"         Output: {details['output_dir']}")
                elif not details["success"] and details.get("error"):
                    print(f"         Error: {details['error'][:80]}")

        print(f"\n📁 Output directory: {self.analysis_dir}")
        print("=" * 80)

    def run_full_analysis(
        self,
        modules: Optional[List[str]] = None,
        domains: Optional[List[str]] = None,
        verbose: bool = False,
    ):
        """Run complete analysis pipeline across specified domains."""
        print("=" * 80)
        print("HYPATIAX MASTER ANALYSIS ORCHESTRATOR".center(80))
        print("=" * 80)

        available_domains = self.get_all_domains_with_results()

        if not available_domains:
            print("\n⚠️  No results found in any domain!")
            print(f"   Expected location: {self.comparison_dir}")
            return None

        print(f"\n📊 Available domains: {', '.join(available_domains)}")

        if domains is None:
            domains = available_domains
        else:
            domains = [d for d in domains if d in available_domains]

        if not domains:
            print("\n⚠️  No valid domains specified!")
            return None

        if modules is None:
            modules = list(self.modules.keys())

        print(f"\n📋 Modules to execute: {', '.join(modules)}")
        print(f"📋 Domains to analyze: {', '.join(domains)}")

        results = {}

        for domain in domains:
            print(f"\n{'=' * 80}")
            print(f"ANALYZING DOMAIN: {domain.upper()}".center(80))
            print(f"{'=' * 80}")

            domain_results = self.detect_latest_results(domain)
            input_file = domain_results.get("latest")

            for module_name in modules:
                result = self.run_module(
                    module_name, domain=domain, input_file=input_file, verbose=verbose
                )
                results[(module_name, domain)] = result

        report = self.generate_master_report(results)
        self.save_report(report)
        self.print_summary(report)

        return report


def main():
    parser = argparse.ArgumentParser(
        description="HypatiaX Master Analysis Orchestrator (Domain-Aware)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python master_analyzer.py --all
  python master_analyzer.py --all --domains defi
  python master_analyzer.py --modules tables figures
  python master_analyzer.py --list
        """,
    )

    parser.add_argument("--all", action="store_true", help="Run all analysis modules")
    parser.add_argument(
        "--modules", nargs="+", choices=["tables", "figures", "hybrid_viz", "defi_viz"]
    )
    parser.add_argument("--domains", nargs="+", choices=MasterAnalyzer.DOMAINS)
    parser.add_argument("--results-dir", type=str, default="hypatiax/data/results")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--list", action="store_true")

    args = parser.parse_args()

    if args.list:
        print("\n📋 Available Analysis Modules:")
        print("=" * 60)
        analyzer = MasterAnalyzer()
        for name, module in sorted(
            analyzer.modules.items(), key=lambda x: x[1]["priority"]
        ):
            domain_text = "all domains" if module["domain_aware"] else "defi only"
            print(f"\n{name} ({domain_text}):")
            print(f"   Name:    {module['name']}")
            print(f"   Script:  {module['script']}")

        print(f"\n📊 Available Domains:")
        print("=" * 60)
        for domain in MasterAnalyzer.DOMAINS:
            print(f"   • {domain}")
        print("=" * 60)
        return

    if not args.all and not args.modules:
        parser.error("Must specify --all or --modules")

    analyzer = MasterAnalyzer(results_dir=args.results_dir)
    modules = None if args.all else args.modules

    try:
        report = analyzer.run_full_analysis(
            modules=modules, domains=args.domains, verbose=args.verbose
        )
        sys.exit(0 if report and report["summary"]["failed"] == 0 else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
