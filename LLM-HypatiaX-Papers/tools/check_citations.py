#!/usr/bin/env python3
"""
Check for citation consistency across papers
"""

import re
from pathlib import Path

def extract_citations(bib_file):
    """Extract citation keys from .bib file"""
    with open(bib_file, 'r') as f:
        content = f.read()
    return set(re.findall(r'@\w+\{([^,]+),', content))

def main():
    papers_dir = Path('papers')
    all_citations = {}
    
    for paper in papers_dir.iterdir():
        if paper.is_dir():
            bib_file = paper / 'paper' / 'references.bib'
            if bib_file.exists():
                citations = extract_citations(bib_file)
                all_citations[paper.name] = citations
                print(f"{paper.name}: {len(citations)} citations")
    
    # Find common citations
    if len(all_citations) > 1:
        common = set.intersection(*all_citations.values())
        print(f"\nCommon citations across all papers: {len(common)}")
        for cite in sorted(common):
            print(f"  - {cite}")

if __name__ == '__main__':
    main()
