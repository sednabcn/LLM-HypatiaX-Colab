#!/usr/bin/env python3
"""
Bibliography Deduplication Script

This script removes duplicate entries from BibTeX files based on citation keys.
It preserves the first occurrence of each entry and removes subsequent duplicates.

Usage:
    python deduplication_bib.py input.bib [output.bib]

If output file is not specified, the input file will be overwritten with deduplicated entries.
"""

import sys
import re
from collections import OrderedDict


def parse_bibtex_entries(content):
    """
    Parse BibTeX file content into individual entries.
    
    Args:
        content (str): The content of the BibTeX file
        
    Returns:
        list: List of tuples (entry_type, cite_key, full_entry)
    """
    entries = []
    
    # Pattern to match BibTeX entries
    # Matches @type{key, ... }
    pattern = r'@(\w+)\s*\{\s*([^,\s]+)\s*,([^@]*?)(?=\n@|\Z)'
    
    for match in re.finditer(pattern, content, re.DOTALL):
        entry_type = match.group(1)
        cite_key = match.group(2)
        entry_content = match.group(3)
        
        # Reconstruct the full entry
        full_entry = f"@{entry_type}{{{cite_key},{entry_content}"
        entries.append((entry_type, cite_key, full_entry))
    
    return entries


def deduplicate_entries(entries):
    """
    Remove duplicate entries based on citation keys.
    
    Args:
        entries (list): List of tuples (entry_type, cite_key, full_entry)
        
    Returns:
        OrderedDict: Dictionary with cite_key as key and full_entry as value
        list: List of duplicate citation keys that were removed
    """
    deduplicated = OrderedDict()
    duplicates = []
    
    for entry_type, cite_key, full_entry in entries:
        if cite_key in deduplicated:
            duplicates.append(cite_key)
            print(f"Warning: Duplicate entry found - '{cite_key}' (type: @{entry_type})")
        else:
            deduplicated[cite_key] = full_entry
    
    return deduplicated, duplicates


def extract_preamble_and_comments(content):
    """
    Extract @preamble, @string definitions, and comments from BibTeX file.
    
    Args:
        content (str): The content of the BibTeX file
        
    Returns:
        str: Preamble and other non-entry content
    """
    preamble_parts = []
    
    # Extract @preamble
    preamble_pattern = r'@preamble\s*\{[^}]*\}'
    for match in re.finditer(preamble_pattern, content, re.IGNORECASE):
        preamble_parts.append(match.group(0))
    
    # Extract @string
    string_pattern = r'@string\s*\{[^}]*\}'
    for match in re.finditer(string_pattern, content, re.IGNORECASE):
        preamble_parts.append(match.group(0))
    
    # Extract top comments (lines starting with %)
    lines = content.split('\n')
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('%'):
            preamble_parts.append(line)
        elif stripped and not stripped.startswith('@'):
            break
    
    return '\n'.join(preamble_parts) if preamble_parts else ''


def deduplicate_bibtex(input_file, output_file=None):
    """
    Main function to deduplicate a BibTeX file.
    
    Args:
        input_file (str): Path to input BibTeX file
        output_file (str, optional): Path to output file. If None, overwrites input.
    """
    if output_file is None:
        output_file = input_file
    
    # Read input file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    # Extract preamble and comments
    preamble = extract_preamble_and_comments(content)
    
    # Parse entries
    entries = parse_bibtex_entries(content)
    print(f"Total entries found: {len(entries)}")
    
    # Deduplicate
    deduplicated, duplicates = deduplicate_entries(entries)
    print(f"Unique entries: {len(deduplicated)}")
    print(f"Duplicates removed: {len(duplicates)}")
    
    # Write output
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write preamble if exists
            if preamble:
                f.write(preamble)
                f.write('\n\n')
            
            # Write deduplicated entries
            for i, (cite_key, entry) in enumerate(deduplicated.items()):
                f.write(entry)
                # Add newline between entries
                if i < len(deduplicated) - 1:
                    f.write('\n\n')
        
        print(f"\nDeduplicated bibliography written to: {output_file}")
        
        if duplicates:
            print(f"\nDuplicate keys removed:")
            for dup in duplicates:
                print(f"  - {dup}")
    
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: python deduplication_bib.py input.bib [output.bib]")
        print("\nIf output file is not specified, input file will be overwritten.")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    deduplicate_bibtex(input_file, output_file)


if __name__ == '__main__':
    main()
