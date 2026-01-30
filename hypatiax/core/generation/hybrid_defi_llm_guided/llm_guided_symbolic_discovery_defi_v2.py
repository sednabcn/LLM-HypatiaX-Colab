#!/usr/bin/env python3
"""
LLM-GUIDED SYMBOLIC DISCOVERY FOR DEFI v1.1 - FIXED
====================================================
Fixed version with:
- Corrected data generator (no eval of ground_truth)
- Clean unified imports from hybrid_system v4.0
- Proper variable name handling

Author: HypatiaX Team
Version: 1.1
Date: 2026-01-14
"""

import argparse
import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from dotenv import load_dotenv

# ============================================================================
# SETUP & PATHS
# ============================================================================

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

RESULTS_DIR = Path("hypatiax/data/results/llm_guided_defi")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# IMPORTS - UNIFIED
# ============================================================================

try:
    from hypatiax.tools.symbolic.symbolic_engine import DiscoveryConfig
    from hypatiax.tools.symbolic.hybrid_system import (
        HybridDiscoverySystem,
        DiscoveryMode,
    )
    HAS_HYBRID_SYSTEM = True
    print("✅ Using unified HybridDiscoverySystem v4.0")
except ImportError:
    HAS_HYBRID_SYSTEM = False
    print("❌ HybridDiscoverySystem not available")
    sys.exit(1)

try:
    from hypatiax.tools.symbolic.symbolic_engine import (
        LLMConfig,
        SymbolicEngineWithLLM,
    )
    HAS_LLM_ENGINE = True
    print("✅ LLM-guided discovery available")
except ImportError:
    HAS_LLM_ENGINE = False
    print("⚠️  LLM-guided discovery not available (will use standard PySR)")

# Import DeFi Protocol
try:
    from experiment_protocol_defi_20 import DeFiExperimentProtocolExtended
    print("✅ Loaded DeFi Protocol v3.0")
except ImportError:
    print("❌ Error: experiment_protocol_defi_20.py not found")
    sys.exit(1)

# ============================================================================
# JSON SERIALIZATION
# ============================================================================

