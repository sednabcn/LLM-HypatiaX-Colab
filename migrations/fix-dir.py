#!/usr/bin/env python3
"""Run only directory structure creation"""

import sys
sys.path.insert(0, '../hypatiax') 
from extension_project import HypatiaXMigration

migration = HypatiaXMigration(".")
migration.create_directory_structure()
print("✅ Directory structure updated!")
