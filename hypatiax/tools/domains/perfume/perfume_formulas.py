"""
Perfume & Fragrance Formulation
================================

Comprehensive perfume formulation system for drugstore industry including:
- Fragrance concentration calculations (EDT, EDP, Parfum)
- Top/Middle/Base note balancing
- Solvent and fixative calculations
- Dilution and blending formulas
- Stability and preservation
- Cost analysis and batch scaling

All formulas follow IFRA (International Fragrance Association) guidelines.

Author: Perfumery Domain Team
Version: 1.0.0
"""

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

# Constants
EPSILON = 1e-12
ALCOHOL_DENSITY = 0.789  # g/mL at 20°C (ethanol)
WATER_DENSITY = 1.0  # g/mL at 20°C
ML_TO_OZ = 0.033814  # Convert mL to fl oz
PERFUME_SHELF_LIFE_MONTHS = 36  # Typical shelf life


class FragranceType(Enum):
    """Standard fragrance concentration types."""
    PARFUM = "Parfum"  # 20-30% concentration
    EAU_DE_PARFUM = "Eau de Parfum"  # 15-20%
    EAU_DE_TOILETTE = "Eau de Toilette"  # 5-15%
    EAU_DE_COLOGNE = "Eau de Cologne"  # 2-5%
    BODY_SPLASH = "Body Splash"  # 1-3%


class NoteCategory(Enum):
    """Fragrance note pyramid categories."""
    TOP = "Top Notes"  # 15-30% (evaporate in 15-30 min)
    MIDDLE = "Middle Notes"  # 40-60% (last 2-4 hours)
    BASE = "Base Notes"  # 20-35% (last 5-24 hours)


@dataclass
class FragranceIngredient:
    """Represents a single fragrance ingredient."""
    name: str
    concentration_percent: float  # % in fragrance compound
    note_type: NoteCategory
    cost_per_gram: float
    ifra_max_limit: Optional[float] = None  # Max % allowed in finished product
    allergen: bool = False
    natural: bool = True

    def validate(self) -> bool:
        """Validate ingredient parameters."""
        if self.concentration_percent < 0 or self.concentration_percent > 100:
            raise ValueError(f"Concentration must be 0-100%, got {self.concentration_percent}")
        if self.cost_per_gram < 0:
            raise ValueError(f"Cost cannot be negative, got {self.cost_per_gram}")
        return True


@dataclass
class FragranceFormula:
    """Complete perfume formulation."""
    name: str
    fragrance_type: FragranceType
    ingredients: List[FragranceIngredient] = field(default_factory=list)
    alcohol_percent: float = 0.0
    water_percent: float = 0.0
    fixatives_percent: float = 0.0
    batch_size_ml: float = 100.0

    def total_fragrance_percent(self) -> float:
        """Calculate total fragrance compound percentage."""
        return sum(ing.concentration_percent for ing in self.ingredients)

    def validate_totals(self) -> bool:
        """Validate that all percentages sum to 100%."""
        total = (self.total_fragrance_percent() +
                self.alcohol_percent +
                self.water_percent +
                self.fixatives_percent)

        if abs(total - 100.0) > EPSILON:
            raise ValueError(
                f"Formula must total 100%. Current total: {total:.2f}%"
            )
        return True


