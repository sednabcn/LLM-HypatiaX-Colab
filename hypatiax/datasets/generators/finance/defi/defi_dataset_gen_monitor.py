"""
DeFi Formula Discovery Dataset Generator with Resource Monitoring
Tracks CPU, memory, and progress in real-time
"""

import json
import os
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, Optional, Tuple

import numpy as np
import psutil

from hypatiax.tools.symbolic.hybrid_system import HybridDiscoverySystem


@dataclass
class ResourceSnapshot:
    """Snapshot of system resources at a point in time."""

    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    available_memory_mb: float

    def __str__(self):
        return (
            f"CPU: {self.cpu_percent:.1f}% | "
            f"RAM: {self.memory_mb:.0f}MB ({self.memory_percent:.1f}%) | "
            f"Available: {self.available_memory_mb:.0f}MB"
        )


class ResourceMonitor:
    """Monitor system resources during execution."""

    def __init__(self, check_interval: float = 2.0):
        """
        Initialize resource monitor.

        Args:
            check_interval: Seconds between resource checks
        """
        self.check_interval = check_interval
        self.snapshots = []
        self.monitoring = False
        self.monitor_thread = None
        self.start_time = None

    def start(self):
        """Start monitoring in background thread."""
        if self.monitoring:
            return

        self.monitoring = True
        self.start_time = time.time()
        self.snapshots = []

        # Take initial snapshot
        self._take_snapshot()

        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        print(f"🔍 Resource monitoring started (interval: {self.check_interval}s)")

    def stop(self):
        """Stop monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

        elapsed = time.time() - self.start_time if self.start_time else 0
        print(f"🔍 Resource monitoring stopped (duration: {elapsed:.1f}s)")

    def _monitor_loop(self):
        """Background monitoring loop."""
        while self.monitoring:
            time.sleep(self.check_interval)
            if self.monitoring:  # Check again in case stopped during sleep
                self._take_snapshot()

    def _take_snapshot(self):
        """Take a snapshot of current resources."""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            virtual_memory = psutil.virtual_memory()

            snapshot = ResourceSnapshot(
                timestamp=datetime.now().isoformat(),
                cpu_percent=process.cpu_percent(interval=0.1),
                memory_percent=virtual_memory.percent,
                memory_mb=memory_info.rss / (1024 * 1024),
                available_memory_mb=virtual_memory.available / (1024 * 1024),
            )

            self.snapshots.append(snapshot)

        except Exception as e:
            print(f"⚠️  Error taking resource snapshot: {e}")

    def get_current_snapshot(self) -> Optional[ResourceSnapshot]:
        """Get most recent snapshot."""
        return self.snapshots[-1] if self.snapshots else None

    def get_statistics(self) -> Dict:
        """Calculate statistics from all snapshots."""
        if not self.snapshots:
            return {}

        cpu_values = [s.cpu_percent for s in self.snapshots]
        memory_values = [s.memory_mb for s in self.snapshots]

        return {
            "duration_seconds": time.time() - self.start_time if self.start_time else 0,
            "num_snapshots": len(self.snapshots),
            "cpu_percent": {
                "mean": np.mean(cpu_values),
                "max": np.max(cpu_values),
                "min": np.min(cpu_values),
            },
            "memory_mb": {
                "mean": np.mean(memory_values),
                "max": np.max(memory_values),
                "min": np.min(memory_values),
            },
            "memory_available_mb": {
                "min": min(s.available_memory_mb for s in self.snapshots),
            },
        }

    def print_summary(self):
        """Print resource usage summary."""
        stats = self.get_statistics()
        if not stats:
            print("No resource data collected")
            return

        print("\n" + "=" * 70)
        print("RESOURCE USAGE SUMMARY")
        print("=" * 70)
        print(f"Duration: {stats['duration_seconds']:.1f}s")
        print(f"Snapshots: {stats['num_snapshots']}")
        print(f"\nCPU Usage:")
        print(f"  Average: {stats['cpu_percent']['mean']:.1f}%")
        print(f"  Peak: {stats['cpu_percent']['max']:.1f}%")
        print(f"\nMemory Usage:")
        print(f"  Average: {stats['memory_mb']['mean']:.0f} MB")
        print(f"  Peak: {stats['memory_mb']['max']:.0f} MB")
        print(f"  Min Available: {stats['memory_available_mb']['min']:.0f} MB")
        print("=" * 70)


class ProgressTracker:
    """Track progress through multiple stages."""

    def __init__(self, total_formulas: int):
        """
        Initialize progress tracker.

        Args:
            total_formulas: Total number of formulas to process
        """
        self.total_formulas = total_formulas
        self.current_formula = 0
        self.current_stage = ""
        self.stage_start_time = None
        self.formula_start_time = None
        self.stage_times = {}

    def start_formula(self, formula_name: str):
        """Start tracking a new formula."""
        self.current_formula += 1
        self.formula_start_time = time.time()

        print("\n" + "=" * 70)
        print(f"FORMULA {self.current_formula}/{self.total_formulas}: {formula_name}")
        print(
            f"Progress: [{'█' * self.current_formula}{'░' * (self.total_formulas - self.current_formula)}] "
            f"{self.current_formula}/{self.total_formulas} ({self.current_formula/self.total_formulas*100:.1f}%)"
        )
        print("=" * 70)

    def start_stage(self, stage_name: str):
        """Start tracking a stage within a formula."""
        self.current_stage = stage_name
        self.stage_start_time = time.time()
        print(f"\n[Stage] {stage_name}...")

    def end_stage(self, success: bool = True, message: str = ""):
        """End current stage."""
        if self.stage_start_time:
            elapsed = time.time() - self.stage_start_time

            if self.current_stage not in self.stage_times:
                self.stage_times[self.current_stage] = []
            self.stage_times[self.current_stage].append(elapsed)

            status = "✅" if success else "❌"
            print(f"{status} {self.current_stage} completed in {elapsed:.2f}s")
            if message:
                print(f"   {message}")

    def end_formula(self):
        """End current formula."""
        if self.formula_start_time:
            elapsed = time.time() - self.formula_start_time
            print(f"\n⏱️  Total formula time: {elapsed:.2f}s")

    def print_summary(self):
        """Print timing summary for all stages."""
        if not self.stage_times:
            return

        print("\n" + "=" * 70)
        print("STAGE TIMING SUMMARY")
        print("=" * 70)

        for stage, times in self.stage_times.items():
            avg_time = np.mean(times)
            total_time = np.sum(times)
            count = len(times)
            print(f"\n{stage}:")
            print(f"  Count: {count}")
            print(f"  Average: {avg_time:.2f}s")
            print(f"  Total: {total_time:.2f}s")
            print(f"  Min/Max: {min(times):.2f}s / {max(times):.2f}s")

        print("=" * 70)


class DeFiFormulaGenerator:
    """Generate synthetic DeFi data and discover formulas with monitoring."""

    def __init__(self, domain: str = "defi", seed: int = 42, monitor_resources: bool = True):
        """
        Initialize the generator.

        Args:
            domain: Domain for validation
            seed: Random seed for reproducibility
            monitor_resources: Enable resource monitoring
        """
        print("🚀 Initializing DeFi Formula Generator...")

        # Check initial resources
        self._check_system_resources()

        self.system = HybridDiscoverySystem(domain=domain, max_results=100)
        self.seed = seed
        np.random.seed(seed)
        self.results = []

        # Initialize monitoring
        self.monitor_resources = monitor_resources
        if monitor_resources:
            self.resource_monitor = ResourceMonitor(check_interval=2.0)
        else:
            self.resource_monitor = None

        self.progress_tracker = None

        print("✅ Generator initialized\n")

    def _check_system_resources(self):
        """Check if system has sufficient resources."""
        virtual_memory = psutil.virtual_memory()
        cpu_count = psutil.cpu_count()

        print("\n" + "=" * 70)
        print("SYSTEM RESOURCE CHECK")
        print("=" * 70)
        print(f"CPU Cores: {cpu_count}")
        print(f"Total RAM: {virtual_memory.total / (1024**3):.2f} GB")
        print(f"Available RAM: {virtual_memory.available / (1024**3):.2f} GB")
        print(f"RAM Usage: {virtual_memory.percent:.1f}%")

        # Warn if resources are low
        if virtual_memory.available < 1024**3:  # Less than 1GB available
            print("\n⚠️  WARNING: Less than 1GB RAM available!")
            print("   Consider closing other applications.")

        if virtual_memory.percent > 80:
            print("\n⚠️  WARNING: High memory usage detected!")
            print("   System may slow down during generation.")

        print("=" * 70)

    def generate_impermanent_loss(self, n_samples: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """Generate impermanent loss data."""
        price_ratios = np.random.uniform(0.1, 10, (n_samples, 1))
        il = 2 * np.sqrt(price_ratios[:, 0]) / (price_ratios[:, 0] + 1) - 1
        il += np.random.normal(0, 0.01, n_samples)

        print(f"   Samples: {n_samples}")
        print(f"   Price ratio range: [{price_ratios.min():.2f}, {price_ratios.max():.2f}]")
        print(f"   IL range: [{il.min():.4f}, {il.max():.4f}]")

        return price_ratios, il

    def generate_amm_swap_output(self, n_samples: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """Generate AMM swap output data."""
        amount_in = np.random.uniform(1, 100, n_samples)
        reserve_in = np.random.uniform(1000, 10000, n_samples)
        reserve_out = np.random.uniform(1000, 10000, n_samples)

        X_data = np.column_stack([amount_in, reserve_in, reserve_out])
        y_out = (amount_in * 0.997 * reserve_out) / (reserve_in + amount_in * 0.997)
        y_out += np.random.normal(0, 0.5, n_samples)

        print(f"   Samples: {n_samples}")
        print(f"   Amount in range: [{amount_in.min():.2f}, {amount_in.max():.2f}]")

        return X_data, y_out

    def generate_utilization_rate(self, n_samples: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """Generate utilization rate data."""
        borrowed = np.random.uniform(0, 1000, n_samples)
        utilization_target = np.random.uniform(0.3, 0.9, n_samples)
        supplied = borrowed / utilization_target

        X_util = np.column_stack([borrowed, supplied])
        util = borrowed / supplied
        util += np.random.normal(0, 0.01, n_samples)

        print(f"   Samples: {n_samples}")
        print(f"   Utilization range: [{util.min():.4f}, {util.max():.4f}]")

        return X_util, util

    def generate_liquidity_value(self, n_samples: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """Generate liquidity value data."""
        reserve0 = np.random.uniform(100, 10000, n_samples)
        reserve1 = np.random.uniform(100, 10000, n_samples)

        X_data = np.column_stack([reserve0, reserve1])
        value = 2 * np.sqrt(reserve0 * reserve1)
        value += np.random.normal(0, 10, n_samples)

        print(f"   Samples: {n_samples}")
        print(f"   Value range: [{value.min():.2f}, {value.max():.2f}]")

        return X_data, value

    def run_all_formulas(self, n_samples: int = 100):
        """Generate and discover all DeFi formulas with monitoring."""

        formulas = [
            ("Impermanent Loss", self.generate_impermanent_loss),
            ("AMM Swap Output", self.generate_amm_swap_output),
            ("Utilization Rate", self.generate_utilization_rate),
            ("Liquidity Value", self.generate_liquidity_value),
        ]

        # Initialize progress tracker
        self.progress_tracker = ProgressTracker(len(formulas))

        # Start resource monitoring
        if self.resource_monitor:
            self.resource_monitor.start()

        print("\n" + "#" * 70)
        print("# DeFi Formula Discovery - MONITORED EXECUTION")
        print(f"# Timestamp: {datetime.now().isoformat()}")
        print(f"# Total formulas: {len(formulas)}")
        print(f"# Samples per formula: {n_samples}")
        print("#" * 70)

        # Process each formula
        for formula_name, generator_func in formulas:
            self.progress_tracker.start_formula(formula_name)

            try:
                # Stage 1: Data generation
                self.progress_tracker.start_stage("Data Generation")
                X, y = generator_func(n_samples)

                # Show current resources
                if self.resource_monitor:
                    snapshot = self.resource_monitor.get_current_snapshot()
                    if snapshot:
                        print(f"   Resources: {snapshot}")

                self.progress_tracker.end_stage(success=True)

                # Stage 2: Discovery
                self.progress_tracker.start_stage("Symbolic Discovery")

                # Prepare parameters based on formula
                if formula_name == "Impermanent Loss":
                    params = {
                        "variable_names": ["price_ratio"],
                        "variable_descriptions": {"price_ratio": "Ratio of current price to initial price"},
                        "variable_units": {"price_ratio": "dimensionless"},
                    }
                elif formula_name == "AMM Swap Output":
                    X_norm = X.copy()
                    X_norm[:, 0] = X[:, 0] / np.mean(X[:, 0])
                    X_norm[:, 1] = X[:, 1] / np.mean(X[:, 1])
                    X_norm[:, 2] = X[:, 2] / np.mean(X[:, 2])
                    X = X_norm
                    params = {
                        "variable_names": ["amount_in_ratio", "reserve_in_ratio", "reserve_out_ratio"],
                        "variable_descriptions": {
                            "amount_in_ratio": "Input token amount (normalized)",
                            "reserve_in_ratio": "Input token reserve ratio",
                            "reserve_out_ratio": "Output token reserve ratio",
                        },
                        "variable_units": {
                            "amount_in_ratio": "dimensionless",
                            "reserve_in_ratio": "dimensionless",
                            "reserve_out_ratio": "dimensionless",
                        },
                    }
                elif formula_name == "Utilization Rate":
                    params = {
                        "variable_names": ["borrowed", "supplied"],
                        "variable_descriptions": {
                            "borrowed": "Total amount borrowed from pool",
                            "supplied": "Total amount supplied to pool",
                        },
                        "variable_units": {"borrowed": "dimensionless", "supplied": "dimensionless"},
                    }
                else:  # Liquidity Value
                    X_norm = X.copy()
                    X_norm[:, 0] = X[:, 0] / np.mean(X[:, 0])
                    X_norm[:, 1] = X[:, 1] / np.mean(X[:, 1])
                    X = X_norm
                    params = {
                        "variable_names": ["reserve0_ratio", "reserve1_ratio"],
                        "variable_descriptions": {
                            "reserve0_ratio": "Reserve amount of token 0 (normalized)",
                            "reserve1_ratio": "Reserve amount of token 1 (normalized)",
                        },
                        "variable_units": {"reserve0_ratio": "dimensionless", "reserve1_ratio": "dimensionless"},
                    }

                result = self.system.discover_validate_interpret(
                    X=X,
                    y=y,
                    description=formula_name,
                    validate_first=False,
                    show_formatted=False,  # Disable to reduce clutter
                    **params,
                )

                # Show results
                discovery = result.get("discovery", {})
                validation = result.get("validation", {})

                message = (
                    f"Expression: {discovery.get('expression', 'N/A')[:60]}... | "
                    f"R²: {discovery.get('r2_score', 0):.4f} | "
                    f"Validation: {validation.get('total_score', 0):.1f}/100"
                )

                self.progress_tracker.end_stage(success=True, message=message)

                self.results.append((formula_name, result))
                self.progress_tracker.end_formula()

            except Exception as e:
                self.progress_tracker.end_stage(success=False, message=f"Error: {str(e)[:100]}")
                print(f"❌ Failed to process {formula_name}")
                import traceback

                traceback.print_exc()

        # Stop monitoring
        if self.resource_monitor:
            self.resource_monitor.stop()

    def save_results(self, output_dir: str = "hypatiax/data/finance/defi"):
        """Save results with monitoring data."""
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save main results
        json_path = os.path.join(output_dir, f"defi_formulas_{timestamp}.json")
        self.system.export_results(json_path, format="json")

        csv_path = os.path.join(output_dir, f"defi_summary_{timestamp}.csv")
        self.system.export_results(csv_path, format="csv")

        # Save monitoring data if available
        if self.resource_monitor:
            monitor_path = os.path.join(output_dir, f"resource_monitoring_{timestamp}.json")
            with open(monitor_path, "w") as f:
                json.dump(
                    {
                        "statistics": self.resource_monitor.get_statistics(),
                        "snapshots": [asdict(s) for s in self.resource_monitor.snapshots],
                    },
                    f,
                    indent=2,
                )
            print(f"   Monitoring data: {monitor_path}")

        return json_path, csv_path

    def print_summary(self):
        """Print comprehensive summary."""
        print("\n" + "=" * 70)
        print("GENERATION COMPLETE - FINAL SUMMARY")
        print("=" * 70)

        # Formula results
        stats = self.system.get_statistics()
        print(f"\nFormula Statistics:")
        print(f"  Total formulas: {stats['total_runs']}")
        print(f"  Valid: {stats['valid_count']} | Invalid: {stats['invalid_count']}")
        print(f"  Success rate: {stats['success_rate']:.1%}")
        print(f"  Average R²: {stats['average_r2']:.4f}")
        print(f"  Average validation: {stats['average_validation_score']:.1f}/100")

        # Resource usage
        if self.resource_monitor:
            self.resource_monitor.print_summary()

        # Stage timing
        if self.progress_tracker:
            self.progress_tracker.print_summary()

        print("\n" + "=" * 70)


def main():
    """Main execution with monitoring."""
    print("\n" + "█" * 70)
    print("█  DeFi Formula Discovery - MONITORED VERSION  █")
    print("█  Features:                                    █")
    print("█    ✓ Real-time resource monitoring           █")
    print("█    ✓ Progress tracking with visual feedback  █")
    print("█    ✓ Stage-by-stage timing                   █")
    print("█    ✓ Comprehensive statistics                █")
    print("█" * 70)

    # Initialize with monitoring
    generator = DeFiFormulaGenerator(domain="defi", seed=42, monitor_resources=True)

    # Run with monitoring
    generator.run_all_formulas(n_samples=100)

    # Save everything
    json_path, csv_path = generator.save_results()

    # Print comprehensive summary
    generator.print_summary()

    print(f"\n✅ Complete! Results saved to:")
    print(f"   JSON: {json_path}")
    print(f"   CSV:  {csv_path}")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()


"""
I've created an enhanced version with comprehensive monitoring and progress tracking. Here's what's new:
Key Features:
1. Resource Monitoring 🔍