def convert_to_json_serializable(obj):
    """Convert numpy types to JSON-serializable Python types."""
    if obj is None:
        return None
    if isinstance(obj, (bool, np.bool_)):
        return bool(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [convert_to_json_serializable(v) for v in obj]
    if hasattr(obj, "__dict__"):
        return convert_to_json_serializable(obj.__dict__)
    return obj

# ============================================================================
# DEFI PROTOCOL TO TEST CASES CONVERTER - FIXED
# ============================================================================

def convert_defi_protocol_to_test_cases(
    protocol: DeFiExperimentProtocolExtended,
    domains: Optional[List[str]] = None
) -> Dict[str, Dict]:
    """Convert DeFi protocol to test cases dictionary."""
    
    test_cases = {}
    all_domains = protocol.get_all_domains()
    domains_to_load = domains if domains else all_domains
    
    print(f"\n📥 Converting DeFi Protocol to test cases...")
    print(f"   Domains: {', '.join(domains_to_load)}")
    
    for domain in domains_to_load:
        if domain not in all_domains:
            print(f"⚠️  Domain '{domain}' not found, skipping...")
            continue
        
        protocol_tests = protocol.load_test_data(domain, num_samples=100)
        
        for desc, X_sample, y_sample, var_names, metadata in protocol_tests:
            eq_name = metadata.get('equation_name', 'unknown')
            test_name = f"{domain}_{eq_name}"
            
            # FIXED: Create data generator that returns pre-computed y values
            def make_generator(prot, dom, eq):
                def generator(n):
                    tests = prot.load_test_data(dom, num_samples=n)
                    for d, X, y, v, m in tests:
                        if m.get('equation_name') == eq:
                            # Protocol already computed y correctly
                            # Just return it wrapped in a function
                            y_copy = y.copy()
                            
                            def y_func(X_input):
                                return y_copy
                            
                            return X, y_func
                    raise ValueError(f"Test {eq} not found in domain {dom}")
                return generator
            
            # Extract metadata
            var_descriptions = {var: f"{var} in {desc}" for var in var_names}
            units = metadata.get('units', {var: "dimensionless" for var in var_names})
            
            test_cases[test_name] = {
                "domain": domain,
                "equation_name": eq_name,
                "name": metadata.get('equation_name', desc).replace("_", " ").title(),
                "description": desc,
                "ground_truth": metadata.get('ground_truth', ''),
                "variables": var_names,
                "variable_descriptions": var_descriptions,
                "variable_units": units,
                "variable_roles": metadata.get('variable_roles', {}),
                "generate_data": make_generator(protocol, domain, eq_name),
                "use_enhanced_config": metadata.get('use_enhanced_config', False),
                "extrapolation_test": metadata.get('extrapolation_test', False),
                "difficulty": metadata.get('difficulty', 'medium'),
                "metadata": metadata,
            }
    
    print(f"✅ Converted {len(test_cases)} test cases from protocol")
    
    # Show extrapolation tests
    extrap_tests = [name for name, tc in test_cases.items() if tc.get('extrapolation_test')]
    if extrap_tests:
        print(f"\n🚀 Extrapolation tests ({len(extrap_tests)}):")
        for name in extrap_tests:
            print(f"   - {name}")
    
    return test_cases

# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

class SessionManager:
    """Manages test sessions with checkpointing."""
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"llm_defi_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_dir = RESULTS_DIR / self.session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_file = self.session_dir / "checkpoint.json"
        self.completed_tests = set()
        self.failed_tests = set()
        self._load_checkpoint()
    
    def _load_checkpoint(self):
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, "r") as f:
                    data = json.load(f)
                    self.completed_tests = set(data.get("completed", []))
                    self.failed_tests = set(data.get("failed", []))
                    print(f"\n📂 Checkpoint: {len(self.completed_tests)} completed, {len(self.failed_tests)} failed")
            except Exception as e:
                print(f"⚠️  Failed to load checkpoint: {e}")
    
    def _save_checkpoint(self):
        try:
            with open(self.checkpoint_file, "w") as f:
                json.dump({
                    "session_id": self.session_id,
                    "timestamp": datetime.now().isoformat(),
                    "completed": list(self.completed_tests),
                    "failed": list(self.failed_tests),
                }, f, indent=2)
        except Exception as e:
            print(f"⚠️  Failed to save checkpoint: {e}")
    
    def is_completed(self, test_name: str) -> bool:
        return test_name in self.completed_tests
    
    def save_test_result(self, test_name: str, result: Dict, passed: bool):
        """Save test result with proper JSON serialization."""
        test_file = self.session_dir / f"{test_name}.json"
        
        result["_metadata"] = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "passed": bool(passed),
            "test_name": test_name,
            "method": "llm_guided_defi_v1.1",
        }
        
        clean_result = convert_to_json_serializable(result)
        
        try:
            with open(test_file, "w") as f:
                json.dump(clean_result, f, indent=2, default=str)
            
            if passed:
                self.completed_tests.add(test_name)
            else:
                self.failed_tests.add(test_name)
            self._save_checkpoint()
            print(f"   💾 Saved: {test_file.name}")
            
        except Exception as e:
            print(f"   ❌ Failed to save {test_file.name}: {e}")
            if passed:
                self.completed_tests.add(test_name)
            else:
                self.failed_tests.add(test_name)
            self._save_checkpoint()
    
    def load_all_results(self) -> Dict[str, Dict]:
        results = {}
        for f in self.session_dir.glob("*.json"):
            if f.name not in ["checkpoint.json", "summary.json", "complete_results.json"]:
                try:
                    with open(f, "r") as file:
                        results[f.stem] = json.load(file)
                except Exception as e:
                    print(f"⚠️  Failed to load {f.name}: {e}")
        return results
    
    def get_pending_tests(self, all_tests: List[str]) -> List[str]:
        return [t for t in all_tests if t not in self.completed_tests]
    
    def save_summary(self, summary: Dict):
        """Save summary with complete JSON export."""
        summary_file = self.session_dir / "summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"\n📊 Summary saved: {summary_file}")
        
        complete_export = self._generate_complete_export(summary)
        complete_file = self.session_dir / "complete_results.json"
        with open(complete_file, 'w') as f:
            json.dump(complete_export, f, indent=2, default=str)
        print(f"📦 Complete results: {complete_file}")
        print(f"   Size: {complete_file.stat().st_size / 1024:.1f} KB")
    
    def _generate_complete_export(self, summary: Dict) -> Dict:
        """Generate complete JSON export."""
        all_results = self.load_all_results()
        
        export = {
            'session_metadata': {
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat(),
                'configuration': summary.get('configuration', {}),
                'total_tests': summary.get('total_tests', 0),
                'passed': summary.get('passed', 0),
                'failed': summary.get('failed', 0),
                'pass_rate': (summary.get('passed', 0) / max(summary.get('total_tests', 1), 1)) * 100,
            },
            'summary_statistics': {
                'by_domain': dict(summary.get('by_domain', {})),
                'by_difficulty': dict(summary.get('by_difficulty', {})),
                'extrapolation_tests': summary.get('extrapolation_results', []),
                'detailed_results_table': summary.get('detailed_results', [])
            },
            'individual_test_results': {}
        }
        
        for test_name, result in all_results.items():
            test_export = {
                'metadata': {
                    'test_name': test_name,
                    'domain': result.get('domain', 'unknown'),
                    'difficulty': result.get('difficulty', 'unknown'),
                    'ground_truth': result.get('ground_truth', 'N/A'),
                    'extrapolation_test': result.get('extrapolation_test', False),
                },
                'discovery': result.get('discovery', {}),
                'validation': result.get('validation', {}),
                'variables': {
                    'names': result.get('test_config', {}).get('variables', []),
                },
                'error': result.get('error'),
            }
            
            export['individual_test_results'][test_name] = test_export
        
        return export

