import json 
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, time

@dataclass
class PrescriptionMed:
    name: str
    brand_name: str
    dosage: str
    unit: str
    frequency: str
    timing: str
    purpose: str
    instructions: str
    prescribed_by: str
    start_date: datetime
    review_date: datetime

@dataclass
class Supplement:
    name: str
    dosage: str
    unit: str
    frequency: str
    timing: str
    purpose: str
    instructions: str

@dataclass
class AsNeededMed:
    name: str
    brand_name: str
    dosage: str
    unit: str
    max_frequency: str
    purpose: str
    instructions: str
    contraindications: Optional[str]

@dataclass
class ScheduleTime:
    time: time
    medications: List[str]

@dataclass
class Monitoring:
    required_tests: List[Dict[str, str]]
    side_effects_to_watch: List[str]

class MedicationRegimen:
    def __init__(self, json_file_path: str):
        """Initialize with path to JSON file"""
        with open(json_file_path, 'r') as f:
            self.raw_data = json.load(f)["medications"]

        # Parse each section
        self.prescription_meds = self._parse_prescription_meds()
        self.supplements = self._parse_supplements()
        self.as_needed = self._parse_as_needed()
        self.schedule = self._parse_schedule()
        self.monitoring = self._parse_monitoring()
        
        # Create lookup for easy access
        self._create_med_lookup()

    def _parse_prescription_meds(self) -> List[PrescriptionMed]:
        meds = []
        for med in self.raw_data["prescriptionMeds"]:
            meds.append(PrescriptionMed(
                name=med["name"],
                brand_name=med["brandName"],
                dosage=med["dosage"],
                unit=med["unit"],
                frequency=med["frequency"],
                timing=med["timing"],
                purpose=med["purpose"],
                instructions=med["instructions"],
                prescribed_by=med["prescribedBy"],
                start_date=datetime.strptime(med["startDate"], "%Y-%m-%d"),
                review_date=datetime.strptime(med["reviewDate"], "%Y-%m-%d")
            ))
        return meds

    def _parse_supplements(self) -> List[Supplement]:
        supps = []
        for supp in self.raw_data["supplements"]:
            supps.append(Supplement(
                name=supp["name"],
                dosage=supp["dosage"],
                unit=supp["unit"],
                frequency=supp["frequency"],
                timing=supp["timing"],
                purpose=supp["purpose"],
                instructions=supp["instructions"]
            ))
        return supps

    def _parse_as_needed(self) -> List[AsNeededMed]:
        meds = []
        for med in self.raw_data["asNeeded"]:
            meds.append(AsNeededMed(
                name=med["name"],
                brand_name=med["brandName"],
                dosage=med["dosage"],
                unit=med["unit"],
                max_frequency=med["maxFrequency"],
                purpose=med["purpose"],
                instructions=med["instructions"],
                contraindications=med.get("contraindications")
            ))
        return meds

    def _parse_schedule(self) -> Dict[str, ScheduleTime]:
        schedule = {}
        for time_of_day, details in self.raw_data["schedule"].items():
            schedule[time_of_day] = ScheduleTime(
                time=datetime.strptime(details["time"], "%H:%M").time(),
                medications=details["medications"]
            )
        return schedule

    def _parse_monitoring(self) -> Monitoring:
        mon = self.raw_data["monitoring"]
        return Monitoring(
            required_tests=mon["requiredTests"],
            side_effects_to_watch=mon["sideEffectsToWatch"]
        )

    def _create_med_lookup(self):
        """Creates a lookup dictionary for quick access to medication details by name"""
        self.med_lookup = {}
        
        # Add prescription meds
        for med in self.prescription_meds:
            self.med_lookup[med.name] = {
                "type": "prescription",
                "details": med
            }
        
        # Add supplements
        for supp in self.supplements:
            self.med_lookup[supp.name] = {
                "type": "supplement",
                "details": supp
            }
        
        # Add as-needed meds
        for med in self.as_needed:
            self.med_lookup[med.name] = {
                "type": "as_needed",
                "details": med
            }

    def get_medication_details(self, med_name: str) -> Optional[Dict]:
        """Get details for a specific medication by name"""
        return self.med_lookup.get(med_name)

    def get_medications_by_time(self, time_of_day: str) -> List[Dict]:
        """Get all medications scheduled for a specific time of day"""
        if time_of_day not in self.schedule:
            return []
        
        meds = []
        for med_name in self.schedule[time_of_day].medications:
            med_details = self.get_medication_details(med_name)
            if med_details:
                meds.append(med_details)
        return meds

    def get_upcoming_reviews(self, days: int = 30) -> List[Dict]:
        """Get medications with upcoming review dates within specified days"""
        upcoming = []
        today = datetime.now()
        for med in self.prescription_meds:
            days_until_review = (med.review_date - today).days
            if 0 <= days_until_review <= days:
                upcoming.append({
                    "name": med.name,
                    "review_date": med.review_date,
                    "days_until_review": days_until_review
                })
        return upcoming

    def generate_daily_schedule(self) -> List[Dict]:
        """Generate a chronological daily medication schedule"""
        schedule_items = []
        for time_slot, details in self.schedule.items():
            meds = self.get_medications_by_time(time_slot)
            schedule_items.append({
                "time": details.time,
                "time_slot": time_slot,
                "medications": meds
            })
        return sorted(schedule_items, key=lambda x: x["time"])

    def get_daily_summary(self) -> Dict:
        """
        Generate a comprehensive summary of all medications for today.
        Returns a structured dictionary with timing, medications, and important notes.
        """
        summary = {
            "total_medications": 0,
            "schedule": {},
            "monitoring": {
                "upcoming_reviews": [],
                "side_effects_to_watch": self.monitoring.side_effects_to_watch
            },
            "totals": {
                "prescription_meds": len(self.prescription_meds),
                "supplements": len(self.supplements),
                "as_needed_available": len(self.as_needed)
            }
        }

        # Get today's date for review checking
        today = datetime.now()

        # Check for upcoming reviews in next 7 days
        for med in self.prescription_meds:
            days_until_review = (med.review_date - today).days
            if 0 <= days_until_review <= 7:
                summary["monitoring"]["upcoming_reviews"].append({
                    "medication": med.name,
                    "review_date": med.review_date.strftime("%Y-%m-%d"),
                    "days_until_review": days_until_review
                })

        # Organize medications by time slot
        for time_slot, schedule in self.schedule.items():
            meds_at_time = self.get_medications_by_time(time_slot)
            if meds_at_time:
                summary["schedule"][time_slot] = {
                    "time": schedule.time.strftime("%H:%M"),
                    "medications": []
                }
                
                for med in meds_at_time:
                    med_details = med["details"]
                    med_info = {
                        "name": med_details.name,
                        "dosage": f"{med_details.dosage}{med_details.unit}",
                        "instructions": med_details.instructions,
                        "type": med["type"]
                    }
                    summary["schedule"][time_slot]["medications"].append(med_info)
                    summary["total_medications"] += 1

        # Add as-needed medications separately
        summary["as_needed_medications"] = [{
            "name": med.name,
            "dosage": f"{med.dosage}{med.unit}",
            "max_frequency": med.max_frequency,
            "instructions": med.instructions,
            "purpose": med.purpose
        } for med in self.as_needed]

        # Add important instructions
        summary["important_notes"] = []
        
        # Add notes about timing conflicts
        for med in self.prescription_meds:
            if med.instructions.lower().startswith("take on empty stomach"):
                summary["important_notes"].append(
                    f"{med.name}: Must be taken on empty stomach"
                )
        
        # Add notes about medications requiring special handling
        for med in [*self.prescription_meds, *self.supplements]:
            if "with food" in med.instructions.lower():
                summary["important_notes"].append(
                    f"{med.name}: Must be taken with food"
                )

        return summary

    def get_daily_summary_string(self):
        """
        Return a formatted daily medication summary as a string
        
        Returns:
            str: Formatted medication summary
        """
        summary = self.get_daily_summary()
        output = []
        
        output.append("=== DAILY MEDICATION SUMMARY ===")
        output.append(f"\nTotal medications to take today: {summary['total_medications']}")
        
        output.append("\n--- SCHEDULE ---")
        for time_slot, details in summary["schedule"].items():
            output.append(f"\n{time_slot.upper()} - {details['time']}")
            for med in details["medications"]:
                output.append(f"  • {med['name']} - {med['dosage']}")
                output.append(f"    Instructions: {med['instructions']}")
        
        if summary["as_needed_medications"]:
            output.append("\n--- AS NEEDED MEDICATIONS ---")
            for med in summary["as_needed_medications"]:
                output.append(f"  • {med['name']} - {med['dosage']}")
                output.append(f"    Max frequency: {med['max_frequency']}")
                output.append(f"    Purpose: {med['purpose']}")
        
        if summary["monitoring"]["upcoming_reviews"]:
            output.append("\n--- UPCOMING MEDICATION REVIEWS ---")
            for review in summary["monitoring"]["upcoming_reviews"]:
                output.append(f"  • {review['medication']}: Due in {review['days_until_review']} days")
        
        if summary["important_notes"]:
            output.append("\n--- IMPORTANT NOTES ---")
            for note in summary["important_notes"]:
                output.append(f"  • {note}")
        
        output.append("\n--- MEDICATION TOTALS ---")
        output.append(f"  • Prescription medications: {summary['totals']['prescription_meds']}")
        output.append(f"  • Supplements: {summary['totals']['supplements']}")
        output.append(f"  • As-needed medications available: {summary['totals']['as_needed_available']}")
        
        # Join all lines with newline characters
        return "\n".join(output)

    def print_daily_summary(self):
        """
        Print the formatted daily medication summary to console
        """
        print(self.get_daily_summary_string())