class FragranceCalculator:
    """Core fragrance calculation engine."""

    @staticmethod
    def get_concentration_range(fragrance_type: FragranceType) -> Tuple[float, float]:
        """
        Get recommended fragrance oil concentration range.

        Args:
            fragrance_type: Type of fragrance product

        Returns:
            Tuple of (min_percent, max_percent)
        """
        ranges = {
            FragranceType.PARFUM: (20.0, 30.0),
            FragranceType.EAU_DE_PARFUM: (15.0, 20.0),
            FragranceType.EAU_DE_TOILETTE: (5.0, 15.0),
            FragranceType.EAU_DE_COLOGNE: (2.0, 5.0),
            FragranceType.BODY_SPLASH: (1.0, 3.0)
        }
        return ranges[fragrance_type]

    @staticmethod
    def calculate_note_balance(
        ingredients: List[FragranceIngredient],
        validate: bool = True
    ) -> Dict[str, float]:
        """
        Calculate the balance of top, middle, and base notes.

        Recommended ratios:
        - Top notes: 15-30%
        - Middle notes: 40-60%
        - Base notes: 20-35%

        Args:
            ingredients: List of fragrance ingredients
            validate: Enable validation checks

        Returns:
            Dictionary with note percentages and recommendations
        """
        top_total = sum(
            ing.concentration_percent
            for ing in ingredients
            if ing.note_type == NoteCategory.TOP
        )
        middle_total = sum(
            ing.concentration_percent
            for ing in ingredients
            if ing.note_type == NoteCategory.MIDDLE
        )
        base_total = sum(
            ing.concentration_percent
            for ing in ingredients
            if ing.note_type == NoteCategory.BASE
        )

        total = top_total + middle_total + base_total

        if validate and abs(total - 100.0) > EPSILON:
            raise ValueError(
                f"Fragrance notes must sum to 100%, got {total:.2f}%"
            )

        # Check if balance is within recommended ranges
        balanced = (
            15 <= top_total <= 30 and
            40 <= middle_total <= 60 and
            20 <= base_total <= 35
        )

        return {
            'top_notes_percent': top_total,
            'middle_notes_percent': middle_total,
            'base_notes_percent': base_total,
            'is_balanced': balanced,
            'recommended_top': (15, 30),
            'recommended_middle': (40, 60),
            'recommended_base': (20, 35)
        }

    @staticmethod
    def calculate_alcohol_water_ratio(
        fragrance_percent: float,
        fragrance_type: FragranceType,
        fixatives_percent: float = 0.0,
        validate: bool = True
    ) -> Dict[str, float]:
        """
        Calculate alcohol and water percentages for fragrance.

        Typical ratios:
        - Parfum: 85-90% alcohol, 5-10% water
        - EDP: 80-85% alcohol, 10-15% water
        - EDT: 70-80% alcohol, 15-25% water
        - EDC: 60-70% alcohol, 25-35% water

        Args:
            fragrance_percent: Fragrance compound percentage
            fragrance_type: Type of product
            fixatives_percent: Additional fixatives (e.g., glycerin)
            validate: Enable validation

        Returns:
            Dictionary with calculated percentages
        """
        if validate:
            if not 0 <= fragrance_percent <= 100:
                raise ValueError("Fragrance percent must be 0-100%")
            if not 0 <= fixatives_percent <= 10:
                raise ValueError("Fixatives typically 0-10%")

        # Remaining percentage after fragrance and fixatives
        remaining = 100.0 - fragrance_percent - fixatives_percent

        # Determine alcohol ratio based on fragrance type
        alcohol_ratios = {
            FragranceType.PARFUM: 0.90,
            FragranceType.EAU_DE_PARFUM: 0.82,
            FragranceType.EAU_DE_TOILETTE: 0.75,
            FragranceType.EAU_DE_COLOGNE: 0.65,
            FragranceType.BODY_SPLASH: 0.60
        }

        alcohol_ratio = alcohol_ratios.get(fragrance_type, 0.75)

        alcohol_percent = remaining * alcohol_ratio
        water_percent = remaining - alcohol_percent

        return {
            'alcohol_percent': alcohol_percent,
            'water_percent': water_percent,
            'fixatives_percent': fixatives_percent,
            'fragrance_percent': fragrance_percent,
            'total_percent': fragrance_percent + alcohol_percent + water_percent + fixatives_percent
        }

    @staticmethod
    def calculate_batch_quantities(
        formula: FragranceFormula,
        batch_size_ml: float,
        validate: bool = True
    ) -> Dict[str, float]:
        """
        Calculate ingredient quantities for a batch.

        Args:
            formula: Complete fragrance formula
            batch_size_ml: Target batch size in mL
            validate: Enable validation

        Returns:
            Dictionary with quantities in grams and mL
        """
        if validate:
            if batch_size_ml <= 0:
                raise ValueError("Batch size must be positive")
            formula.validate_totals()

        # Calculate volumes
        alcohol_ml = (formula.alcohol_percent / 100.0) * batch_size_ml
        water_ml = (formula.water_percent / 100.0) * batch_size_ml
        fixatives_ml = (formula.fixatives_percent / 100.0) * batch_size_ml

        # Calculate masses (assuming fragrance oil density ≈ 0.9 g/mL)
        FRAGRANCE_OIL_DENSITY = 0.9

        alcohol_g = alcohol_ml * ALCOHOL_DENSITY
        water_g = water_ml * WATER_DENSITY
        fixatives_g = fixatives_ml * 1.26  # Glycerin density

        fragrance_ml = (formula.total_fragrance_percent() / 100.0) * batch_size_ml
        fragrance_g = fragrance_ml * FRAGRANCE_OIL_DENSITY

        # Individual ingredient quantities
        ingredient_quantities = {}
        for ing in formula.ingredients:
            fraction = ing.concentration_percent / formula.total_fragrance_percent()
            ing_g = fragrance_g * fraction
            ingredient_quantities[ing.name] = {
                'grams': ing_g,
                'percent_of_fragrance': ing.concentration_percent,
                'note_type': ing.note_type.value
            }

        return {
            'batch_size_ml': batch_size_ml,
            'batch_size_oz': batch_size_ml * ML_TO_OZ,
            'alcohol_ml': alcohol_ml,
            'alcohol_g': alcohol_g,
            'water_ml': water_ml,
            'water_g': water_g,
            'fixatives_ml': fixatives_ml,
            'fixatives_g': fixatives_g,
            'fragrance_oil_ml': fragrance_ml,
            'fragrance_oil_g': fragrance_g,
            'ingredients': ingredient_quantities,
            'total_mass_g': alcohol_g + water_g + fixatives_g + fragrance_g
        }

    @staticmethod
    def dilute_fragrance(
        current_concentration: float,
        current_volume_ml: float,
        target_concentration: float,
        validate: bool = True
    ) -> Dict[str, float]:
        """
        Calculate dilution to achieve target concentration.

        Formula: C₁V₁ = C₂V₂

        Args:
            current_concentration: Current fragrance % (e.g., 20%)
            current_volume_ml: Current volume in mL
            target_concentration: Desired fragrance % (e.g., 15%)
            validate: Enable validation

        Returns:
            Dictionary with dilution calculations
        """
        if validate:
            if target_concentration >= current_concentration:
                raise ValueError(
                    "Target concentration must be less than current "
                    f"(current: {current_concentration}%, target: {target_concentration}%)"
                )
            if current_concentration <= 0 or target_concentration <= 0:
                raise ValueError("Concentrations must be positive")
            if current_volume_ml <= 0:
                raise ValueError("Volume must be positive")

        # C₁V₁ = C₂V₂ → V₂ = C₁V₁/C₂
        final_volume_ml = (current_concentration * current_volume_ml) / target_concentration

        # Volume of diluent (alcohol + water) to add
        diluent_to_add_ml = final_volume_ml - current_volume_ml

        # Assume 80% alcohol, 20% water for diluent
        alcohol_to_add_ml = diluent_to_add_ml * 0.80
        water_to_add_ml = diluent_to_add_ml * 0.20

        return {
            'current_concentration_percent': current_concentration,
            'current_volume_ml': current_volume_ml,
            'target_concentration_percent': target_concentration,
            'final_volume_ml': final_volume_ml,
            'diluent_to_add_ml': diluent_to_add_ml,
            'alcohol_to_add_ml': alcohol_to_add_ml,
            'water_to_add_ml': water_to_add_ml,
            'dilution_factor': current_concentration / target_concentration
        }

    @staticmethod
    def scale_formula(
        original_batch_ml: float,
        target_batch_ml: float,
        ingredient_quantities: Dict[str, float],
        validate: bool = True
    ) -> Dict[str, float]:
        """
        Scale formula up or down while maintaining ratios.

        Args:
            original_batch_ml: Original batch size
            target_batch_ml: Desired batch size
            ingredient_quantities: Dictionary of ingredient amounts (in g)
            validate: Enable validation

        Returns:
            Dictionary with scaled quantities
        """
        if validate:
            if original_batch_ml <= 0 or target_batch_ml <= 0:
                raise ValueError("Batch sizes must be positive")

        scale_factor = target_batch_ml / original_batch_ml

        scaled_quantities = {}
        for ingredient, amount in ingredient_quantities.items():
            scaled_quantities[ingredient] = amount * scale_factor

        return {
            'original_batch_ml': original_batch_ml,
            'target_batch_ml': target_batch_ml,
            'scale_factor': scale_factor,
            'scaled_quantities_g': scaled_quantities
        }


