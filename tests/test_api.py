"""
Automated Evaluation Suite for CareCompass API.
Tests:
1. Multilingual Smart Intake (Hinglish, English)
2. Follow-up Dialogue Generation
3. Zero-Tolerance Red-Flag Emergency Recall
4. Nursing / Paramedic / GP Classification
5. Caregiver Geodesic Ranking & Reasoning
"""

import unittest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestCareCompassAPI(unittest.TestCase):

    def test_health_endpoint(self):
        res = client.get("/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "healthy")

    def test_red_flag_emergency_recall(self):
        """Zero tolerance test: Chest pain must trigger emergency with 108 ambulance guidance."""
        payload = {
            "user_input": "seene me tez dard ho raha hai aur saans phool rahi hai",
            "language": "auto",
            "location": {"lat": 28.54, "lng": 77.27},
            "conversation_history": []
        }
        res = client.post("/api/v1/triage", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["care_type"], "emergency")
        self.assertEqual(data["urgency"], "immediate")
        self.assertGreater(len(data["red_flags"]), 0)
        self.assertIn("108", data["reasoning"])
        # Red flags must skip caregiver matching
        self.assertEqual(len(data["matched_caregivers"]), 0)

    def test_hinglish_follow_up_inquiry(self):
        """Initial brief fever and cough must ask targeted clinical question."""
        payload = {
            "user_input": "papa ko do din se bukhar hai aur khansi bhi",
            "language": "auto",
            "location": {"lat": 28.54, "lng": 77.27},
            "conversation_history": []
        }
        res = client.post("/api/v1/triage", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsNotNone(data["follow_up_question"])
        self.assertIn("saans", data["follow_up_question"].lower())

    def test_paramedic_home_visit_after_followup(self):
        """After answering follow-up (no breathing difficulty), should recommend paramedic home visit for elderly."""
        payload = {
            "user_input": "nahi saans me koi dikkat nahi hai bas bukhar hai",
            "language": "auto",
            "location": {"lat": 28.5445, "lng": 77.2725},
            "conversation_history": [
                {"role": "user", "content": "papa ko do din se bukhar hai aur khansi bhi"},
                {"role": "assistant", "content": "Kya unko saans lene me koi dikkat ho rahi hai?"}
            ]
        }
        res = client.post("/api/v1/triage", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsNone(data["follow_up_question"])
        self.assertIn(data["care_type"], ["paramedic_home_visit", "gp_teleconsult"])
        self.assertEqual(data["urgency"], "same_day")
        self.assertGreater(len(data["matched_caregivers"]), 0)
        # Check caregiver score and reason
        top_cg = data["matched_caregivers"][0]
        self.assertGreater(top_cg["score"], 0.7)
        self.assertTrue(len(top_cg["reason"]) > 10)

    def test_nursing_wound_care(self):
        """Wound care and injection should route to nurse with same_day urgency."""
        payload = {
            "user_input": "dadi ke pair me ghav hai aur dressing karni hai",
            "language": "auto",
            "location": {"lat": 28.54, "lng": 77.27},
            "conversation_history": [
                {"role": "user", "content": "dadi ke pair me ghav hai"},
                {"role": "assistant", "content": "Ghav se khoon to nahi nikal raha?"}
            ]
        }
        res = client.post("/api/v1/triage", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["care_type"], "nurse")
        self.assertEqual(data["urgency"], "same_day")
        self.assertGreater(len(data["matched_caregivers"]), 0)


if __name__ == "__main__":
    unittest.main()
