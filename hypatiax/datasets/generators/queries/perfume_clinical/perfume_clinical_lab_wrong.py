"""
AI Training Datasets Generator - COMPLETE 300 ENTRIES EACH
===========================================================
Generates TWO independent CSV files:
1. perfume_formulation_dataset.csv (300 entries)
2. clinical_laboratory_dataset.csv (300 entries)

Total: 600 detailed formulas
Format: query_description, formula
"""

import csv
import os

# I'll provide the continuation of both datasets to reach 300 entries each.
# First, I'll complete the PERFUME dataset, then the CLINICAL dataset.

# PERFUME DATASET CONTINUATION (entries 201-300)
perfume_continuation = [
    # Production & Quality Control (30 entries)
    ["Calculate days inventory outstanding", "DIO = (Average Inventory / COGS) × 365"],
    [
        "Determine gross profit margin",
        "Gross Margin % = (Revenue - COGS) / Revenue × 100",
    ],
    [
        "Calculate contribution margin ratio",
        "CM Ratio = (Sales - Variable Costs) / Sales",
    ],
    [
        "Find return on investment perfume line",
        "ROI % = (Net Profit / Investment Cost) × 100",
    ],
    [
        "Calculate production cycle time",
        "Cycle Time = Total Production Time / Units Produced",
    ],
    [
        "Determine first-pass yield rate",
        "FPY % = (Good Units First Time / Total Units) × 100",
    ],
    [
        "Calculate overall equipment effectiveness",
        "OEE = Availability × Performance × Quality",
    ],
    [
        "Find defect rate per million",
        "DPMO = (Defects / Units × Opportunities) × 1,000,000",
    ],
    ["Calculate process capability index", "Cpk = min[(USL - μ) / 3σ, (μ - LSL) / 3σ]"],
    [
        "Determine statistical process control limits",
        "UCL = Mean + 3σ, LCL = Mean - 3σ",
    ],
    ["Calculate standard deviation batch consistency", "σ = √[Σ(x - μ)² / (n - 1)]"],
    [
        "Find coefficient of variation quality",
        "CV % = (Standard Deviation / Mean) × 100",
    ],
    ["Calculate color consistency Delta E", "ΔE = √[(ΔL*)² + (Δa*)² + (Δb*)²]"],
    [
        "Determine shelf life acceleration factor",
        "AF = Q10^[(T_test - T_storage) / 10]",
    ],
    ["Calculate Arrhenius degradation rate", "k = A × e^(-Ea / RT)"],
    [
        "Find remaining shelf life prediction",
        "RSL = Initial SL × [Current Quality / Initial Quality]",
    ],
    ["Calculate fill weight tolerance", "Tolerance = Target Weight ± (Target × %)"],
    ["Determine container closure integrity", "CCI = Leak Rate < Maximum Allowable"],
    [
        "Calculate microbial contamination limit",
        "Total Count < 100 CFU/g for cosmetics",
    ],
    ["Find preservative challenge test result", "PCT = Log Reduction ≥ 3 for bacteria"],
    [
        "Calculate stability testing time points",
        "Time Points = 0, 1, 2, 3, 6, 9, 12, 18, 24 months",
    ],
    [
        "Determine photostability light exposure",
        "Light Exposure = 1.2 million lux-hours",
    ],
    ["Calculate freeze-thaw cycle stability", "Cycles = 5 cycles (-10°C to +40°C)"],
    [
        "Find viscosity temperature correction",
        "Viscosity_20C = Measured × Temperature Factor",
    ],
    [
        "Calculate density temperature adjustment",
        "Density_20C = Measured / [1 + β(T - 20)]",
    ],
    [
        "Determine sample size for QC testing",
        "n = (Z² × σ² × N) / (e² × (N-1) + Z² × σ²)",
    ],
    ["Calculate confidence interval for mean", "CI = Mean ± (Z × σ / √n)"],
    ["Find acceptable quality level sampling", "AQL = Maximum % defective acceptable"],
    [
        "Calculate measurement system analysis",
        "MSA: Gage R&R = √(Repeatability² + Reproducibility²)",
    ],
    ["Determine total measurement uncertainty", "U = k × √(u1² + u2² + ... + un²)"],
    # Accord Formulations (20 entries)
    [
        "Calculate floral bouquet balance",
        "Floral = Rose 30% + Jasmine 25% + Lily 20% + Violet 15% + Iris 10%",
    ],
    [
        "Determine oriental spicy accord",
        "Oriental = Vanilla 25% + Cinnamon 20% + Amber 20% + Patchouli 20% + Clove 15%",
    ],
    [
        "Calculate fresh aquatic composition",
        "Aquatic = Calone 25% + Marine 20% + Melon 20% + Lotus 20% + Mint 15%",
    ],
    [
        "Find woody aromatic structure",
        "Woody Aromatic = Cedar 30% + Vetiver 25% + Pine 20% + Sage 15% + Lavender 10%",
    ],
    [
        "Calculate fruity floral harmony",
        "Fruity Floral = Peach 25% + Rose 25% + Pear 20% + Jasmine 20% + Raspberry 10%",
    ],
    [
        "Determine leather animalic depth",
        "Leather = Birch Tar 30% + Labdanum 25% + Castoreum 20% + Tobacco 15% + Styrax 10%",
    ],
    [
        "Calculate green chypre classic",
        "Green Chypre = Galbanum 25% + Oakmoss 25% + Bergamot 20% + Rose 15% + Patchouli 15%",
    ],
    [
        "Find gourmand sweet harmony",
        "Gourmand = Vanilla 30% + Caramel 25% + Tonka 20% + Praline 15% + Honey 10%",
    ],
    [
        "Calculate citrus aromatic freshness",
        "Citrus Aromatic = Bergamot 30% + Lemon 25% + Lavender 20% + Rosemary 15% + Neroli 10%",
    ],
    [
        "Determine amber oriental warmth",
        "Amber Oriental = Labdanum 30% + Benzoin 25% + Vanilla 20% + Frankincense 15% + Myrrh 10%",
    ],
    [
        "Calculate tropical exotic blend",
        "Tropical = Coconut 25% + Mango 20% + Pineapple 20% + Tiare 20% + Ylang 15%",
    ],
    [
        "Find tobacco vanilla richness",
        "Tobacco Vanilla = Tobacco 35% + Vanilla 30% + Tonka 20% + Hay 10% + Caramel 5%",
    ],
    [
        "Calculate oud oriental luxury",
        "Oud Oriental = Oud 30% + Rose 25% + Saffron 20% + Amber 15% + Sandalwood 10%",
    ],
    [
        "Determine marine ozonic freshness",
        "Marine Ozone = Calone 30% + Sea Salt 25% + Ambroxan 20% + Seaweed 15% + Citrus 10%",
    ],
    [
        "Calculate aldehydic floral elegance",
        "Aldehydic Floral = Aldehydes 25% + Rose 25% + Jasmine 20% + Ylang 15% + Iris 15%",
    ],
    [
        "Find spicy oriental intensity",
        "Spicy Oriental = Cinnamon 25% + Cardamom 20% + Clove 20% + Nutmeg 20% + Pepper 15%",
    ],
    [
        "Calculate powdery soft feminine",
        "Powdery = Iris 30% + Violet 25% + Heliotrope 20% + Vanilla 15% + Musk 10%",
    ],
    [
        "Determine tea aromatic delicate",
        "Tea Accord = Green Tea 30% + Bergamot 25% + Jasmine 20% + Lemon 15% + Mate 10%",
    ],
    [
        "Calculate moss woody earthy",
        "Moss Woody = Oakmoss 30% + Vetiver 25% + Patchouli 20% + Cedar 15% + Cypress 10%",
    ],
    [
        "Find incense mystical sacred",
        "Incense = Frankincense 35% + Myrrh 25% + Olibanum 20% + Benzoin 10% + Opoponax 10%",
    ],
    # Advanced Blending (20 entries)
    [
        "Calculate synergy coefficient blend",
        "Synergy = (Blend Strength / Σ Individual Strengths) × 100",
    ],
    [
        "Determine harmonic mean molecular weight",
        "HM = n / (1/MW1 + 1/MW2 + ... + 1/MWn)",
    ],
    [
        "Calculate olfactive power index",
        "OPI = log(Concentration) + Diffusivity Factor",
    ],
    ["Find blending threshold minimum", "Threshold = Minimum % for detectability"],
    ["Calculate odor value contribution", "OV = Concentration / Odor Threshold"],
    [
        "Determine masking efficiency ratio",
        "Masking = (Masked Odor Strength / Original) × 100",
    ],
    [
        "Calculate note pyramid distribution",
        "Pyramid: Top 20-30%, Heart 30-50%, Base 30-50%",
    ],
    ["Find volatility index weighted", "VI = Σ(Component % × Vapor Pressure)"],
    ["Calculate tenacity factor blend", "Tenacity = Σ(Base Note % × MW) / Total MW"],
    [
        "Determine diffusion radius estimate",
        "Diffusion = k × √(Temperature × Volatility)",
    ],
    ["Calculate blooming time prediction", "Bloom Time = α × log(MW) + β × Polarity"],
    ["Find evolution curve parameters", "Evolution: Top 0-2h, Heart 2-8h, Base 8h+"],
    ["Calculate intensity decay rate", "Decay = Initial Intensity × e^(-kt)"],
    ["Determine half-life fragrance note", "t½ = ln(2) / k (decay constant)"],
    [
        "Calculate persistence score formula",
        "Persistence = (Base % × 5) + (Heart % × 3) + (Top % × 1)",
    ],
    ["Find projection power metric", "Projection = Sillage × Longevity × Intensity"],
    [
        "Calculate complexity index blend",
        "Complexity = Number of Notes × Average Interaction Strength",
    ],
    ["Determine balance ratio accord", "Balance = Σ|Deviation from Ideal %|, minimize"],
    [
        "Calculate aesthetic harmony score",
        "Harmony = 1 - (σ of Note Intensities / Mean Intensity)",
    ],
    [
        "Find olfactive signature uniqueness",
        "Uniqueness = Euclidean Distance from Similar Formulas",
    ],
    # Regulatory & Compliance (20 entries)
    [
        "Calculate IFRA Category maximum usage",
        "Max % = IFRA Standard Level for Product Category",
    ],
    [
        "Determine restricted substance compliance",
        "Restricted: Sum of all restricted materials ≤ limit",
    ],
    [
        "Calculate allergen declaration threshold",
        "Declare if: Individual Allergen > 0.001% (10 ppm)",
    ],
    [
        "Find total allergen content",
        "Total Allergens = Σ(Each Natural Material × % Allergen)",
    ],
    ["Calculate coumarin compliance limit", "Coumarin: Max 0.1% leave-on, 1% wash-off"],
    [
        "Determine eugenol safety level",
        "Eugenol: Max varies by category, typically 0.5-2%",
    ],
    [
        "Calculate citral sensitization limit",
        "Citral: Max 0.6-2% depending on category",
    ],
    ["Find limonene oxidation products", "Limonene Oxides must be ≤ 1% for stability"],
    [
        "Calculate methyl eugenol restriction",
        "Methyl Eugenol: Max 0.0002% (extremely limited)",
    ],
    [
        "Determine oakmoss IFRA compliance",
        "Oakmoss: Max 0.1% (due to atranol/chloroatranol)",
    ],
    [
        "Calculate hydroxycitronellal limit",
        "Hydroxycitronellal: Max 1% in EU cosmetics",
    ],
    [
        "Find geraniol oxidation stability",
        "Geraniol: Minimize oxidation with antioxidants",
    ],
    [
        "Calculate linalool peroxide control",
        "Linalool: Control hydroperoxide formation",
    ],
    [
        "Determine farnesol sensitization check",
        "Farnesol: Monitor cumulative allergen exposure",
    ],
    ["Calculate benzyl alcohol preservative", "Benzyl Alcohol: 0.5-1% as preservative"],
    [
        "Find benzyl benzoate solvent limit",
        "Benzyl Benzoate: Generally safe, no specific limit",
    ],
    [
        "Calculate benzyl salicylate usage",
        "Benzyl Salicylate: No restriction, common fixative",
    ],
    [
        "Determine cinnamyl alcohol IFRA",
        "Cinnamyl Alcohol: Restricted in some categories",
    ],
    [
        "Calculate citronellol safety margin",
        "Citronellol: Safe but declare as allergen",
    ],
    [
        "Find alpha-isomethyl ionone limit",
        "Alpha-Isomethyl Ionone: Restricted, max varies",
    ],
    # Sustainability & Natural Calculations (20 entries)
    [
        "Calculate natural origin index",
        "NOI % = (Natural Materials Weight / Total Weight) × 100",
    ],
    [
        "Determine biodegradability percentage",
        "Biodegradable % = (Biodegradable Components / Total) × 100",
    ],
    [
        "Calculate carbon footprint per bottle",
        "CO2e = Σ(Ingredient kg × CO2 factor + Transport + Package)",
    ],
    [
        "Find renewable content ratio",
        "Renewable % = (Renewable Source Materials / Total) × 100",
    ],
    [
        "Calculate water footprint production",
        "Water Footprint = Direct Use + Indirect (Ingredients)",
    ],
    [
        "Determine upcycled material percentage",
        "Upcycled % = (Upcycled Ingredients / Total) × 100",
    ],
    [
        "Calculate fair trade certified content",
        "Fair Trade % = (Certified Materials / Total) × 100",
    ],
    [
        "Find organic certification eligibility",
        "Organic: ≥ 95% organic ingredients for certification",
    ],
    ["Calculate palm oil free verification", "Palm-Free: 0% palm-derived ingredients"],
    ["Determine vegan formula compliance", "Vegan: 0% animal-derived ingredients"],
    [
        "Calculate cruelty-free certification",
        "Cruelty-Free: No animal testing at any stage",
    ],
    [
        "Find sustainably sourced percentage",
        "Sustainable % = (Certified Sustainable / Total) × 100",
    ],
    [
        "Calculate packaging recyclability rate",
        "Recyclable % = (Recyclable Materials / Total Package) × 100",
    ],
    [
        "Determine post-consumer recycled content",
        "PCR % = (PCR Material / Total Package Weight) × 100",
    ],
    [
        "Calculate ocean-bound plastic usage",
        "OBP % = (Ocean Plastic / Total Plastic) × 100",
    ],
    [
        "Find refillable design efficiency",
        "Refill Efficiency = (Refill Weight / Original Package) × 100",
    ],
    [
        "Calculate microplastic-free compliance",
        "Microplastic: 0% particles < 5mm synthetic polymer",
    ],
    [
        "Determine toxic substance elimination",
        "Toxic-Free: 0% substances on restricted lists",
    ],
    [
        "Calculate clean beauty score",
        "Clean Score = (Compliant Ingredients / Total) × 100",
    ],
    [
        "Find transparency index formula",
        "Transparency: All ingredients disclosed with origin",
    ],
    # Marketing & Consumer Metrics (20 entries)
    [
        "Calculate fragrance family classification",
        "Family: Floral, Oriental, Woody, Fresh, or hybrid",
    ],
    [
        "Determine target demographic appeal",
        "Demo Score = Weighted preference by age/gender",
    ],
    [
        "Calculate price positioning index",
        "PPI = (Product Price / Category Average) × 100",
    ],
    [
        "Find perceived value ratio",
        "Perceived Value = Consumer Valuation / Actual Price",
    ],
    [
        "Calculate brand equity contribution",
        "Brand Equity = (Premium Price / Base Price) × 100",
    ],
    [
        "Determine market penetration rate",
        "Penetration % = (Customers / Target Market) × 100",
    ],
    [
        "Calculate customer lifetime value",
        "CLV = (Average Purchase × Frequency × Lifespan) - Acquisition Cost",
    ],
    [
        "Find repeat purchase rate",
        "Repeat Rate % = (Repeat Customers / Total Customers) × 100",
    ],
    ["Calculate net promoter score weight", "NPS = % Promoters - % Detractors"],
    [
        "Determine customer satisfaction index",
        "CSI = Σ(Rating × Weight) / Total Weight",
    ],
    [
        "Calculate social media engagement rate",
        "Engagement % = (Interactions / Followers) × 100",
    ],
    [
        "Find influencer impact coefficient",
        "IIC = (Sales Lift / Normal Sales) during campaign",
    ],
    [
        "Calculate conversion rate e-commerce",
        "Conversion % = (Purchases / Visitors) × 100",
    ],
    [
        "Determine cart abandonment recovery",
        "Recovery % = (Recovered Carts / Abandoned) × 100",
    ],
    ["Calculate average order value", "AOV = Total Revenue / Number of Orders"],
    ["Find customer acquisition cost", "CAC = Total Marketing Spend / New Customers"],
    ["Calculate return on ad spend", "ROAS = Revenue from Ads / Ad Spend"],
    [
        "Determine seasonal demand variation",
        "Seasonality Index = Period Sales / Average Period Sales",
    ],
    [
        "Calculate inventory sell-through rate",
        "Sell-Through % = (Units Sold / Units Received) × 100",
    ],
    [
        "Find optimal stock keeping units",
        "Optimal SKUs = Balance diversity vs. inventory cost",
    ],
    # Sensory Evaluation (20 entries)
    [
        "Calculate olfactory intensity scale",
        "Intensity: 0=None, 1=Slight, 2=Moderate, 3=Strong, 4=Extreme",
    ],
    [
        "Determine hedonic rating score",
        "Hedonic: 1=Dislike extremely to 9=Like extremely",
    ],
    [
        "Calculate just noticeable difference",
        "JND = Minimum ΔConcentration for detection",
    ],
    [
        "Find threshold detection value",
        "Detection Threshold = Minimum perceivable concentration",
    ],
    [
        "Calculate recognition threshold level",
        "Recognition Threshold = Minimum identifiable concentration",
    ],
    ["Determine difference-from-control score", "DFC = |Sample Score - Control Score|"],
    [
        "Calculate triangle test probability",
        "Triangle: Correct selections / Total assessments",
    ],
    [
        "Find duo-trio test significance",
        "Duo-Trio: Compare to statistical tables for significance",
    ],
    [
        "Calculate paired comparison preference",
        "Preference % = (Selection Count / Total) × 100",
    ],
    [
        "Determine attribute intensity rating",
        "Attribute Rating: Scale specific to descriptor",
    ],
    [
        "Calculate overall liking composite",
        "Overall Liking = Weighted average of all attributes",
    ],
    [
        "Find purchase intent percentage",
        "Purchase Intent = (Definitely/Probably Buy / Total) × 100",
    ],
    ["Calculate quality perception index", "QPI = Σ(Quality Attributes × Importance)"],
    [
        "Determine uniqueness perception",
        "Uniqueness = Differentiation from competitors (scale)",
    ],
    ["Calculate memorability score", "Memorability = Recall % after time period"],
    [
        "Find emotional response mapping",
        "Emotion Map: Plot arousal vs. valence coordinates",
    ],
    [
        "Calculate appropriate usage occasion",
        "Occasion Fit = % respondents selecting each occasion",
    ],
    ["Determine gender perception skew", "Gender Skew = (Female % - Male %) / 100"],
    ["Calculate age appropriateness rating", "Age Fit = Modal age group selection %"],
    [
        "Find price sensitivity threshold",
        "PST = Price where demand drops significantly",
    ],
    # Final Technical Entries (20 entries)
    [
        "Calculate molecular dynamics simulation",
        "MD: Track molecular interactions over time",
    ],
    ["Determine QSAR property prediction", "QSAR: Property = f(molecular descriptors)"],
    [
        "Calculate Hansen solubility parameters",
        "HSP: δD² + δP² + δH² = Ra² (solubility sphere)",
    ],
    ["Find octanol-water partition prediction", "Log Kow = Σ(fragment coefficients)"],
    [
        "Calculate bioavailability estimate",
        "F% = Fraction absorbed × (1 - First-pass metabolism)",
    ],
    ["Determine dermal absorption rate", "Flux = (Kp × C × A) / MW"],
    ["Calculate skin permeability coefficient", "Kp = D × K / h (diffusion model)"],
    ["Find stratum corneum partition", "Ksc/w = exp(a × log P + b)"],
    ["Calculate reservoir effect duration", "Reservoir Time = (Skin Content / Flux)"],
    ["Determine photostability UV absorption", "Absorbance = ε × c × l (Beer-Lambert)"],
    [
        "Calculate oxidative stability index",
        "OSI = Induction time at accelerated conditions",
    ],
    [
        "Find radical scavenging activity",
        "RSA % = [(A_control - A_sample) / A_control] × 100",
    ],
    ["Calculate antioxidant capacity DPPH", "DPPH = IC50 (inhibitory concentration)"],
    [
        "Determine lipid peroxidation inhibition",
        "LPI % = [(Control MDA - Sample MDA) / Control] × 100",
    ],
    [
        "Calculate metal chelating ability",
        "Chelating % = [(A_control - A_sample) / A_control] × 100",
    ],
    [
        "Find pro-oxidant transition point",
        "Transition = Concentration where antioxidant → pro-oxidant",
    ],
    [
        "Calculate critical micelle concentration",
        "CMC = Inflection point in surface tension curve",
    ],
    [
        "Determine emulsion stability time",
        "Stability = Time until phase separation occurs",
    ],
    ["Calculate interfacial tension reduction", "γ_reduction = γ_initial - γ_final"],
    [
        "Find cloud point temperature",
        "Cloud Point = Temperature of phase separation onset",
    ],
]

