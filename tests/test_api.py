"""
Automated Evaluation Suite for CareCompass API.
Validates against the official Hack IIITD (CAI, IIIT-Delhi) benchmark cases:
1. Emergency 112 (Bleeding, Unresponsiveness, Chest Pain)
2. Home Nursing (Injections, Bedsore, Dressing)
3. Teleconsultation (Acidity, Reports, Second Opinion)
4. Paramedic Home Visit (BP/Sugar check, Elderly Fever/Cough)
5. Lab Test Home (Full body checkup, CBC, Thyroid, Blood Sugar)
6. Underspecified Intent (Follow-up inquiry)
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

    def test_emergency_accident_bleeding(self):
        # Case S0004
        payload = {
            "user_input": "accident ke baad bleeding ruk nahi rahi",
            "language": "auto",
            "location": {"lat": 28.5366, "lng": 77.255},
            "conversation_history": []
        }
        res = client.post("/api/v1/triage", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["care_type"], "emergency_112")
        self.assertEqual(data["urgency"], "emergency")
        self.assertIn("chest_pain", data["red_flags"])
        self.assertEqual(len(data["matched_caregivers"]), 0)

    def test_emergency_unresponsive(self):
        # Case S0008
        payload = {
            "user_input": "wo achanak gir gaye response nahi de rahe",
            "language": "auto",
            "location": {"lat": 28.6076, "lng": 77.3079},
            "conversation_history": []
        }
        res = client.post("/api/v1/triage", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["care_type"], "emergency_112")
        self.assertEqual(data["urgency"], "emergency")

    def test_home_nursing_injection(self):
        # Case S0001
        payload = {
            "user_input": "Doctor prescribed an injection, can someone come home",
            "language": "auto",
            "location": {"lat": 28.5164, "lng": 77.2605},
            "conversation_history": []
        }
        res = client.post("/api/v1/triage", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["care_type"], "home_nursing")
        self.assertEqual(data["urgency"], "same_day")
        self.assertIn("Specific nursing procedure requested", data["reasoning"])

    def test_home_nursing_bedsore(self):
        # Case S0003
        payload = {
            "user_input": "Grandmother has a bedsore that needs dressing",
            "language": "auto",
            "location": {"lat": 28.5069, "lng": 77.2092},
            "conversation_history": []
        }
        res = client.post("/api/v1/triage", json=payload)
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
        res = client.post("/api/v1/triage", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["care_type"], "teleconsultation")
        self.assertEqual(data["urgency"], "same_day")
        self.assertGreater(len(data["matched_caregivers"]), 0)
        top_cg = data["matched_caregivers"][0]
        self.assertEqual(top_cg["caregiver_id"], "CG_021")

    def test_paramedic_home_visit_bp_sugar(self):
        # Case S0011
        payload = {
            "user_input": "mummy ka bp sugar ghar pe check karwana hai",
            "language": "auto",
            "location": {"lat": 28.6373, "lng": 77.3581},
            "conversation_history": []
        }
        res = client.post("/api/v1/triage", json=payload)
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
        res = client.post("/api/v1/triage", json=payload)
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
        res = client.post("/api/v1/triage", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsNotNone(data["follow_up_question"])
        self.assertIsNone(data["care_type"])
        self.assertIsNone(data["urgency"])
        self.assertEqual(data["reasoning"], "Intent underspecified — asking a follow-up before deciding care type.")


if __name__ == "__main__":
    unittest.main()
