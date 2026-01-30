#!/usr/bin/env python3
"""
Bibliography Deduplication and Merging Tool

This script:
1. Parses both bibliography.bib (new) and ref.bib (original)
2. Identifies overlapping entries by citation key
3. Reports conflicts and suggests resolution
4. Generates deduplicated merged bibliography
5. Extracts genuinely new references for integration

Usage:
    python deduplicate_bibliography.py --new bibliography.bib --original ref.bib --output merged.bib
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass, field


@dataclass
class BibEntry:
    """Represents a single bibliography entry"""
    key: str
    entry_type: str  # @article, @book, etc.
    fields: Dict[str, str] = field(default_factory=dict)
    raw_text: str = ""
    source_file: str = ""
    
    def __str__(self):
        return f"@{self.entry_type}{{{self.key},\n" + \
               "\n".join(f"  {k} = {{{v}}}," for k, v in self.fields.items()) + "\n}"


class BibliographyParser:
    """Parse .bib files into structured entries"""
    
    ENTRY_PATTERN = r'@(\w+)\{([^,]+),\s*(.*?)\n\}'
    FIELD_PATTERN = r'(\w+)\s*=\s*\{([^}]*)\}'
    
    def parse_file(self, filepath: Path) -> Dict[str, BibEntry]:
        """Parse a .bib file and return dictionary of entries keyed by citation key"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Normalize line endings and whitespace
        content = content.replace('\r\n', '\n')
        
        entries = {}
        
        # Find all bibliography entries
        for match in re.finditer(self.ENTRY_PATTERN, content, re.DOTALL):
            entry_type = match.group(1).lower()
            key = match.group(2).strip()
            fields_text = match.group(3)
            
            # Parse fields
            fields = {}
            for field_match in re.finditer(self.FIELD_PATTERN, fields_text):
                field_name = field_match.group(1).lower()
                field_value = field_match.group(2).strip()
                fields[field_name] = field_value
            
            entry = BibEntry(
                key=key,
                entry_type=entry_type,
                fields=fields,
                raw_text=match.group(0),
                source_file=str(filepath)
            )
            
            entries[key] = entry
        
        return entries


