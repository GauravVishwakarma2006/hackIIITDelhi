import unittest
from app.main import app
from fastapi.testclient import TestClient

class TestConversationalFlow(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.loc = {"lat": 28.5445, "lng": 77.2725}

    def test_emergency_flow_and_clean_subsequent_messages(self):
        # 1. Critical Emergency Trigger
        r1 = self.client.post("/triage", json={
            "user_input": "seene me tez dard hai aur paseena aa raha hai",
            "language": "auto",
            "location": self.loc,
            "conversation_history": []
        })
        self.assertEqual(r1.status_code, 200)
        d1 = r1.json()
        self.assertEqual(d1["care_type"], "emergency_112")
        self.assertEqual(d1["urgency"], "emergency")

        # 2. First aid / waiting advice while waiting for ambulance
        r2 = self.client.post("/triage", json={
            "user_input": "ambulance aane tak kya karein, what should I do while waiting",
            "language": "auto",
            "location": self.loc,
            "conversation_history": []
        })
        self.assertEqual(r2.status_code, 200)
        d2 = r2.json()
        self.assertEqual(d2["care_type"], "emergency_112")
        self.assertIn("First-Aid", d2["reasoning"])

        # 3. Question about giving water
        r3 = self.client.post("/triage", json={
            "user_input": "can I give him water or paani",
            "language": "auto",
            "location": self.loc,
            "conversation_history": []
        })
        self.assertEqual(r3.status_code, 200)
        d3 = r3.json()
        self.assertEqual(d3["care_type"], "emergency_112")

        # 4. Acknowledgment
        r4 = self.client.post("/triage", json={
            "user_input": "theek hai, dhanyawad",
            "language": "auto",
            "location": self.loc,
            "conversation_history": []
        })
        self.assertEqual(r4.status_code, 200)
        d4 = r4.json()
        self.assertEqual(d4["care_type"], "teleconsultation")

        # 5. Subsequent inquiry for Papa's fever (MUST NOT be emergency!)
        r5 = self.client.post("/triage", json={
            "user_input": "mere papa ko 2 din se bukhar aur khansi hai",
            "language": "auto",
            "location": self.loc,
            "conversation_history": []
        })
        self.assertEqual(r5.status_code, 200)
        d5 = r5.json()
        self.assertEqual(d5["care_type"], "paramedic_home_visit")
        self.assertEqual(d5["urgency"], "same_day")
        self.assertGreater(len(d5["matched_caregivers"]), 0)

        # 6. Subsequent inquiry for injection (MUST NOT be emergency!)
        r6 = self.client.post("/triage", json={
            "user_input": "Doctor prescribed injection, ghar pe lagwana hai",
            "language": "auto",
            "location": self.loc,
            "conversation_history": []
        })
        self.assertEqual(r6.status_code, 200)
        d6 = r6.json()
        self.assertEqual(d6["care_type"], "home_nursing")
        self.assertEqual(d6["urgency"], "same_day")

        # 7. Subsequent inquiry for blood test (MUST NOT be emergency!)
        r7 = self.client.post("/triage", json={
            "user_input": "khoon ki jaanch karwani hai, full body checkup sample collection",
            "language": "auto",
            "location": self.loc,
            "conversation_history": []
        })
        self.assertEqual(r7.status_code, 200)
        d7 = r7.json()
        self.assertEqual(d7["care_type"], "lab_test_home")
        self.assertNotEqual(d7["urgency"], "emergency")

if __name__ == "__main__":
    unittest.main()
