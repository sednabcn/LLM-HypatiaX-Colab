"""
AI Training Datasets Generator - 150 DETAILED SCENARIOS EACH
=============================================================
Creates 2 comprehensive CSV files:
1. perfume_detailed_150.csv (150 detailed scenarios)
2. clinical_detailed_150.csv (150 detailed scenarios)

Total: 300 detailed step-by-step training examples
Format: Real-world scenarios with complete calculations
"""

import csv

# ============================================================================
# PERFUME DETAILED SCENARIOS (150 ENTRIES)
# ============================================================================

PERFUME_DETAILED = [
    # SECTION 1: BASIC FORMULATION (20 entries)
    ("Calculate alcohol and water percentages for EDP with 18% fragrance and 2% fixatives", """FORMULA: Alcohol-Water Ratio Calculation
Given:
- Fragrance concentration: 18%
- Fixatives: 2%
- Fragrance type: Eau de Parfum (EDP)

Step 1: Calculate remaining percentage
Remaining = 100% - 18% - 2% = 80%

Step 2: Apply EDP alcohol ratio (82% of remaining)
Alcohol = 80% × 0.82 = 65.6%
Water = 80% - 65.6% = 14.4%

Step 3: Verify total
18% + 2% + 65.6% + 14.4% = 100% ✓

RESULT:
- Fragrance oil: 18%
- Fixatives: 2%
- Alcohol (96%): 65.6%
- Distilled water: 14.4%
Total: 100%"""),

    ("Calculate batch quantities for 500ml perfume with 15% fragrance oil", """FORMULA: Batch Quantity Calculation
Given:
- Target batch: 500 mL
- Fragrance: 15%, Alcohol: 70%, Water: 13%, Fixatives: 2%

Step 1: Calculate volumes
- Fragrance: 500 × 0.15 = 75 mL
- Alcohol: 500 × 0.70 = 350 mL
- Water: 500 × 0.13 = 65 mL
- Fixatives: 500 × 0.02 = 10 mL

Step 2: Convert to masses
- Fragrance: 75 × 0.90 = 67.5 g
- Alcohol: 350 × 0.789 = 276.2 g
- Water: 65 × 1.00 = 65.0 g
- Glycerin: 10 × 1.26 = 12.6 g

RESULT: Total 421.3g for 500mL batch"""),

    ("Validate note pyramid: Top 25%, Middle 45%, Base 30%", """FORMULA: Note Balance Validation
Given: Top 25%, Middle 45%, Base 30%

Recommended ranges:
- Top: 15-30%
- Middle: 40-60%
- Base: 20-35%

Analysis:
✓ Top: 25% (within range)
✓ Middle: 45% (within range)
✓ Base: 30% (within range)
✓ Total: 100%

RESULT: BALANCED, Score 95/100"""),

    ("Dilute 100ml of 20% EDP to 15% EDT", """FORMULA: Dilution C₁V₁=C₂V₂
Given: 20% in 100mL → 15% target

Step 1: V₂ = (20×100)/15 = 133.33mL
Step 2: Add = 133.33-100 = 33.33mL
Step 3: Split 80/20
- Alcohol: 26.67mL
- Water: 6.67mL

RESULT: Final 133.33mL at 15%"""),

    ("Production cost per 100ml: oil $3.50, bottle $2.50, alcohol $15/L, water $0.50/L", """FORMULA: Cost Analysis
Components (100mL, 18% frag):
- Fragrance: $3.50
- Alcohol 70mL: $1.05
- Water 10mL: $0.01
- Glycerin 2mL: $0.03
- Bottle: $2.50
Total: $7.09

Retail (5×): $35.45
Profit: $28.36 (80%)

RESULT: Production $7.09, Retail $35.45"""),

    ("Scale 250ml to 1000ml: 25% frag, 67.5% alcohol, 6% water, 1.5% fix", """FORMULA: Batch Scaling
Scale factor: 1000/250 = 4×

Original (250mL):
62.5, 168.75, 15, 3.75 mL

Scaled (1000mL):
250, 675, 60, 15 mL

RESULT: All ×4, ratios maintained"""),

    ("IFRA check: Bergamot 10% in compound, 18% EDP, limit 0.4%", """FORMULA: IFRA Compliance
Actual: 10% × 18% = 1.8%
IFRA limit: 0.4%
Excess: 1.4%

Correction: Max 2.22% in compound
(2.22% × 18% = 0.4%)

RESULT: NOT COMPLIANT, reduce to 2.22%"""),

    ("Maturation for EDP with 65% naturals", """FORMULA: Maceration Time
Base EDP: 21 days
Natural adj: 1+(65-50)/100 = 1.15
Adjusted: 21×1.15 = 24 days

RESULT: Min 24d, Rec 31d, Opt 48d"""),

    ("EDT concentration specifications", """FORMULA: EDT Standards
Range: 5-15%
Typical: 10%
Longevity: 3-4 hrs
Sillage: Moderate

Comparison:
Parfum 20-30%, EDP 15-20%, EDT 5-15%, EDC 2-5%

RESULT: EDT = 5-15% fragrance"""),

    ("Convert $7.09 per 100ml to per ounce", """FORMULA: Unit Conversion
Per mL: $7.09/100 = $0.0709
Per oz: $0.0709 × 29.5735 = $2.10

Alternative: 100mL = 3.38oz
$7.09/3.38 = $2.10

RESULT: $2.10 per fluid ounce"""),

    ("Calculate fragrance needed for 250ml at 12% EDT concentration", """FORMULA: Component Calculation
Given: 250mL total, 12% EDT

Fragrance oil = 250 × 0.12 = 30 mL

In grams: 30 × 0.90 = 27 g

Cost at $8/mL: 30 × 8 = $240

RESULT: 30mL (27g) fragrance needed"""),

    ("Determine alcohol proof from 96% ethanol perfume base", """FORMULA: Alcohol Proof
Given: 96% ethanol by volume

Proof = ABV × 2
Proof = 96 × 2 = 192 proof

US standard: 192 proof
UK standard: 96% ABV

RESULT: 192 proof (96% ABV)"""),

    ("Calculate density of perfume: 70% alcohol, 20% water, 10% oil", """FORMULA: Mixture Density
Components:
- Alcohol 70%: 0.789 g/mL
- Water 20%: 1.00 g/mL
- Oil 10%: 0.90 g/mL

Density = Σ(fraction × density)
= 0.70×0.789 + 0.20×1.0 + 0.10×0.9
= 0.552 + 0.20 + 0.09 = 0.842 g/mL

RESULT: 0.842 g/mL (100mL = 84.2g)"""),

    ("Find profit margin: cost $8.50, retail $45.00", """FORMULA: Profit Margin
Cost: $8.50
Retail: $45.00
Profit: $36.50

Markup: ($36.50/$8.50)×100 = 429%
Margin: ($36.50/$45.00)×100 = 81.1%

RESULT: 429% markup, 81% margin"""),

    ("Calculate yield loss with 3% evaporation in 500ml batch", """FORMULA: Yield Loss
Target: 500mL
Evaporation: 3%

Loss: 500 × 0.03 = 15mL
Yield: 500 - 15 = 485mL
Required: 500/0.97 = 515.46mL

RESULT: Produce 515mL to yield 500mL"""),

    ("Determine fixative percentage for 300ml with 9ml benzoin", """FORMULA: Fixative Calculation
Total: 300mL
Benzoin: 9mL

% = (9/300) × 100 = 3%

Range: 2-5% recommended
Status: Optimal ✓

RESULT: 3% fixative (within range)"""),

    ("Classify 12% concentration: EDT or EDP?", """FORMULA: Classification Check
Given: 12% concentration

EDT range: 5-15%
EDP range: 15-20%

12% falls in EDT range
Close to EDP threshold
Longevity: ~4 hours

RESULT: EDT (or EDT Intense)"""),

    ("Calculate rose oil cost: $120/oz, using 5ml in 100ml perfume", """FORMULA: Essential Oil Costing
Rose: $120/oz = $120/29.57mL = $4.06/mL
Amount: 5mL
Cost: 5 × $4.06 = $20.30

Per mL perfume: $20.30/100 = $0.203/mL

RESULT: $20.30 for rose in 100ml batch"""),

    ("Fragrance load for 8oz soy candle at 8%", """FORMULA: Candle Fragrance Load
Wax: 8oz = 226.8g
Load: 8%

Fragrance: 226.8 × 0.08 = 18.14g
Volume: 18.14/0.9 = 20.16mL

Range: 6-10% for soy ✓

RESULT: 18.14g (20mL) fragrance"""),

    ("Water content if 250ml has 180ml alcohol, 30ml fragrance", """FORMULA: Component Determination
Total: 250mL
Alcohol: 180mL
Fragrance: 30mL

Water = 250 - 180 - 30 = 40mL

Percentages:
Alc 72%, Frag 12%, Water 16%

RESULT: 40mL water (16%)"""),

    # SECTION 2: ACCORD FORMULATION (25 entries)
    ("Design rose-centered floral for 60ml compound", """FORMULA: Floral Accord Design
Target: 60mL rose-dominant

Top (22% = 13.2mL):
- Bergamot: 4.8mL (8%)
- Lemon: 3.6mL (6%)
- Pink pepper: 2.4mL (4%)
- Neroli: 2.4mL (4%)

Heart (50% = 30mL):
- Rose absolute: 10.8mL (18%) ← Main
- Jasmine: 7.2mL (12%)
- Geranium: 6.0mL (10%)
- Ylang ylang: 3.6mL (6%)
- Violet leaf: 2.4mL (4%)

Base (28% = 16.8mL):
- Sandalwood: 6.0mL (10%)
- Vanilla: 4.8mL (8%)
- Patchouli: 3.0mL (5%)
- Musk: 3.0mL (5%)

RESULT: Balanced floral, rose 18%"""),

    ("Create citrus accord: bergamot 40%, lemon 30%, grapefruit 20%, lime 10% for 30ml", """FORMULA: Citrus Accord
Total: 30mL

Components:
- Bergamot: 12mL (40%)
- Lemon: 9mL (30%)
- Grapefruit: 6mL (20%)
- Lime: 3mL (10%)

Verification: 12+9+6+3 = 30 ✓

Character: Bright, fresh, elegant

RESULT: Citrus blend 30mL"""),

    ("Calculate woody base: sandalwood 50%, cedar 30%, vetiver 20% for 40ml", """FORMULA: Woody Accord
Total: 40mL woody base

Volumes:
- Sandalwood: 20mL (50%)
- Cedar: 12mL (30%)
- Vetiver: 8mL (20%)

Masses (×0.92 g/mL):
18.4g, 11.04g, 7.36g

RESULT: 40mL (36.8g) woody base"""),

    ("Formulate oriental: vanilla 30%, amber 30%, patchouli 25%, spices 15% for 60ml", """FORMULA: Oriental Accord
Total: 60mL

Main components:
- Vanilla: 18mL (30%)
- Amber: 18mL (30%)
- Patchouli: 15mL (25%)
- Spice blend: 9mL (15%)

Spice breakdown (9mL):
Cinnamon 40%, Cardamom 30%, Clove 20%, Nutmeg 10%

RESULT: Rich oriental 60mL"""),

    ("Create fougère: lavender 50%, coumarin 30%, oakmoss 20% for 35ml with IFRA check", """FORMULA: Fougère with IFRA
Given: 35mL base

Original:
- Lavender: 17.5mL (50%)
- Coumarin: 10.5mL (30%)
- Oakmoss: 7mL (20%)

IFRA issue: Oakmoss restricted to 0.1%
If accord is 15% in product:
20% × 15% = 3% ✗ EXCEEDS

Adjustment: Use synthetic oakmoss alt

RESULT: Use Evernyl substitute"""),

    ("Design chypre: bergamot 25%, rose 25%, oakmoss 25%, patchouli 25% for 40ml", """FORMULA: Chypre Structure
Total: 40mL equal parts

Components (10mL each):
- Bergamot (Top)
- Rose (Heart)
- Oakmoss (Base) *IFRA
- Patchouli (Base)

Modern: Replace oakmoss with Evernyl

RESULT: Classic chypre 40mL"""),

    ("Calculate aquatic: calone 30%, marine 40%, citrus 30% for 25ml with safety", """FORMULA: Aquatic Accord
Total: 25mL

Original:
- Calone: 7.5mL (30%)
- Marine: 10mL (40%)
- Citrus: 7.5mL (30%)

Calone check:
At 20% in fragrance: 30%×20% = 6%
Recommended max: 3-5%

Adjusted: Reduce calone to 15%
= 3.75mL in 25mL

RESULT: Aquatic 25mL, calone 15%"""),

    ("Formulate gourmand: vanilla 40%, caramel 20%, tonka 20%, fruits 20% for 50ml", """FORMULA: Gourmand Accord
Total: 50mL sweet base

Main (50mL):
- Vanilla: 20mL (40%)
- Caramel: 10mL (20%)
- Tonka: 10mL (20%)
- Fruit: 10mL (20%)

Fruit breakdown (10mL):
Strawberry 40%, Peach 30%, Pear 20%, Apple 10%

RESULT: Sweet gourmand 50mL"""),

    ("Create green accord: galbanum 40%, violet leaf 35%, grass 25% for 20ml", """FORMULA: Green Accord
Total: 20mL intense green

Components:
- Galbanum: 8mL (40%)
- Violet leaf: 7mL (35%)
- Cut grass: 5mL (25%)

Usage: Very powerful
Recommend 6-8% in final

RESULT: Green accord 20mL"""),

    ("Design leather: birch tar 45%, castoreum 30%, labdanum 25% for 30ml", """FORMULA: Leather Accord
Total: 30mL animalic

Components:
- Birch tar: 13.5mL (45%)
- Castoreum: 9mL (30%)
- Labdanum: 7.5mL (25%)

Note: Use synthetic castoreum
Usage: 8-15% in final

RESULT: Leather accord 30mL"""),

    ("Calculate aromatic: lavender 40%, rosemary 30%, sage 20%, thyme 10% for 45ml", """FORMULA: Aromatic Accord
Total: 45mL herbal

Volumes:
- Lavender: 18mL (40%)
- Rosemary: 13.5mL (30%)
- Sage: 9mL (20%)
- Thyme: 4.5mL (10%)

Usage: 15-25% in fougère

RESULT: Aromatic 45mL"""),

    ("Formulate tobacco: tobacco 40%, hay 25%, honey 20%, spice 15% for 55ml", """FORMULA: Tobacco Accord
Total: 55mL complex

Components:
- Tobacco abs: 22mL (40%)
- Hay abs: 13.75mL (25%)
- Honey: 11mL (20%)
- Spice: 8.25mL (15%)

Spice (8.25mL):
Cinnamon 40%, Vanilla 30%, Tonka 20%, Clove 10%

RESULT: Tobacco 55mL"""),

    ("Create aldehyde sparkle: C-12 40%, C-11 30%, C-14 20%, C-18 10% for 10ml", """FORMULA: Aldehyde Complex
Total: 10mL POWERFUL

Volumes:
- C-12 MNA: 4mL (40%)
- C-11: 3mL (30%)
- C-14: 2mL (20%)
- C-18: 1mL (10%)

Safety: Use at 1-3% in final
Very irritating if too concentrated

RESULT: Aldehyde 10mL, use 1-3%"""),

    ("Design powdery: iris 35%, violet 30%, heliotrope 20%, musk 15% for 40ml", """FORMULA: Powdery Accord
Total: 40mL soft

Components:
- Iris: 14mL (35%)
- Methyl ionone: 12mL (30%)
- Heliotropin: 8mL (20%)
- White musk: 6mL (15%)

Budget alt: Reduce iris to 20%, increase violet to 45%

RESULT: Powdery 40mL"""),

    ("Calculate ozonic: calone 25%, marine 35%, melon 25%, citrus 15% for 30ml", """FORMULA: Ozonic Accord
Total: 30mL fresh

Components:
- Calone: 7.5mL (25%)
- Marine: 10.5mL (35%)
- Melon: 7.5mL (25%)
- Citrus: 4.5mL (15%)

Calone adjust: At 15% in frag = 3.75%
Reduce to 1.5% → use 1.8mL

RESULT: Ozonic 30mL"""),

    ("Formulate spicy: pink pepper 30%, cardamom 25%, cinnamon 25%, nutmeg 20%", """FORMULA: Spicy Accord
Total: 35mL warm spice

Components:
- Pink pepper: 10.5mL (30%)
- Cardamom: 8.75mL (25%)
- Cinnamon: 8.75mL (25%)
- Nutmeg: 7mL (20%)

IFRA: Cinnamon limited
At 12% in product: 25%×12% = 3% ✗
Adjust to 8% of accord

RESULT: Spicy 35mL, adjusted"""),

    ("Create fruity: strawberry 30%, peach 30%, pear 25%, apple 15% for 40ml", """FORMULA: Fruity Accord
Total: 40mL sweet

Volumes:
- Strawberry: 12mL (30%)
- Peach: 12mL (30%)
- Pear: 10mL (25%)
- Apple: 6mL (15%)

Usage: 5-15% floral, 10-20% gourmand

RESULT: Fruity 40mL"""),

    ("Design tropical: coconut 40%, pineapple 30%, mango 20%, passion fruit 10%", """FORMULA: Tropical Accord
Total: 35mL exotic

Components:
- Coconut: 14mL (40%)
- Pineapple: 10.5mL (30%)
- Mango: 7mL (20%)
- Passion fruit: 3.5mL (10%)

Character: Sweet, vacation-like

RESULT: Tropical 35mL"""),

    ("Calculate marine: seaweed 30%, salt 25%, driftwood 25%, ambergris 20%", """FORMULA: Marine Accord
Total: 30mL oceanic

Volumes:
- Seaweed: 9mL (30%)
- Sea salt: 7.5mL (25%)
- Driftwood: 7.5mL (25%)
- Ambroxan: 6mL (20%)

Usage: 10-20% in aquatic frags

RESULT: Marine 30mL"""),

    ("Formulate incense: frankincense 40%, myrrh 30%, benzoin 20%, opoponax 10%", """FORMULA: Incense Accord
Total: 40mL sacred

Components:
- Frankincense: 16mL (40%)
- Myrrh: 12mL (30%)
- Benzoin: 8mL (20%)
- Opoponax: 4mL (10%)

Character: Spiritual, deep

RESULT: Incense 40mL"""),

    ("Create mint fresh: peppermint 40%, spearmint 35%, eucalyptus 25% for 25ml", """FORMULA: Mint Accord
Total: 25mL cooling

Volumes:
- Peppermint: 10mL (40%)
- Spearmint: 8.75mL (35%)
- Eucalyptus: 6.25mL (25%)

Usage: 1-5% for freshness
Higher % can be irritating

RESULT: Mint 25mL, use sparingly"""),

    ("Design tea accord: green tea 45%, black tea 30%, bergamot 25% for 30ml", """FORMULA: Tea Accord
Total: 30mL refined

Components:
- Green tea: 13.5mL (45%)
- Black tea: 9mL (30%)
- Bergamot: 7.5mL (25%)

Character: Clean, modern

RESULT: Tea 30mL"""),

    ("Calculate coffee: coffee abs 50%, cocoa 25%, vanilla 15%, caramel 10%", """FORMULA: Coffee Accord
Total: 35mL rich

Volumes:
- Coffee abs: 17.5mL (50%)
- Cocoa abs: 8.75mL (25%)
- Vanilla: 5.25mL (15%)
- Caramel: 3.5mL (10%)

Usage: 3-10% in gourmands

RESULT: Coffee 35mL"""),

    ("Formulate wine accord: grape 40%, oak 30%, tannin 20%, blackcurrant 10%", """FORMULA: Wine Accord
Total: 30mL vinous

Components:
- Grape: 12mL (40%)
- Oak: 9mL (30%)
- Tannin: 6mL (20%)
- Blackcurrant: 3mL (10%)

Character: Sophisticated, rich

RESULT: Wine 30mL"""),

    ("Create honey accord: honey abs 50%, beeswax 30%, propolis 20% for 25ml", """FORMULA: Honey Accord
Total: 25mL sweet

Volumes:
- Honey abs: 12.5mL (50%)
- Beeswax abs: 7.5mL (30%)
- Propolis: 5mL (20%)

Character: Warm, golden

RESULT: Honey 25mL"""),

    # SECTION 3: CONCENTRATION ADJUSTMENTS (15 entries)
    ("Convert EDP 18% to body spray 4%", """FORMULA: Concentration Reduction
Given: EDP 18% → Body spray 4%

Dilution factor: 18/4 = 4.5×

For 100mL body spray:
- EDP: 100/4.5 = 22.22mL
- Add diluent: 77.78mL (80% alc, 20% water)

RESULT: 22.22mL EDP + 77.78mL diluent"""),

    ("Calculate splash cologne from 25% concentrate", """FORMULA: Splash Cologne
Given: 25% concentrate
Target: 3-5% splash

Use: 25% concentrate at 16% = 4% final

For 200mL:
- Concentrate: 32mL
- Alcohol: 148mL
- Water: 20mL

RESULT: 4% splash cologne"""),

    ("Determine aftershave from 20% perfume base", """FORMULA: Aftershave Dilution
Given: 20% base
Target: 2-4% aftershave

Use 15% of base (20%×0.15 = 3%)

100mL aftershave:
- Perfume base: 15mL
- Alcohol: 70mL
- Water: 10mL
- Glycerin: 3mL
- Menthol: 2mL

RESULT: 3% aftershave"""),

    ("Calculate hair mist from 18% EDP", """FORMULA: Hair Mist
Given: 18% EDP
Target: 1-3% hair safe

Use 11% of EDP (18%×0.11 = 2%)

150mL mist:
- EDP: 16.5mL
- Light alcohol: 110mL
- Water: 20mL
- Conditioner: 3.5mL

RESULT: 2% hair mist"""),

    ("Formulate linen spray from fragrance compound", """FORMULA: Linen Spray
Target: 2-5% fragrance

100mL spray:
- Fragrance: 3mL (3%)
- Vodka: 30mL
- Water: 65mL
- Fabric softener: 2mL

Shake before use

RESULT: 3% linen spray"""),

    ("Calculate reed diffuser from 25% accord", """FORMULA: Reed Diffuser
Target: 10-20% in carrier

200mL diffuser:
- Fragrance 25%: 80mL (gives 10% final)
- DPG: 100mL
- Mineral oil: 20mL

Or 15%:
- Fragrance: 120mL
- DPG: 70mL
- Mineral oil: 10mL

RESULT: 10-15% reed diffuser"""),

    ("Determine candle load for paraffin wax", """FORMULA: Paraffin Candle
Wax: 500g paraffin
Load: 6-8%

At 7%:
Fragrance = 500 × 0.07 = 35g

Volume: 35/0.9 = 38.9mL

Pour temp: 80-85°C

RESULT: 35g (39mL) fragrance"""),

    ("Calculate soap safe percentage", """FORMULA: Cold Process Soap
Base: 1000g oils
Safe range: 2-4%

At 3%:
Fragrance = 1000 × 0.03 = 30g

Check IFRA Category 9 limits
Use skin-safe fragrances only

RESULT: 30g for 1kg soap"""),

    ("Formulate lotion fragrance load", """FORMULA: Body Lotion
Base: 500g lotion
Load: 1-3%

At 2%:
Fragrance = 500 × 0.02 = 10g

Emulsify first with polysorbate 20

Mix ratio:
Fragrance 10g + Polys 2g into 500g lotion

RESULT: 2% lotion (10g)"""),

    ("Calculate shampoo fragrance percentage", """FORMULA: Shampoo/Body Wash
Base: 1L shampoo
Load: 0.5-2%

At 1%:
Fragrance = 1000mL × 0.01 = 10mL

Mix with surfactant first
IFRA Cat 9 limits apply

RESULT: 1% (10mL per liter)"""),

    ("Determine bath oil concentration", """FORMULA: Bath Oil
Base: 250mL carrier oil
Fragrance: 5-10%

At 8%:
Fragrance = 250 × 0.08 = 20mL

Carrier options:
- Jojoba 50%
- Sweet almond 50%

RESULT: 20mL in 250mL"""),

    ("Calculate room spray strength", """FORMULA: Room Spray
Target: 5-10% fragrance

500mL spray:
- Fragrance: 40mL (8%)
- Alcohol: 350mL
- Water: 105mL
- Emulsifier: 5mL

Shake before use

RESULT: 8% room spray"""),

    ("Formulate car diffuser oil", """FORMULA: Car Diffuser
Target: 20-30% highly concentrated

30mL diffuser:
- Fragrance compound: 7.5mL (25%)
- DPG: 20mL
- Fixative: 2.5mL

Lasts: 30-45 days

RESULT: 25% car diffuser"""),

    ("Calculate drawer sachet intensity", """FORMULA: Drawer Sachet
Fabric pouch method

Per sachet:
- Fragrance oil: 2mL
- Orris root powder: 10g
- Cellulose: 5g

Let cure 1 week
Lasts: 2-3 months

RESULT: 2mL per sachet"""),

    ("Determine potpourri refresher spray", """FORMULA: Potpourri Refresher
Target: 15-20% fragrance

100mL spray:
- Fragrance: 18mL (18%)
- Alcohol: 70mL
- DPG: 10mL
- Water: 2mL