# ============================================================================
# TEST EXECUTION
# ============================================================================

def run_single_test(
    test_name: str,
    test_cases: Dict,
    llm_mode: str = "hybrid",
    api_key: Optional[str] = None,
    niterations: int = 50,
    verbose: bool = True,
    session: Optional[SessionManager] = None,
) -> Dict:
    """Run single test with hybrid discovery system."""
    
    test_config = test_cases[test_name]
    
    if verbose:
        print(f"\n{'='*80}")
        print(f"Running: {test_config['name']} | Domain: {test_config['domain']}")
        print(f"{'='*80}")
        print(f"Difficulty: {test_config.get('difficulty', 'unknown')}")
        if test_config.get('extrapolation_test'):
            print(f"🚀 EXTRAPOLATION TEST")
    
    start = time.time()
    
    try:
        # Generate data
        X, y_func = test_config["generate_data"](1000)
        y = y_func(X)
        
        # Create discovery config
        discovery_config = DiscoveryConfig(
            niterations=niterations,
            enable_auto_configuration=True,
        )
        
        # Create LLM config if using LLM mode
        llm_config = None
        if HAS_LLM_ENGINE and llm_mode != "none":
            llm_config = LLMConfig(
                enabled=True,
                api_key=api_key,
                n_candidates=5,
                model="claude-sonnet-4-20250514"
            )
        
        # Create hybrid system
        system = HybridDiscoverySystem(
            domain=test_config["domain"],
            discovery_config=discovery_config,
            discovery_mode=DiscoveryMode.CALIBRATED,
            max_retries=3,
            enable_physics_fallback=False,
        )
        
        # If LLM mode requested and available, patch with LLM engine
        if HAS_LLM_ENGINE and llm_config:
            print(f"   🔧 Using LLM-guided discovery ({llm_mode})")
            symbolic_engine_llm = SymbolicEngineWithLLM(
                config=discovery_config,
                domain=test_config["domain"],
                llm_config=llm_config,
                llm_mode=llm_mode
            )
            system.symbolic_engine = symbolic_engine_llm
        
        # Run discovery
        result = system.discover_validate_interpret(
            X=X, y=y,
            variable_names=test_config["variables"],
            variable_descriptions=test_config.get("variable_descriptions", {}),
            variable_units=test_config.get("variable_units", {}),
            description=test_config.get("name", test_name),
            equation_name=test_config.get("equation_name"),
        )
        
        # Extract results
        discovery = result.get('discovery', {})
        validation = result.get('validation', {})
        
        r2 = discovery.get('r2_score', 0.0)
        val_score = validation.get('total_score', 0.0)
        
        # Determine success
        success = (r2 > 0.99 and val_score > 30.0) or (r2 > 0.95 and val_score > 80.0)
        
        result.update({
            "success": success,
            "test_name": test_name,
            "ground_truth": test_config.get("ground_truth", ""),
            "difficulty": test_config.get("difficulty", "unknown"),
            "extrapolation_test": test_config.get("extrapolation_test", False),
            "test_config": test_config,
            "timing": {"total": time.time() - start},
            "r2_score": r2,
            "validation_score": val_score,
        })
        
        if session:
            session.save_test_result(test_name, result, success)
        
        return result
        
    except Exception as e:
        error_result = {
            "error": str(e),
            "test_name": test_name,
            "timing": {"total": time.time() - start},
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "difficulty": test_config.get("difficulty", "unknown"),
            "extrapolation_test": test_config.get("extrapolation_test", False),
        }
        if session:
            session.save_test_result(test_name, error_result, False)
        if verbose:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        return error_result

