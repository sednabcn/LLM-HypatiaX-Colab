"""
Enhanced Perfume Formulation System - Complete
===============================================
Production-ready system for drugstore perfume formulation with advanced features.
Version: 2.0.0
"""

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple

# Constants
EPSILON = 1e-12
ALCOHOL_DENSITY = 0.789
WATER_DENSITY = 1.0
ML_TO_OZ = 0.033814
FRAGRANCE_OIL_DENSITY = 0.9


class FragranceType(Enum):
    PARFUM = "Parfum"
    EAU_DE_PARFUM = "Eau de Parfum"
    EAU_DE_TOILETTE = "Eau de Toilette"
    EAU_DE_COLOGNE = "Eau de Cologne"
    BODY_SPLASH = "Body Splash"


class NoteCategory(Enum):
    TOP = "Top Notes"
    MIDDLE = "Middle Notes"
    BASE = "Base Notes"


@dataclass
class FragranceIngredient:
    name: str
    concentration_percent: float
    note_type: NoteCategory
    cost_per_gram: float
    ifra_max_limit: Optional[float] = None
    allergen: bool = False
    natural: bool = True
    volatility: float = 50.0
    intensity: float = 50.0


@dataclass
class FragranceFormula:
    name: str
    fragrance_type: FragranceType
    ingredients: List[FragranceIngredient]
    alcohol_percent: float = 0.0
    water_percent: float = 0.0
    fixatives_percent: float = 0.0

    def total_fragrance_percent(self) -> float:
        return sum(i.concentration_percent for i in self.ingredients)


