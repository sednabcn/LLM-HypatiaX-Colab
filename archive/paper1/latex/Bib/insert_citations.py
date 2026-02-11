#!/usr/bin/env python3
"""
Automated Citation Insertion for LaTeX Documents

This script intelligently inserts citations from new_entries.bib into
your LaTeX document based on contextual relevance.

Features:
- Scans LaTeX for keywords matching bibliography topics
- Suggests citation placements with confidence scores
- Generates properly formatted \citep{} or \citet{} commands
- Handles multiple citation styles (author-year, numeric)
- Creates diff preview before modifying files

Usage:
    python insert_citations.py --latex paper.tex --bib new_entries.bib --output paper_cited.tex
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class Citation:
    """Represents a potential citation insertion point"""

    key: str
    line_number: int
    context: str
    confidence: float
    citation_style: str  # 'citep' or 'citet'
    reason: str

    def __str__(self):
        return (
            f"Line {self.line_number}: \\{self.citation_style}{{{self.key}}} "
            f"(confidence: {self.confidence:.2f})\n"
            f"  Context: {self.context[:70]}...\n"
            f"  Reason: {self.reason}"
        )


@dataclass
class BibEntry:
    """Simplified bibliography entry for citation matching"""

    key: str
    title: str
    author: str
    year: str
    keywords: Set[str] = field(default_factory=set)
    abstract: str = ""

    @classmethod
    def from_bibtex(cls, key: str, fields: Dict[str, str]):
        """Create BibEntry from parsed BibTeX fields"""
        title = fields.get("title", "")
        author = fields.get("author", "")
        year = fields.get("year", "")

        # Extract keywords from title, abstract, journal
        keywords = set()
        for text in [title, fields.get("abstract", ""), fields.get("journal", "")]:
            # Remove common words and extract significant terms
            words = re.findall(r"\b[a-z]{4,}\b", text.lower())
            keywords.update(words)

        # Remove stopwords
        stopwords = {
            "from",
            "with",
            "that",
            "this",
            "were",
            "have",
            "been",
            "their",
            "which",
            "about",
            "other",
            "into",
            "through",
        }
        keywords = keywords - stopwords

        return cls(
            key=key,
            title=title,
            author=author,
            year=year,
            keywords=keywords,
            abstract=fields.get("abstract", ""),
        )


class CitationMatcher:
    """Match bibliography entries to LaTeX content"""

    # High-value keywords that strongly suggest citation need
    STRONG_KEYWORDS = {
        "neural networks",
        "deep learning",
        "machine learning",
        "symbolic regression",
        "extrapolation",
        "generalization",
        "physics-informed",
        "language models",
        "llm",
        "gpt",
        "transformer",
        "reasoning",
        "discovery",
        "scientific",
        "dimensional analysis",
        "pareto",
        "genetic programming",
        "evolutionary",
        "interpretability",
        "explainability",
        "uncertainty",
        "calibration",
    }

    def __init__(self, bibliography: Dict[str, BibEntry]):
        self.bibliography = bibliography
        self.keyword_index = self._build_keyword_index()

    def _build_keyword_index(self) -> Dict[str, List[str]]:
        """Build reverse index: keyword -> list of citation keys"""
        index = defaultdict(list)

        for key, entry in self.bibliography.items():
            for keyword in entry.keywords:
                index[keyword].append(key)

        return index

    def find_citations(self, latex_content: str) -> List[Citation]:
        """Find potential citation insertion points in LaTeX document"""

        citations = []
        lines = latex_content.split("\n")

        # Track existing citations to avoid duplicates
        existing_citations = set(re.findall(r"\\cite[tp]?\{([^}]+)\}", latex_content))

        for line_num, line in enumerate(lines, start=1):
            # Skip comments and already-cited lines
            if line.strip().startswith("%"):
                continue

            # Skip lines that already have citations
            if "\\cite" in line:
                continue

            # Skip non-prose content (tables, figures, equations)
            if any(
                cmd in line for cmd in ["\\begin{", "\\end{", "\\caption", "\\label"]
            ):
                continue

            # Look for strong keyword matches
            line_lower = line.lower()

            for keyword in self.STRONG_KEYWORDS:
                if keyword in line_lower:
                    # Find relevant citations
                    relevant_keys = self._find_relevant_citations(
                        keyword, existing_citations
                    )

                    for key in relevant_keys:
                        # Determine citation style
                        citation_style = self._determine_citation_style(line)

                        # Calculate confidence based on context
                        confidence = self._calculate_confidence(line, keyword, key)

                        if confidence > 0.3:  # Only suggest if reasonably confident
                            citation = Citation(
                                key=key,
                                line_number=line_num,
                                context=line.strip(),
                                confidence=confidence,
                                citation_style=citation_style,
                                reason=f"Matched keyword: '{keyword}'",
                            )
                            citations.append(citation)

        # Sort by confidence (highest first)
        citations.sort(key=lambda c: c.confidence, reverse=True)

        return citations

    def _find_relevant_citations(self, keyword: str, existing: Set[str]) -> List[str]:
        """Find bibliography entries relevant to keyword"""

        candidates = []

        for key, entry in self.bibliography.items():
            if key in existing:
                continue  # Already cited

            # Check if keyword appears in entry's keywords or title
            if keyword in entry.keywords or keyword in entry.title.lower():
                candidates.append(key)

        return candidates[:3]  # Limit to top 3 matches

    def _determine_citation_style(self, line: str) -> str:
        """Determine whether to use \citep{} or \citet{}"""

        # Use \citet{} if line contains author-subject pattern
        # e.g., "Smith showed that..." or "Recent work by..."
        if re.search(
            r"\b(showed|demonstrated|found|proposed|developed|presented)\b", line, re.I
        ):
            return "citet"

        # Use \citep{} for general statements
        return "citep"

    def _calculate_confidence(
        self, line: str, keyword: str, citation_key: str
    ) -> float:
        """Calculate confidence score for citation placement"""

        confidence = 0.5  # Base confidence

        entry = self.bibliography[citation_key]

        # Boost if multiple keywords match
        line_lower = line.lower()
        keyword_matches = sum(1 for kw in entry.keywords if kw in line_lower)
        confidence += 0.1 * min(keyword_matches, 3)

        # Boost if in introduction or related work section
        if "recent" in line_lower or "prior" in line_lower or "existing" in line_lower:
            confidence += 0.2

        # Boost if author name appears in text
        author_last = entry.author.split()[-1] if entry.author else ""
        if author_last.lower() in line_lower:
            confidence += 0.3

        # Penalize if line is very short (likely a heading)
        if len(line.strip()) < 30:
            confidence -= 0.3

        return min(1.0, max(0.0, confidence))


class LatexCitationInserter:
    """Insert citations into LaTeX document"""

    def __init__(self, latex_path: Path):
        self.latex_path = latex_path
        with open(latex_path, "r", encoding="utf-8") as f:
            self.content = f.read()
        self.lines = self.content.split("\n")

    def insert_citation(self, citation: Citation) -> None:
        """Insert a single citation at specified line"""

        line_idx = citation.line_number - 1
        if line_idx >= len(self.lines):
            return

        line = self.lines[line_idx]

        # Find best insertion point (end of sentence or clause)
        insertion_point = self._find_insertion_point(line)

        # Format citation
        cite_cmd = f"\\{citation.citation_style}{{{citation.key}}}"

        # Insert citation
        modified_line = line[:insertion_point] + cite_cmd + line[insertion_point:]
        self.lines[line_idx] = modified_line

    def _find_insertion_point(self, line: str) -> int:
        """Find best position to insert citation in line"""

        # Prefer end of sentence
        sentence_end = line.rfind(".")
        if sentence_end > 0 and sentence_end < len(line) - 5:
            return sentence_end

        # Otherwise, insert before period
        period = line.rfind(".")
        if period > 0:
            return period

        # Last resort: end of line
        return len(line.rstrip())

    def generate_diff(self, original_content: str) -> str:
        """Generate human-readable diff"""

        original_lines = original_content.split("\n")
        modified_lines = self.lines

        diff = []
        diff.append("=" * 80)
        diff.append("CITATION INSERTION DIFF")
        diff.append("=" * 80)
        diff.append("")

        for i, (orig, mod) in enumerate(zip(original_lines, modified_lines), start=1):
            if orig != mod:
                diff.append(f"Line {i}:")
                diff.append(f"  - {orig}")
                diff.append(f"  + {mod}")
                diff.append("")

        return "\n".join(diff)

    def save(self, output_path: Path) -> None:
        """Save modified LaTeX document"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.lines))