def run_defi_suite(
    test_cases: Dict,
    llm_mode: str = "hybrid",
    api_key: Optional[str] = None,
    niterations: int = 50,
    resume: bool = False,
    session_id: Optional[str] = None,
) -> Dict[str, Dict]:
    """Run full DeFi suite."""
    
    # Session management
    if resume and Path(RESULTS_DIR / "current_session.json").exists():
        with open(RESULTS_DIR / "current_session.json", "r") as f:
            session_id = json.load(f).get("session_id")
    
    session = SessionManager(session_id)
    with open(RESULTS_DIR / "current_session.json", "w") as f:
        json.dump({"session_id": session.session_id}, f)
    
    print(f"\n{'='*80}")
    print(f"LLM-GUIDED DISCOVERY - DEFI SUITE v1.1")
    print(f"{'='*80}")
    print(f"Tests: {len(test_cases)}")
    print(f"Mode: {llm_mode}")
    print(f"Iterations: {niterations}")
    
    pending = session.get_pending_tests(list(test_cases.keys())) if resume else list(test_cases.keys())
    
    if not pending:
        print("✅ All tests completed!")
        results = session.load_all_results()
        return results
    
    print(f"Running: {len(pending)}/{len(test_cases)} tests")
    
    for i, test_name in enumerate(pending, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(pending)}: {test_name}")
        print(f"{'='*80}")
        
        try:
            run_single_test(
                test_name, test_cases, llm_mode, api_key,
                niterations, verbose=True, session=session
            )
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted! Progress saved. Use --resume")
            break
        except Exception as e:
            print(f"❌ Test failed: {e}")
            continue
    
    results = session.load_all_results()
    
    # Generate and save summary
    summary = generate_summary(results, test_cases, llm_mode, niterations)
    session.save_summary(summary)
    
    print_results_table(results, test_cases)
    return results

# ============================================================================
# SUMMARY GENERATION
# ============================================================================

def generate_summary(results: Dict[str, Dict], test_cases: Dict, 
                    llm_mode: str, niterations: int) -> Dict:
    """Generate comprehensive summary."""
    
    summary = {
        'total_tests': len(results),
        'passed': 0,
        'failed': 0,
        'by_domain': defaultdict(lambda: {'passed': 0, 'failed': 0}),
        'by_difficulty': defaultdict(lambda: {'passed': 0, 'failed': 0}),
        'extrapolation_results': [],
        'detailed_results': [],
        'configuration': {
            'mode': llm_mode,
            'iterations': niterations,
        },
        'total_time': 0.0
    }
    
    for test_name, result in results.items():
        metadata = result.get('_metadata', {})
        passed = metadata.get('passed', False)
        
        if passed:
            summary['passed'] += 1
        else:
            summary['failed'] += 1
        
        domain = result.get('domain', 'unknown')
        if passed:
            summary['by_domain'][domain]['passed'] += 1
        else:
            summary['by_domain'][domain]['failed'] += 1
        
        if result.get('extrapolation_test'):
            summary['extrapolation_results'].append({
                'test_name': test_name,
                'domain': domain,
                'passed': passed,
                'r2': result.get('r2_score', 0.0)
            })
        
        difficulty = result.get('difficulty', 'unknown')
        if passed:
            summary['by_difficulty'][difficulty]['passed'] += 1
        else:
            summary['by_difficulty'][difficulty]['failed'] += 1
        
        summary['total_time'] += result.get('timing', {}).get('total', 0.0)
        
        discovery = result.get('discovery', {})
        validation = result.get('validation', {})
        
        summary['detailed_results'].append({
            'test_name': test_name,
            'domain': domain,
            'difficulty': difficulty,
            'r2': discovery.get('r2_score', 0.0),
            'validation_score': validation.get('total_score', 0.0),
            'time': result.get('timing', {}).get('total', 0.0),
            'passed': passed,
            'extrapolation': result.get('extrapolation_test', False),
            'expression': discovery.get('expression', 'N/A'),
            'ground_truth': result.get('ground_truth', 'N/A'),
            'error': result.get('error')
        })
    
    summary['detailed_results'].sort(key=lambda x: (x['domain'], x['test_name']))
    
    return summary

