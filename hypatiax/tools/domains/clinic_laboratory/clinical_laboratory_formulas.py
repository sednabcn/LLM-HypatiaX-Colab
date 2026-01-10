"""
Clinical Laboratory Analysis System - Enhanced Edition
======================================================
Production-ready blood analysis and clinical calculations for health clinics.
Version: 2.0.0
"""

import math
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple

EPSILON = 1e-12


class Gender(Enum):
    MALE = "Male"
    FEMALE = "Female"


class RiskLevel(Enum):
    LOW = "Low Risk"
    BORDERLINE = "Borderline"
    MODERATE = "Moderate Risk"
    HIGH = "High Risk"
    VERY_HIGH = "Very High Risk"


class Status(Enum):
    NORMAL = "Normal"
    LOW = "Below Normal"
    HIGH = "Above Normal"
    CRITICAL_LOW = "Critically Low"
    CRITICAL_HIGH = "Critically High"


@dataclass
class ReferenceRange:
    min_val: float
    max_val: float
    unit: str
    critical_low: Optional[float] = None
    critical_high: Optional[float] = None

    def interpret(self, value: float) -> Status:
        if self.critical_low and value < self.critical_low:
            return Status.CRITICAL_LOW
        if self.critical_high and value > self.critical_high:
            return Status.CRITICAL_HIGH
        if value < self.min_val:
            return Status.LOW
        if value > self.max_val:
            return Status.HIGH
        return Status.NORMAL


class CompleteCBCPanel:
    """Complete Blood Count with advanced analysis."""

    RANGES_MALE = {
        "wbc": ReferenceRange(4.5, 11.0, "10³/µL", 2.0, 30.0),
        "rbc": ReferenceRange(4.5, 5.9, "10⁶/µL", 2.5, 7.0),
        "hemoglobin": ReferenceRange(13.5, 17.5, "g/dL", 7.0, 20.0),
        "hematocrit": ReferenceRange(39.0, 50.0, "%", 20.0, 60.0),
        "platelets": ReferenceRange(150, 400, "10³/µL", 20, 1000),
    }

    RANGES_FEMALE = {
        "wbc": ReferenceRange(4.5, 11.0, "10³/µL", 2.0, 30.0),
        "rbc": ReferenceRange(4.0, 5.2, "10⁶/µL", 2.5, 7.0),
        "hemoglobin": ReferenceRange(12.0, 16.0, "g/dL", 7.0, 20.0),
        "hematocrit": ReferenceRange(36.0, 46.0, "%", 20.0, 60.0),
        "platelets": ReferenceRange(150, 400, "10³/µL", 20, 1000),
    }

    @staticmethod
    def calculate_indices(
        hemoglobin: float, rbc: float, hematocrit: float
    ) -> Dict[str, any]:
        """
        Calculate red blood cell indices.
        MCV = (Hct × 10) / RBC
        MCH = (Hgb × 10) / RBC
        MCHC = (Hgb × 100) / Hct
        """
        mcv = (hematocrit * 10) / rbc  # fL
        mch = (hemoglobin * 10) / rbc  # pg
        mchc = (hemoglobin * 100) / hematocrit  # g/dL

        # Classify anemia
        if mcv < 80:
            classification = "Microcytic (Iron deficiency, thalassemia)"
        elif mcv > 100:
            classification = "Macrocytic (B12/folate deficiency, liver disease)"
        else:
            classification = "Normocytic (Chronic disease, hemorrhage)"

        return {
            "mcv": round(mcv, 1),
            "mcv_unit": "fL",
            "mcv_status": "Low" if mcv < 80 else ("High" if mcv > 100 else "Normal"),
            "mch": round(mch, 1),
            "mch_unit": "pg",
            "mchc": round(mchc, 1),
            "mchc_unit": "g/dL",
            "anemia_type": classification,
        }

    @staticmethod
    def analyze_complete_cbc(
        wbc: float,
        rbc: float,
        hemoglobin: float,
        hematocrit: float,
        platelets: float,
        gender: Gender,
    ) -> Dict[str, any]:
        """Complete CBC with interpretation."""

        ranges = (
            CompleteCBCPanel.RANGES_MALE
            if gender == Gender.MALE
            else CompleteCBCPanel.RANGES_FEMALE
        )

        # Calculate indices
        indices = CompleteCBCPanel.calculate_indices(hemoglobin, rbc, hematocrit)

        # Interpret all values
        results = {
            "wbc": {
                "value": wbc,
                "status": ranges["wbc"].interpret(wbc).value,
                "unit": "10³/µL",
            },
            "rbc": {
                "value": rbc,
                "status": ranges["rbc"].interpret(rbc).value,
                "unit": "10⁶/µL",
            },
            "hemoglobin": {
                "value": hemoglobin,
                "status": ranges["hemoglobin"].interpret(hemoglobin).value,
                "unit": "g/dL",
            },
            "hematocrit": {
                "value": hematocrit,
                "status": ranges["hematocrit"].interpret(hematocrit).value,
                "unit": "%",
            },
            "platelets": {
                "value": platelets,
                "status": ranges["platelets"].interpret(platelets).value,
                "unit": "10³/µL",
            },
            "mcv": {
                "value": indices["mcv"],
                "status": indices["mcv_status"],
                "unit": "fL",
            },
            "mch": {"value": indices["mch"], "unit": "pg"},
            "mchc": {"value": indices["mchc"], "unit": "g/dL"},
        }

        # Check for anemia
        anemia = hemoglobin < ranges["hemoglobin"].min_val

        # Critical findings
        critical = []
        for test, data in results.items():
            if "Critical" in data["status"]:
                critical.append(f"{test.upper()}: {data['status']}")

        # Clinical interpretation
        interpretation = []
        if anemia:
            interpretation.append(f"Anemia present: {indices['anemia_type']}")
        if wbc > 11.0:
            interpretation.append("Leukocytosis - possible infection or inflammation")
        elif wbc < 4.5:
            interpretation.append("Leukopenia - possible bone marrow issue")
        if platelets < 150:
            interpretation.append("Thrombocytopenia - bleeding risk")
        elif platelets > 400:
            interpretation.append("Thrombocytosis - clotting risk")

        return {
            "test_date": datetime.now().strftime("%Y-%m-%d"),
            "patient_gender": gender.value,
            "results": results,
            "anemia_detected": anemia,
            "anemia_classification": indices["anemia_type"] if anemia else None,
            "critical_findings": critical,
            "requires_urgent_attention": len(critical) > 0,
            "clinical_interpretation": interpretation,
            "reference_ranges": {
                "hemoglobin": f"{ranges['hemoglobin'].min_val}-{ranges['hemoglobin'].max_val} {ranges['hemoglobin'].unit}",
                "hematocrit": f"{ranges['hematocrit'].min_val}-{ranges['hematocrit'].max_val} {ranges['hematocrit'].unit}",
            },
        }


