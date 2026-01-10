"""
Enhanced formatting for HybridDiscoverySystem results
Provides beautiful output for discovery, validation, and interpretation
"""

import json
from typing import Dict, List, Optional

from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class HybridFormatter:
    """Format hybrid discovery system results."""

    def __init__(self):
        self.console = Console()

    def format_result(self, result: Dict, show_full: bool = True):
        """
        Display a complete result with discovery, validation, and interpretation.

        Args:
            result: Result dictionary from hybrid system
            show_full: If True, show full details; if False, show summary only
        """
        if show_full:
            self._display_full_result(result)
        else:
            self._display_summary(result)

    def _display_full_result(self, result: Dict):
        """Display complete result with all sections."""

        # Header with metadata
        self._display_header(result)

        # Discovery section
        self._display_discovery(result.get("discovery", {}))

        # Validation section
        self._display_validation(result.get("validation", {}))

        # Interpretation section
        if result.get("interpretation"):
            self._display_interpretation(result.get("interpretation", {}))

    def _display_header(self, result: Dict):
        """Display header with metadata."""
        metadata = result.get("metadata", {})
        description = result.get("description", "Unnamed Discovery")

        header_text = f"[bold cyan]{description}[/bold cyan]\n"
        header_text += f"Domain: [green]{result.get('domain', 'N/A').upper()}[/green]\n"
        header_text += f"Timestamp: {result.get('timestamp', 'N/A')}\n"
        header_text += f"Samples: {metadata.get('n_samples', 'N/A')} | "
        header_text += f"Features: {metadata.get('n_features', 'N/A')}"

        self.console.print(
            Panel(
                header_text,
                title="[bold]Discovery Report[/bold]",
                border_style="blue",
                padding=(1, 2),
            )
        )

    def _display_discovery(self, discovery: Dict):
        """Display discovery results."""
        if not discovery:
            return

        expr = discovery.get("expression", "N/A")
        r2 = discovery.get("r2_score", 0)
        complexity = discovery.get("complexity", "N/A")

        # Expression panel
        expr_text = Text()
        expr_text.append(expr, style="bold yellow")

        self.console.print("\n")
        self.console.print(
            Panel(
                expr_text,
                title="[bold green]🔍 Discovered Expression[/bold green]",
                border_style="green",
                padding=(1, 2),
            )
        )

        # Metrics table
        metrics_table = Table(show_header=False, box=box.SIMPLE)
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="yellow")

        # R² score with color coding
        r2_color = "green" if r2 >= 0.95 else "yellow" if r2 >= 0.85 else "red"
        metrics_table.add_row("R² Score", f"[{r2_color}]{r2:.4f}[/{r2_color}]")
        metrics_table.add_row("Complexity", str(complexity))

        self.console.print(metrics_table)

    def _display_validation(self, validation: Dict):
        """Display validation results."""
        if not validation:
            return

        self.console.print("\n")

        # Overall validation status
        valid = validation.get("valid", False)
        total_score = validation.get("total_score", 0)

        status_symbol = "✓" if valid else "✗"
        status_color = "green" if valid else "red"

        status_text = f"[{status_color}]{status_symbol} Overall Score: {total_score:.1f}/100[/{status_color}]"

        self.console.print(
            Panel(
                status_text,
                title="[bold]✓ Validation Results[/bold]",
                border_style=status_color,
                padding=(0, 2),
            )
        )

        # Layer scores table
        layer_scores = validation.get("layer_scores", {})
        if layer_scores:
            self.console.print("\n[bold]Layer Scores:[/bold]")
            scores_table = Table(box=box.ROUNDED)
            scores_table.add_column("Layer", style="cyan")
            scores_table.add_column("Score", justify="right")
            scores_table.add_column("Status", justify="center")

            for layer, score in layer_scores.items():
                # Color based on score
                if score >= 90:
                    score_color = "green"
                    symbol = "✓"
                elif score >= 70:
                    score_color = "yellow"
                    symbol = "⚠"
                else:
                    score_color = "red"
                    symbol = "✗"

                scores_table.add_row(
                    layer.capitalize(),
                    f"[{score_color}]{score:.1f}[/{score_color}]",
                    f"[{score_color}]{symbol}[/{score_color}]",
                )

            self.console.print(scores_table)

        # Errors
        errors = validation.get("errors", [])
        if errors:
            self.console.print("\n[bold red]⚠ Errors:[/bold red]")
            for i, error in enumerate(errors[:5], 1):
                self.console.print(f"  {i}. {error}", style="red")
            if len(errors) > 5:
                self.console.print(f"  ... and {len(errors) - 5} more", style="dim")

        # Warnings
        warnings = validation.get("warnings", [])
        if warnings:
            self.console.print("\n[bold yellow]ℹ Warnings:[/bold yellow]")
            for i, warning in enumerate(warnings[:5], 1):
                self.console.print(f"  {i}. {warning}", style="yellow")
            if len(warnings) > 5:
                self.console.print(f"  ... and {len(warnings) - 5} more", style="dim")

        # Recommendations
        recommendations = validation.get("recommendations", [])
        if recommendations:
            self.console.print("\n[bold blue]💡 Recommendations:[/bold blue]")
            for i, rec in enumerate(recommendations[:5], 1):
                self.console.print(f"  {i}. {rec}", style="blue")
            if len(recommendations) > 5:
                self.console.print(
                    f"  ... and {len(recommendations) - 5} more", style="dim"
                )

    def _display_interpretation(self, interpretation: Dict):
        """Display LLM interpretation."""
        if not interpretation or interpretation.get("status") == "unparsed":
            return

        self.console.print("\n")
        self.console.print(
            Panel("[bold]🤖 AI Interpretation[/bold]", border_style="magenta")
        )

        sections = [
            ("interpretation", "🔍 Interpretation", "green"),
            ("analogies", "🔗 Known Analogies", "blue"),
            ("novelty", "✨ Novel Aspects", "magenta"),
            ("predictions", "🎯 Predictions", "yellow"),
            ("limitations", "⚠️ Limitations", "red"),
        ]

        for key, title, color in sections:
            content = interpretation.get(key)
            if content:
                self.console.print(f"\n[bold {color}]{title}[/bold {color}]")
                self.console.print(content, style="white")

    def _display_summary(self, result: Dict):
        """Display compact summary of result."""
        discovery = result.get("discovery", {})
        validation = result.get("validation", {})

        expr = discovery.get("expression", "N/A")
        r2 = discovery.get("r2_score", 0)
        val_score = validation.get("total_score", 0)
        valid = validation.get("valid", False)

        status = "✓ VALID" if valid else "✗ INVALID"
        status_color = "green" if valid else "red"

        summary = f"""[bold cyan]{result.get('description', 'Discovery')}[/bold cyan]
Expression: [yellow]{expr}[/yellow]
R²: {r2:.4f} | Validation: {val_score:.1f}/100 | [{status_color}]{status}[/{status_color}]"""

        self.console.print(Panel(summary, border_style="blue", padding=(0, 2)))

    def compare_results(self, results: List[Dict], top_n: int = 10):
        """
        Display comparison table of multiple results.

        Args:
            results: List of result dictionaries
            top_n: Number of top results to show
        """
        if not results:
            self.console.print("[yellow]No results to compare[/yellow]")
            return

        table = Table(
            title=f"Top {min(top_n, len(results))} Discovery Results", box=box.ROUNDED
        )

        table.add_column("Rank", justify="center", style="cyan")
        table.add_column("Expression", style="yellow", no_wrap=False, max_width=40)
        table.add_column("R²", justify="right", style="green")
        table.add_column("Val", justify="right", style="blue")
        table.add_column("Status", justify="center")
        table.add_column("Domain", style="magenta")

        # Sort by validation score, then R²
        sorted_results = sorted(
            results,
            key=lambda x: (
                x.get("validation", {}).get("total_score", 0),
                x.get("discovery", {}).get("r2_score", 0),
            ),
            reverse=True,
        )[:top_n]

        for i, result in enumerate(sorted_results, 1):
            discovery = result.get("discovery", {})
            validation = result.get("validation", {})

            expr = discovery.get("expression", "N/A")
            if len(expr) > 40:
                expr = expr[:37] + "..."

            r2 = discovery.get("r2_score", 0)
            val_score = validation.get("total_score", 0)
            valid = validation.get("valid", False)

            status = "✓" if valid else "✗"
            status_color = "green" if valid else "red"

            table.add_row(
                str(i),
                expr,
                f"{r2:.4f}",
                f"{val_score:.1f}",
                f"[{status_color}]{status}[/{status_color}]",
                result.get("domain", "N/A").upper(),
            )

        self.console.print(table)

    def export_markdown(self, result: Dict, filepath: str):
        """Export result to markdown file."""
        discovery = result.get("discovery", {})
        validation = result.get("validation", {})
        interpretation = result.get("interpretation", {})

        md = f"""# {result.get('description', 'Discovery Report')}

**Domain:** {result.get('domain', 'N/A').upper()}
**Timestamp:** {result.get('timestamp', 'N/A')}

---

## 🔍 Discovered Expression

```
{discovery.get('expression', 'N/A')}
```

### Metrics
- **R² Score:** {discovery.get('r2_score', 0):.4f}
- **Complexity:** {discovery.get('complexity', 'N/A')}

---

## ✓ Validation Results

**Overall Score:** {validation.get('total_score', 0):.1f}/100
**Status:** {"✓ VALID" if validation.get('valid') else "✗ INVALID"}

### Layer Scores
"""

        for layer, score in validation.get("layer_scores", {}).items():
            symbol = "✓" if score >= 70 else "⚠" if score >= 50 else "✗"
            md += f"- {symbol} **{layer.capitalize()}:** {score:.1f}/100\n"

        if validation.get("errors"):
            md += "\n### ⚠ Errors\n"
            for error in validation["errors"]:
                md += f"- {error}\n"

        if validation.get("warnings"):
            md += "\n### ℹ Warnings\n"
            for warning in validation["warnings"]:
                md += f"- {warning}\n"

        if interpretation and interpretation.get("interpretation"):
            md += "\n---\n\n## 🤖 AI Interpretation\n\n"

            sections = [
                ("interpretation", "### 🔍 Interpretation"),
                ("analogies", "### 🔗 Known Analogies"),
                ("novelty", "### ✨ Novel Aspects"),
                ("predictions", "### 🎯 Predictions"),
                ("limitations", "### ⚠️ Limitations"),
            ]

            for key, title in sections:
                content = interpretation.get(key)
                if content:
                    md += f"\n{title}\n\n{content}\n"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md)

        self.console.print(f"[green]✓ Exported to {filepath}[/green]")

    def export_html(self, result: Dict, filepath: str):
        """Export result to beautiful HTML file."""
        discovery = result.get("discovery", {})
        validation = result.get("validation", {})
        interpretation = result.get("interpretation", {})

        valid = validation.get("valid", False)
        status_color = "#4CAF50" if valid else "#F44336"

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{result.get('description', 'Discovery Report')}</title>
    <style>
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        .container {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }}
        h1 {{
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 15px;
        }}
        .metadata {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        .metadata-item {{
            display: flex;
            flex-direction: column;
        }}
        .metadata-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }}
        .metadata-value {{
            font-size: 18px;
            font-weight: bold;
            color: #667eea;
        }}
        .expression {{
            background: #2d3748;
            color: #f7fafc;
            padding: 30px;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            font-size: 24px;
            margin: 30px 0;
            border-left: 5px solid #667eea;
            overflow-x: auto;
        }}
        .section {{
            margin: 30px 0;
            padding: 25px;
            border-radius: 10px;
            border-left: 4px solid;
        }}
        .section-title {{
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }}
        .section-title .emoji {{
            margin-right: 10px;
            font-size: 28px;
        }}
        .validation {{
            background: #f0fdf4;
            border-left-color: {status_color};
        }}
        .validation .status {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            background: {status_color};
            color: white;
            font-weight: bold;
            margin: 10px 0;
        }}
        .scores {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .score-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .score-card .score {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }}
        .score-card .label {{
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }}
        .interpretation {{ background: #fef3c7; border-left-color: #f59e0b; }}
        .analogies {{ background: #dbeafe; border-left-color: #3b82f6; }}
        .novelty {{ background: #fae8ff; border-left-color: #a855f7; }}
        .predictions {{ background: #fef3c7; border-left-color: #eab308; }}
        .limitations {{ background: #fee2e2; border-left-color: #ef4444; }}
        .error-list, .warning-list {{
            list-style: none;
            padding: 0;
        }}
        .error-list li, .warning-list li {{
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
        }}
        .error-list li {{
            background: #fee;
            border-left: 3px solid #f44336;
        }}
        .warning-list li {{
            background: #fffbeb;
            border-left: 3px solid #f59e0b;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{result.get('description', 'Discovery Report')}</h1>

        <div class="metadata">
            <div class="metadata-item">
                <span class="metadata-label">Domain</span>
                <span class="metadata-value">{result.get('domain', 'N/A').upper()}</span>
            </div>
            <div class="metadata-item">
                <span class="metadata-label">Timestamp</span>
                <span class="metadata-value">{result.get('timestamp', 'N/A')[:10]}</span>
            </div>
            <div class="metadata-item">
                <span class="metadata-label">Samples</span>
                <span class="metadata-value">{result.get('metadata', {}).get('n_samples', 'N/A')}</span>
            </div>
        </div>

        <div class="section">
            <div class="section-title"><span class="emoji">🔍</span> Discovered Expression</div>
            <div class="expression">{discovery.get('expression', 'N/A')}</div>
            <div class="scores">
                <div class="score-card">
                    <div class="score">{discovery.get('r2_score', 0):.4f}</div>
                    <div class="label">R² Score</div>
                </div>
                <div class="score-card">
                    <div class="score">{discovery.get('complexity', 'N/A')}</div>
                    <div class="label">Complexity</div>
                </div>
            </div>
        </div>

        <div class="section validation">
            <div class="section-title"><span class="emoji">✓</span> Validation Results</div>
            <div class="status">{"✓ VALID" if valid else "✗ INVALID"}</div>
            <div class="scores">
"""

        for layer, score in validation.get("layer_scores", {}).items():
            html += f"""
                <div class="score-card">
                    <div class="score">{score:.1f}</div>
                    <div class="label">{layer.capitalize()}</div>
                </div>
"""

        html += """
            </div>
"""

        if validation.get("errors"):
            html += '<h4>⚠ Errors</h4><ul class="error-list">'
            for error in validation["errors"]:
                html += f"<li>{error}</li>"
            html += "</ul>"

        if validation.get("warnings"):
            html += '<h4>ℹ Warnings</h4><ul class="warning-list">'
            for warning in validation["warnings"]:
                html += f"<li>{warning}</li>"
            html += "</ul>"

        html += """
        </div>
"""

        if interpretation and interpretation.get("interpretation"):
            sections_html = [
                ("interpretation", "🔍 Interpretation", "interpretation"),
                ("analogies", "🔗 Known Analogies", "analogies"),
                ("novelty", "✨ Novel Aspects", "novelty"),
                ("predictions", "🎯 Predictions", "predictions"),
                ("limitations", "⚠️ Limitations", "limitations"),
            ]

            for key, title, css_class in sections_html:
                content = interpretation.get(key)
                if content:
                    html += f"""
        <div class="section {css_class}">
            <div class="section-title"><span class="emoji">{title.split()[0]}</span> {title.split(maxsplit=1)[1]}</div>
            <p>{content}</p>
        </div>
"""

        html += """
    </div>
</body>
</html>
"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        self.console.print(f"[green]✓ Exported to {filepath}[/green]")


# Integration example
if __name__ == "__main__":
    # Sample result (like from your hybrid system)
    sample_result = {
        "timestamp": "2025-01-15T10:30:00",
        "description": "AMM Constant Product Formula Discovery",
        "domain": "defi",
        "discovery": {
            "expression": "sqrt(reserve0*reserve1)",
            "r2_score": 0.9995,
            "complexity": 4,
        },
        "validation": {
            "valid": False,
            "total_score": 89.0,
            "layer_scores": {
                "symbolic": 98.0,
                "dimensional": 65.0,
                "domain": 95.0,
                "numerical": 100.0,
            },
            "errors": [
                "Invalid unit for 'reserve0': 'USD' - 'USD' is not defined in the unit registry",
                "Invalid unit for 'reserve1': 'USD' - 'USD' is not defined in the unit registry",
            ],
            "warnings": [
                "Check AMM constant product invariant preservation",
                "Fractional exponent (1/2) - verify dimensional consistency",
                "Variable 'reserve' should be positive - add validation",
            ],
            "recommendations": [
                "FIX CRITICAL: Resolve dimensional inconsistencies",
                "REVIEW: Address domain-specific warnings for defi",
            ],
        },
        "interpretation": {
            "interpretation": "This expression represents the geometric mean of two token reserves, which is the fundamental constant product invariant used in Automated Market Makers (AMMs) like Uniswap.",
            "analogies": "Similar to the geometric mean in statistics and the constant product formula x*y=k in AMM protocols.",
            "novelty": "Direct application of geometric mean to liquidity pool reserves with high predictive accuracy.",
            "predictions": "Can be used to calculate pool invariants, predict price impact, and optimize liquidity provision strategies.",
            "limitations": "Assumes constant product model; may not apply to other AMM designs like Curve's stableswap.",
        },
        "metadata": {"n_samples": 100, "n_features": 2},
    }

    formatter = HybridFormatter()

    # Display full result
    formatter.format_result(sample_result)

    # Export to files
    formatter.export_markdown(sample_result, "/tmp/discovery_report.md")
    formatter.export_html(sample_result, "/tmp/discovery_report.html")

    print("\n")
    formatter.console.print(
        "[bold green]✓ Demo complete! Check /tmp for exported files[/bold green]"
    )
