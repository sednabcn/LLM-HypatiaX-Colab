"""
Extract JSON data from baseline text output files
"""

import json
import re
from pathlib import Path


def find_json_file_reference(txt_content):
    """Find the JSON filename mentioned in the text output."""
    patterns = [
        r"Results saved to:?\s+(.+\.json)",
        r"saved to:?\s+(.+\.json)",
        r"💾 Results saved to:\s+(.+\.json)",
        r"✅ Results saved to:\s+(.+\.json)",
    ]

    for pattern in patterns:
        match = re.search(pattern, txt_content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def main():
    print("=" * 80)
    print("SEARCHING FOR JSON FILES IN HYPATIAX/DATA DIRECTORY")
    print("=" * 80)

    # Search in hypatiax/data/results directory
    data_results_dir = Path("results")

    if data_results_dir.exists():
        print(f"\n📁 Checking: {data_results_dir.absolute()}")
        json_files = list(data_results_dir.glob("*.json"))

        if json_files:
            print(f"\n✅ Found {len(json_files)} JSON files:")

            llm_files = []
            nn_files = []

            for f in sorted(json_files):
                size = f.stat().st_size
                print(f"  • {f.name} ({size:,} bytes)")

                # Categorize files
                if "llm" in f.name.lower() or "pure_llm" in f.name.lower():
                    llm_files.append(f)
                elif "nn" in f.name.lower() or "neural" in f.name.lower():
                    nn_files.append(f)

            print(f"\n📊 Categorized files:")
            print(f"  LLM files: {len(llm_files)}")
            for f in llm_files:
                print(f"    • {f.name}")

            print(f"\n  NN files: {len(nn_files)}")
            for f in nn_files:
                print(f"    • {f.name}")

            # Recommend which files to use
            print("\n" + "=" * 80)
            print("RECOMMENDATIONS")
            print("=" * 80)

            if llm_files and nn_files:
                # Find the most complete files
                llm_best = max(llm_files, key=lambda f: f.stat().st_size)
                nn_best = max(nn_files, key=lambda f: f.stat().st_size)

                print("\n🎯 Suggested files for ALL domains comparison:")
                print(f"\n  LLM: {llm_best.name}")

                # Check content
                try:
                    with open(llm_best) as f:
                        llm_data = json.load(f)
                        if isinstance(llm_data, list):
                            llm_domains = set(
                                item.get("domain", "unknown") for item in llm_data
                            )
                            print(f"       {len(llm_data)} test cases")
                            print(f"       Domains: {sorted(llm_domains)}")
                except:
                    print("       (Could not parse)")

                print(f"\n  NN:  {nn_best.name}")
                try:
                    with open(nn_best) as f:
                        nn_data = json.load(f)
                        if isinstance(nn_data, list):
                            nn_domains = set(
                                item.get("domain", "unknown") for item in nn_data
                            )
                            print(f"       {len(nn_data)} test cases")
                            print(f"       Domains: {sorted(nn_domains)}")
                except:
                    print("       (Could not parse)")

                # Copy to results directory for easy access
                print("\n" + "=" * 80)
                print("COPYING FILES TO RESULTS DIRECTORY")
                print("=" * 80)

                import shutil

                results_dir = Path(".")

                llm_dest = results_dir / "baseline_llm_ALL.json"
                nn_dest = results_dir / "baseline_nn_ALL.json"

                shutil.copy(llm_best, llm_dest)
                shutil.copy(nn_best, nn_dest)

                print(f"✅ Copied {llm_best.name} → {llm_dest.name}")
                print(f"✅ Copied {nn_best.name} → {nn_dest.name}")

                print("\n" + "=" * 80)
                print("READY TO COMPARE")
                print("=" * 80)
                print("\nRun comparison with:")
                print(
                    f"  python comparison_analysis_improved.py baseline_llm_ALL.json baseline_nn_ALL.json"
                )

            else:
                print("\n⚠️  Could not find both LLM and NN JSON files")
        else:
            print("\n❌ No JSON files found")
    else:
        print(f"\n❌ Directory not found: {data_results_dir.absolute()}")
        print("\nSearching in current directory...")
        json_files = list(Path(".").glob("*.json"))
        if json_files:
            print(f"✅ Found {len(json_files)} JSON files in current directory:")
            for f in json_files:
                print(f"  • {f.name}")


if __name__ == "__main__":
    main()
