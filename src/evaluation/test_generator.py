# evaluation/test_generator.py
import json
import random
from typing import List, Dict
from pathlib import Path

class TestCaseGenerator:
    def __init__(self):
        self.chapter_scenarios = {
            1: {
                "name": "Emergencies and Trauma",
                "scenarios": [
                    {
                        "condition": "acute MI",
                        "symptoms": "chest pain, sweating, shortness of breath",
                        "urgency": "immediate"
                    },
                    {
                        "condition": "polytrauma",
                        "symptoms": "multiple injuries, bleeding, unconscious",
                        "urgency": "immediate"
                    },
                    {
                        "condition": "status epilepticus",
                        "symptoms": "continuous seizures, altered consciousness",
                        "urgency": "immediate"
                    },
                    {
                        "condition": "anaphylaxis",
                        "symptoms": "difficulty breathing, rash, swelling",
                        "urgency": "immediate"
                    }
                ]
            },
            2: {
                "name": "Infectious Diseases",
                "scenarios": [
                    {
                        "condition": "severe malaria",
                        "symptoms": "fever, convulsions, altered consciousness",
                        "urgency": "immediate"
                    },
                    {
                        "condition": "bacterial meningitis",
                        "symptoms": "fever, neck stiffness, headache",
                        "urgency": "immediate"
                    },
                    {
                        "condition": "tuberculosis",
                        "symptoms": "chronic cough, weight loss, night sweats",
                        "urgency": "urgent"
                    }
                ]
            },
            3: {
                "name": "HIV/AIDS and STIs",
                "scenarios": [
                    {
                        "condition": "new HIV diagnosis",
                        "symptoms": "weight loss, recurring infections",
                        "urgency": "urgent"
                    },
                    {
                        "condition": "PMTCT",
                        "symptoms": "pregnant HIV positive patient",
                        "urgency": "urgent"
                    }
                ]
            },
            4: {
                "name": "Cardiovascular Diseases",
                "scenarios": [
                    {
                        "condition": "hypertensive emergency",
                        "symptoms": "severe headache, visual disturbance, very high BP",
                        "urgency": "immediate"
                    },
                    {
                        "condition": "heart failure",
                        "symptoms": "shortness of breath, peripheral edema",
                        "urgency": "urgent"
                    }
                ]
            },
            5: {
                "name": "Respiratory Diseases",
                "scenarios": [
                    {
                        "condition": "severe asthma",
                        "symptoms": "severe breathlessness, unable to speak",
                        "urgency": "immediate"
                    },
                    {
                        "condition": "pneumonia",
                        "symptoms": "fever, cough, fast breathing",
                        "urgency": "urgent"
                    }
                ]
            },
            6: {
                "name": "Gastrointestinal and Hepatic Diseases",
                "scenarios": [
                    {
                        "condition": "acute gastroenteritis",
                        "symptoms": "severe diarrhea, vomiting, dehydration",
                        "urgency": "urgent"
                    },
                    {
                        "condition": "upper GI bleeding",
                        "symptoms": "hematemesis, melena",
                        "urgency": "immediate"
                    }
                ]
            },
            7: {
                "name": "Renal and Urinary Diseases",
                "scenarios": [
                    {
                        "condition": "acute kidney injury",
                        "symptoms": "decreased urine output, confusion",
                        "urgency": "urgent"
                    },
                    {
                        "condition": "urinary tract infection",
                        "symptoms": "dysuria, frequency, fever",
                        "urgency": "routine"
                    }
                ]
            },
            8: {
                "name": "Endocrine and Metabolic Disorders",
                "scenarios": [
                    {
                        "condition": "diabetic ketoacidosis",
                        "symptoms": "polyuria, polydipsia, confusion",
                        "urgency": "immediate"
                    },
                    {
                        "condition": "thyroid storm",
                        "symptoms": "fever, tachycardia, agitation",
                        "urgency": "immediate"
                    }
                ]
            },
            9: {
                "name": "Mental, Neurological and Substance Use Disorders",
                "scenarios": [
                    {
                        "condition": "acute psychosis",
                        "symptoms": "hallucinations, agitation, aggression",
                        "urgency": "immediate"
                    },
                    {
                        "condition": "severe depression",
                        "symptoms": "suicidal ideation, social withdrawal",
                        "urgency": "urgent"
                    }
                ]
            },
            10: {
                "name": "Musculoskeletal Conditions",
                "scenarios": [
                    {
                        "condition": "septic arthritis",
                        "symptoms": "hot swollen joint, fever",
                        "urgency": "urgent"
                    },
                    {
                        "condition": "acute back pain",
                        "symptoms": "severe pain, neurological symptoms",
                        "urgency": "urgent"
                    }
                ]
            },
            11: {
                "name": "Blood Diseases",
                "scenarios": [
                    {
                        "condition": "severe anemia",
                        "symptoms": "shortness of breath, fatigue, pallor",
                        "urgency": "urgent"
                    },
                    {
                        "condition": "sickle cell crisis",
                        "symptoms": "severe pain, fever",
                        "urgency": "immediate"
                    }
                ]
            },
            12: {
                "name": "Oncology",
                "scenarios": [
                    {
                        "condition": "neutropenic sepsis",
                        "symptoms": "fever, chills in cancer patient",
                        "urgency": "immediate"
                    },
                    {
                        "condition": "spinal cord compression",
                        "symptoms": "back pain, neurological symptoms",
                        "urgency": "immediate"
                    }
                ]
            },
            13: {
                "name": "Palliative Care",
                "scenarios": [
                    {
                        "condition": "terminal pain",
                        "symptoms": "severe pain, distress",
                        "urgency": "urgent"
                    },
                    {
                        "condition": "terminal dyspnea",
                        "symptoms": "severe breathlessness, anxiety",
                        "urgency": "urgent"
                    }
                ]
            },
            14: {
                "name": "Gynecological Conditions",
                "scenarios": [
                    {
                        "condition": "ectopic pregnancy",
                        "symptoms": "acute abdominal pain, vaginal bleeding",
                        "urgency": "immediate"
                    },
                    {
                        "condition": "severe PID",
                        "symptoms": "pelvic pain, fever",
                        "urgency": "urgent"
                    }
                ]
            },
            15: {
                "name": "Family Planning",
                "scenarios": [
                    {
                        "condition": "contraception counseling",
                        "symptoms": "seeking family planning advice",
                        "urgency": "routine"
                    },
                    {
                        "condition": "IUD complications",
                        "symptoms": "pelvic pain, bleeding",
                        "urgency": "urgent"
                    }
                ]
            },
            16: {
                "name": "Obstetric Conditions",
                "scenarios": [
                    {
                        "condition": "severe pre-eclampsia",
                        "symptoms": "headache, high BP, proteinuria",
                        "urgency": "immediate"
                    },
                    {
                        "condition": "postpartum hemorrhage",
                        "symptoms": "excessive bleeding after delivery",
                        "urgency": "immediate"
                    }
                ]
            },
            17: {
                "name": "Childhood Illness",
                "scenarios": [
                    {
                        "condition": "severe pneumonia",
                        "symptoms": "fast breathing, chest indrawing",
                        "urgency": "immediate"
                    },
                    {
                        "condition": "severe malnutrition",
                        "symptoms": "edema, severe wasting",
                        "urgency": "urgent"
                    }
                ]
            },
            18: {
                "name": "Immunization",
                "scenarios": [
                    {
                        "condition": "routine vaccination",
                        "symptoms": "healthy child visit",
                        "urgency": "routine"
                    },
                    {
                        "condition": "vaccination side effects",
                        "symptoms": "fever, local reaction",
                        "urgency": "routine"
                    }
                ]
            },
            19: {
                "name": "Nutrition",
                "scenarios": [
                    {
                        "condition": "severe acute malnutrition",
                        "symptoms": "severe wasting, edema",
                        "urgency": "urgent"
                    },
                    {
                        "condition": "micronutrient deficiency",
                        "symptoms": "weakness, pallor",
                        "urgency": "routine"
                    }
                ]
            },
            20: {
                "name": "Eye Conditions",
                "scenarios": [
                    {
                        "condition": "acute glaucoma",
                        "symptoms": "severe eye pain, red eye",
                        "urgency": "immediate"
                    },
                    {
                        "condition": "chemical eye injury",
                        "symptoms": "eye pain, redness after exposure",
                        "urgency": "immediate"
                    }
                ]
            },
            21: {
                "name": "Ear, Nose & Throat Conditions",
                "scenarios": [
                    {
                        "condition": "peritonsillar abscess",
                        "symptoms": "severe sore throat, difficulty swallowing",
                        "urgency": "urgent"
                    },
                    {
                        "condition": "foreign body airway",
                        "symptoms": "choking, difficulty breathing",
                        "urgency": "immediate"
                    }
                ]
            },
            22: {
                "name": "Skin Diseases",
                "scenarios": [
                    {
                        "condition": "severe cellulitis",
                        "symptoms": "spreading redness, fever",
                        "urgency": "urgent"
                    },
                    {
                        "condition": "stevens-johnson syndrome",
                        "symptoms": "widespread rash, mucosal involvement",
                        "urgency": "immediate"
                    }
                ]
            },
            23: {
                "name": "Oral and Dental Conditions",
                "scenarios": [
                    {
                        "condition": "dental abscess",
                        "symptoms": "severe tooth pain, facial swelling",
                        "urgency": "urgent"
                    },
                    {
                        "condition": "acute gingivitis",
                        "symptoms": "bleeding gums, pain",
                        "urgency": "routine"
                    }
                ]
            },
            24: {
                "name": "Surgery, Radiology and Anaesthesia",
                "scenarios": [
                    {
                        "condition": "acute appendicitis",
                        "symptoms": "right lower abdominal pain, fever",
                        "urgency": "urgent"
                    },
                    {
                        "condition": "bowel obstruction",
                        "symptoms": "severe abdominal pain, vomiting",
                        "urgency": "immediate"
                    }
                ]
            }
        }
        
        self.evaluation_criteria = [
            {
                "name": "medical_accuracy",
                "description": "Accuracy of medical information and adherence to UCG 2023",
                "evaluation_type": "factual",
                "scale": {"type": "numeric", "min": 0, "max": 1},
                "rubric": {
                    "1.0": "Perfect adherence to UCG 2023 guidelines with all key points covered",
                    "0.8": "Minor omissions but clinically accurate",
                    "0.6": "Some important elements missing",
                    "0.4": "Significant omissions or inaccuracies",
                    "0.2": "Major errors present",
                    "0.0": "Completely incorrect or dangerous advice"
                }
            },
            {
                "name": "resource_consideration",
                "description": "Consideration of local resource constraints and alternatives",
                "evaluation_type": "contextual",
                "scale": {"type": "numeric", "min": 0, "max": 1},
                "rubric": {
                    "1.0": "Excellent consideration of resource constraints with alternatives",
                    "0.8": "Good consideration of local resources",
                    "0.6": "Basic consideration of resources",
                    "0.4": "Limited resource consideration",
                    "0.2": "Poor resource awareness",
                    "0.0": "No consideration of resources"
                }
            },
            {
                "name": "guideline_adherence",
                "description": "Adherence to specific UCG 2023 protocols and citations",
                "evaluation_type": "factual",
                "scale": {"type": "numeric", "min": 0, "max": 1},
                "rubric": {
                    "1.0": "Perfect adherence with proper citations",
                    "0.8": "Strong adherence with minor deviations",
                    "0.6": "Moderate adherence to guidelines",
                    "0.4": "Poor adherence to guidelines",
                    "0.2": "Minimal guideline consideration",
                    "0.0": "No adherence to guidelines"
                }
            },
            {
                "name": "completeness",
                "description": "Completeness of response including all necessary steps",
                "evaluation_type": "factual",
                "scale": {"type": "numeric", "min": 0, "max": 1},
                "rubric": {
                    "1.0": "All necessary steps included in proper order",
                    "0.8": "Most steps included with proper prioritization",
                    "0.6": "Key steps included but some missing",
                    "0.4": "Important steps missing",
                    "0.2": "Many critical steps missing",
                    "0.0": "Incomplete or missing critical information"
                }
            },
            {
                "name": "clinical_urgency",
                "description": "Appropriate recognition and response to clinical urgency",
                "evaluation_type": "factual",
                "scale": {"type": "numeric", "min": 0, "max": 1},
                "rubric": {
                    "1.0": "Perfect urgency recognition and response",
                    "0.8": "Good urgency recognition",
                    "0.6": "Basic urgency recognition",
                    "0.4": "Poor urgency recognition",
                    "0.2": "Missed urgency signals",
                    "0.0": "No urgency consideration"
                }
            },
{
                "name": "referral_appropriateness",
                "description": "Appropriate referral decisions and timing",
                "evaluation_type": "contextual",
                "scale": {"type": "numeric", "min": 0, "max": 1},
                "rubric": {
                    "1.0": "Perfect referral decisions with clear criteria",
                    "0.8": "Appropriate referral considerations",
                    "0.6": "Basic referral guidance",
                    "0.4": "Unclear referral criteria",
                    "0.2": "Inappropriate referral decisions",
                    "0.0": "Missing critical referral information"
                }
            },
            {
                "name": "cultural_appropriateness",
                "description": "Consideration of local cultural context and practices",
                "evaluation_type": "contextual",
                "scale": {"type": "numeric", "min": 0, "max": 1},
                "rubric": {
                    "1.0": "Excellent cultural sensitivity and local context",
                    "0.8": "Good cultural awareness",
                    "0.6": "Basic cultural consideration",
                    "0.4": "Limited cultural awareness",
                    "0.2": "Poor cultural consideration",
                    "0.0": "Culturally inappropriate"
                }
            },
            {
                "name": "communication_clarity",
                "description": "Clarity and accessibility of medical instructions",
                "evaluation_type": "contextual",
                "scale": {"type": "numeric", "min": 0, "max": 1},
                "rubric": {
                    "1.0": "Crystal clear, actionable instructions",
                    "0.8": "Clear and well-structured",
                    "0.6": "Generally clear but some ambiguity",
                    "0.4": "Significant clarity issues",
                    "0.2": "Confusing or unclear",
                    "0.0": "Incomprehensible"
                }
            },
            {
                "name": "follow_up_planning",
                "description": "Appropriate follow-up and monitoring plans",
                "evaluation_type": "contextual",
                "scale": {"type": "numeric", "min": 0, "max": 1},
                "rubric": {
                    "1.0": "Comprehensive follow-up plan with clear timelines",
                    "0.8": "Good follow-up guidance",
                    "0.6": "Basic follow-up mentioned",
                    "0.4": "Limited follow-up planning",
                    "0.2": "Inadequate follow-up",
                    "0.0": "No follow-up mentioned"
                }
            },
            {
                "name": "safety_considerations",
                "description": "Attention to patient safety and risk management",
                "evaluation_type": "factual",
                "scale": {"type": "numeric", "min": 0, "max": 1},
                "rubric": {
                    "1.0": "Excellent safety considerations and risk management",
                    "0.8": "Good safety awareness",
                    "0.6": "Basic safety considerations",
                    "0.4": "Limited safety awareness",
                    "0.2": "Poor safety consideration",
                    "0.0": "Missing critical safety elements"
                }
            }
        ]

    def generate_test_cases(self, num_cases: int = 100) -> List[Dict]:
        """Generate comprehensive test cases"""
        test_cases = []
        cases_per_chapter = max(2, num_cases // 24)  # At least 2 cases per chapter
        
        for chapter, content in self.chapter_scenarios.items():
            chapter_cases = self._generate_chapter_cases(
                chapter,
                content,
                cases_per_chapter
            )
            test_cases.extend(chapter_cases)
        
        # Add resource variations
        test_cases = self._add_resource_variations(test_cases)
        
        # Add complexity variations
        test_cases = self._add_complexity_variations(test_cases)
        
        return test_cases
    
    def _generate_chapter_cases(
        self,
        chapter: int,
        content: Dict,
        num_cases: int
    ) -> List[Dict]:
        """Generate cases for specific chapter with variations"""
        cases = []
        scenarios = content["scenarios"]
        
        for _ in range(num_cases):
            scenario = random.choice(scenarios)
            
            # Generate variations of the base scenario
            variations = self._generate_scenario_variations(scenario)
            
            for variation in variations:
                case = {
                    "id": f"CH{chapter:02d}_{len(cases):03d}",
                    "category": content["name"].lower().replace(" ", "_"),
                    "input": self._generate_question(variation),
                    "ideal": self._generate_ideal_response(chapter, variation),
                    "context": self._generate_context(variation),
                    "metadata": {
                        "chapter": chapter,
                        "urgency": variation["urgency"],
                        "resource_level": random.choice(["limited", "moderate", "standard"]),
                        "complexity": variation.get("complexity", "moderate")
                    }
                }
                cases.append(case)
        
        return cases
    
    def _generate_scenario_variations(self, base_scenario: Dict) -> List[Dict]:
        """Generate variations of a base scenario"""
        variations = [base_scenario.copy()]  # Include original scenario
        
        # Add complexity variations
        complexities = ["simple", "moderate", "complex"]
        for complexity in complexities:
            variation = base_scenario.copy()
            variation["complexity"] = complexity
            variations.append(variation)
        
        # Add comorbidity variations
        comorbidities = ["diabetes", "hypertension", "HIV", "pregnancy"]
        for comorbidity in comorbidities:
            variation = base_scenario.copy()
            variation["symptoms"] = f"{variation['symptoms']}, with {comorbidity}"
            variations.append(variation)
        
        return variations
    
    def _generate_question(self, scenario: Dict) -> str:
        """Generate varied clinical questions"""
        templates = [
            f"Patient presents with {scenario['symptoms']}. How do you manage {scenario['condition']}?",
            f"What is the immediate management for {scenario['condition']} presenting with {scenario['symptoms']}?",
            f"In a resource-limited setting, how would you handle {scenario['condition']} with {scenario['symptoms']}?",
            f"Given a patient with {scenario['symptoms']}, what is your approach to managing {scenario['condition']}?",
            f"What are the key steps in managing {scenario['condition']} when presenting with {scenario['symptoms']}?"
        ]
        return random.choice(templates)
    
    def save_to_jsonl(self, cases: List[Dict], output_path: str):
        """Save cases in JSONL format for OpenAI evaluation"""
        with open(output_path, 'w') as f:
            for case in cases:
                f.write(json.dumps(case) + '\n')
        
        # Also save evaluation criteria
        criteria_path = output_path.replace('.jsonl', '_criteria.json')
        with open(criteria_path, 'w') as f:
            json.dump(self.evaluation_criteria, f, indent=2)

# Usage example
if __name__ == "__main__":
    generator = TestCaseGenerator()
    
    # Generate comprehensive test set
    test_cases = generator.generate_test_cases(240)  # 10 cases per chapter
    
    # Save as JSONL for OpenAI evaluation
    generator.save_to_jsonl(test_cases, "uganda_healthcare_tests.jsonl")
    
    # Print summary
    print(f"Generated {len(test_cases)} test cases across {len(generator.chapter_scenarios)} chapters")
    print(f"Evaluation criteria: {len(generator.evaluation_criteria)} dimensions")