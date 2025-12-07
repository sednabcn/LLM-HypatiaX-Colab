"""
AI Training Datasets Generator - SEPARATED DATASETS
====================================================
Generates TWO independent CSV files:
1. perfume_formulation_dataset.csv (150+ entries)
2. clinical_laboratory_dataset.csv (150+ entries)

Format: query_description, formula
"""

import csv

# ============================================================================
# DATASET 1: PERFUME FORMULATION (150+ entries)
# ============================================================================

perfume_data = [
    [
        "Calculate perfume concentration percentage",
        "Concentration % = (Fragrance Oil Weight / Total Formula Weight) × 100",
    ],
    ["Determine eau de parfum dilution ratio", "EDP = 15-20% fragrance + 75-80% alcohol + 5% water"],
    ["Calculate eau de toilette strength", "EDT = 5-15% fragrance oil in alcohol base"],
    ["Compute cologne concentration", "Cologne = 2-5% fragrance in 70-90% alcohol"],
    ["Find parfum extrait percentage", "Parfum = 20-40% fragrance concentration"],
    ["Calculate alcohol volume for dilution", "Alcohol mL = Total Volume × (Alcohol % / 100)"],
    ["Determine fragrance oil needed for 100ml EDP", "Fragrance Oil = 100ml × 0.18 = 18ml"],
    ["Calculate water content in perfume", "Water mL = Total Volume - (Alcohol + Fragrance)"],
    ["Find total perfume weight from volumes", "Total Weight = (Volume₁ × Density₁) + (Volume₂ × Density₂) + ..."],
    ["Calculate cost per ml of perfume", "Cost/mL = Total Ingredient Cost / Final Volume"],
    # Top Notes Formulation
    ["Calculate top note percentage in formula", "Top Notes % = (Top Note Weight / Total Fragrance Weight) × 100"],
    ["Determine citrus oil ratio for freshness", "Citrus Ratio = Bergamot:Lemon:Orange = 3:2:1"],
    ["Calculate bergamot evaporation rate compensation", "Bergamot Adjusted = Base Amount × (1 + Evaporation Rate)"],
    ["Find optimal lemon oil concentration", "Lemon Oil = 5-15% of total fragrance oil"],
    ["Calculate grapefruit blend ratio", "Grapefruit = 10-25% of top note accord"],
    ["Determine mandarin oil proportion", "Mandarin = 8-20% of citrus blend"],
    ["Calculate neroli concentration for elegance", "Neroli = 2-8% of total fragrance"],
    ["Find petitgrain balance with citrus", "Petitgrain = 3-12% of top notes"],
    ["Calculate mint freshness factor", "Mint Oil = 1-5% for fresh effect"],
    ["Determine lavender top note amount", "Lavender = 5-15% in fougère compositions"],
    # Heart/Middle Notes
    ["Calculate heart note percentage", "Heart Notes % = (Middle Note Weight / Total Fragrance) × 100"],
    ["Determine rose absolute concentration", "Rose Absolute = 2-10% of fragrance oil"],
    ["Calculate jasmine dilution ratio", "Jasmine = 3-15% in floral formulas"],
    ["Find ylang-ylang optimal level", "Ylang-Ylang = 2-8% of total fragrance"],
    ["Calculate geranium balance", "Geranium = 5-20% in rose accords"],
    ["Determine iris butter percentage", "Iris = 1-5% for powdery effect"],
    ["Calculate tuberose intensity", "Tuberose = 2-10% for white floral"],
    ["Find orange blossom concentration", "Orange Blossom = 5-15% in florals"],
    ["Calculate carnation spice level", "Carnation = 2-8% for spicy florals"],
    ["Determine lily of valley accord", "Lily = 10-25% of heart notes"],
    # Base Notes
    ["Calculate base note percentage", "Base Notes % = (Base Weight / Total Fragrance) × 100"],
    ["Determine sandalwood concentration", "Sandalwood = 10-30% of base notes"],
    ["Calculate patchouli earthiness level", "Patchouli = 5-20% for oriental blends"],
    ["Find vetiver grounding proportion", "Vetiver = 8-25% in woody bases"],
    ["Calculate cedarwood ratio", "Cedarwood = 10-30% of woody accord"],
    ["Determine amber fixative amount", "Amber = 5-15% for warmth"],
    ["Calculate vanilla sweetness level", "Vanilla = 3-15% in gourmand bases"],
    ["Find tonka bean proportion", "Tonka Bean = 2-10% for coumarin notes"],
    ["Calculate musk fixative concentration", "Musk = 5-20% for longevity"],
    ["Determine oakmoss classic chypre ratio", "Oakmoss = 2-8% (IFRA compliant)"],
    # Accord Building
    ["Calculate floral accord balance", "Floral Accord = Rose:Jasmine:Ylang = 40:40:20"],
    ["Determine citrus accord composition", "Citrus = Bergamot:Lemon:Orange:Grapefruit = 40:25:20:15"],
    ["Calculate woody accord ratio", "Woody = Sandalwood:Cedar:Vetiver = 50:30:20"],
    ["Find oriental accord balance", "Oriental = Vanilla:Amber:Patchouli:Spices = 30:30:25:15"],
    ["Calculate fougère accord structure", "Fougère = Lavender:Coumarin:Oakmoss = 50:30:20"],
    ["Determine chypre accord formula", "Chypre = Bergamot:Rose:Oakmoss:Patchouli = 25:25:25:25"],
    ["Calculate aquatic accord freshness", "Aquatic = Calone:Citrus:Marine Notes = 30:40:30"],
    ["Find gourmand accord sweetness", "Gourmand = Vanilla:Caramel:Tonka:Fruits = 40:20:20:20"],
    ["Calculate green accord composition", "Green = Galbanum:Violet Leaf:Cut Grass = 40:35:25"],
    ["Determine leather accord intensity", "Leather = Birch Tar:Castoreum:Labdanum = 45:30:25"],
    # Fixative Calculations
    ["Calculate total fixative percentage", "Fixatives = 10-25% of total fragrance base"],
    ["Determine benzoin resin amount", "Benzoin = 3-10% as fixative"],
    ["Calculate labdanum stickiness factor", "Labdanum = 5-15% for longevity"],
    ["Find ambergris synthetic ratio", "Ambroxan = 2-8% for diffusion"],
    ["Calculate ISO E Super background", "ISO E Super = 10-40% for radiance"],
    ["Determine Galaxolide musk level", "Galaxolide = 5-15% for softness"],
    ["Calculate myrrh resinous depth", "Myrrh = 2-8% in base"],
    ["Find frankincense sacred ratio", "Frankincense = 3-10% for spirituality"],
    ["Calculate coumarin sweet warmth", "Coumarin = 5-15% in fougères"],
    ["Determine styrax balsamic level", "Styrax = 2-8% for depth"],
    # Solvent and Carrier Calculations
    ["Calculate ethanol purity for perfume", "Ethanol = 95-96% purity, denatured"],
    ["Determine dipropylene glycol (DPG) amount", "DPG = 5-20% for oil solubilization"],
    ["Calculate isopropyl myristate carrier", "IPM = 2-10% for skin feel"],
    ["Find benzyl benzoate solvent ratio", "Benzyl Benzoate = 5-15% for solubilization"],
    ["Calculate triethyl citrate amount", "Triethyl Citrate = 3-10% as solvent"],
    ["Determine propylene glycol level", "Propylene Glycol = 5-15% in water-based"],
    ["Calculate glycerin moisture content", "Glycerin = 2-8% for hydration"],
    ["Find ethyl alcohol concentration", "Ethyl Alcohol = 70-90% in final formula"],
    ["Calculate distilled water purification", "Distilled Water = 5-10% in formula"],
    ["Determine jojoba oil carrier amount", "Jojoba = 10-30% in oil-based perfumes"],
    # Specific Ingredient Ratios
    ["Calculate oud oil luxury concentration", "Oud = 0.5-5% for intense woody"],
    ["Determine saffron spice level", "Saffron = 0.1-1% for exotic touch"],
    ["Calculate cardamom warmth factor", "Cardamom = 1-5% in spicy accords"],
    ["Find cinnamon bark intensity", "Cinnamon = 0.5-3% (skin-safe limit)"],
    ["Calculate clove bud spiciness", "Clove = 0.5-2% for warmth"],
    ["Determine nutmeg aromatic level", "Nutmeg = 1-4% in oriental blends"],
    ["Calculate black pepper sharpness", "Black Pepper = 1-5% for spicy top"],
    ["Find pink pepper fizz factor", "Pink Pepper = 2-8% for modern freshness"],
    ["Calculate coffee absolute richness", "Coffee = 1-5% in gourmands"],
    ["Determine chocolate intensity", "Chocolate = 2-8% for sweetness"],
    # Aldehyde Formulations
    ["Calculate aldehyde C-12 soapy effect", "Aldehyde C-12 = 0.5-2% for classic soapiness"],
    ["Determine aldehyde C-11 fatty floral", "Aldehyde C-11 = 0.3-1.5% for lift"],
    ["Calculate aldehyde C-14 peachy note", "Aldehyde C-14 = 0.5-2% for fruity"],
    ["Find aldehyde C-18 coconut cream", "Aldehyde C-18 = 0.2-1% for lactonic"],
    ["Calculate mixed aldehydes sparkle", "Mixed Aldehydes = 1-3% total"],
    ["Determine bourgeonal lily effect", "Bourgeonal = 1-5% for muguet"],
    ["Calculate methyl ionone violet", "Methyl Ionone = 2-8% for powdery"],
    ["Find hydroxycitronellal fresh floral", "Hydroxycitronellal = 5-15% for clean"],
    ["Calculate hexyl cinnamic aldehyde jasmine", "HCA = 2-10% for jasmine facet"],
    ["Determine anisic aldehyde sweet hawthorn", "Anisic Aldehyde = 1-5% for sweet floral"],
    # Modern Synthetic Molecules
    ["Calculate Iso E Super halo effect", "Iso E Super = 10-40% for radiance"],
    ["Determine Hedione jasmine transparency", "Hedione = 10-30% for diffusive floral"],
    ["Calculate Ambroxan ambery warmth", "Ambroxan = 2-10% for marine amber"],
    ["Find Calone aquatic freshness", "Calone = 0.5-3% for marine ozone"],
    ["Calculate Georgywood intensity", "Georgywood = 5-20% for woody"],
    ["Determine Cashmeran soft musk", "Cashmeran = 5-15% for velvet"],
    ["Calculate Timberol cedar freshness", "Timberol = 5-15% for dry wood"],
    ["Find Javanol sandalwood creaminess", "Javanol = 10-30% for creamy wood"],
    ["Calculate Nirvanolide skin musk", "Nirvanolide = 2-8% for intimate"],
    ["Determine Ambrofix amber crystal", "Ambrofix = 3-12% for transparent amber"],
    # Fruit Notes
    ["Calculate apple fresh sweetness", "Apple = 3-10% in fruity florals"],
    ["Determine peach soft fuzziness", "Peach = 2-8% for velvety fruit"],
    ["Calculate pear juicy crispness", "Pear = 3-10% for elegant fruit"],
    ["Find strawberry candy sweetness", "Strawberry = 2-8% in gourmands"],
    ["Calculate raspberry tartness", "Raspberry = 2-6% for berry notes"],
    ["Determine blackcurrant bud cassis", "Blackcurrant = 2-8% for green fruit"],
    ["Calculate coconut creamy tropical", "Coconut = 3-12% for exotic"],
    ["Find pineapple tropical brightness", "Pineapple = 2-8% for juicy top"],
    ["Calculate mango lush sweetness", "Mango = 2-8% in tropical blends"],
    ["Determine fig milky green", "Fig = 3-10% for Mediterranean"],
    # Green and Herbal Notes
    ["Calculate galbanum sharp greenness", "Galbanum = 1-5% for intense green"],
    ["Determine violet leaf cucumber cool", "Violet Leaf = 2-8% for aquatic green"],
    ["Calculate basil aromatic freshness", "Basil = 1-5% for herbal top"],
    ["Find rosemary herbaceous clarity", "Rosemary = 2-8% for aromatic"],
    ["Calculate thyme Mediterranean warmth", "Thyme = 1-4% for herbal spice"],
    ["Determine sage clary aromatic depth", "Clary Sage = 3-10% for amber herb"],
    ["Calculate tea green freshness", "Green Tea = 2-8% for modern fresh"],
    ["Find cucumber water coolness", "Cucumber = 1-5% for aquatic fresh"],
    ["Calculate cut grass lawn freshness", "Cut Grass = 2-6% for green outdoors"],
    ["Determine ivy green leafy", "Ivy = 2-8% for forest green"],
    # Resinous and Balsamic
    ["Calculate elemi fresh resin", "Elemi = 2-8% for citrus spice"],
    ["Determine Peru balsam vanilla rich", "Peru Balsam = 3-10% for sweet resin"],
    ["Calculate Tolu balsam cinnamon sweet", "Tolu Balsam = 2-8% for balsamic"],
    ["Find benzoin vanilla resin", "Benzoin = 3-10% for sweet fixative"],
    ["Calculate opoponax sweet myrrh", "Opoponax = 2-8% for honey resin"],
    ["Determine cistus labdanum amber", "Cistus = 5-15% for leather amber"],
    ["Calculate storax balsam intensity", "Storax = 2-8% for oriental depth"],
    ["Find propolis honey resin", "Propolis = 1-5% for honey animalic"],
    ["Calculate pine resin forest depth", "Pine Resin = 2-8% for coniferous"],
    ["Determine fir balsam Christmas tree", "Fir Balsam = 3-10% for evergreen"],
    # Tobacco and Leather Notes
    ["Calculate tobacco absolute richness", "Tobacco = 2-10% for smoky depth"],
    ["Determine birch tar leather smokiness", "Birch Tar = 1-5% for leather"],
    ["Calculate castoreum animalic leather", "Castoreum = 0.5-3% for vintage leather"],
    ["Find cade oil smoky tar", "Cade Oil = 1-5% for campfire"],
    ["Calculate guaiacwood smoky sweet", "Guaiacwood = 5-15% for rose wood"],
    ["Determine hay absolute tobacco facet", "Hay = 2-8% for warm dried"],
    ["Calculate immortelle curry tobacco", "Immortelle = 1-5% for maple curry"],
    ["Find mate absolute green tobacco", "Mate = 2-6% for bitter green"],
    ["Calculate nagarmotha cypriol woody leather", "Nagarmotha = 2-8% for earthy leather"],
    ["Determine papyrus dry woody", "Papyrus = 3-10% for mineral wood"],
    # Aquatic and Marine
    ["Calculate calone ozone marine", "Calone = 0.5-3% for seabreeze"],
    ["Determine marine algae saltiness", "Marine Notes = 2-8% for ocean"],
    ["Calculate water notes transparency", "Water Accord = 5-15% for fresh aquatic"],
    ["Find sea salt mineral crispness", "Sea Salt = 1-5% for coastal"],
    ["Calculate seaweed iodine marine", "Seaweed = 1-4% for authentic ocean"],
    ["Determine melon aquatic juiciness", "Melon = 3-10% for fruity aquatic"],
    ["Calculate lotus water floral", "Lotus = 2-8% for Asian aquatic"],
    ["Find rain accord fresh wetness", "Rain = 5-15% for petrichor"],
    ["Calculate mineral notes stone coolness", "Mineral = 2-8% for rock water"],
    ["Determine seaspray salty mist", "Sea Spray = 2-8% for coastal breeze"],
    # Concentration Adjustments
    ["Calculate perfume to body spray dilution", "Body Spray = Perfume concentration × 0.25"],
    ["Determine splash cologne from concentrate", "Splash = 3-5% in 80% alcohol"],
    ["Calculate aftershave lotion strength", "Aftershave = 2-4% fragrance + soothing agents"],
    ["Find hair mist safe concentration", "Hair Mist = 1-3% in light alcohol"],
    ["Calculate linen spray dilution", "Linen Spray = 2-5% in water-alcohol mix"],
    ["Determine reed diffuser oil strength", "Reed Diffuser = 10-20% in carrier oil"],
    ["Calculate candle fragrance load", "Candle = 6-10% fragrance in wax"],
    ["Find soap safe fragrance level", "Soap = 2-4% skin-safe fragrance"],
    ["Calculate lotion perfume percentage", "Lotion = 1-3% in emulsion base"],
    ["Determine shampoo fragrance load", "Shampoo = 0.5-2% in surfactant base"],
    # Maturation and Aging
    ["Calculate maceration time formula", "Maceration Days = 30-90 for optimal blending"],
    ["Determine aging improvement factor", "Aging Improvement = log(Days + 1) × Quality Factor"],
    ["Calculate temperature for maturation", "Maturation Temp = 15-20°C constant"],
    ["Find optimal storage humidity", "Storage Humidity = 40-60% RH"],
    ["Calculate evaporation loss percentage", "Evaporation Loss = 2-5% over 6 months"],
    ["Determine bottle fill headspace", "Headspace = 5-10% of bottle volume"],
    ["Calculate oxidation prevention", "Nitrogen Blanket = 100% headspace fill"],
    ["Find light protection requirement", "Amber Glass = 99% UV filtration"],
    ["Calculate shake-and-settle time", "Settling = 24-48 hours after mixing"],
    ["Determine cold stability test", "Cold Test = 0°C for 48 hours, no cloudiness"],
    # Allergen Management
    ["Calculate total allergen percentage", "Total Allergens = Sum(Each Allergen %) must be listed if >0.001%"],
    ["Determine IFRA category compliance", "IFRA Cat = Product Type QRA limit check"],
    ["Calculate limonene natural level", "Limonene = 60-95% in citrus oils"],
    ["Find linalool lavender content", "Linalool = 25-45% in lavender oil"],
    ["Calculate geraniol rose concentration", "Geraniol = 15-30% in rose oil"],
    ["Determine citronellol content", "Citronellol = 18-55% in rose/geranium"],
    ["Calculate eugenol clove limitation", "Eugenol = Max 0.5-1% (IFRA restricted)"],
    ["Find coumarin tonka restriction", "Coumarin = Max 0.1-1% depending category"],
    ["Calculate citral limit compliance", "Citral = Max 0.6-2% (skin sensitizer)"],
    ["Determine farnesol natural occurrence", "Farnesol = 2-15% in jasmine/ylang"],
    # Cost Analysis Formulas
    ["Calculate raw material cost per batch", "Batch Cost = Σ(Ingredient Weight × Price per kg)"],
    ["Determine cost per finished unit", "Unit Cost = Batch Cost / Number of Units"],
    ["Calculate markup for retail price", "Retail Price = Unit Cost × (1 + Markup %)"],
    ["Find break-even production volume", "Break-Even = Fixed Costs / (Price - Variable Cost)"],
    ["Calculate ingredient cost percentage", "Ingredient % = (Ingredient Cost / Total Cost) × 100"],
    ["Determine profit margin on perfume", "Profit Margin = (Revenue - Cost) / Revenue × 100"],
    ["Calculate wholesale discount amount", "Wholesale = Retail × (1 - Discount %)"],
    ["Find production cost efficiency", "Efficiency = Actual Yield / Theoretical Yield × 100"],
    ["Calculate packaging cost ratio", "Packaging % = Packaging Cost / Total Cost × 100"],
    ["Determine sample vial costing", "Sample Cost = (Fragrance Cost × Sample mL) + Vial Cost"],
]