class MetabolicPanel:
    """Comprehensive Metabolic Panel Analysis."""

    @staticmethod
    def calculate_egfr(creatinine: float, age: int, gender: Gender) -> Dict[str, any]:
        """
        Calculate eGFR using CKD-EPI 2021 equation (race-free).
        eGFR in mL/min/1.73m²
        """
        kappa = 0.7 if gender == Gender.FEMALE else 0.9
        alpha = -0.241 if gender == Gender.FEMALE else -0.302

        min_ratio = min(creatinine / kappa, 1.0)
        max_ratio = max(creatinine / kappa, 1.0)

        egfr = 142 * (min_ratio**alpha) * (max_ratio**-1.200)
        egfr *= 0.9938**age

        if gender == Gender.FEMALE:
            egfr *= 1.012

        # CKD Staging
        if egfr >= 90:
            stage = "G1 - Normal"
            risk = "Normal kidney function"
        elif egfr >= 60:
            stage = "G2 - Mildly decreased"
            risk = "Mild reduction in kidney function"
        elif egfr >= 45:
            stage = "G3a - Mild-Moderate"
            risk = "Mild to moderate reduction"
        elif egfr >= 30:
            stage = "G3b - Moderate-Severe"
            risk = "Moderate to severe reduction"
        elif egfr >= 15:
            stage = "G4 - Severe"
            risk = "Severe reduction - nephrology referral needed"
        else:
            stage = "G5 - Kidney Failure"
            risk = "Kidney failure - dialysis may be needed"

        return {
            "egfr": round(egfr, 1),
            "egfr_unit": "mL/min/1.73m²",
            "ckd_stage": stage,
            "risk_level": risk,
            "kidney_disease": egfr < 60,
            "requires_nephrology": egfr < 30,
            "creatinine_input": creatinine,
        }

    @staticmethod
    def calculate_anion_gap(
        sodium: float, chloride: float, bicarbonate: float
    ) -> Dict[str, any]:
        """
        Anion Gap = Na⁺ - (Cl⁻ + HCO₃⁻)
        Normal: 8-16 mEq/L
        """
        ag = sodium - (chloride + bicarbonate)

        if ag < 8:
            interpretation = "Low AG - Check for hypoalbuminemia"
            causes = ["Hypoalbuminemia", "Multiple myeloma", "Lithium toxicity"]
        elif ag <= 16:
            interpretation = "Normal AG"
            causes = []
        elif ag <= 20:
            interpretation = "Mildly elevated AG"
            causes = ["Lactic acidosis", "Early ketoacidosis"]
        else:
            interpretation = "High AG - Metabolic acidosis"
            causes = [
                "Diabetic ketoacidosis",
                "Lactic acidosis",
                "Renal failure",
                "Toxic ingestion (methanol, ethylene glycol)",
            ]

        return {
            "anion_gap": round(ag, 1),
            "unit": "mEq/L",
            "interpretation": interpretation,
            "elevated": ag > 16,
            "possible_causes": causes,
            "normal_range": "8-16 mEq/L",
        }

    @staticmethod
    def assess_glucose_diabetes(
        fasting_glucose: Optional[float] = None,
        hba1c: Optional[float] = None,
        random_glucose: Optional[float] = None,
    ) -> Dict[str, any]:
        """
        Comprehensive diabetes assessment.
        Criteria:
        - Normal: FPG <100, HbA1c <5.7%
        - Prediabetes: FPG 100-125, HbA1c 5.7-6.4%
        - Diabetes: FPG ≥126, HbA1c ≥6.5%, Random ≥200
        """
        status_fpg = None
        status_a1c = None
        status_random = None

        if fasting_glucose:
            if fasting_glucose < 100:
                status_fpg = "Normal"
            elif fasting_glucose < 126:
                status_fpg = "Prediabetes"
            else:
                status_fpg = "Diabetes"

        if hba1c:
            if hba1c < 5.7:
                status_a1c = "Normal"
            elif hba1c < 6.5:
                status_a1c = "Prediabetes"
            else:
                status_a1c = "Diabetes"

        if random_glucose:
            if random_glucose >= 200:
                status_random = "Diabetes"
            else:
                status_random = "Below diabetes threshold"

        # Overall diagnosis
        statuses = [s for s in [status_fpg, status_a1c, status_random] if s]
        if "Diabetes" in statuses:
            diagnosis = "Diabetes Mellitus"
            recommendation = (
                "Start diabetes management protocol, refer to endocrinologist"
            )
        elif "Prediabetes" in statuses:
            diagnosis = "Prediabetes"
            recommendation = "Lifestyle modification, repeat testing in 3-6 months"
        else:
            diagnosis = "Normal Glucose Metabolism"
            recommendation = "Continue routine screening"

        return {
            "diagnosis": diagnosis,
            "fasting_glucose": (
                {"value": fasting_glucose, "status": status_fpg}
                if fasting_glucose
                else None
            ),
            "hba1c": {"value": hba1c, "status": status_a1c} if hba1c else None,
            "random_glucose": (
                {"value": random_glucose, "status": status_random}
                if random_glucose
                else None
            ),
            "recommendation": recommendation,
            "criteria": {
                "normal_fpg": "<100 mg/dL",
                "prediabetes_fpg": "100-125 mg/dL",
                "diabetes_fpg": "≥126 mg/dL",
                "normal_hba1c": "<5.7%",
                "prediabetes_hba1c": "5.7-6.4%",
                "diabetes_hba1c": "≥6.5%",
            },
        }


