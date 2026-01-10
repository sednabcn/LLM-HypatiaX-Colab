import json
from typing import Dict

import yaml
from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table


class InterpretationFormatter:
    """Format interpretation results for better readability."""

    def __init__(self):
        self.console = Console()

    def to_markdown(self, result: Dict) -> str:
        """Convert interpretation to markdown format."""
        md = f"""# Expression Interpretation

## Expression
```
{result['expression']}
```

**Domain:** {result['domain']}
**R² Score:** {result['r2_score']:.4f}

---

## Interpretation
{result.get('interpretation', 'N/A')}

---

## Known Analogies
{result.get('analogies', 'N/A')}

---

## Novel Aspects
{result.get('novelty', 'N/A')}

---

## Predictions & Use Cases
{result.get('predictions', 'N/A')}

---

## Limitations
{result.get('limitations', 'N/A')}
"""
        return md

    def to_rich_panel(self, result: Dict):
        """Display using rich library with panels and formatting."""
        # Header
        self.console.print(
            Panel(
                f"[bold cyan]{result['expression']}[/bold cyan]",
                title=f"[bold]Expression ({result['domain'].upper()})[/bold]",
                subtitle=f"R² = {result['r2_score']:.4f}",
                border_style="cyan",
            )
        )

        # Main sections
        sections = {
            "interpretation": ("🔍", "Interpretation", "green"),
            "analogies": ("🔗", "Known Analogies", "blue"),
            "novelty": ("✨", "Novel Aspects", "magenta"),
            "predictions": ("🎯", "Predictions", "yellow"),
            "limitations": ("⚠️", "Limitations", "red"),
        }

        for key, (emoji, title, color) in sections.items():
            if key in result:
                self.console.print(f"\n[bold {color}]{emoji} {title}[/bold {color}]")
                self.console.print(result[key])

    def to_html(self, result: Dict) -> str:
        """Convert to HTML format."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .expression {{
            background: #f0f0f0;
            padding: 20px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 18px;
            margin: 20px 0;
            border-left: 4px solid #2196F3;
        }}
        .metadata {{
            display: flex;
            gap: 20px;
            margin: 20px 0;
            padding: 15px;
            background: #e3f2fd;
            border-radius: 5px;
        }}
        .metadata-item {{
            display: flex;
            flex-direction: column;
        }}
        .metadata-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }}
        .metadata-value {{
            font-size: 16px;
            font-weight: bold;
            color: #1976D2;
        }}
        .section {{
            margin: 25px 0;
            padding: 20px;
            border-left: 3px solid #ddd;
        }}
        .section-title {{
            font-size: 20px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }}
        .section-content {{
            color: #555;
            line-height: 1.6;
        }}
        .interpretation {{ border-left-color: #4CAF50; }}
        .analogies {{ border-left-color: #2196F3; }}
        .novelty {{ border-left-color: #9C27B0; }}
        .predictions {{ border-left-color: #FF9800; }}
        .limitations {{ border-left-color: #F44336; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Expression Interpretation</h1>

        <div class="expression">{result['expression']}</div>

        <div class="metadata">
            <div class="metadata-item">
                <span class="metadata-label">Domain</span>
                <span class="metadata-value">{result['domain'].upper()}</span>
            </div>
            <div class="metadata-item">
                <span class="metadata-label">R² Score</span>
                <span class="metadata-value">{result['r2_score']:.4f}</span>
            </div>
        </div>

        <div class="section interpretation">
            <div class="section-title">🔍 Interpretation</div>
            <div class="section-content">{result.get('interpretation', 'N/A')}</div>
        </div>

        <div class="section analogies">
            <div class="section-title">🔗 Known Analogies</div>
            <div class="section-content">{result.get('analogies', 'N/A')}</div>
        </div>

        <div class="section novelty">
            <div class="section-title">✨ Novel Aspects</div>
            <div class="section-content">{result.get('novelty', 'N/A')}</div>
        </div>

        <div class="section predictions">
            <div class="section-title">🎯 Predictions & Use Cases</div>
            <div class="section-content">{result.get('predictions', 'N/A')}</div>
        </div>

        <div class="section limitations">
            <div class="section-title">⚠️ Limitations</div>
            <div class="section-content">{result.get('limitations', 'N/A')}</div>
        </div>
    </div>
</body>
</html>
"""
        return html

    def to_yaml(self, result: Dict) -> str:
        """Convert to YAML format (more readable than JSON)."""
        return yaml.dump(
            result, default_flow_style=False, allow_unicode=True, sort_keys=False
        )

    def to_table(self, results: list[Dict]):
        """Display multiple results in a comparison table."""
        table = Table(title="Expression Interpretations", box=box.ROUNDED)

        table.add_column("Expression", style="cyan", no_wrap=False, width=30)
        table.add_column("R²", justify="right", style="magenta")
        table.add_column("Domain", style="green")
        table.add_column("Key Insight", no_wrap=False, width=40)

        for result in results:
            insight = result.get("interpretation", "")[:100] + "..."
            table.add_row(
                result["expression"],
                f"{result['r2_score']:.4f}",
                result["domain"].upper(),
                insight,
            )

        self.console.print(table)

    def to_report(self, result: Dict) -> str:
        """Generate a formatted text report."""
        report = f"""
{'='*80}
EXPRESSION INTERPRETATION REPORT
{'='*80}

EXPRESSION:
  {result['expression']}

METADATA:
  Domain      : {result['domain'].upper()}
  R² Score    : {result['r2_score']:.4f}
  Status      : {'Parsed' if result.get('status') != 'unparsed' else 'Unparsed'}

{'─'*80}
INTERPRETATION
{'─'*80}
{result.get('interpretation', 'N/A')}

{'─'*80}
KNOWN ANALOGIES
{'─'*80}
{result.get('analogies', 'N/A')}

{'─'*80}
NOVEL ASPECTS
{'─'*80}
{result.get('novelty', 'N/A')}

{'─'*80}
PREDICTIONS & USE CASES
{'─'*80}
{result.get('predictions', 'N/A')}

{'─'*80}
LIMITATIONS
{'─'*80}
{result.get('limitations', 'N/A')}

{'='*80}
"""
        return report