# ============================================================================
# DATASET 2: CLINICAL LABORATORY (150+ entries)
# ============================================================================

clinical_data = [
    ["Calculate absolute neutrophil count (ANC)", "ANC = WBC × (% Neutrophils + % Bands) / 100"],
    ["Determine corrected calcium for albumin", "Corrected Ca = Measured Ca + 0.8 × (4.0 - Albumin g/dL)"],
    ["Calculate anion gap", "Anion Gap = Na⁺ - (Cl⁻ + HCO₃⁻)"],
    [
        "Find creatinine clearance (Cockcroft-Gault)",
        "CrCl = [(140 - Age) × Weight kg × (0.85 if female)] / (72 × SCr mg/dL)",
    ],
    ["Calculate body mass index (BMI)", "BMI = Weight kg / (Height m)²"],
    ["Determine mean corpuscular volume (MCV)", "MCV fL = (Hematocrit % × 10) / RBC count (millions/μL)"],
    ["Calculate mean corpuscular hemoglobin (MCH)", "MCH pg = (Hemoglobin g/dL × 10) / RBC count (millions/μL)"],
    ["Find MCHC concentration", "MCHC g/dL = (Hemoglobin g/dL × 100) / Hematocrit %"],
    [
        "Calculate reticulocyte production index",
        "RPI = (Reticulocyte % × Patient Hct) / (Normal Hct × Maturation Factor)",
    ],
    ["Determine absolute reticulocyte count", "Absolute Retic = Reticulocyte % × RBC count / 100"],
    # Renal Function Tests
    ["Calculate estimated GFR (MDRD)", "eGFR = 175 × (SCr)⁻¹·¹⁵⁴ × (Age)⁻⁰·²⁰³ × (0.742 if female) × (1.212 if Black)"],
    ["Determine BUN to creatinine ratio", "BUN/Cr Ratio = BUN mg/dL / Creatinine mg/dL"],
    ["Calculate fractional excretion of sodium", "FENa % = [(UNa × PCr) / (PNa × UCr)] × 100"],
    ["Find urine protein to creatinine ratio", "UPCR = Urine Protein mg/dL / Urine Creatinine mg/dL"],
    ["Calculate albumin to creatinine ratio", "ACR mg/g = (Urine Albumin mg/L / Urine Creatinine mg/L) × 1000"],
    ["Determine protein excretion rate", "24h Protein = Urine Protein mg/dL × 24h Volume L × 10"],
    ["Calculate osmolal gap (serum)", "Osm Gap = Measured Osm - Calculated Osm (2×Na + Glucose/18 + BUN/2.8)"],
    ["Find urine osmolal gap", "Urine Osm Gap = Measured - 2×(Na + K) - Urea/2.8 - Glucose/18"],
    ["Calculate transtubular potassium gradient", "TTKG = (Urine K / Plasma K) / (Urine Osm / Plasma Osm)"],
    ["Determine creatinine production rate", "Cr Production = UCr × 24h Volume / (1440 × Weight kg)"],
    # Liver Function Tests
    ["Calculate Child-Pugh score", "Child-Pugh = Points(Bilirubin + Albumin + INR + Ascites + Encephalopathy)"],
    ["Determine MELD score", "MELD = 3.78×ln(Bili) + 11.2×ln(INR) + 9.57×ln(Cr) + 6.43"],
    ["Calculate AST to ALT ratio", "AST/ALT Ratio = AST IU/L / ALT IU/L"],
    ["Find alkaline phosphatase to bilirubin ratio", "ALP/Bili = ALP IU/L / Total Bili mg/dL"],
    ["Calculate APRI score (fibrosis)", "APRI = [(AST/ULN) / Platelet count (10⁹/L)] × 100"],
    ["Determine FIB-4 index", "FIB-4 = (Age × AST) / (Platelet count × √ALT)"],
    ["Calculate direct to total bilirubin ratio", "Direct/Total Bili = Direct Bili / Total Bili"],
    ["Find albumin to globulin ratio", "A/G Ratio = Albumin g/dL / (Total Protein - Albumin)"],
    ["Calculate prothrombin time ratio", "PT Ratio = Patient PT / Control PT"],
    ["Determine INR value", "INR = (Patient PT / Mean Normal PT)^ISI"],
    # Lipid Panel Calculations
    ["Calculate LDL cholesterol (Friedewald)", "LDL = Total Chol - HDL - (Triglycerides / 5) [if TG < 400]"],
    ["Determine non-HDL cholesterol", "Non-HDL = Total Cholesterol - HDL"],
    ["Calculate VLDL cholesterol estimate", "VLDL = Triglycerides / 5"],
    ["Find cholesterol to HDL ratio", "Total Chol/HDL = Total Cholesterol / HDL"],
    ["Calculate LDL to HDL ratio", "LDL/HDL = LDL Cholesterol / HDL Cholesterol"],
    ["Determine atherogenic index", "Atherogenic Index = log(TG / HDL)"],
    ["Calculate Castelli risk index I", "Castelli I = Total Cholesterol / HDL"],
    ["Find Castelli risk index II", "Castelli II = LDL / HDL"],
    ["Calculate coronary risk ratio", "Coronary Risk = Total Chol / HDL"],
    ["Determine apoB to apoA1 ratio", "ApoB/ApoA1 = Apolipoprotein B / Apolipoprotein A1"],
    # Acid-Base Balance
    ["Calculate base excess", "Base Excess = (HCO₃⁻ - 24.4) + (2.3 × Hgb + 7.7) × (pH - 7.4)"],
    ["Determine expected PCO₂ in metabolic acidosis", "Expected PCO₂ = 1.5 × HCO₃⁻ + 8 (±2)"],
    ["Calculate expected HCO₃⁻ in respiratory disorder", "Acute: ΔHCO₃⁻ = ΔPCo₂ × 0.1; Chronic: ΔHCO₃⁻ = ΔPCO₂ × 0.4"],
    ["Find delta ratio (gap-gap)", "Delta Ratio = (Anion Gap - 12) / (24 - HCO₃⁻)"],
    ["Calculate osmolar gap", "Osm Gap = Measured Osm - (2×Na + Glucose/18 + BUN/2.8 + Ethanol/4.6)"],
    ["Determine Henderson-Hasselbalch pH", "pH = 6.1 + log(HCO₃⁻ / (0.03 × PCO₂))"],
    ["Calculate alveolar-arterial gradient", "A-a Gradient = [(FiO₂ × (Patm - 47) - PaCO₂/0.8] - PaO₂"],
    ["Find oxygen content arterial", "CaO₂ = (1.34 × Hgb × SaO₂) + (0.003 × PaO₂)"],
    ["Calculate PaO₂/FiO₂ ratio", "P/F Ratio = PaO₂ mmHg / FiO₂ (decimal)"],
    ["Determine oxygen saturation gap", "O₂ Sat Gap = Calculated SaO₂ - Measured SpO₂"],
    # Diabetes and Glucose Monitoring
    ["Calculate estimated average glucose from HbA1c", "eAG mg/dL = (28.7 × HbA1c %) - 46.7"],
    ["Determine HOMA-IR insulin resistance", "HOMA-IR = (Fasting Insulin μU/mL × Fasting Glucose mg/dL) / 405"],
    ["Calculate HOMA-B beta cell function", "HOMA-B = (360 × Fasting Insulin) / (Fasting Glucose - 63)"],
    ["Find glucose management indicator", "GMI % = 3.31 + 0.02392 × Mean Glucose mg/dL"],
    ["Calculate insulin to carb ratio", "I:C Ratio = 500 / Total Daily Insulin"],
    ["Determine correction factor (insulin sensitivity)", "Correction Factor = 1800 / Total Daily Insulin"],
    ["Calculate glycemic variability (CV)", "CV % = (SD of Glucose / Mean Glucose) × 100"],
    ["Find time in range percentage", "TIR % = (Readings 70-180 mg/dL / Total Readings) × 100"],
    ["Calculate glucose area under curve", "AUC = Σ[(Glucose₁ + Glucose₂)/2 × Time Interval]"],
    ["Determine fructosamine-estimated A1c", "Est A1c = (Fructosamine μmol/L - 158) / 21.3"],
    # Thyroid Function Tests
    ["Calculate free thyroxine index (FTI)", "FTI = Total T4 × T3 Uptake / 100"],
    ["Determine thyroid hormone ratio", "T3/T4 Ratio = Total T3 / Total T4"],
    ["Calculate thyrotropin index", "TSHI = log(TSH) + 0.1345 × FT4"],
    ["Find thyroid secretion rate", "TSR = FT4 × 0.138 × Weight kg"],
    ["Calculate T3 resin uptake ratio", "T3RU Ratio = Patient T3RU / Mean Normal T3RU"],
    ["Determine total T3 from free T3", "Total T3 ≈ Free T3 × 154"],
    ["Calculate reverse T3 ratio", "rT3 Ratio = Reverse T3 / Total T3"],
    ["Find TSH-T4 dissociation index", "SPINA-GT = (TSH × FT4) / Reference Range Product"],
    # Coagulation Studies
    ["Calculate activated clotting time ratio", "ACT Ratio = Patient ACT / Control ACT"],
    ["Determine aPTT ratio", "aPTT Ratio = Patient aPTT / Mean Normal aPTT"],
    ["Calculate thrombin time ratio", "TT Ratio = Patient TT / Control TT"],
    ["Find fibrinogen activity percentage", "Fibrinogen Activity = (Patient Clot / Reference) × 100"],
    ["Calculate D-dimer FEU conversion", "D-dimer FEU = DDU × 2"],
    ["Determine bleeding time adjusted", "Bleeding Time Adjusted = Observed Time / Template Width"],
    ["Calculate platelet function analyzer closure time", "PFA-CT = Closure Time (ADP or Epi cartridge)"],
    ["Find clot retraction percentage", "Clot Retraction % = (Serum Volume / Total Volume) × 100"],
    ["Calculate mixing study correction", "Correction = [(Mix PT - Patient PT) / Patient PT] × 100 > 10%"],
    ["Determine factor VIII activity", "Factor VIII = % Activity from PT-based assay"],
    # Electrolyte and Mineral Balance
    ["Calculate corrected sodium for glucose", "Corrected Na = Measured Na + 0.016 × (Glucose - 100)"],
    ["Determine free calcium from total", "Free Ca = 0.9 + 0.55 × Total Ca - 0.3 × Albumin"],
    ["Calculate calcium-phosphate product", "Ca × PO₄ = Calcium mg/dL × Phosphate mg/dL"],
    ["Find potassium correction for pH", "K⁺ change = 0.6 mEq/L per 0.1 pH unit"],
    ["Calculate magnesium to calcium ratio", "Mg/Ca Ratio = Magnesium mg/dL / Calcium mg/dL"],
    ["Determine sodium deficit", "Na Deficit = 0.6 × Weight kg × (Desired Na - Actual Na)"],
    ["Calculate free water deficit", "Water Deficit = TBW × [(Actual Na / Desired Na) - 1]"],
    ["Find chloride to sodium ratio", "Cl/Na Ratio = Chloride mEq/L / Sodium mEq/L"],
    ["Calculate phosphate correction for albumin", "Corrected PO₄ = Measured PO₄ + (3.5 - Albumin)"],
    ["Determine ionized calcium from pH", "ΔiCa = 0.05 mmol/L per 0.1 pH increase"],
    # Hematology Indices
    ["Calculate red cell distribution width CV", "RDW-CV % = (SD of RBC Volume / MCV) × 100"],
    ["Determine platelet distribution width", "PDW = SD of Platelet Volume"],
    ["Calculate mean platelet volume", "MPV fL = Plateletcrit % / Platelet Count × 10⁶"],
    ["Find plateletcrit percentage", "PCT % = (Platelet Count × MPV) / 10,000"],
    ["Calculate immature platelet fraction", "IPF % = Immature Platelets / Total Platelets × 100"],
    ["Determine nucleated RBC count", "nRBC/100 WBC, Corrected WBC = Counted WBC × 100/(100 + nRBC)"],
    ["Calculate large unstained cells", "LUC = Total WBC - (Lymph + Mono + Gran)"],
    ["Find red cell hemoglobin content", "CHr pg = Mean Hgb Content of Reticulocytes"],
    ["Calculate RBC morphology index", "RDW-SD fL = Width at 20% Height of RBC Histogram"],
    ["Determine blast percentage", "Blast % = (Blast Count / Total WBC) × 100"],
    # Tumor Markers and Ratios
    ["Calculate PSA density", "PSAD = Total PSA / Prostate Volume mL"],
    ["Determine PSA velocity", "PSA Velocity = (PSA₂ - PSA₁) / Time years"],
    ["Calculate free to total PSA ratio", "Free/Total PSA % = (Free PSA / Total PSA) × 100"],
    ["Find CA-125 to CEA ratio", "CA-125/CEA = CA-125 U/mL / CEA ng/mL"],
    ["Calculate AFP to total protein ratio", "AFP Ratio = AFP ng/mL / Total Protein g/L"],
    ["Determine tumor marker doubling time", "Doubling Time = (t × ln2) / ln(C₂/C₁)"],
    ["Calculate HCG discriminatory zone", "HCG Threshold = 1500-2000 mIU/mL for IUP visualization"],
    ["Find CA 19-9 to bilirubin ratio", "CA 19-9/Bili = CA 19-9 / Total Bilirubin"],
    ["Calculate CEA to CA 19-9 ratio", "CEA/CA 19-9 = CEA ng/mL / CA 19-9 U/mL"],
    ["Determine LDH to ALT ratio", "LDH/ALT = LDH IU/L / ALT IU/L"],
    # Urinalysis Calculations
    ["Calculate specific gravity from osmolality", "Specific Gravity ≈ 1.000 + (Osm / 1000 × 0.035)"],
    ["Determine urine albumin excretion rate", "AER mg/24h = Urine Albumin × 24h Volume / 1000"],
    ["Calculate urine protein excretion", "Protein g/24h = Urine Protein mg/dL × Volume L × 0.01"],
    ["Find fractional excretion of urea", "FEUrea % = [(Uurea × PCr) / (Purea × UCr)] × 100"],
    ["Calculate renal failure index", "RFI = UNa / (UCr / PCr)"],
    ["Determine urine anion gap", "Urine AG = (UNa + UK) - UCl"],
    ["Calculate urine osmolal gap for NH₄⁺", "UOG = Measured Osm - Calculated, NH₄⁺ ≈ UOG/2"],
    ["Find urine calcium to creatinine ratio", "UCa/Cr = (Urine Ca mg/dL / Urine Cr mg/dL)"],
    ["Calculate 24-hour calcium excretion", "Ca Excretion = Urine Ca mg/dL × Volume L × 10"],
    ["Determine urine uric acid to creatinine ratio", "U-UA/Cr = Urine Uric Acid / Urine Creatinine"],
    # Immunology and Serology
    ["Calculate antibody titer dilution", "Titer = Highest Dilution with Positive Reaction"],
    ["Determine IgG index for CSF", "IgG Index = (CSF IgG / Serum IgG) / (CSF Albumin / Serum Albumin)"],
    ["Calculate CSF/serum albumin ratio", "Albumin Ratio = (CSF Albumin / Serum Albumin) × 1000"],
    ["Find IgG synthesis rate", "IgG Synthesis = [(CSF IgG - Serum IgG/369) - (CSF Alb/230)] × 5"],
    ["Calculate C3 to C4 ratio", "C3/C4 = Complement C3 / Complement C4"],
    ["Determine CH50 complement activity", "CH50 = Dilution causing 50% Hemolysis"],
    ["Calculate antigen-antibody ratio", "Ag:Ab = Antigen Conc / Antibody Conc"],
    ["Find rheumatoid factor units", "RF IU/mL = Patient OD / Cutoff OD × Calibrator Value"],
    ["Calculate anti-CCP antibody level", "Anti-CCP U/mL from Standard Curve"],
    ["Determine ANA titer pattern", "ANA = Titer × Pattern (e.g., 1:320 Homogeneous)"],
    # Cardiac Biomarkers
    ["Calculate troponin delta change", "Δ Troponin = Troponin₂ - Troponin₁"],
    ["Determine troponin relative change", "% Change = [(Trop₂ - Trop₁) / Trop₁] × 100"],
    ["Calculate BNP to NT-proBNP conversion", "NT-proBNP ≈ BNP × 8"],
    ["Find CK-MB relative index", "CK-MB Index % = (CK-MB / Total CK) × 100"],
    ["Calculate myoglobin to troponin ratio", "Myoglobin/Trop = Myoglobin ng/mL / Troponin ng/mL"],
    ["Determine hs-cTn delta at 1 hour", "1h Δhs-cTn for Rule-in/Rule-out Protocol"],
    ["Calculate copeptin combined with troponin", "Combined Score = Troponin + Copeptin Algorithm"],
    ["Find H-FABP heart fatty acid protein", "H-FABP ng/mL elevation for early MI"],
    ["Calculate troponin clearance rate", "Clearance = (Peak - Current) / Time hours"],
    ["Determine GRACE risk score", "GRACE = Points(Age + HR + SBP + Cr + Killip + Arrest + ST + Cardiac Enzymes)"],
    # Microbiology Calculations
    ["Calculate colony forming units", "CFU/mL = (Colony Count × Dilution Factor) / Volume Plated"],
    ["Determine bacterial growth rate", "Growth Rate = ln(N₂/N₁) / (t₂ - t₁)"],
    ["Calculate doubling time", "Doubling Time = ln(2) / Growth Rate"],
    ["Find minimum inhibitory concentration", "MIC = Lowest Antibiotic Conc with No Visible Growth"],
    ["Calculate zone of inhibition diameter", "ZOI = Diameter mm of Clear Zone"],
    ["Determine bacterial load reduction", "Log Reduction = log₁₀(Initial CFU) - log₁₀(Final CFU)"],
    ["Calculate D-value sterilization", "D-value = Time for 1 Log₁₀ Reduction"],
    ["Find bactericidal ratio", "MBC/MIC Ratio = Bactericidal / Inhibitory Concentration"],
    ["Calculate viral load copies", "Viral Load = Copies/mL from PCR Ct Value"],
    ["Determine antibiotic synergy", "FIC Index = (MIC_A combo / MIC_A alone) + (MIC_B combo / MIC_B alone)"],
    # Cerebrospinal Fluid Analysis
    ["Calculate CSF protein to albumin ratio", "CSF Protein/Albumin = CSF Total Protein / CSF Albumin"],
    ["Determine CSF glucose to serum ratio", "CSF/Serum Glucose = CSF Glucose / Serum Glucose"],
    ["Calculate CSF WBC corrected for RBC", "Corrected WBC = Observed WBC - (Blood WBC × CSF RBC / Blood RBC)"],
    ["Find CSF opening pressure", "Opening Pressure mmH₂O via Manometry"],
    ["Calculate oligoclonal band number", "OCB = Number of Bands in CSF not in Serum"],
    ["Determine CSF IgG to total protein", "IgG % = (CSF IgG / CSF Total Protein) × 100"],
    ["Calculate intrathecal IgG synthesis", "IgG Synthesis = (CSF IgG / Serum IgG) - (CSF Alb / Serum Alb)"],
    ["Find CSF lactate to glucose ratio", "Lactate/Glucose = CSF Lactate / CSF Glucose"],
    ["Calculate CSF chloride significance", "CSF Chloride mEq/L (↓ in bacterial meningitis)"],
    ["Determine xanthochromia index", "Xanthochromia = Spectrophotometry at 460nm"],
    # Hormone Assays
    ["Calculate testosterone free from total", "Free Testosterone = Total × % Free (from SHBG calculation)"],
    ["Determine DHEA-S to testosterone ratio", "DHEAS/Testosterone = DHEAS μg/dL / Testosterone ng/dL"],
    ["Calculate estradiol to estrone ratio", "E2/E1 = Estradiol pg/mL / Estrone pg/mL"],
    ["Find progesterone luteal adequacy", "Progesterone > 10 ng/mL in mid-luteal phase"],
    ["Calculate cortisol to ACTH ratio", "Cortisol/ACTH = Cortisol μg/dL / ACTH pg/mL"],
    ["Determine aldosterone to renin ratio", "ARR = Aldosterone ng/dL / Renin ng/mL/h"],
    ["Calculate free androgen index", "FAI = (Total Testosterone / SHBG) × 100"],
    ["Find bioavailable testosterone", "BioT = Total T - SHBG-bound T"],
    ["Calculate PTH to calcium ratio", "PTH/Ca = PTH pg/mL / Calcium mg/dL"],
    ["Determine 25-OH vitamin D total", "Total Vit D = 25-OH-D2 + 25-OH-D3"],
    # Toxicology Screening
    ["Calculate ethanol blood level", "Ethanol mg/dL = BAC % × 1000"],
    ["Determine salicylate level significance", "Salicylate mg/dL + Done Nomogram for Toxicity"],
    ["Calculate acetaminophen hepatotoxicity", "APAP μg/mL on Rumack-Matthew Nomogram"],
    ["Find lithium therapeutic index", "Lithium = 0.6-1.2 mEq/L Therapeutic Range"],
    ["Calculate digoxin steady state", "Digoxin SS = Dose / (CLr + CLnr) × F"],
    ["Determine phenytoin corrected for albumin", "Corrected Phenytoin = Measured / (0.2 × Albumin + 0.1)"],
    ["Calculate carboxyhemoglobin percentage", "COHb % = (COHb / Total Hb) × 100"],
    ["Find methemoglobin level", "MetHb % = (MetHb / Total Hb) × 100"],
    ["Calculate osmolal gap for toxins", "Osm Gap > 10 suggests volatile toxin"],
    ["Determine theophylline clearance", "Theophylline CL = Dose / (Css × τ)"],
    # Blood Gas Analysis
    ["Calculate bicarbonate from pH and PCO₂", "HCO₃⁻ = 0.03 × PCO₂ × 10^(pH - 6.1)"],
    ["Determine oxygen saturation from PO₂", "SaO₂ % from Oxygen Dissociation Curve"],
    ["Calculate P50 oxygen affinity", "P50 = PO₂ at 50% Saturation (normal 26-27 mmHg)"],
    ["Find shunt fraction", "Qs/Qt = (CcO₂ - CaO₂) / (CcO₂ - CvO₂)"],
    ["Calculate oxygen delivery", "DO₂ = CO × CaO₂ × 10"],
    ["Determine oxygen consumption", "VO₂ = CO × (CaO₂ - CvO₂) × 10"],
    ["Calculate oxygen extraction ratio", "O₂ER = (CaO₂ - CvO₂) / CaO₂"],
    ["Find respiratory quotient", "RQ = VCO₂ / VO₂"],
    ["Calculate alveolar oxygen tension", "PAO₂ = (FiO₂ × (Patm - 47)) - (PaCO₂ / RQ)"],
    ["Determine dead space fraction", "Vd/Vt = (PaCO₂ - PĒCO₂) / PaCO₂"],
    # Hemostasis Testing
    ["Calculate reptilase time ratio", "Reptilase Ratio = Patient Time / Control Time"],
    ["Determine euglobulin lysis time", "ELT = Time for Clot Lysis (normal 2-4 hours)"],
    ["Calculate factor assay percentage", "Factor % = Patient / Normal Pool × 100"],
    ["Find von Willebrand activity ratio", "vWF:RCo / vWF:Ag Ratio"],
    ["Calculate ADAMTS13 activity", "ADAMTS13 % = Enzyme Activity Assay"],
    ["Determine protein C activity", "Protein C % Activity from Clotting Assay"],
    ["Calculate protein S free antigen", "Free Protein S % of Total"],
    ["Find antithrombin activity", "AT % = Heparin Cofactor Activity"],
    ["Calculate lupus anticoagulant ratio", "LA Ratio = (Patient / Control) for dRVVT or aPTT"],
    ["Determine platelet aggregation response", "Aggregation % = ΔLight Transmission"],
    # Special Chemistry
    ["Calculate serum viscosity relative", "Relative Viscosity = Serum Viscosity / Water Viscosity"],
    ["Determine cryoglobulin precipitation", "Cryoglobulin mg/dL after 72h at 4°C"],
    ["Calculate amylase to lipase ratio", "Amylase/Lipase = Amylase IU/L / Lipase IU/L"],
    ["Find lipase to amylase ratio significance", "Lipase/Amylase > 2 suggests acute pancreatitis"],
    ["Calculate sweat chloride for CF", "Sweat Cl⁻ > 60 mEq/L positive for CF"],
    ["Determine alpha-1 antitrypsin phenotype", "AAT mg/dL + PI Typing for Deficiency"],
    ["Calculate ceruloplasmin to copper ratio", "Ceruloplasmin/Copper for Wilson's Disease"],
    ["Find lactate to pyruvate ratio", "L/P Ratio = Lactate / Pyruvate (normal 10:1)"],
    ["Calculate ammonia to glutamine ratio", "NH₃/Glutamine for hepatic encephalopathy"],
    ["Determine porphobilinogen quantitative", "PBG mg/24h for Acute Porphyria"],
]