Real-time tracking of CPU and memory usage
Background thread monitors every 2 seconds
Statistics showing average, peak, and minimum usage
Pre-flight check warns if your system is low on resources

2. Progress Tracking 📊

Visual progress bar showing which formula you're on
Stage-by-stage updates (Data Generation → Discovery → Validation)
Timing for each stage so you know what's slow
Clear success/failure indicators (✅/❌)

3. Real-time Feedback 💬
Shows you exactly what's happening:

Current formula (1/4, 2/4, etc.)
Current stage with timing
Resource usage at key points
Expression and scores immediately after discovery

4. Comprehensive Statistics 📈
Final summary includes:

Formula success rates
Average R² scores
Resource usage (CPU, memory)
Stage timing breakdown

What You'll See During Execution:
🔍 Resource monitoring started (interval: 2.0s)

======================================================================
FORMULA 1/4: Impermanent Loss
Progress: [█░░░] 1/4 (25.0%)
======================================================================

[Stage] Data Generation...
   Samples: 100
   Price ratio range: [0.10, 9.95]
   Resources: CPU: 15.2% | RAM: 1024MB (45.3%) | Available: 1234MB
✅ Data Generation completed in 0.15s

[Stage] Symbolic Discovery...
✅ Symbolic Discovery completed in 2.34s
   Expression: 2*sqrt(price_ratio)/(price_ratio + 1) - 1 | R²: 0.9987 | Validation: 92.3/100

⏱️  Total formula time: 2.49s
Installation Requirement:
You'll need the psutil library for resource monitoring:
bashpip install psutil
Usage:
The script will:

Check your system resources before starting
Warn you if memory is low (< 1GB available)
Monitor continuously while running
Save monitoring data alongside results

This way you can:

See if your laptop can handle it before committing
Track progress so you're not left wondering
Identify bottlenecks (which stage is slow)
Get detailed resource usage reports
"""
