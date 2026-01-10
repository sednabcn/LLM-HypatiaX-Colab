"""
HypatiaX UI Components - Reusable UI building blocks
Provides rich console output, visualizations, and interactive components
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


class Colors:
    """ANSI color codes for terminal output"""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


class UIComponents:
    """Collection of reusable UI components"""

    @staticmethod
    def header(text: str, width: int = 80, char: str = "=") -> str:
        """Create a formatted header"""
        return f"\n{char * width}\n{text.center(width)}\n{char * width}\n"

    @staticmethod
    def subheader(text: str, width: int = 80, char: str = "-") -> str:
        """Create a formatted subheader"""
        return f"\n{text}\n{char * width}\n"

    @staticmethod
    def box(
        text: str, width: int = 80, padding: int = 2, border_char: str = "│"
    ) -> str:
        """Create a text box"""
        lines = text.split("\n")
        top = "┌" + "─" * (width - 2) + "┐"
        bottom = "└" + "─" * (width - 2) + "┘"

        content = []
        for line in lines:
            padded = " " * padding + line + " " * padding
            padded = padded.ljust(width - 2)
            content.append(f"{border_char}{padded}{border_char}")

        return "\n".join([top] + content + [bottom])

    @staticmethod
    def table(
        headers: List[str],
        rows: List[List[Any]],
        col_widths: Optional[List[int]] = None,
    ) -> str:
        """Create a formatted table"""
        if not col_widths:
            col_widths = [
                max(len(str(row[i])) for row in [headers] + rows) + 2
                for i in range(len(headers))
            ]

        # Create separator
        separator = "+" + "+".join("-" * width for width in col_widths) + "+"

        # Format header
        header_row = (
            "|"
            + "|".join(str(h).center(col_widths[i]) for i, h in enumerate(headers))
            + "|"
        )

        # Format rows
        data_rows = []
        for row in rows:
            data_row = (
                "|"
                + "|".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
                + "|"
            )
            data_rows.append(data_row)

        return "\n".join([separator, header_row, separator] + data_rows + [separator])

    @staticmethod
    def progress_bar(
        current: int, total: int, width: int = 50, prefix: str = "", suffix: str = ""
    ) -> str:
        """Create a progress bar"""
        percent = current / total if total > 0 else 0
        filled = int(width * percent)
        bar = "█" * filled + "░" * (width - filled)

        return f"{prefix}[{bar}] {percent:.1%} {suffix}"

    @staticmethod
    def entity_visualization(
        text: str, entities: List[Dict[str, Any]], use_colors: bool = True
    ) -> str:
        """Visualize entities in text with colors/highlighting"""
        if not use_colors:
            # Simple bracket notation
            result = text
            for entity in sorted(entities, key=lambda e: e["start"], reverse=True):
                result = (
                    result[: entity["start"]]
                    + f"[{entity['text']}:{entity['label']}]"
                    + result[entity["end"] :]
                )
            return result

        # Color-coded visualization
        entity_colors = {
            "OPER": Colors.BRIGHT_MAGENTA,
            "ARG": Colors.BRIGHT_CYAN,
            "VERB": Colors.BRIGHT_GREEN,
            "NOUN": Colors.BRIGHT_BLUE,
            "ADP": Colors.BRIGHT_YELLOW,
            "NUM": Colors.BRIGHT_RED,
        }

        result = ""
        last_pos = 0

        for entity in sorted(entities, key=lambda e: e["start"]):
            # Add text before entity
            result += text[last_pos : entity["start"]]

            # Add colored entity
            color = entity_colors.get(entity["label"], Colors.WHITE)
            result += (
                f"{color}{Colors.BOLD}{entity['text']}{Colors.RESET}"
                f"{Colors.DIM}[{entity['label']}]{Colors.RESET}"
            )

            last_pos = entity["end"]

        # Add remaining text
        result += text[last_pos:]

        return result

    @staticmethod
    def formula_display(
        formula: str, confidence: float, use_colors: bool = True
    ) -> str:
        """Display formula with confidence indicator"""
        if not use_colors:
            return f"Formula: {formula} (Confidence: {confidence:.1%})"

        # Color based on confidence
        if confidence >= 0.9:
            color = Colors.BRIGHT_GREEN
        elif confidence >= 0.7:
            color = Colors.BRIGHT_YELLOW
        else:
            color = Colors.BRIGHT_RED

        conf_bar = "█" * int(confidence * 10) + "░" * (10 - int(confidence * 10))

        return (
            f"{Colors.BOLD}Formula:{Colors.RESET} "
            f"{Colors.BRIGHT_CYAN}{formula}{Colors.RESET}\n"
            f"{Colors.BOLD}Confidence:{Colors.RESET} "
            f"{color}{conf_bar} {confidence:.1%}{Colors.RESET}"
        )

    @staticmethod
    def metric_cards(metrics: Dict[str, Any], columns: int = 4) -> str:
        """Display metrics in card format"""
        cards = []
        for key, value in metrics.items():
            card = (
                "┌─────────────────┐\n"
                f"│ {str(value).center(15)} │\n"
                f"│ {key.replace('_', ' ').title().center(15)} │\n"
                "└─────────────────┘"
            )
            cards.append(card)

        # Arrange cards in grid
        result = []
        for i in range(0, len(cards), columns):
            row_cards = cards[i : i + columns]
            # Split each card into lines and zip them
            lines = [card.split("\n") for card in row_cards]
            for line_group in zip(*lines):
                result.append("  ".join(line_group))
            result.append("")  # Empty line between rows

        return "\n".join(result)

    @staticmethod
    def comparison_table(
        results: List[Dict[str, Any]], show_entities: bool = False
    ) -> str:
        """Create comparison table for multiple methods"""
        headers = ["Method", "Formula", "Confidence", "Time (ms)"]
        if show_entities:
            headers.append("Entities")

        rows = []
        for result in results:
            row = [
                result["method"],
                result["formula"],
                f"{result['confidence']:.1%}",
                f"{result.get('processing_time', 0):.2f}",
            ]
            if show_entities:
                row.append(str(result.get("entity_count", 0)))
            rows.append(row)

        return UIComponents.table(headers, rows)

    @staticmethod
    def menu(title: str, options: List[str], show_numbers: bool = True) -> str:
        """Create an interactive menu"""
        lines = [f"\n{Colors.BOLD}{title}{Colors.RESET}\n"]

        for i, option in enumerate(options, 1):
            if show_numbers:
                lines.append(f"  {Colors.BRIGHT_CYAN}[{i}]{Colors.RESET} {option}")
            else:
                lines.append(f"  • {option}")

        return "\n".join(lines) + "\n"

    @staticmethod
    def status_message(
        message: str, status: str = "info", use_icons: bool = True
    ) -> str:
        """Display a status message"""
        icons = {
            "success": "✓",
            "error": "✗",
            "warning": "⚠",
            "info": "ℹ",
            "processing": "⟳",
        }

        colors = {
            "success": Colors.BRIGHT_GREEN,
            "error": Colors.BRIGHT_RED,
            "warning": Colors.BRIGHT_YELLOW,
            "info": Colors.BRIGHT_BLUE,
            "processing": Colors.BRIGHT_CYAN,
        }

        icon = icons.get(status, "•")
        color = colors.get(status, Colors.WHITE)

        if use_icons:
            return f"{color}{icon}{Colors.RESET} {message}"
        else:
            return f"{color}[{status.upper()}]{Colors.RESET} {message}"

    @staticmethod
    def divider(width: int = 80, char: str = "─") -> str:
        """Create a horizontal divider"""
        return char * width


class InteractiveDemo:
    """Interactive demo runner with rich UI"""

    def __init__(self, engine):
        """
        Initialize interactive demo

        Args:
            engine: HypatiaXEngine instance
        """
        self.engine = engine
        self.ui = UIComponents()
        self.history: List[Dict[str, Any]] = []

    def run(self):
        """Run interactive demo loop"""
        print(self.ui.header("🚀 HypatiaX Interactive Demo", width=80))
        print(
            self.ui.status_message(
                "Welcome! Enter natural language queries to generate Tableau formulas.",
                "info",
            )
        )

        while True:
            print("\n" + self.ui.divider())
            print(
                self.ui.menu(
                    "Options:",
                    [
                        "Process a query",
                        "Compare methods",
                        "View history",
                        "Show statistics",
                        "Exit",
                    ],
                )
            )

            choice = input(f"{Colors.BRIGHT_CYAN}Your choice:{Colors.RESET} ").strip()

            if choice == "1":
                self._process_query()
            elif choice == "2":
                self._compare_methods()
            elif choice == "3":
                self._view_history()
            elif choice == "4":
                self._show_statistics()
            elif choice == "5":
                print(self.ui.status_message("Goodbye!", "success"))
                break
            else:
                print(self.ui.status_message("Invalid choice", "error"))

    def _process_query(self):
        """Process a single query"""
        query = input(f"\n{Colors.BRIGHT_CYAN}Enter query:{Colors.RESET} ").strip()

        if not query:
            print(self.ui.status_message("Empty query", "warning"))
            return

        print(self.ui.status_message("Processing...", "processing"))

        # Process query
        result = self.engine.process(query, method="vocab", use_model=False)

        # Display results
        print("\n" + self.ui.subheader("Results"))
        print(
            self.ui.entity_visualization(
                result.query,
                [
                    {"text": e.text, "label": e.label, "start": e.start, "end": e.end}
                    for e in result.entities
                ],
                use_colors=True,
            )
        )
        print("\n" + self.ui.formula_display(result.formula, result.confidence))

        # Save to history
        self.history.append(
            {
                "query": result.query,
                "formula": result.formula,
                "method": result.method,
                "confidence": result.confidence,
                "entity_count": len(result.entities),
                "processing_time": result.processing_time,
            }
        )

    def _compare_methods(self):
        """Compare multiple mapping methods"""
        query = input(
            f"\n{Colors.BRIGHT_CYAN}Enter query to compare:{Colors.RESET} "
        ).strip()

        if not query:
            print(self.ui.status_message("Empty query", "warning"))
            return

        methods = ["vocab", "sentence", "regex", "ner"]
        results = []

        print(self.ui.status_message("Comparing methods...", "processing"))

        for method in methods:
            result = self.engine.process(query, method=method, use_model=False)
            results.append(
                {
                    "method": method,
                    "formula": result.formula,
                    "confidence": result.confidence,
                    "processing_time": result.processing_time,
                    "entity_count": len(result.entities),
                }
            )

        print("\n" + self.ui.subheader("Method Comparison"))
        print(self.ui.comparison_table(results, show_entities=True))

    def _view_history(self):
        """View processing history"""
        if not self.history:
            print(self.ui.status_message("No history yet", "info"))
            return

        print("\n" + self.ui.subheader("Processing History"))
        print(self.ui.comparison_table(self.history[-10:]))  # Last 10

    def _show_statistics(self):
        """Show engine statistics"""
        stats = self.engine.get_stats()

        print("\n" + self.ui.subheader("Statistics"))
        print(
            self.ui.metric_cards(
                {
                    "Total Queries": stats["total_queries"],
                    "Successful": stats["successful_mappings"],
                    "Failed": stats["failed_mappings"],
                    "Avg Time (ms)": f"{stats['avg_processing_time']:.2f}",
                }
            )
        )


# Example usage
if __name__ == "__main__":
    from engine import HypatiaXEngine

    # Initialize components
    engine = HypatiaXEngine()
    ui = UIComponents()

    # Demo UI components
    print(ui.header("HypatiaX UI Components Demo"))

    print(ui.subheader("1. Status Messages"))
    print(ui.status_message("Processing completed successfully", "success"))
    print(ui.status_message("Connection failed", "error"))
    print(ui.status_message("Low confidence detected", "warning"))

    print(ui.subheader("2. Progress Bar"))
    for i in range(0, 101, 20):
        print(ui.progress_bar(i, 100, prefix="Loading", suffix=f"{i}/100"))

    print(ui.subheader("3. Entity Visualization"))
    sample_entities = [
        {"text": "sum", "label": "OPER", "start": 14, "end": 17},
        {"text": "sales", "label": "ARG", "start": 21, "end": 26},
    ]
    print(
        ui.entity_visualization("calculate the sum of sales by region", sample_entities)
    )

    print(ui.subheader("4. Formula Display"))
    print(ui.formula_display("SUM([Sales])", 0.95))

    print(ui.subheader("5. Metrics"))
    print(
        ui.metric_cards(
            {"Queries": 150, "Accuracy": "94%", "Avg Time": "12ms", "Success": "142"}
        )
    )
