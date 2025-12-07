#!/usr/bin/env python3
"""
Experiment tracking utility for HypatiaX
Registers and tracks experiments across all technologies
"""

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class TechnologyType(Enum):
    """Types of technologies"""

    NER = "ner"
    TRANSFORMER = "transformers"
    LLM = "llm"
    AGENT = "agents"
    HYBRID = "hybrid"


class ExperimentStatus(Enum):
    """Experiment status"""

    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass
class Experiment:
    """Experiment metadata"""

    id: str
    name: str
    technology: str
    description: str
    status: str
    created_at: str
    updated_at: str
    author: str
    results_path: str
    metrics: Dict[str, Any]
    config: Dict[str, Any]
    tags: List[str]
    notes: str = ""


class ExperimentTracker:
    """Track experiments across all technologies"""

    def __init__(self, experiments_dir: str = "experiments"):
        self.experiments_dir = Path(experiments_dir)
        self.registry_file = self.experiments_dir / "experiment_registry.json"
        self.experiments = self._load_registry()

    def _load_registry(self) -> Dict[str, Experiment]:
        """Load experiment registry from file"""
        if self.registry_file.exists():
            with open(self.registry_file, "r") as f:
                data = json.load(f)
                return {exp_id: Experiment(**exp_data) for exp_id, exp_data in data.items()}
        return {}

    def _save_registry(self):
        """Save experiment registry to file"""
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_file, "w") as f:
            data = {exp_id: asdict(exp) for exp_id, exp in self.experiments.items()}
            json.dump(data, f, indent=2)

    def register_experiment(
        self,
        name: str,
        technology: TechnologyType,
        description: str,
        author: str,
        config: Dict[str, Any] = None,
        tags: List[str] = None,
    ) -> str:
        """Register a new experiment"""
        timestamp = datetime.now().isoformat()
        exp_id = f"{technology.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create results directory
        results_path = self.experiments_dir / technology.value / name.replace(" ", "_") / "results"
        results_path.mkdir(parents=True, exist_ok=True)

        experiment = Experiment(
            id=exp_id,
            name=name,
            technology=technology.value,
            description=description,
            status=ExperimentStatus.PLANNED.value,
            created_at=timestamp,
            updated_at=timestamp,
            author=author,
            results_path=str(results_path),
            metrics={},
            config=config or {},
            tags=tags or [],
            notes="",
        )

        self.experiments[exp_id] = experiment
        self._save_registry()

        print(f"✅ Registered experiment: {exp_id}")
        print(f"   Results path: {results_path}")

        return exp_id

    def update_experiment(
        self,
        exp_id: str,
        status: Optional[ExperimentStatus] = None,
        metrics: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = None,
    ):
        """Update experiment details"""
        if exp_id not in self.experiments:
            raise ValueError(f"Experiment {exp_id} not found")

        exp = self.experiments[exp_id]
        exp.updated_at = datetime.now().isoformat()

        if status:
            exp.status = status.value

        if metrics:
            exp.metrics.update(metrics)

        if notes:
            exp.notes = notes

        self._save_registry()
        print(f"✅ Updated experiment: {exp_id}")

    def get_experiment(self, exp_id: str) -> Optional[Experiment]:
        """Get experiment by ID"""
        return self.experiments.get(exp_id)

    def list_experiments(
        self,
        technology: Optional[TechnologyType] = None,
        status: Optional[ExperimentStatus] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Experiment]:
        """List experiments with optional filters"""
        experiments = list(self.experiments.values())

        if technology:
            experiments = [e for e in experiments if e.technology == technology.value]

        if status:
            experiments = [e for e in experiments if e.status == status.value]

        if tags:
            experiments = [e for e in experiments if any(tag in e.tags for tag in tags)]

        return sorted(experiments, key=lambda x: x.created_at, reverse=True)

    def generate_report(self, output_file: str = "experiments_report.md"):
        """Generate markdown report of all experiments"""
        report_path = self.experiments_dir / output_file

        with open(report_path, "w") as f:
            f.write("# HypatiaX Experiments Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Group by technology
            for tech in TechnologyType:
                tech_experiments = self.list_experiments(technology=tech)
                if not tech_experiments:
                    continue

                f.write(f"## {tech.value.upper()} Experiments\n\n")

                for exp in tech_experiments:
                    f.write(f"### {exp.name}\n\n")
                    f.write(f"- **ID**: `{exp.id}`\n")
                    f.write(f"- **Status**: {exp.status}\n")
                    f.write(f"- **Author**: {exp.author}\n")
                    f.write(f"- **Created**: {exp.created_at}\n")
                    f.write(f"- **Description**: {exp.description}\n")

                    if exp.tags:
                        f.write(f"- **Tags**: {', '.join(exp.tags)}\n")

                    if exp.metrics:
                        f.write(f"- **Metrics**:\n")
                        for key, value in exp.metrics.items():
                            f.write(f"  - {key}: {value}\n")

                    f.write(f"- **Results Path**: `{exp.results_path}`\n\n")

        print(f"✅ Report generated: {report_path}")
        return report_path


# CLI interface
def main():
    """Command-line interface for experiment tracking"""
    import argparse

    parser = argparse.ArgumentParser(description="Track HypatiaX experiments")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Register command
    register_parser = subparsers.add_parser("register", help="Register new experiment")
    register_parser.add_argument("--name", required=True, help="Experiment name")
    register_parser.add_argument("--tech", required=True, choices=["ner", "transformers", "llm", "agents", "hybrid"])
    register_parser.add_argument("--description", required=True, help="Description")
    register_parser.add_argument("--author", required=True, help="Author name")
    register_parser.add_argument("--tags", nargs="+", help="Tags")

    # List command
    list_parser = subparsers.add_parser("list", help="List experiments")
    list_parser.add_argument("--tech", choices=["ner", "transformers", "llm", "agents", "hybrid"])
    list_parser.add_argument("--status", choices=["planned", "running", "completed", "failed", "archived"])

    # Update command
    update_parser = subparsers.add_parser("update", help="Update experiment")
    update_parser.add_argument("--id", required=True, help="Experiment ID")
    update_parser.add_argument("--status", choices=["planned", "running", "completed", "failed", "archived"])
    update_parser.add_argument("--notes", help="Notes")

    # Report command
    subparsers.add_parser("report", help="Generate experiments report")

    args = parser.parse_args()

    tracker = ExperimentTracker()

    if args.command == "register":
        tech = TechnologyType(args.tech)
        exp_id = tracker.register_experiment(
            name=args.name, technology=tech, description=args.description, author=args.author, tags=args.tags or []
        )
        print(f"\n🎯 Experiment ID: {exp_id}")

    elif args.command == "list":
        tech = TechnologyType(args.tech) if args.tech else None
        status = ExperimentStatus(args.status) if args.status else None

        experiments = tracker.list_experiments(technology=tech, status=status)

        if not experiments:
            print("No experiments found")
            return

        print(f"\n📊 Found {len(experiments)} experiments:\n")
        for exp in experiments:
            print(f"[{exp.status.upper()}] {exp.id}")
            print(f"  Name: {exp.name}")
            print(f"  Tech: {exp.technology}")
            print(f"  Author: {exp.author}")
            print(f"  Created: {exp.created_at}")
            print()

    elif args.command == "update":
        status = ExperimentStatus(args.status) if args.status else None
        tracker.update_experiment(exp_id=args.id, status=status, notes=args.notes)

    elif args.command == "report":
        tracker.generate_report()


if __name__ == "__main__":
    main()