class CostAnalyzer:
    """Analyze production costs for fragrance formulas."""

    @staticmethod
    def calculate_formula_cost(
        formula: FragranceFormula,
        batch_size_ml: float,
        alcohol_cost_per_liter: float = 15.0,
        water_cost_per_liter: float = 0.50,
        fixative_cost_per_kg: float = 10.0,
        packaging_cost_per_unit: float = 2.0,
        validate: bool = True
    ) -> Dict[str, float]:
        """
        Calculate total production cost for a batch.

        Args:
            formula: Fragrance formula
            batch_size_ml: Batch size in mL
            alcohol_cost_per_liter: Cost of alcohol per liter
            water_cost_per_liter: Cost of water per liter
            fixative_cost_per_kg: Cost of fixatives per kg
            packaging_cost_per_unit: Cost per bottle/package
            validate: Enable validation

        Returns:
            Complete cost breakdown
        """
        if validate:
            formula.validate_totals()

        calc = FragranceCalculator()
        quantities = calc.calculate_batch_quantities(formula, batch_size_ml)

        # Calculate raw material costs
        alcohol_cost = (quantities['alcohol_ml'] / 1000.0) * alcohol_cost_per_liter
        water_cost = (quantities['water_ml'] / 1000.0) * water_cost_per_liter
        fixatives_cost = (quantities['fixatives_g'] / 1000.0) * fixative_cost_per_kg

        # Fragrance ingredient costs
        fragrance_cost = 0.0
        for ing in formula.ingredients:
            ing_quantity = quantities['ingredients'][ing.name]['grams']
            fragrance_cost += ing_quantity * ing.cost_per_gram

        # Total costs
        raw_material_cost = alcohol_cost + water_cost + fixatives_cost + fragrance_cost
        total_cost = raw_material_cost + packaging_cost_per_unit

        # Cost per mL
        cost_per_ml = total_cost / batch_size_ml
        cost_per_oz = cost_per_ml / ML_TO_OZ

        return {
            'batch_size_ml': batch_size_ml,
            'alcohol_cost': alcohol_cost,
            'water_cost': water_cost,
            'fixatives_cost': fixatives_cost,
            'fragrance_oil_cost': fragrance_cost,
            'raw_material_cost': raw_material_cost,
            'packaging_cost': packaging_cost_per_unit,
            'total_production_cost': total_cost,
            'cost_per_ml': cost_per_ml,
            'cost_per_oz': cost_per_oz,
            'fragrance_cost_percentage': (fragrance_cost / total_cost) * 100
        }

    @staticmethod
    def calculate_retail_pricing(
        production_cost: float,
        markup_percentage: float = 400.0,
        validate: bool = True
    ) -> Dict[str, float]:
        """
        Calculate retail pricing with typical drugstore markup.

        Drugstore markups typically range from 300-500%.

        Args:
            production_cost: Total production cost
            markup_percentage: Retail markup percentage
            validate: Enable validation

        Returns:
            Pricing analysis
        """
        if validate:
            if production_cost <= 0:
                raise ValueError("Production cost must be positive")
            if markup_percentage < 0:
                raise ValueError("Markup cannot be negative")

        retail_price = production_cost * (1 + markup_percentage / 100.0)
        profit_margin = retail_price - production_cost
        profit_percentage = (profit_margin / retail_price) * 100

        return {
            'production_cost': production_cost,
            'markup_percentage': markup_percentage,
            'retail_price': retail_price,
            'profit_margin': profit_margin,
            'profit_percentage': profit_percentage
        }