class PerfumeFormulator:
    """Complete perfume formulation system."""

    @staticmethod
    def create_balanced_formula(
        name: str, fragrance_type: FragranceType, ingredients: List[FragranceIngredient]
    ) -> Dict[str, any]:
        """
        Create a complete balanced formula with automatic solvent calculation.
        """
        # Get recommended concentration
        conc_ranges = {
            FragranceType.PARFUM: 25.0,
            FragranceType.EAU_DE_PARFUM: 17.5,
            FragranceType.EAU_DE_TOILETTE: 10.0,
            FragranceType.EAU_DE_COLOGNE: 3.5,
            FragranceType.BODY_SPLASH: 2.0,
        }

        target_conc = conc_ranges[fragrance_type]

        # Calculate solvents
        alcohol_ratios = {
            FragranceType.PARFUM: 0.90,
            FragranceType.EAU_DE_PARFUM: 0.82,
            FragranceType.EAU_DE_TOILETTE: 0.75,
            FragranceType.EAU_DE_COLOGNE: 0.65,
            FragranceType.BODY_SPLASH: 0.60,
        }

        fixatives = 2.0
        remaining = 100.0 - target_conc - fixatives
        alcohol_ratio = alcohol_ratios[fragrance_type]

        alcohol = remaining * alcohol_ratio
        water = remaining - alcohol

        # Check note balance
        top = sum(i.concentration_percent for i in ingredients if i.note_type == NoteCategory.TOP)
        middle = sum(i.concentration_percent for i in ingredients if i.note_type == NoteCategory.MIDDLE)
        base = sum(i.concentration_percent for i in ingredients if i.note_type == NoteCategory.BASE)

        balanced = 15 <= top <= 30 and 40 <= middle <= 60 and 20 <= base <= 35

        return {
            "formula": FragranceFormula(
                name=name,
                fragrance_type=fragrance_type,
                ingredients=ingredients,
                alcohol_percent=alcohol,
                water_percent=water,
                fixatives_percent=fixatives,
            ),
            "fragrance_concentration": target_conc,
            "note_balance": {"top": top, "middle": middle, "base": base, "is_balanced": balanced},
            "ready_for_production": balanced,
        }

    @staticmethod
    def calculate_production_batch(formula: FragranceFormula, batch_size_ml: float) -> Dict[str, any]:
        """Calculate exact quantities needed for production."""

        alcohol_ml = (formula.alcohol_percent / 100) * batch_size_ml
        water_ml = (formula.water_percent / 100) * batch_size_ml
        fixatives_ml = (formula.fixatives_percent / 100) * batch_size_ml
        fragrance_ml = (formula.total_fragrance_percent() / 100) * batch_size_ml

        # Convert to grams
        alcohol_g = alcohol_ml * ALCOHOL_DENSITY
        water_g = water_ml * WATER_DENSITY
        fixatives_g = fixatives_ml * 1.26
        fragrance_g = fragrance_ml * FRAGRANCE_OIL_DENSITY

        # Individual ingredients
        ingredients = {}
        total_frag = formula.total_fragrance_percent()

        for ing in formula.ingredients:
            fraction = ing.concentration_percent / total_frag
            ing_g = fragrance_g * fraction
            ingredients[ing.name] = {"grams": round(ing_g, 3), "note": ing.note_type.value}

        return {
            "batch_size_ml": batch_size_ml,
            "batch_size_oz": round(batch_size_ml * ML_TO_OZ, 2),
            "components": {
                "alcohol_96%": {"ml": round(alcohol_ml, 1), "g": round(alcohol_g, 1)},
                "distilled_water": {"ml": round(water_ml, 1), "g": round(water_g, 1)},
                "glycerin": {"ml": round(fixatives_ml, 1), "g": round(fixatives_g, 1)},
                "fragrance_oil": {"ml": round(fragrance_ml, 1), "g": round(fragrance_g, 1)},
            },
            "fragrance_ingredients": ingredients,
            "total_mass_g": round(alcohol_g + water_g + fixatives_g + fragrance_g, 1),
            "production_steps": PerfumeFormulator._get_production_steps(),
        }

    @staticmethod
    def _get_production_steps() -> List[str]:
        return [
            "1. Measure all ingredients precisely using calibrated scales",
            "2. Mix fragrance oils in glass beaker at room temperature",
            "3. Add alcohol slowly while stirring gently",
            "4. Add glycerin (fixative) and mix thoroughly",
            "5. Add distilled water in small increments",
            "6. Stir gently for 2-3 minutes (avoid creating bubbles)",
            "7. Filter through coffee filter if needed",
            "8. Pour into amber glass bottles",
            "9. Seal tightly and label with date",
            "10. Store in cool, dark place for maturation",
        ]

    @staticmethod
    def calculate_costs(
        formula: FragranceFormula, bottle_size_ml: float = 100.0, bottle_cost: float = 2.50
    ) -> Dict[str, any]:
        """Complete cost analysis."""

        # Calculate quantities
        alcohol_ml = (formula.alcohol_percent / 100) * bottle_size_ml
        water_ml = (formula.water_percent / 100) * bottle_size_ml
        fixatives_ml = (formula.fixatives_percent / 100) * bottle_size_ml
        fragrance_g = (formula.total_fragrance_percent() / 100) * bottle_size_ml * FRAGRANCE_OIL_DENSITY

        # Costs
        alcohol_cost = (alcohol_ml / 1000) * 15.0  # $15/L
        water_cost = (water_ml / 1000) * 0.50  # $0.50/L
        fixatives_cost = (fixatives_ml * 1.26 / 1000) * 10.0  # $10/kg

        # Fragrance ingredient costs
        fragrance_cost = 0
        total_frag = formula.total_fragrance_percent()

        for ing in formula.ingredients:
            fraction = ing.concentration_percent / total_frag
            ing_g = fragrance_g * fraction
            fragrance_cost += ing_g * ing.cost_per_gram

        raw_materials = alcohol_cost + water_cost + fixatives_cost + fragrance_cost
        total_cost = raw_materials + bottle_cost

        # Retail pricing
        retail_price = total_cost * 5.0  # 400% markup
        profit = retail_price - total_cost

        return {
            "bottle_size": f"{bottle_size_ml} ml ({round(bottle_size_ml * ML_TO_OZ, 1)} oz)",
            "cost_breakdown": {
                "fragrance_oils": round(fragrance_cost, 2),
                "alcohol": round(alcohol_cost, 2),
                "water": round(water_cost, 2),
                "fixatives": round(fixatives_cost, 2),
                "packaging": bottle_cost,
                "total_production": round(total_cost, 2),
            },
            "pricing": {
                "production_cost": round(total_cost, 2),
                "suggested_retail": round(retail_price, 2),
                "profit_per_unit": round(profit, 2),
                "profit_margin_percent": round((profit / retail_price) * 100, 1),
            },
            "cost_per_ml": round(total_cost / bottle_size_ml, 3),
        }

    @staticmethod
    def check_safety_compliance(formula: FragranceFormula) -> Dict[str, any]:
        """Check IFRA compliance and allergen content."""

        violations = []
        allergens = []
        total_frag = formula.total_fragrance_percent()

        for ing in formula.ingredients:
            actual_in_product = (ing.concentration_percent / 100) * total_frag

            if ing.ifra_max_limit and actual_in_product > ing.ifra_max_limit:
                violations.append(
                    {
                        "ingredient": ing.name,
                        "actual": round(actual_in_product, 3),
                        "max_allowed": ing.ifra_max_limit,
                        "reduction_needed": round(actual_in_product - ing.ifra_max_limit, 3),
                    }
                )

            if ing.allergen:
                allergens.append({"name": ing.name, "percent_in_product": round(actual_in_product, 3)})

        total_allergen = sum(a["percent_in_product"] for a in allergens)

        return {
            "ifra_compliant": len(violations) == 0,
            "violations": violations,
            "allergens_detected": allergens,
            "total_allergen_percent": round(total_allergen, 2),
            "labeling_required": total_allergen > 1.0,
            "label_text": f"Contains: {', '.join(a['name'] for a in allergens)}" if allergens else "No allergens",
        }

    @staticmethod
    def calculate_maturation_time(fragrance_type: FragranceType, natural_percent: float = 50.0) -> Dict[str, any]:
        """Calculate recommended maturation period."""

        base_days = {
            FragranceType.PARFUM: 30,
            FragranceType.EAU_DE_PARFUM: 21,
            FragranceType.EAU_DE_TOILETTE: 14,
            FragranceType.EAU_DE_COLOGNE: 7,
            FragranceType.BODY_SPLASH: 3,
        }

        days = base_days[fragrance_type]

        # Adjust for natural ingredients
        if natural_percent > 50:
            multiplier = 1 + (natural_percent - 50) / 100
            days = int(days * multiplier)

        maturation_date = datetime.now() + timedelta(days=days)
        optimal_date = datetime.now() + timedelta(days=days * 2)

        return {
            "minimum_days": days,
            "recommended_days": days + 7,
            "optimal_days": days * 2,
            "ready_by": maturation_date.strftime("%Y-%m-%d"),
            "optimal_by": optimal_date.strftime("%Y-%m-%d"),
            "storage_instructions": [
                "Store in amber glass bottles",
                f"Keep at {20}°C (room temperature)",
                "Avoid direct sunlight",
                "Shake gently daily for first week",
            ],
        }


