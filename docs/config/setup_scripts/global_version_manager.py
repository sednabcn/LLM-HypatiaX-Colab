#!/usr/bin/env python3
"""
Global Version Manager for HypatiaX System
Automatically tracks versions for all data types across the entire system.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import hashlib


class GlobalVersionManager:
    """Manages versions for all data types in the HypatiaX system."""
    
    # Define all versionable directories in the system
    VERSION_DIRECTORIES = {
        # Rules
        "rules": {
            "path": "custom_ner/queries/tableau/rules",
            "patterns": ["*.jsonl"],
            "exclude": ["rules_versions/*"]
        },
        # Training data (Excel/CSV)
        "training_data": {
            "path": "datasets/queries/tableau/training",
            "patterns": ["*.xlsx", "*.csv"],
            "exclude": ["training_versions/*"]
        },
        # Training data (spaCy format)
        "training_spacy": {
            "path": "datasets/queries/tableau/training_spacy",
            "patterns": ["*.json"],
            "exclude": ["training_spacy_versions/*"]
        },
        # Testing data (Excel/CSV)
        "testing_data": {
            "path": "datasets/queries/tableau/testing",
            "patterns": ["*.xlsx", "*.csv"],
            "exclude": ["testing_versions/*"]
        },
        # Testing data (spaCy format)
        "testing_spacy": {
            "path": "datasets/queries/tableau/testing_spacy",
            "patterns": ["*.json"],
            "exclude": ["testing_spacy_versions/*"]
        },
        # Trained models
        "trained_models": {
            "path": "data_spacy/queries/tableau",
            "patterns": ["ner_tableau*/meta.json"],
            "exclude": ["ner_versions/*"]
        },
        # Vocabulary files
        "vocab": {
            "path": "data_spacy/queries/tableau/vocab",
            "patterns": ["vocab_*"],
            "exclude": ["vocab_versions/*"]
        },
        # Model configs
        "model_configs": {
            "path": "models/queries/tableau/model_configs",
            "patterns": ["*.json", "*.cfg"],
            "exclude": []
        },
        # Patterns
        "patterns": {
            "path": "patterns/queries/tableau",
            "patterns": ["*.py"],
            "exclude": []
        }
    }
    
    def __init__(self, base_path: Path):
        """
        Initialize the global version manager.
        
        Args:
            base_path: Base path to the hypatiax directory
        """
        self.base_path = Path(base_path)
        self.versions_root = self.base_path / ".versions"
        self.versions_root.mkdir(exist_ok=True)
        
        # Global metadata file
        self.global_metadata_file = self.versions_root / "global_versions.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load global version metadata."""
        if self.global_metadata_file.exists():
            with open(self.global_metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "system_version": "1.0.0",
            "last_updated": None,
            "data_types": {},
            "snapshots": []
        }
    
    def _save_metadata(self):
        """Save global version metadata."""
        self.metadata["last_updated"] = datetime.now().isoformat()
        with open(self.global_metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2)
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file."""
        md5_hash = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5_hash.update(chunk)
            return md5_hash.hexdigest()
        except Exception:
            return "error"
    
    def _get_next_version(self, data_type: str) -> int:
        """Get the next version number for a data type."""
        if data_type not in self.metadata["data_types"]:
            self.metadata["data_types"][data_type] = {
                "current_version": 0,
                "versions": []
            }
        
        current_version = self.metadata["data_types"][data_type]["current_version"]
        return current_version + 1
    
    def find_all_versionable_files(self) -> Dict[str, List[Path]]:
        """
        Find all versionable files in the system.
        
        Returns:
            Dictionary mapping data types to lists of file paths
        """
        all_files = {}
        
        for data_type, config in self.VERSION_DIRECTORIES.items():
            data_path = self.base_path / config["path"]
            
            if not data_path.exists():
                all_files[data_type] = []
                continue
            
            files = []
            for pattern in config["patterns"]:
                files.extend(data_path.glob(pattern))
            
            # Filter out excluded patterns
            for exclude_pattern in config["exclude"]:
                exclude_files = set(data_path.glob(exclude_pattern))
                files = [f for f in files if f not in exclude_files]
            
            all_files[data_type] = sorted(files)
        
        return all_files
    
    def create_snapshot(self, name: str = None, notes: str = "") -> int:
        """
        Create a complete snapshot of all versionable data.
        
        Args:
            name: Optional name for the snapshot
            notes: Optional notes about the snapshot
        
        Returns:
            Snapshot ID
        """
        snapshot_id = len(self.metadata["snapshots"]) + 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if not name:
            name = f"snapshot_{snapshot_id}"
        
        snapshot_dir = self.versions_root / f"snapshot_{snapshot_id}_{timestamp}"
        snapshot_dir.mkdir(exist_ok=True)
        
        print(f"\n{'='*80}")
        print(f"📸 Creating Snapshot #{snapshot_id}: {name}")
        print(f"{'='*80}\n")
        
        snapshot_data = {
            "snapshot_id": snapshot_id,
            "name": name,
            "timestamp": timestamp,
            "datetime": datetime.now().isoformat(),
            "notes": notes,
            "data_types": {}
        }
        
        all_files = self.find_all_versionable_files()
        
        for data_type, files in all_files.items():
            if not files:
                continue
            
            print(f"📂 {data_type}: {len(files)} file(s)")
            
            # Create directory for this data type
            type_dir = snapshot_dir / data_type
            type_dir.mkdir(exist_ok=True)
            
            snapshot_data["data_types"][data_type] = {
                "file_count": len(files),
                "files": []
            }
            
            for file in files:
                # Calculate hash
                file_hash = self._calculate_file_hash(file)
                
                # Copy file to snapshot
                relative_path = file.relative_to(self.base_path)
                dest_path = type_dir / file.name
                
                try:
                    shutil.copy2(file, dest_path)
                    
                    snapshot_data["data_types"][data_type]["files"].append({
                        "name": file.name,
                        "original_path": str(relative_path),
                        "hash": file_hash,
                        "size": file.stat().st_size
                    })
                    
                    print(f"   ✅ {file.name}")
                except Exception as e:
                    print(f"   ❌ {file.name}: {e}")
        
        # Save snapshot metadata
        snapshot_metadata_file = snapshot_dir / "snapshot_metadata.json"
        with open(snapshot_metadata_file, 'w', encoding='utf-8') as f:
            json.dump(snapshot_data, f, indent=2)
        
        # Update global metadata
        self.metadata["snapshots"].append(snapshot_data)
        self._save_metadata()
        
        print(f"\n✅ Snapshot created: {snapshot_dir}")
        print(f"   Total files: {sum(len(files) for files in all_files.values())}")
        
        return snapshot_id
    
    def list_snapshots(self):
        """List all snapshots."""
        if not self.metadata["snapshots"]:
            print("ℹ️  No snapshots found")
            return
        
        print(f"\n{'='*80}")
        print("📸 SYSTEM SNAPSHOTS")
        print(f"{'='*80}\n")
        
        for snapshot in reversed(self.metadata["snapshots"]):
            print(f"Snapshot #{snapshot['snapshot_id']}: {snapshot['name']}")
            print(f"   Date: {snapshot['datetime']}")
            print(f"   Timestamp: {snapshot['timestamp']}")
            
            total_files = sum(
                dt.get('file_count', 0) 
                for dt in snapshot.get('data_types', {}).values()
            )
            print(f"   Total files: {total_files}")
            
            if snapshot.get('notes'):
                print(f"   Notes: {snapshot['notes']}")
            
            print(f"   Data types:")
            for dt, info in snapshot.get('data_types', {}).items():
                print(f"      • {dt}: {info.get('file_count', 0)} files")
            print()
    
    def restore_snapshot(self, snapshot_id: int, data_types: Optional[List[str]] = None):
        """
        Restore a snapshot.
        
        Args:
            snapshot_id: ID of the snapshot to restore
            data_types: Optional list of specific data types to restore
        """
        # Find snapshot
        snapshot = None
        for s in self.metadata["snapshots"]:
            if s["snapshot_id"] == snapshot_id:
                snapshot = s
                break
        
        if not snapshot:
            print(f"❌ Snapshot #{snapshot_id} not found")
            return False
        
        snapshot_dir = self.versions_root / f"snapshot_{snapshot_id}_{snapshot['timestamp']}"
        
        if not snapshot_dir.exists():
            print(f"❌ Snapshot directory not found: {snapshot_dir}")
            return False
        
        print(f"\n{'='*80}")
        print(f"🔄 Restoring Snapshot #{snapshot_id}: {snapshot['name']}")
        print(f"{'='*80}\n")
        
        # Determine which data types to restore
        if data_types:
            restore_types = [dt for dt in data_types if dt in snapshot.get('data_types', {})]
        else:
            restore_types = list(snapshot.get('data_types', {}).keys())
        
        for data_type in restore_types:
            print(f"\n📂 Restoring {data_type}...")
            
            type_dir = snapshot_dir / data_type
            if not type_dir.exists():
                print(f"   ⚠️  Directory not found: {type_dir}")
                continue
            
            # Get original paths
            files_info = snapshot['data_types'][data_type].get('files', [])
            
            for file_info in files_info:
                source_file = type_dir / file_info['name']
                dest_path = self.base_path / file_info['original_path']
                
                try:
                    # Create parent directory if needed
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Backup existing file if it exists
                    if dest_path.exists():
                        backup_path = dest_path.with_suffix(
                            dest_path.suffix + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        )
                        shutil.copy2(dest_path, backup_path)
                        print(f"   📦 Backed up existing: {dest_path.name}")
                    
                    # Restore file
                    shutil.copy2(source_file, dest_path)
                    print(f"   ✅ Restored: {file_info['name']}")
                    
                except Exception as e:
                    print(f"   ❌ Failed to restore {file_info['name']}: {e}")
        
        print(f"\n✅ Snapshot restoration complete")
        return True
    
    def auto_version_all(self, notes: str = "") -> Dict[str, int]:
        """
        Automatically version all data types that have changed.
        
        Args:
            notes: Optional notes about this versioning
        
        Returns:
            Dictionary mapping data types to new version numbers
        """
        print(f"\n{'='*80}")
        print("🔄 AUTO-VERSIONING ALL DATA TYPES")
        print(f"{'='*80}\n")
        
        versioned = {}
        all_files = self.find_all_versionable_files()
        
        for data_type, files in all_files.items():
            if not files:
                continue
            
            print(f"\n📂 Processing {data_type}...")
            
            # Check if any files have changed
            changed = self._check_for_changes(data_type, files)
            
            if changed:
                version = self._get_next_version(data_type)
                self._version_data_type(data_type, files, version, notes)
                versioned[data_type] = version
                print(f"   ✅ Versioned as v{version}")
            else:
                print(f"   ℹ️  No changes detected, skipping")
        
        if versioned:
            self._save_metadata()
            print(f"\n✅ Auto-versioning complete: {len(versioned)} data type(s) versioned")
        else:
            print(f"\nℹ️  No changes detected in any data type")
        
        return versioned
    
    def _check_for_changes(self, data_type: str, files: List[Path]) -> bool:
        """Check if any files have changed since last version."""
        if data_type not in self.metadata["data_types"]:
            return True
        
        versions = self.metadata["data_types"][data_type].get("versions", [])
        if not versions:
            return True
        
        last_version = versions[-1]
        last_hashes = {f["name"]: f["hash"] for f in last_version.get("files", [])}
        
        # Check for new or modified files
        for file in files:
            current_hash = self._calculate_file_hash(file)
            if file.name not in last_hashes or last_hashes[file.name] != current_hash:
                return True
        
        return False
    
    def _version_data_type(self, data_type: str, files: List[Path], 
                          version: int, notes: str):
        """Version a specific data type."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create version directory
        version_dir = self.versions_root / data_type / f"v{version}_{timestamp}"
        version_dir.mkdir(parents=True, exist_ok=True)
        
        version_data = {
            "version": version,
            "timestamp": timestamp,
            "datetime": datetime.now().isoformat(),
            "notes": notes,
            "file_count": len(files),
            "files": []
        }
        
        for file in files:
            file_hash = self._calculate_file_hash(file)
            dest_path = version_dir / file.name
            
            try:
                shutil.copy2(file, dest_path)
                version_data["files"].append({
                    "name": file.name,
                    "hash": file_hash,
                    "size": file.stat().st_size
                })
            except Exception as e:
                print(f"      ❌ Failed to version {file.name}: {e}")
        
        # Update metadata
        if data_type not in self.metadata["data_types"]:
            self.metadata["data_types"][data_type] = {
                "current_version": 0,
                "versions": []
            }
        
        self.metadata["data_types"][data_type]["versions"].append(version_data)
        self.metadata["data_types"][data_type]["current_version"] = version
    
    def export_version_manifest(self, output_file: Optional[Path] = None) -> Path:
        """
        Export a manifest of all current versions.
        
        Args:
            output_file: Optional output file path
        
        Returns:
            Path to the manifest file
        """
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.versions_root / f"version_manifest_{timestamp}.json"
        
        manifest = {
            "generated": datetime.now().isoformat(),
            "system_version": self.metadata.get("system_version"),
            "current_versions": {}
        }
        
        for data_type, info in self.metadata.get("data_types", {}).items():
            manifest["current_versions"][data_type] = {
                "version": info.get("current_version"),
                "last_updated": info.get("versions", [{}])[-1].get("datetime") if info.get("versions") else None
            }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✅ Version manifest exported: {output_file}")
        return output_file


