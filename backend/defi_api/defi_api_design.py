"""
DeFi Formula Discovery API - Multi-Format Support
Provides all format options for description → formula mappings
"""

import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

# ==================== ENUMS & MODELS ====================


class FormatType(str, Enum):
    """Supported output formats."""

    QUERY_RESPONSE = "query_response"  # Simple Q&A
    STRUCTURED = "structured"  # Full JSON with metadata
    SEMANTIC = "semantic"  # NLP/LLM friendly
    FUNCTION = "function"  # Code generation
    CSV = "csv"  # Tabular data
    LATEX = "latex"  # Mathematical notation
    MINIMAL = "minimal"  # description;formula
    EXTENDED = "extended"  # All fields combined


class Variable(BaseModel):
    """Variable definition."""

    name: str
    description: str
    unit: str
    type: str = "float"


class FormulaMetadata(BaseModel):
    """Formula metadata."""

    id: str
    description: str
    analytical_formula: str
    category: str

    # Additional fields
    latex_formula: Optional[str] = None
    variables: Optional[List[Variable]] = None
    parameters: Optional[Dict[str, Any]] = None
    implementation: Optional[str] = None
    complexity: Optional[str] = None
    test_case_input: Optional[Dict[str, float]] = None
    expected_output: Optional[float] = None
    use_case: Optional[str] = None
    difficulty: Optional[str] = None
    created_at: Optional[str] = None


