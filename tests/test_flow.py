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

    def test_family_proxy_mode_routing_and_reasoning(self):
        # Patient is in Janakpuri, guardian/messenger is reporting from Saket (~15 km away)
        patient_loc = {"lat": 28.6219, "lng": 77.0878}
        messenger_loc = {"lat": 28.5244, "lng": 77.2066}

        res = self.client.post("/triage", json={
            "user_input": "Mere dada ji ko ghar par injection aur dressing karwani hai",
            "language": "auto",
            "location": patient_loc,
            "proxy_mode": True,
            "messenger_location": messenger_loc,
            "conversation_history": []
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["care_type"], "home_nursing")
        self.assertIn("Family Proxy", data["reasoning"])
        self.assertIn("guardian reporting from", data["reasoning"])
        self.assertGreater(len(data["matched_caregivers"]), 0)

    def test_network_ip_location_endpoint(self):
        res = self.client.get("/api/v1/network/ip-location")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("lat", data)
        self.assertIn("lng", data)
        self.assertIn("area", data)

    def test_observer_mode_welfare_dispatch(self):
        # 1. Observer distress report (e.g., neighbor/guard reporting locked door)
        res1 = self.client.post("/triage", json={
            "user_input": "Dadi darwaza nahi khol rahi hain aur phone nahi utha rahi hain, padosi reporting",
            "language": "auto",
            "location": self.loc,
            "observer_mode": True,
            "conversation_history": []
        })
        self.assertEqual(res1.status_code, 200)
        d1 = res1.json()
        self.assertEqual(d1["care_type"], "paramedic_home_visit")
        self.assertEqual(d1["urgency"], "emergency")
        self.assertIn("observer_welfare_alert", d1["red_flags"])

        # 2. Observer mode reporting home nursing request for elder
        res2 = self.client.post("/triage", json={
            "user_input": "Elderly neighbor needs wound dressing assistance, guard assisting",
            "language": "auto",
            "location": self.loc,
            "observer_mode": True,
            "conversation_history": []
        })
        self.assertEqual(res2.status_code, 200)
        d2 = res2.json()
        self.assertEqual(d2["care_type"], "home_nursing")
        self.assertIn("Observer Mode", d2["reasoning"])

    def test_continuous_learning_and_correction_recall(self):
        # Unique test query
        custom_query = "special elder routine checkup and blood pressure reading test"
        
        # 1. Post feedback to teach the system a verified correction
        feedback_res = self.client.post("/api/v1/feedback", json={
            "user_input": custom_query,
            "predicted_care_type": "teleconsultation",
            "predicted_urgency": "same_day",
            "rating": "thumbs_down",
            "suggested_care_type": "paramedic_home_visit",
            "comment": "Patient is elderly and bedridden; vitals check must be done at home by paramedic",
            "observer_mode": False
        })
        self.assertEqual(feedback_res.status_code, 200)
        fb_data = feedback_res.json()
        self.assertTrue(fb_data["learned"])

        # 2. Subsequent inquiry with the exact same query MUST recall the learned correction!
        recall_res = self.client.post("/triage", json={
            "user_input": custom_query,
            "language": "auto",
            "location": self.loc,
            "conversation_history": []
        })
        self.assertEqual(recall_res.status_code, 200)
        rec_data = recall_res.json()
        self.assertEqual(rec_data["care_type"], "paramedic_home_visit")
        self.assertIn("Continuous Learning", rec_data["reasoning"])

    def test_feedback_insights_endpoint(self):
        res = self.client.get("/api/v1/feedback/insights")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_feedbacks", data)
        self.assertIn("learned_corrections_count", data)
        self.assertGreaterEqual(data["total_feedbacks"], 1)

if __name__ == "__main__":
    unittest.main()