def parse_bibliography(bib_path: Path) -> Dict[str, BibEntry]:
    """Parse new_entries.bib into structured format"""

    with open(bib_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse BibTeX entries
    entry_pattern = r"@(\w+)\{([^,]+),\s*(.*?)\n\}"
    field_pattern = r"(\w+)\s*=\s*\{([^}]*)\}"

    entries = {}

    for match in re.finditer(entry_pattern, content, re.DOTALL):
        key = match.group(2).strip()
        fields_text = match.group(3)

        fields = {}
        for field_match in re.finditer(field_pattern, fields_text):
            field_name = field_match.group(1).lower()
            field_value = field_match.group(2).strip()
            fields[field_name] = field_value

        entries[key] = BibEntry.from_bibtex(key, fields)

    return entries


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Automatically insert citations into LaTeX document"
    )
    parser.add_argument("--latex", default="paper.tex", help="LaTeX source file")
    parser.add_argument(
        "--bib", default="new_entries.bib", help="Bibliography with new entries"
    )
    parser.add_argument(
        "--output", default="paper_cited.tex", help="Output LaTeX file with citations"
    )
    parser.add_argument(
        "--diff", default="citation_diff.txt", help="Diff file showing changes"
    )
    parser.add_argument(
        "--threshold", type=float, default=0.5, help="Confidence threshold (0-1)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show suggestions without modifying file"
    )

    args = parser.parse_args()

    # Check files exist
    latex_path = Path(args.latex)
    bib_path = Path(args.bib)

    if not latex_path.exists():
        print(f"ERROR: {args.latex} not found")
        sys.exit(1)

    if not bib_path.exists():
        print(f"ERROR: {args.bib} not found")
        sys.exit(1)

    # Parse bibliography
    print("Parsing bibliography...")
    bibliography = parse_bibliography(bib_path)
    print(f"Found {len(bibliography)} new entries")

    # Read LaTeX content
    with open(latex_path, "r", encoding="utf-8") as f:
        latex_content = f.read()

    # Find citation opportunities
    print("Analyzing LaTeX document...")
    matcher = CitationMatcher(bibliography)
    citations = matcher.find_citations(latex_content)

    # Filter by confidence threshold
    citations = [c for c in citations if c.confidence >= args.threshold]

    print(f"\nFound {len(citations)} potential citation placements:")
    print("=" * 80)

    for i, citation in enumerate(citations[:20], start=1):  # Show top 20
        print(f"\n{i}. {citation}")

    if len(citations) > 20:
        print(f"\n... and {len(citations) - 20} more")

    # Insert citations (if not dry-run)
    if not args.dry_run:
        print("\nInserting citations...")
        inserter = LatexCitationInserter(latex_path)

        for citation in citations:
            inserter.insert_citation(citation)

        # Generate diff
        diff = inserter.generate_diff(latex_content)
        with open(args.diff, "w") as f:
            f.write(diff)
        print(f"✓ Diff saved to: {args.diff}")

        # Save modified file
        output_path = Path(args.output)
        inserter.save(output_path)
        print(f"✓ Modified LaTeX saved to: {args.output}")

        print(f"\nNext steps:")
        print(f"1. Review {args.diff} to verify changes")
        print(f"2. Compile {args.output} to check formatting")
        print(f"3. Manually adjust citations as needed")
    else:
        print("\n[DRY RUN] No files modified. Remove --dry-run to apply changes.")

    return 0


if __name__ == "__main__":
    sys.exit(main())


"""
# Dry-run (preview only)
python3 insert_citations.py \
    --latex jmlr_paper.tex \
    --bib new_entries.bib \
    --dry-run

# Apply citations
python3 insert_citations.py \
    --latex jmlr_paper.tex \
    --bib new_entries.bib \
    --output paper_cited.tex \
    --threshold 0.5

"""
