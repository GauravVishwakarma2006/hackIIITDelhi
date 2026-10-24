"""
Automated Evaluation Suite for CareCompass API.
Validates against the official Hack IIITD (CAI, IIIT-Delhi) benchmark cases & rubric:
1. Emergency 112 (Bleeding, Unresponsiveness, Chest Pain, 0 Caregivers matched)
2. Home Nursing (Injections, Bedsore, Dressing, same_day urgency)
3. Teleconsultation (Acidity, Reports, Second Opinion)
4. Paramedic Home Visit (BP/Sugar check, Elderly Fever/Cough)
5. Lab Test Home (Full body checkup, CBC, Thyroid, Blood Sugar, scheduled urgency)
6. Underspecified Intent (Follow-up inquiry at root)
7. Vulnerability Escalation (Isolation & prolonged symptoms)
8. Root /triage contract adherence
"""

import unittest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestCareCompassOfficialBenchmarks(unittest.TestCase):

    def test_health_check(self):
        res = client.get("/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "healthy")

    def test_endpoint_aliasing(self):
        # Both /triage and /api/v1/triage must work
        payload = {
            "user_input": "seene me tez dard ho raha hai",
            "language": "auto",
            "location": {"lat": 28.5445, "lng": 77.2725},
            "conversation_history": []
        }
        res1 = client.post("/triage", json=payload)
        res2 = client.post("/api/v1/triage", json=payload)
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res1.json()["care_type"], res2.json()["care_type"])

    def test_emergency_chest_pain(self):
        payload = {
            "user_input": "seene me tez dard hai aur chakkar aa raha hai",
            "language": "auto",
            "location": {"lat": 28.5366, "lng": 77.255},
            "conversation_history": []
        }
        res = client.post("/triage", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsNone(data["follow_up_question"])
        self.assertEqual(data["care_type"], "emergency_112")
        self.assertEqual(data["urgency"], "emergency")
        self.assertIn("chest_pain", data["red_flags"])
        self.assertEqual(len(data["matched_caregivers"]), 0)
        self.assertIn("112", data["reasoning"])

    def test_emergency_accident_bleeding(self):
        # Case S0004
        payload = {
            "user_input": "accident ke baad bleeding ruk nahi rahi",
            "language": "auto",
            "location": {"lat": 28.5366, "lng": 77.255},
            "conversation_history": []
        }
        res = client.post("/triage", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["care_type"], "emergency_112")
        self.assertEqual(data["urgency"], "emergency")
        self.assertTrue(any(f in ["severe_bleeding", "severe_trauma"] for f in data["red_flags"]))
        self.assertEqual(len(data["matched_caregivers"]), 0)

    def test_emergency_unresponsive(self):
        # Case S0008
        payload = {
            "user_input": "wo achanak gir gaye response nahi de rahe",
            "language": "auto",
            "location": {"lat": 28.6076, "lng": 77.3079},
            "conversation_history": []
        }
        res = client.post("/triage", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["care_type"], "emergency_112")
        self.assertEqual(data["urgency"], "emergency")
        self.assertIn("unconsciousness", data["red_flags"])
        self.assertEqual(len(data["matched_caregivers"]), 0)

    def test_home_nursing_injection(self):
        # Case S0001
        payload = {
            "user_input": "Doctor prescribed an injection, can someone come home",
            "language": "auto",
            "location": {"lat": 28.5164, "lng": 77.2605},
            "conversation_history": []
        }
        res = client.post("/triage", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["care_type"], "home_nursing")
        self.assertEqual(data["urgency"], "same_day")
        self.assertIn("nursing procedure", data["reasoning"].lower())

    def test_home_nursing_bedsore(self):
        # Case S0003
        payload = {
            "user_input": "Grandmother has a bedsore that needs dressing",
            "language": "auto",
            "location": {"lat": 28.5069, "lng": 77.2092},
            "conversation_history": []
        }
        res = client.post("/triage", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["care_type"], "home_nursing")
        self.assertEqual(data["urgency"], "same_day")
        self.assertGreater(len(data["matched_caregivers"]), 0)
        top_cg = data["matched_caregivers"][0]
        self.assertIn("CG_", top_cg["caregiver_id"])

    def test_teleconsultation_acidity(self):
        # Case S0002
        payload = {
            "user_input": "Mild acidity and gas since morning, want to consult a doctor",
            "language": "auto",
            "location": {"lat": 28.4605, "lng": 77.0883},
            "conversation_history": []
        }
        res = client.post("/triage", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["care_type"], "teleconsultation")
        self.assertEqual(data["urgency"], "same_day")
        self.assertGreater(len(data["matched_caregivers"]), 0)
        top_cg = data["matched_caregivers"][0]
        self.assertIn("CG_", top_cg["caregiver_id"])
        self.assertEqual(top_cg["role"], "doctor")

    def test_paramedic_home_visit_bp_sugar(self):
        # Case S0011
        payload = {
            "user_input": "mummy ka bp sugar ghar pe check karwana hai",
            "language": "auto",
            "location": {"lat": 28.6373, "lng": 77.3581},
            "conversation_history": []
        }
        res = client.post("/triage", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["care_type"], "paramedic_home_visit")
        self.assertEqual(data["urgency"], "same_day")
        self.assertGreater(len(data["matched_caregivers"]), 0)

    def test_lab_test_home_checkup(self):
        # Case S0012
        payload = {
            "user_input": "Book a full body checkup, home collection",
            "language": "auto",
            "location": {"lat": 28.6027, "lng": 77.0489},
            "conversation_history": []
        }
        res = client.post("/triage", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["care_type"], "lab_test_home")
        self.assertEqual(data["urgency"], "scheduled")
        self.assertGreater(len(data["matched_caregivers"]), 0)

    def test_underspecified_follow_up(self):
        # Case S0014
        payload = {
            "user_input": "I want to book something for my mother",
            "language": "auto",
            "location": {"lat": 28.6499, "lng": 77.3536},
            "conversation_history": []
        }
        res = client.post("/triage", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsNotNone(data["follow_up_question"])
        self.assertIsNone(data["care_type"])
        self.assertIsNone(data["urgency"])
        self.assertEqual(data["reasoning"], "Intent underspecified — asking a follow-up before deciding care type.")
        self.assertEqual(len(data["matched_caregivers"]), 0)

    def test_vulnerability_escalation(self):
        payload = {
            "user_input": "Ghar pe akela hoon, uth nahi pa raha aur chakkar aa raha hai",
            "language": "auto",
            "location": {"lat": 28.5445, "lng": 77.2725},
            "conversation_history": []
        }
        res = client.post("/triage", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn(data["urgency"], ["same_day", "emergency"])
        self.assertIn("vulnerability", data["reasoning"].lower())

    def test_non_health_query_math_equation(self):
        # Math queries like "2 + 2" or "quaderatic equation" must NOT give clinical assessment
        test_inputs = [
            "2 + 2",
            "quaderatic equation",
            "quadratic equation",
            "solve x^2 + 5x + 6 = 0",
            "write python code for calculator",
            "who is the president of france"
        ]
        for query in test_inputs:
            payload = {
                "user_input": query,
                "language": "auto",
                "location": {"lat": 28.5445, "lng": 77.2725},
                "conversation_history": []
            }
            res = client.post("/triage", json=payload)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertIsNotNone(data["follow_up_question"], f"Failed for {query}")
            self.assertIsNone(data["care_type"], f"care_type should be None for {query}")
            self.assertIsNone(data["urgency"], f"urgency should be None for {query}")
    def test_heart_attack_typos_always_emergency(self):
        # Heart attack misspellings (heart attck, hart attack, heart failure) must ALWAYS be emergency_112, NEVER teleconsultation
        typo_queries = [
            "heart attck",
            "heart attack",
            "heartattack",
            "heart attak",
            "hart attack",
            "hart attck",
            "heart failure",
            "severe chest",
            "cant breathe",
            "breath problem"
        ]
        for query in typo_queries:
            payload = {
                "user_input": query,
                "language": "auto",
                "location": {"lat": 28.5445, "lng": 77.2725},
                "conversation_history": []
            }
            res = client.post("/triage", json=payload)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["care_type"], "emergency_112", f"Expected emergency_112 for '{query}' but got {data['care_type']}")
            self.assertEqual(data["urgency"], "emergency", f"Expected emergency urgency for '{query}' but got {data['urgency']}")
            self.assertEqual(len(data["matched_caregivers"]), 0, f"Expected 0 caregivers for emergency '{query}'")


if __name__ == "__main__":
    unittest.main()