class LipidProfile:
    """Complete lipid panel and cardiovascular risk."""

    @staticmethod
    def calculate_ldl(
        total_chol: float, hdl: float, triglycerides: float
    ) -> Dict[str, any]:
        """
        Friedewald equation: LDL = TC - HDL - (TG/5)
        Valid only if TG <400 mg/dL
        """
        if triglycerides > 400:
            return {
                "ldl": None,
                "error": "Friedewald equation invalid for TG >400 mg/dL",
                "recommendation": "Direct LDL measurement required",
            }

        ldl = total_chol - hdl - (triglycerides / 5.0)

        # Risk classification
        if ldl < 100:
            risk = "Optimal"
            level = RiskLevel.LOW
        elif ldl < 130:
            risk = "Near optimal"
            level = RiskLevel.BORDERLINE
        elif ldl < 160:
            risk = "Borderline high"
            level = RiskLevel.MODERATE
        elif ldl < 190:
            risk = "High"
            level = RiskLevel.HIGH
        else:
            risk = "Very high"
            level = RiskLevel.VERY_HIGH

        return {
            "ldl_cholesterol": round(ldl, 1),
            "unit": "mg/dL",
            "risk_category": risk,
            "risk_level": level.value,
            "treatment_threshold": ldl >= 190,
            "targets": {
                "optimal": "<100 mg/dL",
                "near_optimal": "100-129 mg/dL",
                "borderline": "130-159 mg/dL",
                "high": "160-189 mg/dL",
                "very_high": "≥190 mg/dL",
            },
        }

    @staticmethod
    def calculate_ratios(
        total_chol: float, hdl: float, ldl: float, triglycerides: float
    ) -> Dict[str, any]:
        """
        Calculate cardiovascular risk ratios.
        """
        tc_hdl = total_chol / hdl
        ldl_hdl = ldl / hdl
        tg_hdl = triglycerides / hdl

        # TC/HDL interpretation
        if tc_hdl < 3.5:
            tc_risk = "Low risk"
        elif tc_hdl < 5.0:
            tc_risk = "Moderate risk"
        else:
            tc_risk = "High risk"

        # TG/HDL (insulin resistance marker)
        if tg_hdl < 2.0:
            tg_risk = "Low insulin resistance"
        elif tg_hdl < 4.0:
            tg_risk = "Moderate insulin resistance"
        else:
            tg_risk = "High insulin resistance - evaluate for metabolic syndrome"

        return {
            "tc_hdl_ratio": round(tc_hdl, 2),
            "tc_hdl_risk": tc_risk,
            "ldl_hdl_ratio": round(ldl_hdl, 2),
            "tg_hdl_ratio": round(tg_hdl, 2),
            "tg_hdl_interpretation": tg_risk,
            "optimal_tc_hdl": "<3.5",
            "optimal_tg_hdl": "<2.0",
        }

    @staticmethod
    def complete_lipid_analysis(
        total_chol: float, hdl: float, triglycerides: float
    ) -> Dict[str, any]:
        """Full lipid panel with risk assessment."""

        ldl_result = LipidProfile.calculate_ldl(total_chol, hdl, triglycerides)

        if ldl_result.get("error"):
            return ldl_result

        ldl = ldl_result["ldl_cholesterol"]
        ratios = LipidProfile.calculate_ratios(total_chol, hdl, ldl, triglycerides)

        # Non-HDL cholesterol
        non_hdl = total_chol - hdl

        # HDL interpretation
        if hdl < 40:
            hdl_status = "Low - Increased CV risk"
        elif hdl < 60:
            hdl_status = "Acceptable"
        else:
            hdl_status = "High - Protective"

        # Triglycerides interpretation
        if triglycerides < 150:
            tg_status = "Normal"
        elif triglycerides < 200:
            tg_status = "Borderline high"
        elif triglycerides < 500:
            tg_status = "High"
        else:
            tg_status = "Very high - Pancreatitis risk"

        return {
            "test_date": datetime.now().strftime("%Y-%m-%d"),
            "lipid_values": {
                "total_cholesterol": {"value": total_chol, "unit": "mg/dL"},
                "ldl_cholesterol": {
                    "value": ldl,
                    "unit": "mg/dL",
                    "status": ldl_result["risk_category"],
                },
                "hdl_cholesterol": {
                    "value": hdl,
                    "unit": "mg/dL",
                    "status": hdl_status,
                },
                "triglycerides": {
                    "value": triglycerides,
                    "unit": "mg/dL",
                    "status": tg_status,
                },
                "non_hdl_cholesterol": {"value": round(non_hdl, 1), "unit": "mg/dL"},
            },
            "ratios": ratios,
            "cardiovascular_risk": ldl_result["risk_level"],
            "requires_treatment": ldl >= 190 or (ldl >= 130 and hdl < 40),
            "lifestyle_modifications_needed": ldl >= 130 or triglycerides >= 150,
            "recommendations": LipidProfile._get_recommendations(
                ldl, hdl, triglycerides
            ),
        }

    @staticmethod
    def _get_recommendations(ldl: float, hdl: float, tg: float) -> List[str]:
        recs = []
        if ldl >= 130:
            recs.append("Reduce saturated fat intake, increase fiber")
        if hdl < 40:
            recs.append("Increase physical activity, consider omega-3 supplementation")
        if tg >= 150:
            recs.append("Reduce simple carbohydrates and alcohol")
        if ldl >= 190:
            recs.append("Consider statin therapy - discuss with physician")
        if not recs:
            recs.append("Maintain current healthy lifestyle")
        return recs