class BibliographyDeduplicator:
    """Identify and resolve duplicate bibliography entries"""
    
    def __init__(self):
        self.parser = BibliographyParser()
    
    def compare_entries(self, entry1: BibEntry, entry2: BibEntry) -> str:
        """Compare two entries and return 'identical', 'similar', or 'different'"""
        if entry1.entry_type != entry2.entry_type:
            return 'different'
        
        # Check critical fields
        critical_fields = ['title', 'author', 'year', 'journal']
        similarities = 0
        
        for field in critical_fields:
            val1 = entry1.fields.get(field, '').lower()
            val2 = entry2.fields.get(field, '').lower()
            
            if val1 and val2:
                # Fuzzy comparison (normalize spaces, punctuation)
                val1_norm = re.sub(r'[^a-z0-9]', '', val1)
                val2_norm = re.sub(r'[^a-z0-9]', '', val2)
                
                if val1_norm == val2_norm:
                    similarities += 1
                elif val1_norm in val2_norm or val2_norm in val1_norm:
                    similarities += 0.5
        
        if similarities >= 3:
            return 'identical'
        elif similarities >= 2:
            return 'similar'
        else:
            return 'different'
    
    def find_duplicates(self, 
                       new_entries: Dict[str, BibEntry], 
                       original_entries: Dict[str, BibEntry]) -> Tuple[Set[str], Dict[str, str], Set[str]]:
        """
        Find duplicate, similar, and genuinely new entries
        
        Returns:
            (duplicate_keys, similar_mapping, new_keys)
        """
        duplicate_keys = set()
        similar_mapping = {}  # new_key -> original_key
        new_keys = set()
        
        for new_key, new_entry in new_entries.items():
            if new_key in original_entries:
                # Exact key match
                duplicate_keys.add(new_key)
            else:
                # Check for similar entries with different keys
                found_similar = False
                
                for orig_key, orig_entry in original_entries.items():
                    comparison = self.compare_entries(new_entry, orig_entry)
                    
                    if comparison in ['identical', 'similar']:
                        similar_mapping[new_key] = orig_key
                        found_similar = True
                        break
                
                if not found_similar:
                    new_keys.add(new_key)
        
        return duplicate_keys, similar_mapping, new_keys
    
    def generate_report(self,
                       new_entries: Dict[str, BibEntry],
                       original_entries: Dict[str, BibEntry],
                       duplicate_keys: Set[str],
                       similar_mapping: Dict[str, str],
                       new_keys: Set[str]) -> str:
        """Generate human-readable deduplication report"""
        
        report = []
        report.append("=" * 80)
        report.append("BIBLIOGRAPHY DEDUPLICATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary statistics
        report.append(f"NEW FILE ENTRIES:      {len(new_entries)}")
        report.append(f"ORIGINAL FILE ENTRIES: {len(original_entries)}")
        report.append(f"EXACT DUPLICATES:      {len(duplicate_keys)}")
        report.append(f"SIMILAR ENTRIES:       {len(similar_mapping)}")
        report.append(f"GENUINELY NEW:         {len(new_keys)}")
        report.append("")
        
        # Exact duplicates
        if duplicate_keys:
            report.append("-" * 80)
            report.append("EXACT DUPLICATES (Same citation key in both files)")
            report.append("-" * 80)
            for key in sorted(duplicate_keys):
                report.append(f"  ✗ {key}")
                report.append(f"      Keep: ORIGINAL (from ref.bib)")
            report.append("")
        
        # Similar entries
        if similar_mapping:
            report.append("-" * 80)
            report.append("SIMILAR ENTRIES (Different keys, same content)")
            report.append("-" * 80)
            for new_key, orig_key in sorted(similar_mapping.items()):
                report.append(f"  ≈ {new_key} → {orig_key}")
                report.append(f"      New:      {new_entries[new_key].fields.get('title', 'N/A')[:60]}")
                report.append(f"      Original: {original_entries[orig_key].fields.get('title', 'N/A')[:60]}")
                report.append(f"      Action: Use original key '{orig_key}' in LaTeX")
            report.append("")
        
        # New entries
        if new_keys:
            report.append("-" * 80)
            report.append("GENUINELY NEW ENTRIES (Add to merged bibliography)")
            report.append("-" * 80)
            for key in sorted(new_keys):
                entry = new_entries[key]
                report.append(f"  ✓ {key}")
                report.append(f"      Title:  {entry.fields.get('title', 'N/A')[:60]}")
                report.append(f"      Author: {entry.fields.get('author', 'N/A')[:60]}")
                report.append(f"      Year:   {entry.fields.get('year', 'N/A')}")
            report.append("")
        
        report.append("=" * 80)
        report.append("RECOMMENDATION: Add only GENUINELY NEW entries to ref.bib")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def extract_new_entries(self, 
                          new_entries: Dict[str, BibEntry],
                          new_keys: Set[str]) -> str:
        """Extract genuinely new entries as formatted BibTeX"""
        
        output = []
        output.append("% ========== NEW ENTRIES TO ADD ==========")
        output.append("% The following entries are not present in ref.bib")
        output.append("% Add them to ref.bib in appropriate sections")
        output.append("")
        
        for key in sorted(new_keys):
            entry = new_entries[key]
            output.append(entry.raw_text)
            output.append("")
        
        return "\n".join(output)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Deduplicate and merge bibliography files"
    )
    parser.add_argument('--new', default='bibliography.bib',
                       help='New bibliography file (bibliography.bib)')
    parser.add_argument('--original', default='ref.bib',
                       help='Original bibliography file (ref.bib)')
    parser.add_argument('--output', default='new_entries.bib',
                       help='Output file for new entries only')
    parser.add_argument('--report', default='deduplication_report.txt',
                       help='Output file for deduplication report')
    
    args = parser.parse_args()
    
    # Check files exist
    new_path = Path(args.new)
    original_path = Path(args.original)
    
    if not new_path.exists():
        print(f"ERROR: {args.new} not found")
        sys.exit(1)
    
    if not original_path.exists():
        print(f"ERROR: {args.original} not found")
        sys.exit(1)
    
    # Parse bibliographies
    print("Parsing bibliography files...")
    deduplicator = BibliographyDeduplicator()
    new_entries = deduplicator.parser.parse_file(new_path)
    original_entries = deduplicator.parser.parse_file(original_path)
    
    # Find duplicates
    print("Analyzing duplicates...")
    duplicate_keys, similar_mapping, new_keys = deduplicator.find_duplicates(
        new_entries, original_entries
    )
    
    # Generate report
    report = deduplicator.generate_report(
        new_entries, original_entries,
        duplicate_keys, similar_mapping, new_keys
    )
    
    # Save report
    with open(args.report, 'w') as f:
        f.write(report)
    print(f"\n✓ Deduplication report saved to: {args.report}")
    
    # Extract new entries
    new_entries_text = deduplicator.extract_new_entries(new_entries, new_keys)
    with open(args.output, 'w') as f:
        f.write(new_entries_text)
    print(f"✓ New entries extracted to: {args.output}")
    
    # Print summary to console
    print("\n" + "=" * 80)
    print(f"SUMMARY: {len(new_keys)} genuinely new entries found")
    print("=" * 80)
    print(f"\nNext steps:")
    print(f"1. Review {args.report}")
    print(f"2. Copy new entries from {args.output} to ref.bib")
    print(f"3. Update LaTeX citations using similar_mapping if needed")
    print(f"4. Run citation insertion script")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


    """
    # Step 1: Deduplicate

    python3 deduplicate_bib.py \
    --new ref.bib \
    --original bibliography.bib \
    --output new_entries.bib \
    --report deduplication_report.txt

    # Step 2: Review
    cat deduplication_report.txt

    # Step 3: Insert citations (dry-run)
    python3 insert_citations.py --latex jmlr_paper.tex --bib new_entries.bib --dry-run

    # Step 4: Apply
    python3 insert_citations.py --latex jmlr_paper.tex --bib new_entries.bib
    """