class DeFiFormulaAPI:
    """DeFi Formula API with multi-format support."""

    def __init__(self):
        """Initialize API with formula data."""
        self.formulas = self._load_formulas()
        self.app = FastAPI(
            title="DeFi Formula Discovery API",
            description="Multi-format API for DeFi formula queries and retrieval",
            version="1.0.0",
        )
        self._setup_routes()

    def _load_formulas(self) -> List[Dict]:
        """Load formulas from dataset."""
        # This would load from CSV/JSON in production
        formulas = [
            {
                "id": "cp_001",
                "description": "Calculate the constant product for a token pair in an AMM",
                "analytical_formula": "k = x * y",
                "latex_formula": r"k = x \times y",
                "category": "Constant Product",
                "variables": [
                    {"name": "x", "description": "Token X reserve", "unit": "tokens", "type": "float"},
                    {"name": "y", "description": "Token Y reserve", "unit": "tokens", "type": "float"},
                    {"name": "k", "description": "Constant product", "unit": "token_pairs", "type": "float"},
                ],
                "parameters": {"fee": 0.003},
                "implementation": "uniswap_v2",
                "complexity": "O(1)",
                "use_case": "Uniswap V2 AMM",
                "difficulty": "beginner",
                "test_case_input": {"x": 1000, "y": 2000},
                "expected_output": 2000000,
            },
            {
                "id": "il_001",
                "description": "Calculate impermanent loss for 50/50 liquidity pool",
                "analytical_formula": "IL = 2*sqrt(p)/(1+p) - 1",
                "latex_formula": r"IL = \frac{2\sqrt{p}}{1+p} - 1",
                "category": "Impermanent Loss",
                "variables": [{"name": "p", "description": "Price ratio", "unit": "dimensionless", "type": "float"}],
                "parameters": None,
                "implementation": "balancer",
                "complexity": "O(1)",
                "use_case": "Loss calculation",
                "difficulty": "intermediate",
                "test_case_input": {"p": 2.0},
                "expected_output": -0.0566,
            },
            # Add more formulas...
        ]
        return formulas

    def _setup_routes(self):
        """Setup API routes."""

        @self.app.get("/api/formulas")
        async def get_all_formulas(
            format: FormatType = Query(FormatType.QUERY_RESPONSE),
            category: Optional[str] = None,
            limit: int = Query(10, ge=1, le=1000),
        ):
            """Get all formulas in specified format."""
            formulas = self.formulas
            if category:
                formulas = [f for f in formulas if f["category"] == category]

            formulas = formulas[:limit]
            return self._format_response(formulas, format)

        @self.app.get("/api/formula/{formula_id}")
        async def get_formula(formula_id: str, format: FormatType = Query(FormatType.STRUCTURED)):
            """Get single formula by ID."""
            formula = next((f for f in self.formulas if f["id"] == formula_id), None)
            if not formula:
                raise HTTPException(status_code=404, detail="Formula not found")

            return self._format_response([formula], format)[0]

        @self.app.get("/api/search")
        async def search_formulas(
            query: str, format: FormatType = Query(FormatType.QUERY_RESPONSE), limit: int = Query(5, ge=1, le=100)
        ):
            """Search formulas by description."""
            query_lower = query.lower()
            results = [f for f in self.formulas if query_lower in f["description"].lower()][:limit]

            if not results:
                raise HTTPException(status_code=404, detail="No formulas found")

            return self._format_response(results, format)

        @self.app.get("/api/categories")
        async def get_categories():
            """Get all formula categories."""
            categories = list(set(f["category"] for f in self.formulas))
            return {"categories": sorted(categories), "count": len(categories), "total_formulas": len(self.formulas)}

        @self.app.get("/api/export")
        async def export_formulas(format: FormatType = Query(FormatType.CSV)):
            """Export all formulas in specified format."""
            if format == FormatType.CSV:
                return self._to_csv(self.formulas)
            elif format == FormatType.JSON:
                return self._to_json(self.formulas)
            else:
                return self._format_response(self.formulas, format)

    # ==================== FORMAT CONVERTERS ====================

    def _format_response(self, formulas: List[Dict], format: FormatType) -> List[Dict]:
        """Convert formulas to requested format."""

        if format == FormatType.QUERY_RESPONSE:
            return self._to_query_response(formulas)
        elif format == FormatType.STRUCTURED:
            return self._to_structured(formulas)
        elif format == FormatType.SEMANTIC:
            return self._to_semantic(formulas)
        elif format == FormatType.FUNCTION:
            return self._to_function(formulas)
        elif format == FormatType.LATEX:
            return self._to_latex(formulas)
        elif format == FormatType.MINIMAL:
            return self._to_minimal(formulas)
        elif format == FormatType.EXTENDED:
            return self._to_extended(formulas)
        else:
            return formulas

    def _to_query_response(self, formulas: List[Dict]) -> List[Dict]:
        """Format: Simple Q&A structure."""
        return [
            {"query": f["description"], "response": f["analytical_formula"], "category": f["category"]}
            for f in formulas
        ]

    def _to_structured(self, formulas: List[Dict]) -> List[Dict]:
        """Format: Full structured JSON with metadata."""
        return [
            {
                "metadata": {
                    "id": f["id"],
                    "category": f["category"],
                    "complexity": f.get("complexity"),
                    "difficulty": f.get("difficulty"),
                    "implementation": f.get("implementation"),
                },
                "query": {"text": f["description"], "semantic_keywords": self._extract_keywords(f["description"])},
                "answer": {
                    "formula": f["analytical_formula"],
                    "latex": f.get("latex_formula"),
                    "variables": f.get("variables"),
                    "parameters": f.get("parameters"),
                },
                "testing": {"test_case_input": f.get("test_case_input"), "expected_output": f.get("expected_output")},
                "use_case": f.get("use_case"),
            }
            for f in formulas
        ]

    def _to_semantic(self, formulas: List[Dict]) -> List[Dict]:
        """Format: NLP/LLM friendly."""
        return [
            {
                "description": f["description"],
                "formula": f["analytical_formula"],
                "latex_formula": f.get("latex_formula"),
                "semantic_meaning": self._generate_semantic_meaning(f),
                "domain": "DeFi",
                "subdomain": f["category"],
                "variables": {v["name"]: v["description"] for v in f.get("variables", [])},
                "context": f.get("use_case"),
            }
            for f in formulas
        ]

    def _to_function(self, formulas: List[Dict]) -> List[Dict]:
        """Format: Code generation ready."""
        return [
            {
                "function_name": self._formula_to_function_name(f["analytical_formula"]),
                "description": f["description"],
                "formula": f["analytical_formula"],
                "signature": self._generate_signature(f),
                "parameters": [v["name"] for v in f.get("variables", [])],
                "return_type": "float",
                "implementation_template": f"return {self._formula_to_code(f['analytical_formula'])}",
                "test_case": {"input": f.get("test_case_input"), "output": f.get("expected_output")},
            }
            for f in formulas
        ]

    def _to_latex(self, formulas: List[Dict]) -> List[Dict]:
        """Format: LaTeX mathematical notation."""
        return [
            {
                "id": f["id"],
                "description": f["description"],
                "formula_text": f["analytical_formula"],
                "formula_latex": f.get("latex_formula", self._to_latex_formula(f["analytical_formula"])),
                "variables_latex": {v["name"]: f"${v['name']}$: {v['description']}" for v in f.get("variables", [])},
            }
            for f in formulas
        ]

    def _to_minimal(self, formulas: List[Dict]) -> List[str]:
        """Format: Minimal semicolon-separated."""
        return [f"{f['description']};{f['analytical_formula']}" for f in formulas]

    def _to_extended(self, formulas: List[Dict]) -> List[Dict]:
        """Format: All fields combined."""
        return [
            {**f, "keywords": self._extract_keywords(f["description"]), "timestamp": datetime.now().isoformat()}
            for f in formulas
        ]

    def _to_csv(self, formulas: List[Dict]) -> str:
        """Export to CSV."""
        df = pd.DataFrame(
            [
                {
                    "id": f["id"],
                    "description": f["description"],
                    "formula": f["analytical_formula"],
                    "category": f["category"],
                    "complexity": f.get("complexity"),
                    "difficulty": f.get("difficulty"),
                    "use_case": f.get("use_case"),
                }
                for f in formulas
            ]
        )
        return df.to_csv(index=False)

    def _to_json(self, formulas: List[Dict]) -> str:
        """Export to JSON."""
        return json.dumps(formulas, indent=2)

    # ==================== HELPER METHODS ====================

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from description."""
        keywords = []
        defi_terms = [
            "pool",
            "fee",
            "swap",
            "liquidity",
            "AMM",
            "impermanent",
            "loss",
            "constant",
            "product",
            "reserve",
            "token",
            "price",
            "yield",
            "APY",
        ]
        for term in defi_terms:
            if term.lower() in text.lower():
                keywords.append(term)
        return keywords

    def _generate_semantic_meaning(self, formula: Dict) -> str:
        """Generate semantic meaning explanation."""
        meanings = {
            "k = x * y": "The product of token reserves equals a constant value",
            "IL = 2*sqrt(p)/(1+p) - 1": "Impermanent loss increases with larger price movements",
            "util = borrowed / supplied": "Utilization measures the ratio of borrowed to supplied assets",
        }
        return meanings.get(formula["analytical_formula"], "Formula meaning")

    def _formula_to_function_name(self, formula: str) -> str:
        """Convert formula to function name."""
        # Simple heuristic
        if "=" not in formula:
            return "calculate_formula"
        var_name = formula.split("=")[0].strip()
        return f"calculate_{var_name.lower()}"

    def _generate_signature(self, formula: Dict) -> str:
        """Generate function signature."""
        params = ", ".join([f"{v['name']}: float" for v in formula.get("variables", [])])
        return f"def {self._formula_to_function_name(formula['analytical_formula'])}({params}) -> float:"

    def _formula_to_code(self, formula: str) -> str:
        """Convert formula to Python code (simplified)."""
        code = formula.replace("sqrt", "np.sqrt").replace("^", "**")
        return code

    def _to_latex_formula(self, formula: str) -> str:
        """Convert formula to LaTeX."""
        latex = formula.replace("sqrt", r"\sqrt").replace("^", "^")
        return f"${latex}$"

    def get_app(self) -> FastAPI:
        """Get FastAPI app."""
        return self.app


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    import uvicorn

    api = DeFiFormulaAPI()

    print("\n" + "=" * 80)
    print("DeFi Formula Discovery API - Multi-Format Support")
    print("=" * 80)
    print("\nSupported Formats:")
    print("  1. query_response  - Simple Q&A structure")
    print("  2. structured      - Full JSON with metadata")
    print("  3. semantic        - NLP/LLM friendly")
    print("  4. function        - Code generation ready")
    print("  5. csv             - Tabular data")
    print("  6. latex           - Mathematical notation")
    print("  7. minimal         - Semicolon-separated")
    print("  8. extended        - All fields combined")

    print("\nAPI Endpoints:")
    print("  GET  /api/formulas?format=query_response&limit=10")
    print("  GET  /api/formula/{formula_id}?format=structured")
    print("  GET  /api/search?query=impermanent+loss&format=semantic")
    print("  GET  /api/categories")
    print("  GET  /api/export?format=csv")

    print("\nExample Formats:")
    print("-" * 80)

    # Create test formula
    test_formula = [
        {
            "id": "cp_001",
            "description": "Calculate constant product for token pair",
            "analytical_formula": "k = x * y",
            "latex_formula": r"k = x \times y",
            "category": "Constant Product",
            "variables": [
                {"name": "x", "description": "Token X reserve", "unit": "tokens", "type": "float"},
                {"name": "y", "description": "Token Y reserve", "unit": "tokens", "type": "float"},
            ],
            "complexity": "O(1)",
            "difficulty": "beginner",
            "use_case": "Uniswap V2",
        }
    ]

    # Show examples
    print("\n1. QUERY_RESPONSE Format:")
    print(json.dumps(api._format_response(test_formula, FormatType.QUERY_RESPONSE), indent=2))

    print("\n2. SEMANTIC Format:")
    print(json.dumps(api._format_response(test_formula, FormatType.SEMANTIC), indent=2))

    print("\n3. FUNCTION Format:")
    print(json.dumps(api._format_response(test_formula, FormatType.FUNCTION), indent=2))

    print("\n4. MINIMAL Format:")
    print(json.dumps(api._format_response(test_formula, FormatType.MINIMAL), indent=2))

    print("\n" + "=" * 80)
    print("To run API server:")
    print("  uvicorn script:api.get_app() --reload")
    print("=" * 80 + "\n")