class ThyroidPanel:
    """Thyroid function testing."""

    @staticmethod
    def analyze_thyroid(
        tsh: float, free_t4: Optional[float] = None, free_t3: Optional[float] = None
    ) -> Dict[str, any]:
        """
        Comprehensive thyroid analysis.
        TSH: 0.4-4.0 mIU/L
        Free T4: 0.8-1.8 ng/dL
        Free T3: 2.3-4.2 pg/mL
        """
        # TSH interpretation
        if tsh < 0.4:
            tsh_status = "Low"
        elif tsh <= 4.0:
            tsh_status = "Normal"
        elif tsh <= 10.0:
            tsh_status = "Mildly elevated"
        else:
            tsh_status = "Significantly elevated"

        diagnosis = "Unknown"
        severity = None

        if free_t4:
            if tsh > 4.0 and free_t4 < 0.8:
                diagnosis = "Primary Hypothyroidism"
                severity = "Overt"
            elif tsh > 4.0 and 0.8 <= free_t4 <= 1.8:
                diagnosis = "Subclinical Hypothyroidism"
                severity = "Subclinical"
            elif tsh < 0.4 and free_t4 > 1.8:
                diagnosis = "Primary Hyperthyroidism"
                severity = "Overt"
            elif tsh < 0.4 and 0.8 <= free_t4 <= 1.8:
                diagnosis = "Subclinical Hyperthyroidism"
                severity = "Subclinical"
            else:
                diagnosis = "Euthyroid (Normal)"
        else:
            if tsh > 4.0:
                diagnosis = "Possible Hypothyroidism - Free T4 needed"
            elif tsh < 0.4:
                diagnosis = "Possible Hyperthyroidism - Free T4 needed"
            else:
                diagnosis = "TSH Normal - No thyroid dysfunction"

        # Treatment recommendations
        if "Hypothyroidism" in diagnosis and severity == "Overt":
            treatment = "Levothyroxine replacement indicated"
        elif "Hypothyroidism" in diagnosis and severity == "Subclinical":
            treatment = "Monitor, consider treatment if TSH >10 or symptomatic"
        elif "Hyperthyroidism" in diagnosis:
            treatment = "Refer to endocrinology for anti-thyroid therapy"
        else:
            treatment = "No treatment needed, routine monitoring"

        result = {
            "test_date": datetime.now().strftime("%Y-%m-%d"),
            "tsh": {"value": tsh, "unit": "mIU/L", "status": tsh_status},
            "diagnosis": diagnosis,
            "severity": severity,
            "treatment_recommendation": treatment,
            "reference_ranges": {
                "tsh": "0.4-4.0 mIU/L",
                "free_t4": "0.8-1.8 ng/dL",
                "free_t3": "2.3-4.2 pg/mL",
            },
        }

        if free_t4:
            t4_status = (
                "Low" if free_t4 < 0.8 else ("High" if free_t4 > 1.8 else "Normal")
            )
            result["free_t4"] = {"value": free_t4, "unit": "ng/dL", "status": t4_status}

        if free_t3:
            t3_status = (
                "Low" if free_t3 < 2.3 else ("High" if free_t3 > 4.2 else "Normal")
            )
            result["free_t3"] = {"value": free_t3, "unit": "pg/mL", "status": t3_status}

        return result


