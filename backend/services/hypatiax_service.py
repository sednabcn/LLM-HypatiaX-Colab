"""
HypatiaX Service - Tableau & DeFi Formula Mapping
File: backend/services/hypatiax_service.py
"""

import logging
import re
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class HypatiaXService:
    """Service for mapping natural language to Tableau and DeFi formulas"""

    # Tableau formula operations mapping
    TABLEAU_OPERATIONS = {
        "sum": "SUM",
        "total": "SUM",
        "add": "SUM",
        "average": "AVG",
        "avg": "AVG",
        "mean": "AVG",
        "count": "COUNT",
        "number": "COUNT",
        "max": "MAX",
        "maximum": "MAX",
        "highest": "MAX",
        "min": "MIN",
        "minimum": "MIN",
        "lowest": "MIN",
        "median": "MEDIAN",
        "stdev": "STDEV",
        "variance": "VAR",
        "var": "VAR",
    }

    # DeFi formula templates
    DEFI_FORMULAS = {
        "impermanent_loss": {
            "keywords": ["impermanent loss", "il", "divergence loss"],
            "formula": "2 * SQRT([price_ratio]) / ([price_ratio] + 1) - 1",
            "latex": r"IL = \frac{2\sqrt{r}}{r + 1} - 1",
            "description": "Impermanent Loss formula",
            "variables": ["price_ratio"],
            "category": "liquidity",
        },
        "constant_product": {
            "keywords": ["constant product", "xy=k", "uniswap invariant"],
            "formula": "[token_a] * [token_b]",
            "latex": r"x \cdot y = k",
            "description": "Constant Product Formula (Uniswap V2)",
            "variables": ["token_a", "token_b"],
            "category": "amm",
        },
        "price_impact": {
            "keywords": ["price impact", "slippage"],
            "formula": "([amount_in] / ([reserve_in] + [amount_in])) * 100",
            "latex": r"PI = \frac{\Delta x}{x + \Delta x} \times 100",
            "description": "Price Impact calculation",
            "variables": ["amount_in", "reserve_in"],
            "category": "trading",
        },
        "pool_share": {
            "keywords": ["pool share", "lp share", "liquidity share"],
            "formula": "[lp_tokens] / [total_supply]",
            "latex": r"share = \frac{LP_{user}}{LP_{total}}",
            "description": "LP Pool Share",
            "variables": ["lp_tokens", "total_supply"],
            "category": "liquidity",
        },
        "daily_fees": {
            "keywords": ["daily fees", "fee earnings", "trading fees"],
            "formula": "[daily_volume] * [fee_rate] * [pool_share]",
            "latex": r"fees = V_{daily} \times r_{fee} \times s_{pool}",
            "description": "Daily Fee Earnings",
            "variables": ["daily_volume", "fee_rate", "pool_share"],
            "category": "yield",
        },
        "apy": {
            "keywords": ["apy", "annual yield", "yearly return"],
            "formula": "POWER((1 + [daily_return]), 365) - 1",
            "latex": r"APY = (1 + r_{daily})^{365} - 1",
            "description": "Annual Percentage Yield",
            "variables": ["daily_return"],
            "category": "yield",
        },
        "position_value": {
            "keywords": ["position value", "lp value", "total value locked"],
            "formula": "[token_a_amount] * [token_a_price] + [token_b_amount] * [token_b_price]",
            "latex": r"V = n_a \times p_a + n_b \times p_b",
            "description": "LP Position Value",
            "variables": ["token_a_amount", "token_a_price", "token_b_amount", "token_b_price"],
            "category": "liquidity",
        },
        "quality_score": {
            "keywords": ["quality score", "pool quality", "fee to il ratio"],
            "formula": "[daily_fees] / [daily_il_rate]",
            "latex": r"Q = \frac{fees_{daily}}{IL_{daily}}",
            "description": "Pool Quality Score (Fee/IL Ratio)",
            "variables": ["daily_fees", "daily_il_rate"],
            "category": "analytics",
        },
        "breakeven_days": {
            "keywords": ["breakeven", "break even days", "recovery time"],
            "formula": "ABS([il_dollar]) / [daily_fees]",
            "latex": r"t_{BE} = \frac{|IL_{\$}|}{fees_{daily}}",
            "description": "Days to Break Even from IL",
            "variables": ["il_dollar", "daily_fees"],
            "category": "analytics",
        },
        "swap_output": {
            "keywords": ["swap output", "token out", "swap amount"],
            "formula": "([amount_in] * [reserve_out] * 997) / ([reserve_in] * 1000 + [amount_in] * 997)",
            "latex": r"\Delta y = \frac{\Delta x \times y \times 997}{x \times 1000 + \Delta x \times 997}",
            "description": "Uniswap V2 Swap Output (0.3% fee)",
            "variables": ["amount_in", "reserve_in", "reserve_out"],
            "category": "trading",
        },
        "tvl": {
            "keywords": ["tvl", "total value locked", "pool liquidity"],
            "formula": "2 * SQRT([reserve_a] * [reserve_b]) * SQRT([price_a] * [price_b])",
            "latex": r"TVL = 2\sqrt{x \times y} \times \sqrt{p_a \times p_b}",
            "description": "Total Value Locked",
            "variables": ["reserve_a", "reserve_b", "price_a", "price_b"],
            "category": "liquidity",
        },
    }

    # Common prepositions and stop words
    PREPOSITIONS = ["of", "by", "for", "in", "on", "at", "from", "to", "with", "using"]
    STOP_WORDS = ["the", "a", "an", "all", "each", "every", "calculate", "compute", "find", "get", "show", "what", "is"]

    def __init__(self, models_loaded: bool = False, nlp_desc=None, nlp_formula=None):
        """
        Initialize HypatiaX service

        Args:
            models_loaded: Whether spaCy models are loaded
            nlp_desc: spaCy NER model for descriptions
            nlp_formula: spaCy NER model for formulas
        """
        self.models_loaded = models_loaded
        self.nlp_desc = nlp_desc
        self.nlp_formula = nlp_formula

        logger.info(f"HypatiaXService initialized (models_loaded={models_loaded})")

    def map_description_to_formula(
        self, description: str, method: str = "vocab", domain: str = "auto"
    ) -> Dict[str, Any]:
        """
        Map natural language description to formula (Tableau or DeFi)

        Args:
            description: Natural language description
            method: Mapping method (vocab, neural, hybrid)
            domain: Formula domain (auto, tableau, defi)

        Returns:
            Dictionary with formula, entities, and confidence
        """
        start_time = time.time()

        try:
            # Auto-detect domain if not specified
            if domain == "auto":
                domain = self._detect_domain(description)

            logger.info(f"Detected domain: {domain}")

            # Route to appropriate mapper
            if domain == "defi":
                result = self._map_defi_formula(description, method)
            else:
                result = self._map_tableau_formula(description, method)

            # Add timing and metadata
            result["processing_time_ms"] = round((time.time() - start_time) * 1000, 2)
            result["mode"] = "production" if self.models_loaded else "demo"
            result["domain"] = domain

            logger.info(
                f"Mapped: '{description}' -> {result['formula']} (confidence={result.get('confidence', 0):.2f})"
            )

            return result

        except Exception as e:
            logger.error(f"Error mapping description: {e}")
            return {"success": False, "error": str(e), "description": description}

    def _detect_domain(self, description: str) -> str:
        """
        Detect whether description is for Tableau or DeFi

        Args:
            description: Natural language description

        Returns:
            Domain string ('tableau' or 'defi')
        """
        desc_lower = description.lower()

        # Check for DeFi keywords
        defi_keywords = [
            "impermanent loss",
            "il",
            "liquidity",
            "pool",
            "swap",
            "amm",
            "token",
            "defi",
            "uniswap",
            "fee",
            "tvl",
            "slippage",
            "apy",
            "yield",
            "reserve",
            "price ratio",
            "breakeven",
        ]

        defi_score = sum(1 for keyword in defi_keywords if keyword in desc_lower)

        # Check for Tableau keywords
        tableau_keywords = list(self.TABLEAU_OPERATIONS.keys())
        tableau_score = sum(1 for keyword in tableau_keywords if keyword in desc_lower)

        # Also check for typical Tableau field references
        if re.search(r"\b(sales|profit|revenue|orders|customers|products)\b", desc_lower):
            tableau_score += 2

        logger.debug(f"Domain detection: DeFi={defi_score}, Tableau={tableau_score}")

        return "defi" if defi_score > tableau_score else "tableau"

    def _map_defi_formula(self, description: str, method: str) -> Dict[str, Any]:
        """
        Map description to DeFi formula

        Args:
            description: Natural language description
            method: Mapping method

        Returns:
            Dictionary with DeFi formula and metadata
        """
        desc_lower = description.lower()

        # Find matching DeFi formula
        best_match = None
        best_score = 0

        for formula_id, formula_data in self.DEFI_FORMULAS.items():
            score = 0
            for keyword in formula_data["keywords"]:
                if keyword in desc_lower:
                    score += 1

            if score > best_score:
                best_score = score
                best_match = (formula_id, formula_data)

        if best_match:
            formula_id, formula_data = best_match

            # Extract any specific values mentioned
            extracted_values = self._extract_values_from_description(description)

            return {
                "success": True,
                "formula": formula_data["formula"],
                "formula_id": formula_id,
                "latex": formula_data["latex"],
                "description": formula_data["description"],
                "variables": formula_data["variables"],
                "category": formula_data["category"],
                "confidence": min(0.95, 0.7 + (best_score * 0.1)),
                "method": method,
                "extracted_values": extracted_values,
                "entities": self._generate_mock_entities(description),
            }
        else:
            # Fallback to generic DeFi formula
            return {
                "success": True,
                "formula": "[value_a] * [value_b]",
                "formula_id": "generic",
                "description": "Generic DeFi calculation",
                "variables": ["value_a", "value_b"],
                "category": "general",
                "confidence": 0.5,
                "method": method,
                "warning": "Could not match specific DeFi formula. Using generic template.",
                "entities": self._generate_mock_entities(description),
            }

    def _map_tableau_formula(self, description: str, method: str) -> Dict[str, Any]:
        """
        Map description to Tableau formula

        Args:
            description: Natural language description
            method: Mapping method

        Returns:
            Dictionary with Tableau formula and metadata
        """
        # Use production models if available
        if self.models_loaded and self.nlp_desc:
            result = self._map_tableau_with_models(description, method)
        else:
            # Fallback to rule-based mapping
            result = self._map_tableau_with_rules(description, method)

        return result

    def _map_tableau_with_models(self, description: str, method: str) -> Dict[str, Any]:
        """Map Tableau formula using spaCy NER models"""
        try:
            # Extract entities using NER model
            doc = self.nlp_desc(description)
            entities = [
                {"text": ent.text, "label": ent.label_, "start": ent.start_char, "end": ent.end_char}
                for ent in doc.ents
            ]

            # Extract operation and field
            operation = self._extract_operation_from_entities(entities, description)
            field_name = self._extract_field_from_entities(entities, description)

            # Generate formula
            formula = self._generate_tableau_formula(operation, field_name)

            # Calculate confidence
            confidence = self._calculate_confidence(entities, description)

            return {
                "success": True,
                "formula": formula,
                "entities": entities,
                "confidence": confidence,
                "operation": operation,
                "field": field_name,
                "method": method,
            }

        except Exception as e:
            logger.warning(f"Model mapping failed: {e}, falling back to rules")
            return self._map_tableau_with_rules(description, method)

    def _map_tableau_with_rules(self, description: str, method: str) -> Dict[str, Any]:
        """Map Tableau formula using rule-based approach"""
        desc_lower = description.lower()

        # Extract operation
        operation = "SUM"  # Default
        for keyword, op in self.TABLEAU_OPERATIONS.items():
            if keyword in desc_lower:
                operation = op
                break

        # Extract field name
        field_name = self._extract_field_name(description)

        # Generate entities for visualization
        entities = self._generate_mock_entities(description)

        # Generate formula
        formula = self._generate_tableau_formula(operation, field_name)

        # Calculate confidence
        confidence = self._calculate_rule_confidence(description, operation, field_name)

        return {
            "success": True,
            "formula": formula,
            "entities": entities,
            "confidence": confidence,
            "operation": operation,
            "field": field_name,
            "method": method,
        }

    def _extract_values_from_description(self, description: str) -> Dict[str, float]:
        """Extract numeric values and their context from description"""
        values = {}

        # Pattern: number + optional unit + context
        pattern = r"(\d+\.?\d*)\s*(%|percent|percentage|dollars?|\$|tokens?)?"
        matches = re.finditer(pattern, description.lower())

        for match in matches:
            value = float(match.group(1))
            unit = match.group(2) if match.group(2) else "number"

            # Get context (word before the number)
            start = match.start()
            words_before = description[:start].split()
            context = words_before[-1] if words_before else "value"

            values[context] = value

        return values

    def _extract_operation_from_entities(self, entities: List[Dict], description: str) -> str:
        """Extract operation from NER entities"""
        for entity in entities:
            if entity["label"] == "OPER":
                text_lower = entity["text"].lower()
                return self.TABLEAU_OPERATIONS.get(text_lower, "SUM")

        # Fallback
        desc_lower = description.lower()
        for keyword, op in self.TABLEAU_OPERATIONS.items():
            if keyword in desc_lower:
                return op

        return "SUM"

    def _extract_field_from_entities(self, entities: List[Dict], description: str) -> str:
        """Extract field name from NER entities"""
        field_candidates = [
            ent["text"]
            for ent in entities
            if ent["label"] == "NOUN" and ent["text"].lower() not in self.TABLEAU_OPERATIONS
        ]

        if field_candidates:
            return field_candidates[-1]

        return self._extract_field_name(description)

    def _extract_field_name(self, description: str) -> str:
        """Extract field name using rules"""
        words = description.split()

        # Look for field after prepositions
        for i, word in enumerate(words):
            if word.lower() in self.PREPOSITIONS:
                if i + 1 < len(words):
                    remaining = words[i + 1 :]
                    field_words = [w for w in remaining if w.lower() not in self.STOP_WORDS + self.PREPOSITIONS]
                    if field_words:
                        return field_words[0].strip(".,!?").capitalize()

        # Fallback: take last meaningful word
        for word in reversed(words):
            clean_word = word.lower().strip(".,!?")
            if clean_word not in list(self.TABLEAU_OPERATIONS.keys()) + self.STOP_WORDS + self.PREPOSITIONS:
                return word.strip(".,!?").capitalize()

        return "Field"

    def _generate_tableau_formula(self, operation: str, field_name: str) -> str:
        """Generate Tableau formula string"""
        field_name = field_name.capitalize()
        return f"{operation}([{field_name}])"

    def _calculate_confidence(self, entities: List[Dict], description: str) -> float:
        """Calculate confidence score based on entity extraction"""
        if not entities:
            return 0.5

        total_chars = len(description)
        entity_chars = sum(e["end"] - e["start"] for e in entities)
        coverage = entity_chars / total_chars if total_chars > 0 else 0

        has_operation = any(e["label"] == "OPER" for e in entities)
        has_field = any(e["label"] == "NOUN" for e in entities)

        confidence = coverage * 0.65 + (0.2 if has_operation else 0) + (0.15 if has_field else 0)
        return round(min(0.95, confidence), 2)

    def _calculate_rule_confidence(self, description: str, operation: str, field: str) -> float:
        """Calculate confidence for rule-based mapping"""
        confidence = 0.70

        desc_lower = description.lower()
        op_mentioned = any(keyword in desc_lower for keyword, op in self.TABLEAU_OPERATIONS.items() if op == operation)

        if op_mentioned:
            confidence += 0.15
        if field != "Field":
            confidence += 0.10

        return round(min(0.95, confidence), 2)

    def _generate_mock_entities(self, description: str) -> List[Dict]:
        """Generate mock entities for demo mode"""
        entities = []
        words = description.split()
        start_pos = 0

        for word in words:
            word_lower = word.lower().strip(".,!?")
            label = None

            if word_lower in self.TABLEAU_OPERATIONS:
                label = "OPER"
            elif word_lower in self.PREPOSITIONS:
                label = "ADP"
            elif word_lower in self.STOP_WORDS:
                label = "DET"
            elif word_lower.replace(".", "").replace(",", "").isdigit():
                label = "NUM"
            else:
                label = "NOUN"

            if label:
                entities.append({"text": word, "label": label, "start": start_pos, "end": start_pos + len(word)})

            start_pos += len(word) + 1

        return entities

    def get_defi_formulas(self, category: Optional[str] = None) -> Dict[str, Dict]:
        """
        Get available DeFi formulas, optionally filtered by category

        Args:
            category: Filter by category (liquidity, amm, trading, yield, analytics)

        Returns:
            Dictionary of formulas
        """
        if category:
            return {k: v for k, v in self.DEFI_FORMULAS.items() if v["category"] == category}
        return self.DEFI_FORMULAS

    def get_defi_categories(self) -> List[str]:
        """Get list of DeFi formula categories"""
        return list(set(f["category"] for f in self.DEFI_FORMULAS.values()))

    def suggest_defi_formula(self, keywords: List[str]) -> List[Dict]:
        """
        Suggest DeFi formulas based on keywords

        Args:
            keywords: List of keywords to match

        Returns:
            List of matching formulas with scores
        """
        suggestions = []

        for formula_id, formula_data in self.DEFI_FORMULAS.items():
            score = 0
            for keyword in keywords:
                for formula_keyword in formula_data["keywords"]:
                    if keyword.lower() in formula_keyword.lower():
                        score += 1

            if score > 0:
                suggestions.append(
                    {
                        "formula_id": formula_id,
                        "formula": formula_data["formula"],
                        "description": formula_data["description"],
                        "category": formula_data["category"],
                        "score": score,
                    }
                )

        # Sort by score
        suggestions.sort(key=lambda x: x["score"], reverse=True)
        return suggestions

    def batch_map(self, descriptions: List[str], method: str = "vocab", domain: str = "auto") -> List[Dict[str, Any]]:
        """
        Map multiple descriptions in batch

        Args:
            descriptions: List of natural language descriptions
            method: Mapping method
            domain: Formula domain

        Returns:
            List of mapping results
        """
        results = []

        for desc in descriptions:
            try:
                result = self.map_description_to_formula(desc, method, domain)
                result["description"] = desc
                results.append(result)
            except Exception as e:
                results.append({"success": False, "description": desc, "error": str(e)})

        logger.info(f"Batch mapped {len(descriptions)} descriptions")
        return results

    def get_supported_operations(self) -> Dict[str, List[str]]:
        """Get list of supported Tableau operations"""
        operations = {}
        for keyword, operation in self.TABLEAU_OPERATIONS.items():
            if operation not in operations:
                operations[operation] = []
            operations[operation].append(keyword)
        return operations


"""
This enhanced version now includes:

1. DeFi Formula Support: 11 pre-defined DeFi formulas (IL, constant product, price impact, fees, APY, etc.)
2. Auto Domain Detection: Automatically detects if the query is for Tableau or DeFi
3. DeFi Formula Categories: liquidity, amm, trading, yield, analytics
4. LaTeX Support: Each DeFi formula includes LaTeX representation
5. Value Extraction: Extracts numeric values from descriptions
6. Formula Suggestions: Suggest formulas based on keywords
7. Category Filtering: Get formulas by category

Now it handles both Tableau BI formulas AND DeFi calculations!
"""
