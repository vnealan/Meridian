import json
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class PersonalInfo:
    age: int
    gender: str
    height: float
    weight: float
    
    @property
    def bmi(self) -> float:
        return self.weight / ((self.height / 100) ** 2)

@dataclass
class DexaData:
    total_body_fat: float
    lean_mass: float
    fat_mass: float
    bone_density: float
    visceral_fat: float
    trunk_fat: float
    trunk_lean_mass: float
    leg_fat: float
    leg_lean_mass: float
    arm_fat: float
    arm_lean_mass: float

@dataclass
class Vo2MaxData:
    max_vo2: float
    anaerobic_threshold: float
    max_heart_rate: int
    recovery_rate: int
    vt1: int
    vt2: int
    max_speed: float
    time_to_exhaustion: float

@dataclass
class DietData:
    calories: int
    protein: float
    carbs: float
    fat: float
    fiber: float
    water_intake: float
    caffeine_intake: float
    recommendations: List[str]

@dataclass
class PhysioData:
    fms_total: int
    foot_strike: str
    cadence: int
    vulnerabilities: List[str]
    recommendations: List[str]

@dataclass
class StrengthData:
    squat_1rm: float
    deadlift_1rm: float
    bench_1rm: float
    max_pullups: int

@dataclass
class BloodworkData:
    total_cholesterol: float
    hdl: float
    ldl: float
    triglycerides: float
    testosterone: float
    hba1c: float
    fasting_glucose: float
    vitamin_d: float
    b12: float
    ferritin: float

class HealthAssessment:
    def __init__(self, data_file: str):
        with open(data_file, 'r') as f:
            self.raw_data = json.load(f)
        
        self.personal = self._parse_personal()
        self.dexa = self._parse_dexa()
        self.vo2 = self._parse_vo2()
        self.diet = self._parse_diet()
        self.physio = self._parse_physio()
        self.strength = self._parse_strength()
        self.blood = self._parse_blood()
        
    def _parse_personal(self) -> PersonalInfo:
        d = self.raw_data['personalInfo']
        return PersonalInfo(
            age=d['age'],
            gender=d['gender'],
            height=d['height'],
            weight=d['weight']
        )
    
    def _parse_dexa(self) -> DexaData:
        d = self.raw_data['dexaScan']
        r = d['regionаlData']
        return DexaData(
            total_body_fat=d['totalBodyFatPercentage'],
            lean_mass=d['leanMass'],
            fat_mass=d['fatMass'],
            bone_density=d['boneMineralDensity'],
            visceral_fat=d['visceralFat'],
            trunk_fat=r['trunk']['fatPercentage'],
            trunk_lean_mass=r['trunk']['leanMass'],
            leg_fat=r['legs']['fatPercentage'],
            leg_lean_mass=r['legs']['leanMass'],
            arm_fat=r['arms']['fatPercentage'],
            arm_lean_mass=r['arms']['leanMass']
        )
    
    def _parse_vo2(self) -> Vo2MaxData:
        d = self.raw_data['vo2MaxTest']
        return Vo2MaxData(
            max_vo2=d['maxVO2'],
            anaerobic_threshold=d['anaerobicThreshold'],
            max_heart_rate=d['maxHeartRate'],
            recovery_rate=d['recoveryRate'],
            vt1=d['ventillatoryThreshold']['vt1'],
            vt2=d['ventillatoryThreshold']['vt2'],
            max_speed=d['maxSpeed'],
            time_to_exhaustion=d['timeToExhaustion']
        )
    
    def _parse_diet(self) -> DietData:
        d = self.raw_data['dietAssessment']
        i = d['averageDailyIntake']
        return DietData(
            calories=i['calories'],
            protein=i['protein'],
            carbs=i['carbohydrates'],
            fat=i['fat'],
            fiber=i['fiber'],
            water_intake=d['hydration']['waterIntake'],
            caffeine_intake=d['hydration']['caffeineIntake'],
            recommendations=d['recommendedChanges']
        )
    
    def _parse_physio(self) -> PhysioData:
        d = self.raw_data['physioAssessment']
        return PhysioData(
            fms_total=d['functionalMovementScreen']['total'],
            foot_strike=d['runningGait']['footStrike'],
            cadence=d['runningGait']['cadence'],
            vulnerabilities=d['vulnerabilities'],
            recommendations=d['recommendations']
        )
    
    def _parse_strength(self) -> StrengthData:
        d = self.raw_data['strengthAssessment']
        return StrengthData(
            squat_1rm=d['squat']['oneRepMax'],
            deadlift_1rm=d['deadlift']['oneRepMax'],
            bench_1rm=d['benchPress']['oneRepMax'],
            max_pullups=d['pullUps']['maxReps']
        )
    
    def _parse_blood(self) -> BloodworkData:
        d = self.raw_data['bloodPanel']
        return BloodworkData(
            total_cholesterol=d['lipids']['totalCholesterol'],
            hdl=d['lipids']['hdl'],
            ldl=d['lipids']['ldl'],
            triglycerides=d['lipids']['triglycerides'],
            testosterone=d['hormones']['totalTestosterone'],
            hba1c=d['glycemicControl']['hba1c'],
            fasting_glucose=d['glycemicControl']['fastingGlucose'],
            vitamin_d=d['vitaminsAndMinerals']['vitaminD'],
            b12=d['vitaminsAndMinerals']['vitaminB12'],
            ferritin=d['vitaminsAndMinerals']['ferritin']
        )

    def generate_summary(self) -> Dict[str, str]:
        """Generate a high-level summary of key health metrics"""
        return {
            "body_composition": f"Body fat: {self.dexa.total_body_fat}%, Lean mass: {self.dexa.lean_mass}kg",
            "fitness_level": f"VO2 Max: {self.vo2.max_vo2} ml/kg/min",
            "strength_profile": f"Squat: {self.strength.squat_1rm}kg, Deadlift: {self.strength.deadlift_1rm}kg",
            "metabolic_health": f"HbA1c: {self.blood.hba1c}%, Fasting glucose: {self.blood.fasting_glucose} mmol/L",
            "nutrition": f"Daily calories: {self.diet.calories}, Protein: {self.diet.protein}g"
        }