class CardiovascularRisk:
    """10-year cardiovascular disease risk calculation."""

    @staticmethod
    def framingham_risk_score(
        age: int,
        gender: Gender,
        total_chol: float,
        hdl: float,
        systolic_bp: float,
        bp_treated: bool,
        smoker: bool,
        diabetes: bool,
    ) -> Dict[str, any]:
        """
        Simplified Framingham Risk Score.
        Estimates 10-year CVD risk.
        """
        if not 30 <= age <= 74:
            return {"error": "Age must be 30-74 for Framingham calculation"}

        points = 0

        # Age points
        if gender == Gender.MALE:
            if age < 35:
                points -= 2
            elif age < 40:
                points += 0
            elif age < 45:
                points += 1
            elif age < 50:
                points += 2
            elif age < 55:
                points += 3
            elif age < 60:
                points += 4
            elif age < 65:
                points += 5
            else:
                points += 6
        else:  # Female
            if age < 35:
                points -= 1
            elif age < 40:
                points += 0
            elif age < 45:
                points += 1
            elif age < 50:
                points += 2
            elif age < 55:
                points += 3
            elif age < 60:
                points += 4
            else:
                points += 5

        # Total cholesterol
        if total_chol < 160:
            points += 0
        elif total_chol < 200:
            points += 1
        elif total_chol < 240:
            points += 2
        elif total_chol < 280:
            points += 3
        else:
            points += 4

        # HDL
        if hdl < 35:
            points += 2
        elif hdl < 45:
            points += 1
        elif hdl >= 60:
            points -= 1

        # Blood pressure
        if systolic_bp < 120:
            points += 0
        elif systolic_bp < 130:
            points += 1
        elif systolic_bp < 140:
            points += 2
        elif systolic_bp < 160:
            points += 3
        else:
            points += 4

        if bp_treated:
            points += 2

        # Risk factors
        if smoker:
            points += 4
        if diabetes:
            points += 3

        # Convert to risk percentage (approximation)
        if points <= 0:
            risk = 1
        elif points <= 5:
            risk = 2 + points
        elif points <= 10:
            risk = 8 + ((points - 5) * 2)
        elif points <= 15:
            risk = 18 + ((points - 10) * 3)
        else:
            risk = min(30 + ((points - 15) * 4), 95)

        # Risk categorization
        if risk < 10:
            category = "Low Risk"
            action = "Lifestyle modifications"
        elif risk < 20:
            category = "Intermediate Risk"
            action = "Consider statin therapy, aggressive lifestyle changes"
        else:
            category = "High Risk"
            action = "Statin therapy recommended, intensive risk factor management"

        return {
            "ten_year_cvd_risk_percent": risk,
            "risk_category": category,
            "point_score": points,
            "recommended_action": action,
            "aspirin_candidate": risk >= 10,
            "statin_candidate": risk >= 7.5,
            "risk_factors": {
                "age": age,
                "smoking": smoker,
                "diabetes": diabetes,
                "hypertension": systolic_bp >= 140 or bp_treated,
                "dyslipidemia": total_chol >= 240 or hdl < 40,
            },
        }


