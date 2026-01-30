"""
LLM-Powered Formula Interpretation Module for HypatiaX
Adds comprehensive explanation layer to discovered formulas
"""

import anthropic
from typing import Dict, Any, List
import json


class FormulaInterpreter:
    """
    Adds intelligent interpretation to discovered formulas.
    Explains what formulas mean, why they have that form, and when they're valid.
    """

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def interpret(
        self,
        formula: str,
        domain: str,
        variables: Dict[str, str],
        r2_score: float,
        validation_score: float,
        data_ranges: Dict[str, tuple],
        is_extrapolation: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive interpretation of discovered formula.

        Args:
            formula: The mathematical expression (e.g., "0.5*m*v**2")
            domain: Application domain (e.g., "physics", "defi")
            variables: Variable names and units (e.g., {"m": "kg", "v": "m/s"})
            r2_score: Model accuracy (0-1)
            validation_score: Validation layer score (0-100)
            data_ranges: Min/max for each variable
            is_extrapolation: Whether this is extrapolation prediction

        Returns:
            Dict with interpretation, warnings, usage guidance, etc.
        """

        # Build context-rich prompt
        prompt = self._build_interpretation_prompt(
            formula,
            domain,
            variables,
            r2_score,
            validation_score,
            data_ranges,
            is_extrapolation,
        )

        # Get LLM interpretation
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        # Parse structured response
        interpretation = self._parse_interpretation(response.content[0].text)

        # Add confidence indicators
        interpretation["confidence"] = self._compute_confidence(
            r2_score, validation_score, is_extrapolation
        )

        return interpretation

    def _build_interpretation_prompt(
        self,
        formula,
        domain,
        variables,
        r2_score,
        validation_score,
        data_ranges,
        is_extrapolation,
    ) -> str:
        """Construct detailed interpretation prompt"""

        return f"""You are a scientific equation interpreter. Analyze this discovered formula:

**Formula:** {formula}
**Domain:** {domain}
**Variables:** {json.dumps(variables, indent=2)}
**Accuracy (R²):** {r2_score:.3f}
**Validation Score:** {validation_score:.1f}/100
**Data Ranges:** {json.dumps(data_ranges, indent=2)}
**Context:** {"Extrapolation" if is_extrapolation else "Interpolation"}

Provide a comprehensive interpretation in this JSON structure:

{{
  "plain_english": "What this formula calculates in simple terms",
  "mathematical_meaning": "Detailed explanation of each term",
  "why_this_form": "Why this functional form emerged (e.g., quadratic, exponential)",
  "physical_intuition": "Physical or domain-specific intuition",
  "domain_of_validity": {{
    "variable_ranges": "Safe ranges for each variable",
    "assumptions": "What assumptions does this formula make?",
    "limitations": "When does this formula break down?"
  }},
  "practical_usage": {{
    "typical_use_case": "Most common application",
    "input_preparation": "How to prepare input data",
    "output_interpretation": "How to interpret results"
  }},
  "warnings": [
    "List any edge cases, numerical issues, or domain violations"
  ],
  "related_concepts": [
    "List related formulas or theories from this domain"
  ],
  "confidence_notes": "Why is this formula trustworthy (or not)?"
}}

**Special Instructions:**
- If this is a well-known formula, NAME IT (e.g., "This is the Kinetic Energy equation")
- If accuracy is low (R² < 0.90), explain likely causes
- If extrapolation, warn about uncertainty outside data range
- For DeFi domain, explain financial implications and risks
- Be honest about limitations

Return ONLY the JSON, no preamble."""

    def _parse_interpretation(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM's structured response"""
        try:
            # Extract JSON from response
            json_start = llm_response.find("{")
            json_end = llm_response.rfind("}") + 1
            json_str = llm_response[json_start:json_end]

            interpretation = json.loads(json_str)
            return interpretation

        except json.JSONDecodeError:
            # Fallback: return raw text
            return {
                "plain_english": llm_response,
                "error": "Failed to parse structured response",
            }

    def _compute_confidence(
        self, r2_score: float, validation_score: float, is_extrapolation: bool
    ) -> Dict[str, Any]:
        """Compute confidence metrics"""

        # Base confidence from accuracy
        if r2_score >= 0.95:
            base_confidence = "HIGH"
        elif r2_score >= 0.85:
            base_confidence = "MEDIUM"
        else:
            base_confidence = "LOW"

        # Adjust for extrapolation
        if is_extrapolation:
            if r2_score < 0.90:
                base_confidence = "LOW"
                warning = "Extrapolation with moderate accuracy - use with caution"
            else:
                warning = "Extrapolation - verify with domain experts"
        else:
            warning = None

        # Validation check
        validation_status = "PASSED" if validation_score >= 85 else "FAILED"

        return {
            "level": base_confidence,
            "r2_score": r2_score,
            "validation_score": validation_score,
            "validation_status": validation_status,
            "is_extrapolation": is_extrapolation,
            "warning": warning,
        }

    def generate_report(self, interpretation: Dict[str, Any]) -> str:
        """Generate human-readable report"""

        report = []
        report.append("=" * 60)
        report.append("FORMULA INTERPRETATION REPORT")
        report.append("=" * 60)
        report.append("")

        # Plain English explanation
        report.append("📖 WHAT IT CALCULATES:")
        report.append(f"   {interpretation['plain_english']}")
        report.append("")

        # Mathematical details
        report.append("🔢 MATHEMATICAL MEANING:")
        report.append(f"   {interpretation['mathematical_meaning']}")
        report.append("")

        # Why this form
        report.append("💡 WHY THIS FORM:")
        report.append(f"   {interpretation['why_this_form']}")
        report.append("")

        # Domain intuition
        report.append("🧠 INTUITION:")
        report.append(f"   {interpretation['physical_intuition']}")
        report.append("")

        # Domain of validity
        dov = interpretation["domain_of_validity"]
        report.append("✅ DOMAIN OF VALIDITY:")
        report.append(f"   Ranges: {dov['variable_ranges']}")
        report.append(f"   Assumes: {dov['assumptions']}")
        report.append(f"   Limits: {dov['limitations']}")
        report.append("")

        # Warnings
        if interpretation["warnings"]:
            report.append("⚠️  WARNINGS:")
            for warning in interpretation["warnings"]:
                report.append(f"   • {warning}")
            report.append("")

        # Confidence
        conf = interpretation["confidence"]
        report.append("🎯 CONFIDENCE:")
        report.append(f"   Level: {conf['level']}")
        report.append(f"   R² Score: {conf['r2_score']:.3f}")
        report.append(f"   Validation: {conf['validation_status']}")
        if conf["warning"]:
            report.append(f"   ⚠️  {conf['warning']}")
        report.append("")

        # Usage guidance
        usage = interpretation["practical_usage"]
        report.append("📋 HOW TO USE:")
        report.append(f"   Use Case: {usage['typical_use_case']}")
        report.append(f"   Inputs: {usage['input_preparation']}")
        report.append(f"   Outputs: {usage['output_interpretation']}")
        report.append("")

        report.append("=" * 60)

        return "\n".join(report)


# Example usage
if __name__ == "__main__":
    # Initialize interpreter
    interpreter = FormulaInterpreter(api_key="your-key-here")

    # Example: Kinetic Energy
    interpretation = interpreter.interpret(
        formula="0.5 * m * v**2",
        domain="physics",
        variables={"m": "kg", "v": "m/s"},
        r2_score=0.998,
        validation_score=95.0,
        data_ranges={"m": (1.0, 100.0), "v": (0.0, 50.0)},
        is_extrapolation=False,
    )

    # Print report
    report = interpreter.generate_report(interpretation)
    print(report)

    """
    Expected output:
    
    ============================================================
    FORMULA INTERPRETATION REPORT
    ============================================================
    
    📖 WHAT IT CALCULATES:
       This calculates the kinetic energy of a moving object.
    
    🔢 MATHEMATICAL MEANING:
       The formula has three components:
       - 0.5: Classical constant from integration of F=ma
       - m: Mass of the object (resistance to acceleration)
       - v²: Velocity squared (energy scales quadratically)
    
    💡 WHY THIS FORM:
       The quadratic relationship (v²) emerges from integrating
       force over distance. Doubling speed quadruples energy.
    
    🧠 INTUITION:
       Heavier objects or faster speeds require more energy.
       The squared term means small speed increases have
       disproportionate energy costs (important for fuel efficiency).
    
    ✅ DOMAIN OF VALIDITY:
       Ranges: 1-100 kg, 0-50 m/s (non-relativistic speeds)
       Assumes: Classical mechanics, v << speed of light
       Limits: Breaks down near c, ignores friction/air resistance
    
    🎯 CONFIDENCE:
       Level: HIGH
       R² Score: 0.998
       Validation: PASSED
    
    📋 HOW TO USE:
       Use Case: Calculate energy for moving vehicles, projectiles
       Inputs: Mass in kg, velocity in m/s
       Outputs: Energy in Joules
    
    ============================================================
    """
