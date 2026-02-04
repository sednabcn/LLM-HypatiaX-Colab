#!/bin/bash

echo "Repository Statistics"
echo "===================="
echo ""
echo "Papers: $(ls -d papers/*/ 2>/dev/null | wc -l)"
echo "Shared code files: $(find shared/code -type f | wc -l)"
echo "Total LaTeX files: $(find papers -name "*.tex" | wc -l)"
echo "Total Python files: $(find . -name "*.py" | wc -l)"
echo ""
echo "Paper Status:"
for paper in papers/*/; do
    name=$(basename $paper)
    if [ -f "$paper/paper/main.pdf" ]; then
        status="✓ Built"
    else
        status="○ Not built"
    fi
    echo "  $name: $status"
done