# Example usage
if __name__ == "__main__":
    # Sample interpretation result
    result = {
        "interpretation": "This expression represents a normalized price performance metric that transforms price ratios into a bounded [-1, 1] range.",
        "analogies": "This resembles the hyperbolic tangent function used in neural networks for activation.",
        "novelty": "The specific combination of square root transformation with harmonic mean-like denominator is uncommon in DeFi metrics.",
        "predictions": "This metric could predict portfolio rebalancing triggers in automated market makers.",
        "limitations": "May fail during flash crashes or extreme volatility events where price_ratio approaches zero.",
        "expression": "2*sqrt(price_ratio)/(price_ratio + 1) - 1",
        "domain": "defi",
        "r2_score": 0.98,
    }

    formatter = InterpretationFormatter()

    # 1. Rich panel output (best for terminal)
    print("\n" + "=" * 80)
    print("OPTION 1: Rich Panel (Best for Terminal)")
    print("=" * 80)
    formatter.to_rich_panel(result)

    # 2. Markdown (best for documentation)
    print("\n" + "=" * 80)
    print("OPTION 2: Markdown (Best for Documentation)")
    print("=" * 80)
    md = formatter.to_markdown(result)
    print(md[:300] + "...\n")

    # 3. YAML (more readable than JSON)
    print("=" * 80)
    print("OPTION 3: YAML (More Readable than JSON)")
    print("=" * 80)
    print(formatter.to_yaml(result))

    # 4. Plain text report (best for logs)
    print("=" * 80)
    print("OPTION 4: Text Report (Best for Logs)")
    print("=" * 80)
    print(formatter.to_report(result)[:400] + "...\n")

    # 5. HTML (best for web/sharing)
    print("=" * 80)
    print("OPTION 5: HTML (Best for Web/Sharing)")
    print("=" * 80)
    print("HTML generated (save to file with .html extension)")

    # Save HTML example
    with open("/tmp/interpretation.html", "w", encoding="utf-8") as f:
        f.write(formatter.to_html(result))
    print("Saved to: /tmp/interpretation.html")

    # 6. Table comparison (for multiple results)
    print("\n" + "=" * 80)
    print("OPTION 6: Table Comparison (Multiple Results)")
    print("=" * 80)
    results = [result, {**result, "expression": "log(x)", "r2_score": 0.85}]
    formatter.to_table(results)

    """
    Quick Comparison of Formats
Format        Best For                    Pros                                Installation

Rich Panel   Terminal/CLI                 Beautiful colors, interactive        pip install rich

Markdown     Documentation, GitHub        Portable, version control friendly   Built-in

YAML         Config files, readable data  More readable than JSON               pip install pyyaml

Text         ReportLog files, plain text  No dependencies, simple               Built-in

HTML         Web, email, sharing           Professional, shareable              Built-in

Table        Comparing multiple            resultsSide-by-side comparison      pip install rich

My Recommendation
For your use case (interpreting symbolic regression results), I'd suggest:

1. For Interactive Development - Rich Panel

    pythonformatter = InterpretationFormatter()
    formatter.to_rich_panel(result)  # Beautiful terminal output

2. For Saving Results - Markdown

    pythonmd = formatter.to_markdown(result)
    with open('interpretations/expr_001.md', 'w') as f:
       f.write(md)

3. For Reports/Papers - HTML

    pythonhtml = formatter.to_html(result)

    with open('report.html', 'w') as f:
         f.write(html)
# Open in browser for presentation-ready output

 """