# Example Usage
if __name__ == "__main__":
    print("=" * 70)
    print("PERFUME FORMULATION SYSTEM - DEMONSTRATION")
    print("=" * 70)

    # Create sample formula
    ingredients = [
        # Top Notes (22%)
        FragranceIngredient("Bergamot Oil", 10.0, NoteCategory.TOP, 0.15, 0.4, True),
        FragranceIngredient("Lemon Oil", 8.0, NoteCategory.TOP, 0.12, allergen=True),
        FragranceIngredient("Lavender", 4.0, NoteCategory.TOP, 0.08),
        # Middle Notes (50%)
        FragranceIngredient("Rose Absolute", 15.0, NoteCategory.MIDDLE, 2.50, allergen=True),
        FragranceIngredient("Jasmine", 12.0, NoteCategory.MIDDLE, 3.20),
        FragranceIngredient("Ylang Ylang", 10.0, NoteCategory.MIDDLE, 0.45),
        FragranceIngredient("Geranium", 8.0, NoteCategory.MIDDLE, 0.25),
        FragranceIngredient("Neroli", 5.0, NoteCategory.MIDDLE, 1.80, allergen=True),
        # Base Notes (28%)
        FragranceIngredient("Sandalwood", 12.0, NoteCategory.BASE, 1.20),
        FragranceIngredient("Vanilla", 8.0, NoteCategory.BASE, 0.80),
        FragranceIngredient("Patchouli", 5.0, NoteCategory.BASE, 0.18),
        FragranceIngredient("Musk Ketone", 3.0, NoteCategory.BASE, 0.95, 1.4, False, False),
    ]

    formulator = PerfumeFormulator()

    # 1. Create Formula
    print("\n1. CREATING EAU DE PARFUM")
    print("-" * 70)
    result = formulator.create_balanced_formula("Rose Garden EDP", FragranceType.EAU_DE_PARFUM, ingredients)

    formula = result["formula"]
    balance = result["note_balance"]

    print(f"Formula: {formula.name}")
    print(f"Type: {formula.fragrance_type.value}")
    print(f"Fragrance: {result['fragrance_concentration']}%")
    print(f"Alcohol: {formula.alcohol_percent:.1f}%")
    print(f"Water: {formula.water_percent:.1f}%")
    print(f"Fixatives: {formula.fixatives_percent:.1f}%")
    print(f"\nNote Balance:")
    print(f"  Top: {balance['top']:.0f}% | Middle: {balance['middle']:.0f}% | Base: {balance['base']:.0f}%")
    print(f"  Balanced: {'✓ Yes' if balance['is_balanced'] else '✗ No'}")

    # 2. Production Batch
    print("\n2. PRODUCTION BATCH (1000 mL)")
    print("-" * 70)
    batch = formulator.calculate_production_batch(formula, 1000.0)

    print(f"Batch Size: {batch['batch_size_ml']} mL ({batch['batch_size_oz']} oz)")
    print(f"\nComponents:")
    for name, qty in batch["components"].items():
        print(f"  {name}: {qty['ml']} mL ({qty['g']} g)")

    print(f"\nTop 5 Fragrance Ingredients:")
    sorted_ings = sorted(batch["fragrance_ingredients"].items(), key=lambda x: x[1]["grams"], reverse=True)[:5]
    for name, data in sorted_ings:
        print(f"  {name}: {data['grams']} g ({data['note']})")

    # 3. Cost Analysis
    print("\n3. COST ANALYSIS (100 mL Bottle)")
    print("-" * 70)
    costs = formulator.calculate_costs(formula, 100.0, 2.50)

    print(f"Bottle Size: {costs['bottle_size']}")
    print(f"\nCost Breakdown:")
    for item, cost in costs["cost_breakdown"].items():
        print(f"  {item.replace('_', ' ').title()}: ${cost:.2f}")

    print(f"\nPricing:")
    print(f"  Production Cost: ${costs['pricing']['production_cost']:.2f}")
    print(f"  Retail Price: ${costs['pricing']['suggested_retail']:.2f}")
    print(f"  Profit: ${costs['pricing']['profit_per_unit']:.2f} ({costs['pricing']['profit_margin_percent']}%)")

    # 4. Safety Check
    print("\n4. SAFETY & COMPLIANCE")
    print("-" * 70)
    safety = formulator.check_safety_compliance(formula)

    print(f"IFRA Compliant: {'✓ Yes' if safety['ifra_compliant'] else '✗ No'}")
    print(f"Total Allergens: {safety['total_allergen_percent']}%")
    print(f"Labeling Required: {'Yes' if safety['labeling_required'] else 'No'}")
    if safety["allergens_detected"]:
        print(f"Label: {safety['label_text']}")

    # 5. Maturation
    print("\n5. MATURATION SCHEDULE")
    print("-" * 70)
    maturation = formulator.calculate_maturation_time(FragranceType.EAU_DE_PARFUM, 60.0)

    print(f"Minimum: {maturation['minimum_days']} days")
    print(f"Recommended: {maturation['recommended_days']} days")
    print(f"Optimal: {maturation['optimal_days']} days")
    print(f"Ready By: {maturation['ready_by']}")
    print(f"Optimal By: {maturation['optimal_by']}")

    print("\n" + "=" * 70)
    print("FORMULATION COMPLETE")
    print("=" * 70)