def print_results_table(results: Dict[str, Dict], test_cases: Dict):
    """Print detailed results table."""
    print(f"\n{'='*120}")
    print(f"RESULTS".center(120))
    print(f"{'='*120}")
    print(f"{'Test Name':<40} | {'R²':>6} | {'Val':>5} | {'Time':>6} | {'Status':>6} | {'Notes':<30}")
    print(f"{'-'*120}")
    
    sorted_tests = sorted(results.items(), key=lambda x: (
        test_cases.get(x[0], {}).get("domain", ""),
        x[0]
    ))
    
    current_domain = None
    for test_name, result in sorted_tests:
        domain = test_cases.get(test_name, {}).get("domain", "unknown")
        if domain != current_domain:
            if current_domain:
                print()
            print(f"{'─'*120}")
            print(f"{domain.upper()}")
            print(f"{'─'*120}")
            current_domain = domain
        
        test_name_short = test_name[:38]
        r2 = result.get("r2_score", 0.0)
        val = result.get("validation_score", 0.0)
        time_taken = result.get("timing", {}).get("total", 0.0)
        passed = result.get("_metadata", {}).get("passed", False)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        
        notes = []
        if result.get('extrapolation_test'):
            notes.append("Extrap")
        if result.get('error'):
            notes.append("ERROR")
        elif r2 >= 0.99:
            notes.append("Excellent")
        
        notes_str = ", ".join(notes)[:28]
        
        print(f"{test_name_short:<40} | {r2:>6.4f} | {val:>5.1f} | {time_taken:>5.1f}s | {status:>6} | {notes_str:<30}")
    
    print(f"{'='*120}")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r.get("_metadata", {}).get("passed", False))
    
    if total > 0:
        print(f"\nSUMMARY: {passed}/{total} passed ({passed/total*100:.1f}%)")
    
    print(f"{'='*120}\n")

# ============================================================================
# MAIN CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="LLM-Guided DeFi Discovery v1.1")
    
    parser.add_argument("--batch", action="store_true", help="Run all tests")
    parser.add_argument("--test", type=str, help="Run single test by name")
    parser.add_argument("--domain", type=str, help="Run specific domain")
    parser.add_argument("--mode", type=str, default="hybrid", help="LLM mode")
    parser.add_argument("--api-key", type=str, help="Anthropic API key")
    parser.add_argument("--niterations", type=int, default=50, help="Iterations")
    parser.add_argument("--resume", action="store_true", help="Resume")
    parser.add_argument("--list", action="store_true", help="List tests")
    
    args = parser.parse_args()
    
    # API key
    api_key = args.api_key
    if not api_key and args.mode != "none":
        load_dotenv()
        api_key = os.getenv("ANTHROPIC_API_KEY")
    
    # Load protocol
    protocol = DeFiExperimentProtocolExtended()
    domains = [args.domain] if args.domain else None
    test_cases = convert_defi_protocol_to_test_cases(protocol, domains)
    
    if args.list:
        print(f"\nAVAILABLE TESTS:")
        for domain in protocol.get_all_domains():
            domain_tests = [n for n, tc in test_cases.items() if tc['domain'] == domain]
            if domain_tests:
                print(f"\n{domain.upper()}:")
                for name in sorted(domain_tests):
                    print(f"  - {name}")
        return 0
    
    if args.batch:
        run_defi_suite(test_cases, args.mode, api_key, args.niterations, args.resume)
    elif args.test:
        result = run_single_test(args.test, test_cases, args.mode, api_key, args.niterations)
        return 0 if result.get('success') else 1
    else:
        parser.print_help()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""
# Run all DeFi tests
python llm_guided_symbolic_discovery_defi.py --batch --mode hybrid

# Single test (e.g., impermanent loss - similar to Nernst)
python llm_guided_symbolic_discovery_defi.py --test impermanent_loss --mode hybrid

# Resume interrupted run
python llm_guided_symbolic_discovery_defi.py --batch --resume

# Specific domain
python llm_guided_symbolic_discovery_defi.py --domain amm --batch

# List all tests
python llm_guided_symbolic_discovery_defi.py --list
"""