class SafetyAndCompliance:
    """IFRA compliance and safety calculations."""

    @staticmethod
    def check_ifra_compliance(
        formula: FragranceFormula,
        validate: bool = True
    ) -> Dict[str, any]:
        """
        Check formula against IFRA restrictions.

        Args:
            formula: Fragrance formula to check
            validate: Enable validation

        Returns:
            Compliance report
        """
        violations = []
        warnings = []
        allergens = []

        for ing in formula.ingredients:
            # Check IFRA limits
            if ing.ifra_max_limit is not None:
                actual_in_product = (
                    ing.concentration_percent / 100.0 *
                    formula.total_fragrance_percent()
                )
                if actual_in_product > ing.ifra_max_limit:
                    violations.append({
                        'ingredient': ing.name,
                        'actual_percent': actual_in_product,
                        'max_allowed': ing.ifra_max_limit,
                        'excess': actual_in_product - ing.ifra_max_limit
                    })

            # Track allergens
            if ing.allergen:
                allergens.append({
                    'ingredient': ing.name,
                    'concentration_in_product': (
                        ing.concentration_percent / 100.0 *
                        formula.total_fragrance_percent()
                    )
                })

        # Check total allergen content
        total_allergen_percent = sum(a['concentration_in_product'] for a in allergens)
        if total_allergen_percent > 1.0:  # EU requires labeling >1%
            warnings.append(
                f"Total allergens {total_allergen_percent:.2f}% - requires labeling"
            )

        compliant = len(violations) == 0

        return {
            'compliant': compliant,
            'violations': violations,
            'warnings': warnings,
            'allergens': allergens,
            'total_allergen_percent': total_allergen_percent,
            'requires_allergen_labeling': total_allergen_percent > 1.0
        }

    @staticmethod
    def calculate_maturation_time(
        fragrance_type: FragranceType,
        natural_ingredient_percent: float = 50.0
    ) -> Dict[str, int]:
        """
        Calculate recommended maturation time.

        Natural ingredients need longer maturation.

        Args:
            fragrance_type: Type of fragrance
            natural_ingredient_percent: Percentage of natural ingredients

        Returns:
            Recommended maturation times
        """
        # Base maturation times in days
        base_times = {
            FragranceType.PARFUM: 30,
            FragranceType.EAU_DE_PARFUM: 21,
            FragranceType.EAU_DE_TOILETTE: 14,
            FragranceType.EAU_DE_COLOGNE: 7,
            FragranceType.BODY_SPLASH: 3
        }

        base_days = base_times[fragrance_type]

        # Increase time for natural ingredients
        if natural_ingredient_percent > 50:
            natural_multiplier = 1 + (natural_ingredient_percent - 50) / 100
            base_days = int(base_days * natural_multiplier)

        return {
            'minimum_days': base_days,
            'recommended_days': base_days + 7,
            'optimal_days': base_days * 2,
            'weeks': base_days // 7
        }


