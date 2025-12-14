#!/bin/bash
###############################################################################
# ONE-CLICK SETUP FOR HYPATIAX VERSION MANAGEMENT
#
# This script does EVERYTHING in one go. Just run it!
#
# Usage:
#   chmod +x one_click_setup.sh
#   ./one_click_setup.sh
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║         HYPATIAX VERSION MANAGEMENT - ONE-CLICK SETUP          ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "This will set up version management in 3 simple steps:"
echo "  1. Create directories"
echo "  2. Create scripts"
echo "  3. Initialize system"
echo ""
read -p "Press ENTER to start..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo ""
echo -e "${GREEN}STEP 1/3: Creating directories...${NC}"
mkdir -p .versions
mkdir -p scripts/version_management
echo "✓ Directories created"

echo ""
echo -e "${GREEN}STEP 2/3: Creating scripts...${NC}"

# Create the main version manager
cat > scripts/version_management/version_manager.py << 'ENDOFFILE'
#!/usr/bin/env python3
"""Simple version management for HypatiaX"""

import json
import shutil
from pathlib import Path
from datetime import datetime
import hashlib

class VersionManager:
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.versions_dir = self.base_path / ".versions"
        self.versions_dir.mkdir(exist_ok=True)
        self.metadata_file = self.versions_dir / "metadata.json"
        self.metadata = self._load_metadata()

    def _load_metadata(self):
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {"snapshots": [], "versions": {}}

    def _save_metadata(self):
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def create_snapshot(self, name=None):
        snapshot_id = len(self.metadata["snapshots"]) + 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if not name:
            name = f"snapshot_{snapshot_id}"

        snapshot_dir = self.versions_dir / f"{snapshot_id}_{timestamp}"
        snapshot_dir.mkdir(exist_ok=True)

        print(f"\n📸 Creating snapshot: {name}")

        # Find and copy all important files
        patterns = [
            "**/*.jsonl",  # Rules
            "**/*.xlsx",   # Training data
            "**/*.csv",    # Training data
        ]

        files_copied = 0
        for pattern in patterns:
            for file in self.base_path.glob(pattern):
                if ".versions" not in str(file) and "versions" not in file.name:
                    relative = file.relative_to(self.base_path)
                    dest = snapshot_dir / relative
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file, dest)
                    files_copied += 1

        snapshot_info = {
            "id": snapshot_id,
            "name": name,
            "timestamp": timestamp,
            "datetime": datetime.now().isoformat(),
            "files": files_copied
        }

        self.metadata["snapshots"].append(snapshot_info)
        self._save_metadata()

        print(f"✅ Snapshot created: {files_copied} files backed up")
        return snapshot_id

    def list_snapshots(self):
        print("\n📸 Snapshots:")
        for snap in self.metadata["snapshots"]:
            print(f"  #{snap['id']}: {snap['name']} - {snap['datetime']} ({snap['files']} files)")

    def set_version(self, component, version):
        self.metadata["versions"][component] = version
        self._save_metadata()
        print(f"✅ Set {component} to version {version}")

    def get_version(self, component):
        return self.metadata["versions"].get(component, 1)

    def export_env(self):
        env_file = self.base_path / ".env.versions"
        with open(env_file, 'w') as f:
            f.write("# HypatiaX Versions - Auto-generated\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
            for comp, ver in self.metadata["versions"].items():
                env_name = f"HYPATIAX_{comp.upper()}_VERSION"
                f.write(f"export {env_name}={ver}\n")
        print(f"✅ Environment file created: .env.versions")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 version_manager.py <command>")
        print("Commands:")
        print("  snapshot [name]  - Create a snapshot")
        print("  list            - List all snapshots")
        print("  set <comp> <ver> - Set version")
        print("  env             - Export environment file")
        sys.exit(1)

    manager = VersionManager(Path.cwd())
    command = sys.argv[1]

    if command == "snapshot":
        name = sys.argv[2] if len(sys.argv) > 2 else None
        manager.create_snapshot(name)
    elif command == "list":
        manager.list_snapshots()
    elif command == "set":
        manager.set_version(sys.argv[2], int(sys.argv[3]))
    elif command == "env":
        manager.export_env()
ENDOFFILE

chmod +x scripts/version_management/version_manager.py

# Create daily update script
cat > daily_update.sh << 'ENDOFFILE'
#!/bin/bash
# Daily update - Run this at end of each day

echo "🔄 Daily Version Update"
echo ""

# Create snapshot
python3 scripts/version_management/version_manager.py snapshot "daily_$(date +%Y%m%d)"

# Export environment
python3 scripts/version_management/version_manager.py env

echo ""
echo "✅ Done! Now run: source .env.versions"
ENDOFFILE

chmod +x daily_update.sh

# Create status check script
cat > check_status.sh << 'ENDOFFILE'
#!/bin/bash
# Check current status

echo "📋 HypatiaX Version Status"
echo ""

python3 scripts/version_management/version_manager.py list

echo ""
if [ -f .env.versions ]; then
    echo "Environment variables:"
    cat .env.versions | grep export
else
    echo "No environment file yet. Run: ./daily_update.sh"
fi
ENDOFFILE

chmod +x check_status.sh

echo "✓ Scripts created"

echo ""
echo -e "${GREEN}STEP 3/3: Initializing system...${NC}"

# Create initial snapshot
python3 scripts/version_management/version_manager.py snapshot "initial_setup"

# Set initial versions
python3 scripts/version_management/version_manager.py set rules 1
python3 scripts/version_management/version_manager.py set training 1
python3 scripts/version_management/version_manager.py set models 1

# Export environment
python3 scripts/version_management/version_manager.py env

echo "✓ System initialized"

echo ""
echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ SETUP COMPLETE! ✅                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "📚 What was created:"
echo "   .versions/           - Your version backups"
echo "   daily_update.sh      - Run this daily"
echo "   check_status.sh      - Check your versions"
echo "   .env.versions        - Version numbers"
echo ""
echo "🚀 How to use:"
echo ""
echo "   1. Load versions:"
echo "      ${GREEN}source .env.versions${NC}"
echo ""
echo "   2. Check status:"
echo "      ${GREEN}./check_status.sh${NC}"
echo ""
echo "   3. At end of day:"
echo "      ${GREEN}./daily_update.sh${NC}"
echo "      ${GREEN}source .env.versions${NC}"
echo ""
echo "That's it! Simple! 🎉"
echo ""
