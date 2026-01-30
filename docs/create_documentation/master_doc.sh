#!/bin/bash
# Master Documentation Generation Script for HypatiaX
# =====================================================
# Runs all documentation generation tools in sequence

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   HypatiaX Master Documentation Generator                      ║"
echo "║   Day 1 Afternoon Session: Complete Project Analysis          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python
echo -e "${BLUE}[1/4] Checking Python environment...${NC}"
python3 --version
echo ""

# Step 1: Generate comprehensive documentation
echo -e "${BLUE}[2/4] Generating comprehensive documentation...${NC}"
python3 generate_docs.py --root ./hypatiax --output ./docs_generated
echo -e "${GREEN}✓ Documentation generated${NC}\n"

# Step 2: Analyze rule files (solve the blocker)
echo -e "${BLUE}[3/4] Analyzing rule file issue...${NC}"
python3 rule_file_analyzer.py
echo -e "${GREEN}✓ Rule analysis complete${NC}\n"

# Step 3: Generate Quick Start guide
echo -e "${BLUE}[4/4] Generating Quick Start guide...${NC}"
python3 quick_start_generator.py
echo -e "${GREEN}✓ Quick Start generated${NC}\n"

# Summary
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                   GENERATION COMPLETE!                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}Generated Files:${NC}"
echo "  📁 docs_generated/          - Full API documentation"
echo "  📄 QUICKSTART.md            - Quick start guide"
echo "  🐍 example_usage.py         - Example usage script"
echo "  📊 project_metadata.json    - Project metadata"
echo "  🔧 fix_rules.sh             - Rule file fix script"
echo "  📋 rule_analysis_report.txt - Rule analysis report"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Read QUICKSTART.md for getting started"
echo "  2. Run ./fix_rules.sh to fix the rule file issue"
echo "  3. Run pytest tests/ to verify everything works"
echo "  4. Try python example_usage.py for a basic example"
echo ""
echo -e "${BLUE}Documentation Stats:${NC}"
if [ -f "docs_generated/project_structure.json" ]; then
    echo "  Modules documented: $(jq 'length' docs_generated/project_structure.json)"
fi
if [ -f "project_metadata.json" ]; then
    echo "  Entry points found: $(jq '.entry_points | length' project_metadata.json)"
    echo "  Test files found: $(jq '.test_files | length' project_metadata.json)"
fi
echo ""

# Check for issues
echo -e "${YELLOW}⚠️  Known Issues:${NC}"
if [ -f "rule_analysis.json" ]; then
    missing_count=$(jq '.findings.missing_files | length' rule_analysis.json)
    if [ "$missing_count" -gt 0 ]; then
        echo "  - $missing_count rule files need to be fixed"
        echo "    Run: ./fix_rules.sh"
    else
        echo "  - No issues detected!"
    fi
fi
echo ""

echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Documentation generation complete! Happy coding! 🚀           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