# Example usage and demonstrations
if __name__ == "__main__":
    print("=" * 80)
    print("PERFUME FORMULATION SYSTEM - DEMONSTRATION")
    print("=" * 80)

    # 1. Create a fragrance formula
    print("\n1. CREATING EAU DE PARFUM FORMULA")
    print("-" * 80)

    # Define ingredients
    ingredients = [
        # Top notes (20%)
        FragranceIngredient("Bergamot Oil", 10.0, NoteCategory.TOP, 0.15,
                           ifra_max_limit=0.4, allergen=True),
        FragranceIngredient("Lemon Oil", 7.0, NoteCategory.TOP, 0.12, allergen=True),
        FragranceIngredient("Lavender Oil", 3.0, NoteCategory.TOP, 0.08),

        # Middle notes (50%)
        FragranceIngredient("Rose Absolute", 15.0, NoteCategory.MIDDLE, 2.50,
                           allergen=True, natural=True),
        FragranceIngredient("Jasmine Sambac", 12.0, NoteCategory.MIDDLE, 3.20,
                           natural=True),
        FragranceIngredient("Ylang Ylang", 10.0, NoteCategory.MIDDLE, 0.45),
        FragranceIngredient("Geranium Oil", 8.0, NoteCategory.MIDDLE, 0.25),
        FragranceIngredient("Neroli Oil", 5.0, NoteCategory.MIDDLE, 1.80, allergen=True),

        # Base notes (30%)
        FragranceIngredient("Sandalwood Oil", 12.0, NoteCategory.BASE, 1.20),
        FragranceIngredient("Vanilla Absolute", 8.0, NoteCategory.BASE, 0.80),
        FragranceIngredient("Patchouli Oil", 5.0, NoteCategory.BASE, 0.18),
        FragranceIngredient("Musk Ketone", 5.0, NoteCategory.BASE, 0.95,
                           natural=False, ifra_max_limit=1.4)
    ]

    # Validate all ingredients
    for ing in ingredients:
        ing.validate()

    print(f"Formula contains {len(ingredients)} ingredients")

    # 2. Check note balance
    print("\n2. NOTE BALANCE ANALYSIS")
    print("-" * 80)
    calc = FragranceCalculator()
    balance = calc.calculate_note_balance(ingredients)

    print(f"Top Notes: {balance['top_notes_percent']:.1f}% "
          f"(recommended: {balance['recommended_top']})")
    print(f"Middle Notes: {balance['middle_notes_percent']:.1f}% "
          f"(recommended: {balance['recommended_middle']})")
    print(f"Base Notes: {balance['base_notes_percent']:.1f}% "
          f"(recommended: {balance['recommended_base']})")
    print(f"Well Balanced: {'✓ Yes' if balance['is_balanced'] else '✗ No'}")

    # 3. Calculate alcohol/water ratio
    print("\n3. SOLVENT CALCULATION")
    print("-" * 80)
    fragrance_concentration = 18.0  # 18% for EDP
    solvents = calc.calculate_alcohol_water_ratio(
        fragrance_concentration,
        FragranceType.EAU_DE_PARFUM,
        fixatives_percent=2.0
    )

    print(f"Fragrance Oil: {solvents['fragrance_percent']:.1f}%")
    print(f"Alcohol (96%): {solvents['alcohol_percent']:.1f}%")
    print(f"Water (Distilled): {solvents['water_percent']:.1f}%")
    print(f"Fixatives (Glycerin): {solvents['fixatives_percent']:.1f}%")
    print(f"Total: {solvents['total_percent']:.1f}%")

    # 4. Create complete formula
    print("\n4. COMPLETE FORMULA")
    print("-" * 80)
    formula = FragranceFormula(
        name="Floral Elegance EDP",
        fragrance_type=FragranceType.EAU_DE_PARFUM,
        ingredients=ingredients,
        alcohol_percent=solvents['alcohol_percent'],
        water_percent=solvents['water_percent'],
        fixatives_percent=solvents['fixatives_percent'],
        batch_size_ml=1000.0
    )

    print(f"Formula: {formula.name}")
    print(f"Type: {formula.fragrance_type.value}")
    print(f"Batch Size: {formula.batch_size_ml} mL")

    # 5. Calculate batch quantities
    print("\n5. BATCH PRODUCTION (1000 mL)")
    print("-" * 80)
    quantities = calc.calculate_batch_quantities(formula, 1000.0)

    print(f"\nSolvents:")
    print(f"  Alcohol: {quantities['alcohol_ml']:.1f} mL ({quantities['alcohol_g']:.1f} g)")
    print(f"  Water: {quantities['water_ml']:.1f} mL ({quantities['water_g']:.1f} g)")
    print(f"  Fixatives: {quantities['fixatives_ml']:.1f} mL ({quantities['fixatives_g']:.1f} g)")
    print(f"\nFragrance Oil: {quantities['fragrance_oil_ml']:.1f} mL "
          f"({quantities['fragrance_oil_g']:.1f} g)")

    print(f"\nTop 5 Ingredients by weight:")
    sorted_ings = sorted(
        quantities['ingredients'].items(),
        key=lambda x: x[1]['grams'],
        reverse=True
    )[:5]
    for name, data in sorted_ings:
        print(f"  {name}: {data['grams']:.2f} g ({data['note_type']})")

    # 6. Cost analysis
    print("\n6. COST ANALYSIS")
    print("-" * 80)
    cost_analyzer = CostAnalyzer()
    costs = cost_analyzer.calculate_formula_cost(
        formula,
        batch_size_ml=100.0,  # Calculate for 100mL bottle
        alcohol_cost_per_liter=15.0,
        water_cost_per_liter=0.50,
        fixative_cost_per_kg=10.0,
        packaging_cost_per_unit=2.50
    )

    print(f"Production Cost Breakdown (100 mL bottle):")
    print(f"  Fragrance Oil: ${costs['fragrance_oil_cost']:.2f}")
    print(f"  Alcohol: ${costs['alcohol_cost']:.2f}")
    print(f"  Water: ${costs['water_cost']:.2f}")
    print(f"  Fixatives: ${costs['fixatives_cost']:.2f}")
    print(f"  Packaging: ${costs['packaging_cost']:.2f}")
    print(f"  TOTAL: ${costs['total_production_cost']:.2f}")
    print(f"\nFragrance represents {costs['fragrance_cost_percentage']:.1f}% of cost")
    print(f"Cost per oz: ${costs['cost_per_oz']:.2f}")

    # 7. Retail pricing
    print("\n7. RETAIL PRICING")
    print("-" * 80)
    pricing = cost_analyzer.calculate_retail_pricing(
        costs['total_production_cost'],
        markup_percentage=400.0
    )

    print(f"Production Cost: ${pricing['production_cost']:.2f}")
    print(f"Retail Price: ${pricing['retail_price']:.2f}")
    print(f"Profit Margin: ${pricing['profit_margin']:.2f} "
          f"({pricing['profit_percentage']:.1f}%)")

    # 8. Dilution example
    print("\n8. DILUTION CALCULATION")
    print("-" * 80)
    print("Converting 100mL of 20% EDP to 15% EDT:")
    dilution = calc.dilute_fragrance(
        current_concentration=20.0,
        current_volume_ml=100.0,
        target_concentration=15.0
    )

    print(f"Add {dilution['diluent_to_add_ml']:.1