# ============================================================================
# EXPORT TO CSV FILES
# ============================================================================


def create_csv_files():
    """Generate two separate CSV files for the datasets"""

    # Create Perfume Dataset CSV
    with open("perfume_formulation_dataset.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["query_description", "formula"])
        writer.writerows(perfume_data)

    # Create Clinical Laboratory Dataset CSV
    with open("clinical_laboratory_dataset.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["query_description", "formula"])
        writer.writerows(clinical_data)

    print(f"✓ Created: perfume_formulation_dataset.csv ({len(perfume_data)} entries)")
    print(f"✓ Created: clinical_laboratory_dataset.csv ({len(clinical_data)} entries)")
    print(f"\nTotal formulas generated: {len(perfume_data) + len(clinical_data)}")


if __name__ == "__main__":
    create_csv_files()

"""
📊 Dataset 1: Perfume Formulation (150 entries)
Covers:

Basic concentration calculations (EDP, EDT, Cologne, Parfum)
Dilution and mixing formulas
Top, heart, and base notes composition
Accord building (floral, citrus, woody, oriental, etc.)
Fixative calculations
Modern synthetic molecules
Fruit, green, and herbal notes
Resinous, tobacco, and leather notes
Aquatic and marine accords
Allergen management (IFRA compliance)
Cost analysis formulas

🧪 Dataset 2: Clinical Laboratory (150 entries)
Covers:

Hematology indices (CBC, MCV, MCH, MCHC)
Renal function tests (GFR, creatinine clearance)
Liver function tests (MELD, Child-Pugh, AST/ALT)
Lipid panel calculations
Acid-base balance
Diabetes monitoring (HbA1c, HOMA-IR)
Thyroid function tests
Coagulation studies
Electrolyte balance
Tumor markers
Urinalysis calculations
Cardiac biomarkers
Microbiology calculations
CSF analysis
Hormone assays
Toxicology screening
Blood gas analysis

Both datasets are in CSV format with columns: query_description and formula. Run the Python script to generate the two separate CSV files!Claude is AI and can make mistakes.

"""