def main():
    """CLI interface for global version manager."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Global version management for HypatiaX system",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "base_path",
        type=Path,
        help="Base path to hypatiax directory"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Snapshot command
    snapshot_parser = subparsers.add_parser("snapshot", help="Create a snapshot")
    snapshot_parser.add_argument("--name", help="Snapshot name")
    snapshot_parser.add_argument("--notes", default="", help="Snapshot notes")
    
    # List snapshots
    subparsers.add_parser("list-snapshots", help="List all snapshots")
    
    # Restore snapshot
    restore_parser = subparsers.add_parser("restore", help="Restore a snapshot")
    restore_parser.add_argument("snapshot_id", type=int, help="Snapshot ID")
    restore_parser.add_argument("--data-types", nargs="+", help="Specific data types to restore")
    
    # Auto-version
    auto_parser = subparsers.add_parser("auto-version", help="Auto-version all changed data")
    auto_parser.add_argument("--notes", default="", help="Version notes")
    
    # Export manifest
    subparsers.add_parser("export-manifest", help="Export version manifest")
    
    # Scan
    subparsers.add_parser("scan", help="Scan for versionable files")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = GlobalVersionManager(args.base_path)
    
    if args.command == "snapshot":
        manager.create_snapshot(name=args.name, notes=args.notes)
    
    elif args.command == "list-snapshots":
        manager.list_snapshots()
    
    elif args.command == "restore":
        manager.restore_snapshot(args.snapshot_id, data_types=args.data_types)
    
    elif args.command == "auto-version":
        manager.auto_version_all(notes=args.notes)
    
    elif args.command == "export-manifest":
        manager.export_version_manifest()
    
    elif args.command == "scan":
        all_files = manager.find_all_versionable_files()
        print(f"\n{'='*80}")
        print("🔍 VERSIONABLE FILES SCAN")
        print(f"{'='*80}\n")
        
        for data_type, files in all_files.items():
            print(f"📂 {data_type}: {len(files)} file(s)")
            for file in files:
                print(f"   • {file.relative_to(manager.base_path)}")
            print()


if __name__ == "__main__":
    main()