# Example Usage
if __name__ == "__main__":
    print("=" * 70)
    print("CLINICAL LABORATORY ANALYSIS - DEMONSTRATION")
    print("=" * 70)

    # 1. Complete Blood Count
    print("\n1. COMPLETE BLOOD COUNT (CBC)")
    print("-" * 70)
    cbc = CompleteCBCPanel.analyze_complete_cbc(
        wbc=7.5,
        rbc=4.8,
        hemoglobin=14.2,
        hematocrit=42.0,
        platelets=250,
        gender=Gender.MALE,
    )

    print(f"Test Date: {cbc['test_date']}")
    print(f"Patient: {cbc['patient_gender']}")
    print(f"\nResults:")
    for test, data in list(cbc["results"].items())[:5]:
        print(f"  {test.upper()}: {data['value']} {data['unit']} - {data['status']}")

    if cbc["anemia_detected"]:
        print(f"\n⚠ Anemia Detected: {cbc['anemia_classification']}")

    if cbc["critical_findings"]:
        print(f"\n🚨 CRITICAL: {', '.join(cbc['critical_findings'])}")

    # 2. Kidney Function
    print("\n2. KIDNEY FUNCTION (eGFR)")
    print("-" * 70)
    kidney = MetabolicPanel.calculate_egfr(
        creatinine=1.2,
        age=55,
        gender=Gender.MALE,
        total_chol=220,
        hdl=45,
        systolic_bp=145,
        bp_treated=True,
        smoker=False,
        diabetes=False,
    )

    print(f"10-Year CVD Risk: {cv_risk['ten_year_cvd_risk_percent']}%")
    print(f"Risk Category: {cv_risk['risk_category']}")
    print(f"Point Score: {cv_risk['point_score']}")
    print(f"\nRecommended Action: {cv_risk['recommended_action']}")
    print(
        f"Aspirin Therapy: {'Recommended' if cv_risk['aspirin_candidate'] else 'Not indicated'}"
    )
    print(
        f"Statin Therapy: {'Recommended' if cv_risk['statin_candidate'] else 'Not indicated'}"
    )

    print(f"\nRisk Factors Present:")
    for factor, present in cv_risk["risk_factors"].items():
        if present and isinstance(present, bool):
            print(f"  ✓ {factor.replace('_', ' ').title()}")

    print("\n" + "=" * 70)
    print("LABORATORY ANALYSIS COMPLETE")
    print("=" * 70)
    print("\nNOTE: These results are for demonstration purposes.")
    print("Always consult with a healthcare provider for interpretation.")