# CLINICAL LABORATORY CONTINUATION (entries 151-300)
clinical_continuation = (
    [
        # Advanced Hematology (30 entries)
        [
            "Calculate reticulocyte hemoglobin content",
            "Ret-He pg = Mean Hgb in reticulocytes",
        ],
        [
            "Determine immature granulocyte percentage",
            "IG % = (Promyelocytes + Myelocytes + Metamyelocytes) / WBC × 100",
        ],
        [
            "Calculate neutrophil-lymphocyte ratio",
            "NLR = Absolute Neutrophil Count / Absolute Lymphocyte Count",
        ],
        [
            "Find platelet-lymphocyte ratio",
            "PLR = Platelet Count / Absolute Lymphocyte Count",
        ],
        [
            "Calculate red cell distribution width SD",
            "RDW-SD fL = Width at 20% frequency on histogram",
        ],
        [
            "Determine mean sphered cell volume",
            "MSCV fL = Volume after sphering transformation",
        ],
        [
            "Calculate hemoglobin distribution width",
            "HDW g/dL = SD of hemoglobin concentration",
        ],
        [
            "Find cellular hemoglobin concentration",
            "CHCM g/dL = Mean Hb concentration in RBCs",
        ],
        ["Calculate low hemoglobin density", "LHD % = % RBCs with low Hgb density"],
        ["Determine microcytic anemia index", "Microcytic Index = MCV × MCH / 100"],
        [
            "Calculate Mentzer index discrimination",
            "Mentzer = MCV / RBC count (< 13 suggests thalassemia)",
        ],
        ["Find Shine-Lal index thalassemia", "Shine-Lal = (MCV × MCV × MCH) / 100"],
        [
            "Calculate England-Fraser index",
            "England-Fraser = MCV - RBC - (5 × Hb) - 3.4",
        ],
        ["Determine Srivastava index", "Srivastava = MCH / RBC"],
        ["Calculate Green-King index", "Green-King = (MCV × MCV × RDW) / (Hb × 100)"],
        [
            "Find RBC fragmentation index",
            "Fragmentation % = Schistocytes / Total RBC × 100",
        ],
        [
            "Calculate corrected reticulocyte count",
            "CRC % = Reticulocyte % × (Patient Hct / Normal Hct)",
        ],
        ["Determine absolute lymphocyte count", "ALC = WBC × Lymphocyte % / 100"],
        ["Calculate absolute monocyte count", "AMC = WBC × Monocyte % / 100"],
        ["Find absolute eosinophil count", "AEC = WBC × Eosinophil % / 100"],
        ["Calculate absolute basophil count", "ABC = WBC × Basophil % / 100"],
        [
            "Determine left shift index",
            "Left Shift = (Bands + Metamyelocytes) / Segmented Neutrophils",
        ],
        [
            "Calculate toxic granulation score",
            "Toxic Gran: 0=None, 1+=Mild, 2+=Moderate, 3+=Severe",
        ],
        ["Find Döhle body presence", "Döhle Bodies: Present/Absent in neutrophils"],
        [
            "Calculate platelet clumping correction",
            "Corrected Plt = Counted Plt × Clump Adjustment Factor",
        ],
        [
            "Determine giant platelet percentage",
            "Giant Plt % = Platelets > 5 μm diameter / Total",
        ],
        ["Calculate mean platelet component", "MPC g/dL = MPM / MPV"],
        ["Find platelet large cell ratio", "P-LCR % = Platelets > 12 fL / Total × 100"],
        [
            "Calculate plateletcrit to MPV ratio",
            "PCT/MPV = Indicator of platelet production",
        ],
        [
            "Determine erythrocyte sedimentation rate",
            "ESR mm/hr via Westergren or Wintrobe method",
        ],
        # Coagulation & Hemostasis (30 entries)
        [
            "Calculate corrected bleeding time",
            "Corrected BT = Observed BT × (Platelet Norm / Patient Plt)",
        ],
        [
            "Determine Russell viper venom time",
            "RVVT seconds = Clotting time with RVVT reagent",
        ],
        ["Calculate dilute RVVT ratio", "dRVVT Ratio = Patient dRVVT / Normal dRVVT"],
        ["Find silica clotting time", "SCT = Clotting time with silica activator"],
        ["Calculate kaolin clotting time", "KCT = Clotting time with kaolin"],
        [
            "Determine hexagonal phospholipid assay",
            "HPA = Confirmatory test for lupus anticoagulant",
        ],
        [
            "Calculate protein C resistance ratio",
            "APC-R = aPTT with APC / aPTT without APC",
        ],
        [
            "Find activated protein C sensitivity",
            "APC Sensitivity = [(aPTT+APC / aPTT-APC) - 1] × 100",
        ],
        [
            "Calculate factor VIII inhibitor titer",
            "Bethesda Units = Residual factor activity assay",
        ],
        [
            "Determine factor IX complex activity",
            "FIX % = Clotting assay with FIX-deficient plasma",
        ],
        [
            "Calculate von Willebrand ristocetin cofactor",
            "vWF:RCo % = Platelet agglutination assay",
        ],
        ["Find von Willebrand antigen level", "vWF:Ag % = Immunoassay for vWF protein"],
        ["Calculate vWF collagen binding", "vWF:CB % = Binding to collagen substrate"],
        ["Determine vWF multimer ratio", "Multimer Ratio = Large / Small multimers"],
        ["Calculate ADAMTS13 inhibitor titer", "Bethesda Units for ADAMTS13"],
        [
            "Find thrombin generation peak",
            "Peak Thrombin nM = Maximum thrombin concentration",
        ],
        [
            "Calculate endogenous thrombin potential",
            "ETP nM·min = Area under thrombin curve",
        ],
        [
            "Determine lag time thrombin generation",
            "Lag Time min = Time to 10% peak thrombin",
        ],
        ["Calculate time to peak thrombin", "TTP min = Time to maximum thrombin"],
        ["Find fibrinogen Clauss method", "Fibrinogen mg/dL = Clotting time method"],
        ["Calculate fibrinogen derived method", "Derived Fib = From PT clot formation"],
        ["Determine fibrin monomer level", "FM = Soluble fibrin monomer complex"],
        [
            "Calculate plasminogen activity",
            "Plasminogen % = Chromogenic substrate assay",
        ],
        ["Find plasmin-antiplasmin complex", "PAP ng/mL = Fibrinolysis marker"],
        [
            "Calculate tissue plasminogen activator",
            "tPA ng/mL = Fibrinolytic enzyme level",
        ],
        [
            "Determine PAI-1 activity level",
            "PAI-1 U/mL = Plasminogen activator inhibitor",
        ],
        [
            "Calculate thrombin-antithrombin complex",
            "TAT ng/mL = Coagulation activation marker",
        ],
        ["Find prothrombin fragment 1+2", "F1+2 pmol/L = Thrombin generation marker"],
        ["Calculate platelet factor 4 level", "PF4 IU/mL = Platelet activation marker"],
        ["Determine beta-thromboglobulin", "β-TG ng/mL = Platelet release marker"],
        # Immunohematology & Transfusion (25 entries)
        [
            "Calculate ABO discrepancy resolution",
            "Front Type vs Back Type: Investigate discrepancies",
        ],
        [
            "Determine antibody screen significance",
            "Clinically Significant if reactive at 37°C + AHG",
        ],
        [
            "Calculate antibody identification panel",
            "Panel: Identify specificity from reaction pattern",
        ],
        ["Find antibody titer strength", "Titer = Highest dilution with 1+ reaction"],
        [
            "Calculate crossmatch compatibility",
            "XM: Immediate spin + 37°C + AHG phases",
        ],
        [
            "Determine direct antiglobulin test",
            "DAT: Positive if RBCs coated with IgG or C3d",
        ],
        ["Calculate indirect antiglobulin test", "IAT: Detects antibodies in serum"],
        [
            "Find Rh phenotype probability",
            "Rh Phenotype = Based on DCE antigen expression",
        ],
        [
            "Calculate Kell antigen frequency",
            "K antigen: 9% Caucasian, 2% African American",
        ],
        ["Determine Duffy antigen status", "Fy(a-b-) prevalent in African populations"],
        ["Calculate Kidd antibody detection", "Jk antibodies: Often cause delayed HTR"],
        [
            "Find Lewis antibody significance",
            "Le antibodies: Usually not clinically significant",
        ],
        ["Calculate MNS system antigen", "MNS: Complex system with multiple antigens"],
        [
            "Determine Lutheran antigen expression",
            "Lu antigens: Rare clinical significance",
        ],
        ["Calculate P1PK blood group", "P system: Anti-P rare but can cause HTR"],
        ["Find red cell unit expiration", "CPDA-1: 35 days, AS-1/AS-3/AS-5: 42 days"],
        [
            "Calculate platelet dose requirement",
            "Plt Dose = 1 unit per 10 kg body weight",
        ],
        [
            "Determine fresh frozen plasma dose",
            "FFP Dose = 10-15 mL/kg for coagulation",
        ],
        [
            "Calculate cryoprecipitate fibrinogen",
            "Cryo: 150-250 mg fibrinogen per unit",
        ],
        ["Find massive transfusion ratio", "MT Protocol: RBC:FFP:Platelets = 1:1:1"],
        [
            "Calculate transfusion reaction rate",
            "Reaction Rate = Events / Total Units × 100",
        ],
        [
            "Determine febrile reaction threshold",
            "FNHTR: Temp rise ≥ 1°C during transfusion",
        ],
        [
            "Calculate TRALI diagnostic criteria",
            "TRALI: Hypoxemia within 6h + bilateral infiltrates",
        ],
        [
            "Find TACO fluid overload signs",
            "TACO: Dyspnea + hypertension + edema + BNP elevation",
        ],
        [
            "Calculate post-transfusion increment",
            "Corrected Count Increment = (Post-Plt - Pre-Plt) × BSA / Units",
        ],
        # Molecular Diagnostics continuation (entries 176-200)
        [
            "Find amplicon size range",
            "Amplicon Length = Reverse Primer Position - Forward Primer Position",
        ],
        [
            "Calculate DNA concentration ratio",
            "260/280 Ratio = 1.8 (pure DNA), <1.8 protein contamination",
        ],
        ["Determine RNA purity ratio", "260/280 Ratio = 2.0 (pure RNA)"],
        ["Calculate DNA yield extraction", "Yield μg = Concentration × Volume"],
        [
            "Find viral load quantification",
            "Viral Load = Copies/mL from standard curve",
        ],
        [
            "Calculate sequencing coverage depth",
            "Coverage = Total Bases Sequenced / Genome Size",
        ],
        [
            "Determine variant allele frequency",
            "VAF % = Variant Reads / Total Reads × 100",
        ],
        [
            "Calculate next-gen sequencing quality",
            "Q Score = -10 × log₁₀(Error Probability)",
        ],
        ["Find microarray normalization", "Normalized = log₂(Sample / Reference)"],
        [
            "Calculate gene expression fold change",
            "Fold Change = Treated Expression / Control Expression",
        ],
        [
            "Determine mutation detection limit",
            "LOD = Minimum % mutant alleles detectable",
        ],
        [
            "Calculate heterozygosity ratio",
            "Heterozygosity = Variant / (Variant + Reference)",
        ],
        ["Find zygosity determination", "Homozygous if VAF ~100%, Heterozygous ~50%"],
        [
            "Calculate chromosomal microarray ratio",
            "Log₂ Ratio = Test / Reference for CNV detection",
        ],
        ["Determine FISH probe signal", "FISH: Count signals per nucleus"],
        # Flow Cytometry (entries 201-225)
        ["Calculate CD4 absolute count", "CD4 = WBC × % Lymph × % CD4⁺ / 100"],
        ["Determine CD4 to CD8 ratio", "CD4/CD8 = CD4⁺ Count / CD8⁺ Count"],
        [
            "Calculate CD34⁺ stem cell dose",
            "CD34⁺ cells/kg = Total CD34⁺ / Recipient Weight",
        ],
        ["Find minimal residual disease", "MRD % = Leukemic Cells / Total Cells × 100"],
        ["Calculate reticulocyte maturity index", "RMI = % High fluorescence retics"],
        [
            "Determine platelet reticulated fraction",
            "Immature Plt % = Thiazole orange positive",
        ],
        [
            "Calculate lymphocyte subset percentage",
            "Subset % = (Subset Count / Lymphocyte Count) × 100",
        ],
        ["Find plasma cell percentage", "Plasma Cells % of total nucleated cells"],
        ["Calculate clonality assessment", "Kappa/Lambda Ratio: Normal 0.5-3.0"],
        [
            "Determine B-cell monoclonality",
            "Monoclonal if restricted light chain expression",
        ],
        ["Calculate T-cell activation markers", "% CD3⁺CD69⁺ or HLA-DR⁺ cells"],
        ["Find NK cell percentage", "NK Cells % = CD3⁻CD16⁺CD56⁺"],
        ["Calculate apoptosis percentage", "Apoptosis % = Annexin V⁺ cells"],
        ["Determine cell cycle phase", "G0/G1, S, G2/M phases by DNA content"],
        [
            "Calculate lymphocyte proliferation",
            "Proliferation = Stimulated CPM / Unstimulated CPM",
        ],
        [
            "Find oxidative burst capacity",
            "DHR Oxidation = Mean fluorescence intensity",
        ],
        [
            "Calculate phagocytosis index",
            "PI = (% Phagocytic Cells × Mean Bacteria) / 100",
        ],
        ["Determine HLA-B27 positivity", "B27⁺ if specific fluorescence detected"],
        ["Calculate PNH clone size", "PNH % = CD55⁻CD59⁻ cells percentage"],
        [
            "Find fetal-maternal hemorrhage",
            "FMH = % Fetal Cells × Maternal Blood Volume / 100",
        ],
        [
            "Calculate basophil activation test",
            "BAT % = CD63⁺ basophils after allergen",
        ],
        ["Determine platelet-bound antibody", "IgG-coated platelets by flow cytometry"],
        ["Calculate eosinophil activation", "% CD69⁺ eosinophils"],
        ["Find lymphocyte adhesion molecules", "CD11/CD18 expression level"],
        ["Calculate granulocyte burst oxidative", "NBT Positive % of granulocytes"],
        # Serology & Immunology (entries 226-250)
        ["Calculate ELISA optical density", "OD = Absorbance at specific wavelength"],
        ["Determine ELISA cutoff value", "Cutoff = Mean Negative Control + (K × SD)"],
        ["Calculate sample to cutoff ratio", "S/CO = Sample OD / Cutoff OD"],
        [
            "Find antibody titer endpoint",
            "Titer = Reciprocal of highest dilution positive",
        ],
        ["Calculate avidity index", "Avidity % = (OD with urea / OD without) × 100"],
        ["Determine IgG subclass ratio", "IgG1:IgG2:IgG3:IgG4 ratio"],
        ["Calculate total IgE level", "Total IgE IU/mL from standard curve"],
        ["Find specific IgE class", "Specific IgE: Class 0-6 based on kU/L"],
        ["Calculate complement C3 ratio", "C3 Ratio = Patient / Normal Pool"],
        ["Determine complement C4 level", "C4 mg/dL by nephelometry/turbidimetry"],
        ["Calculate CH50 hemolytic activity", "CH50 = Units based on 50% lysis"],
        [
            "Find AH50 alternative pathway",
            "AH50 = Alternative complement pathway activity",
        ],
        [
            "Calculate cryoglobulin quantification",
            "Cryoglobulin = Cryocrit % after precipitation",
        ],
        [
            "Determine monoclonal protein quantification",
            "M-Protein g/dL by densitometry",
        ],
        ["Calculate serum free light chains", "FLC Ratio = Kappa / Lambda"],
        ["Find immunofixation interpretation", "IFE: Identify monoclonal band type"],
        [
            "Calculate immunoglobulin replacement",
            "IgG Dose = Target Level - Current × Weight × 1.5",
        ],
        ["Determine vaccine response titer", "Protective Titer specific to pathogen"],
        [
            "Calculate seroconversion rate",
            "Seroconversion % = (Responders / Total) × 100",
        ],
        [
            "Find neutralizing antibody titer",
            "Neutralizing Titer = Highest dilution blocking infection",
        ],
        [
            "Calculate anti-drug antibody level",
            "ADA Titer = Impact on therapeutic efficacy",
        ],
        [
            "Determine autoantibody multiplicity",
            "Number of different autoantibodies present",
        ],
        [
            "Calculate mixed cryoglobulin composition",
            "Type I, II, or III cryoglobulinemia",
        ],
        [
            "Find beta-2 microglobulin level",
            "β2M mg/L = Kidney function + lymphoproliferative",
        ],
        [
            "Calculate serum protein electrophoresis",
            "SPEP: % and g/dL for each fraction",
        ],
        # Urinalysis & Renal (entries 251-275)
        [
            "Calculate absolute protein excretion",
            "Protein g/24h = Concentration × Volume / 100",
        ],
        [
            "Determine creatinine excretion adequacy",
            "Adequate if: 15-25 mg/kg/day (male), 10-20 (female)",
        ],
        [
            "Calculate glomerular filtration marker",
            "Cystatin C-based eGFR more accurate",
        ],
        [
            "Find tubular reabsorption phosphate",
            "TRP % = [1 - (UCr × PPhos) / (PCr × UPhos)] × 100",
        ],
        ["Calculate urine microalbumin rate", "Microalbumin mg/24h or mg/g creatinine"],
        ["Determine stone risk factors", "Calcium, oxalate, citrate, uric acid levels"],
        [
            "Calculate supersaturation ratio",
            "SS = Ion Activity Product / Solubility Product",
        ],
        ["Find Robertson risk index", "RRI for calcium oxalate stone formation"],
        ["Calculate urine saturation index", "SI = Concentration Product / Ksp"],
        [
            "Determine acid-base contribution",
            "Urine pH, titratable acid, NH4⁺ excretion",
        ],
        ["Calculate net acid excretion", "NAE = (NH4⁺ + TA) - HCO3⁻ (all in mEq/day)"],
        ["Find delta anion gap to HCO3", "Δ/Δ = (AG - 12) / (24 - HCO3⁻)"],
        ["Calculate urine output per hour", "UOP mL/hr from timed collection"],
        ["Determine polyuria threshold", "Polyuria if > 3 L/day"],
        ["Calculate urine concentration ability", "Max Osm after fluid restriction"],
        ["Find free water clearance", "CH2O = Urine Volume × (1 - Uosm/Posm)"],
        ["Calculate electrolyte-free water", "EFWC = Urine Vol × [1 - (UNa + UK)/PNa]"],
        ["Determine hyposthenuria degree", "Specific Gravity < 1.010"],
        ["Calculate isosthenuria presence", "SG fixed at 1.010 (renal failure)"],
        ["Find urinary sediment score", "RBCs, WBCs, casts per HPF"],
        [
            "Calculate dysmorphic RBC percentage",
            "Dysmorphic % suggests glomerular bleeding",
        ],
        ["Determine cast type significance", "RBC casts: glomerulonephritis"],
        ["Calculate crystalluria identification", "Crystal type by pH and morphology"],
        [
            "Find bacteria count significance",
            "Bacteriuria: > 100,000 CFU/mL significant",
        ],
        ["Calculate leucocyte esterase activity", "LE: Indicates pyuria/WBCs"],
        # Endocrinology (entries 276-300)
        [
            "Calculate thyroid-stimulating hormone",
            "TSH mIU/L: Reflects thyroid function status",
        ],
        ["Determine free T4 adjusted", "FT4 by equilibrium dialysis or immunoassay"],
        ["Calculate free T3 concentration", "FT3 pg/mL: Active thyroid hormone"],
        [
            "Find thyroglobulin antibody titer",
            "Anti-Tg: Interferes with Tg measurement",
        ],
        ["Calculate TPO antibody level", "Anti-TPO IU/mL: Autoimmune thyroiditis"],
        ["Determine parathyroid hormone intact", "PTH pg/mL: Calcium regulation"],
        ["Calculate vitamin D total", "25-OH Vit D = D2 + D3 (ng/mL)"],
        ["Find vitamin D adequacy", "Sufficient: > 30 ng/mL"],
        [
            "Calculate calcitonin level",
            "Calcitonin pg/mL: Medullary thyroid cancer marker",
        ],
        ["Determine growth hormone peak", "GH Peak ng/mL during stimulation test"],
        ["Calculate IGF-1 Z-score", "IGF-1 Z = (Patient - Age Mean) / SD"],
        ["Find IGFBP-3 ratio", "IGF-1/IGFBP-3 Molar Ratio"],
        [
            "Calculate cortisol response ACTH",
            "Peak Cortisol μg/dL post-ACTH stimulation",
        ],
        [
            "Determine dexamethasone suppression",
            "Cortisol < 1.8 μg/dL (low dose suppresses)",
        ],
        [
            "Calculate midnight cortisol test",
            "Midnight Cortisol < 1.8 μg/dL excludes Cushing's",
        ],
        ["Find urinary free cortisol", "UFC μg/24h: Integrated cortisol production"],
        [
            "Calculate ACTH to cortisol ratio",
            "ACTH/Cortisol helps differentiate causes",
        ],
        [
            "Determine renin to aldosterone ratio",
            "ARR: Screening for primary aldosteronism",
        ],
        ["Calculate aldosterone suppression", "Post-saline load aldosterone level"],
        [
            "Find metanephrine levels plasma",
            "Metanephrines: Pheochromocytoma screening",
        ],
        [
            "Calculate catecholamine fractionation",
            "Epinephrine, Norepinephrine, Dopamine",
        ],
        ["Determine 5-HIAA urine level", "5-HIAA mg/24h: Carcinoid syndrome"],
        ["Calculate testosterone free percentage", "Free % = 2-3% of total (men)"],
        [
            "Find sex hormone binding globulin",
            "SHBG nmol/L: Affects hormone availability",
        ],
        ["Calculate bioavailable testosterone", "BioT = Free T + Albumin-bound T"],
    ],
)
"""
COMPLETE 600-ENTRY DATASET GENERATOR
"""
import csv
import os

DIR = "hypatiax/datasets/generators/queries/"
os.makedirs(DIR, exist_ok=True)

# Combine all perfume entries (base 240 + remaining 60 = 300)
perfume_data_complete = perfume_data + perfume_remaining_60

# Combine all clinical entries (base 250 + remaining 50 = 300)
clinical_data_complete = clinical_data + clinical_continuation

# Write files
with open(
    DIR + "perfume_formulation_dataset_300.csv", "w", newline="", encoding="utf-8"
) as f:
    writer = csv.writer(f)
    writer.writerow(["query_description", "formula"])
    writer.writerows(perfume_data_complete)

with open(
    DIR + "clinical_laboratory_dataset_300.csv", "w", newline="", encoding="utf-8"
) as f:
    writer = csv.writer(f)
    writer.writerow(["query_description", "formula"])
    writer.writerows(clinical_data_complete)

print(f"✓ Perfume Dataset: {len(perfume_data_complete)} entries")
print(f"✓ Clinical Dataset: {len(clinical_data_complete)} entries")
print(f"✓ Total: {len(perfume_data_complete) + len(clinical_data_complete)} formulas")
