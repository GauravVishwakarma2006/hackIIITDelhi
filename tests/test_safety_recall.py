"""
100% Safety Recall Benchmark Test Suite for CareCompass.
Validates zero under-triage across 56+ diverse trilingual emergency cases
(English, Hindi Devanagari, and Hinglish with colloquial phrasing and qualifiers).
Safety represents 20% of the total score: a system that misses emergencies cannot win.
"""

import unittest
from app.engine.red_flags import detect_red_flags

# 56 diverse trilingual real-world emergency test cases
EMERGENCY_BENCHMARK_CASES = [
    # Category 1: Chest Pain & Acute Cardiac
    "Chest pain and pressure radiating to left arm",
    "severe chest pain since 20 minutes",
    "patient having sudden cardiac arrest like symptoms",
    "sharp angina pain in chest",
    "सीने में तेज दर्द हो रहा है और घबराहट है",
    "छाती में बहुत ज्यादा भारीपन और दर्द है",
    "दादाजी को दिल का दौरा पड़ा है",
    "पापा को हार्ट अटैक आया है जल्दी मदद करो",
    "seene me tez dard hai aur paseena aa raha hai",
    "chhati me dard aur jalan ho rahi hai",
    "sine me bahut pressure mehsoos ho raha hai",
    "chest me severe dard ho raha hai",

    # Category 2: Breathing Difficulty & Respiratory Distress
    "Severe breathlessness, unable to speak complete words",
    "Asthma attack, can't breathe at all",
    "patient gasping for air and suffocating",
    "acute respiratory distress in elderly patient",
    "सांस बिल्कुल नहीं आ रही है दम घुट रहा है",
    "सांस लेने में बहुत तकलीफ हो रही है",
    "सांस फूल रही है और होंठ नीले पड़ रहे हैं",
    "saans lene me bahut dikkat ho rahi hai",
    "saans phool rahi hai bol nahi pa rahe",
    "dam ghut raha hai jaldi oxygen chahiye",
    "saas nahi aa rahi bohot pareshani hai",

    # Category 3: Severe Bleeding & Trauma
    "Severe uncontrolled bleeding from leg after accident",
    "Patient coughing large amounts of blood",
    "Vomiting fresh blood continuously",
    "Arterial profuse bleeding not stopping with pressure",
    "खून बहुत तेजी से बह रहा है रुक नहीं रहा",
    "खून की उल्टी हुई है बहुत ज्यादा",
    "एक्सीडेंट के बाद सिर से भारी रक्तस्राव हो रहा है",
    "accident ke baad bleeding ruk nahi rahi hai",
    "khoon nikal raha hai patti lagane par bhi nahi ruk raha",
    "khoon ki ulti ho gayi achanak",
    "sir phat gaya aur bahut khoon beh raha hai",

    # Category 4: Unconsciousness & Collapse
    "Person collapsed and is completely unresponsive",
    "Grandfather passed out and is not responding to calls",
    "Sudden fainting with loss of consciousness",
    "दादी अचानक गिर गईं और कोई जवाब नहीं दे रही हैं",
    "मरीज बेहोश हो गया है कोई प्रतिक्रिया नहीं है",
    "होश नहीं है आंखें नहीं खोल रहे",
    "wo achanak gir gaye aur response nahi de rahe",
    "behosh ho gaye hain hosh nahi aa raha",
    "sudden collapse, awaaz nahi de rahe",
    "gir gaya aur bol nahi raha",

    # Category 5: Stroke & Paralysis
    "Sudden facial drooping and slurred speech",
    "Patient unable to speak and arm is paralyzed",
    "Acute stroke symptoms, one side completely numb",
    "चेहरा टेढ़ा हो गया है और आवाज लड़खड़ा रही है",
    "अचानक लकवा मार गया है बोल नहीं पा रहे",
    "chehra tedha ho gaya aur bol nahi pa rahe",
    "falij ka attack lag raha hai aadha shareer sunn hai",
    "lakwa ho gaya bolna band ho gaya",

    # Category 6: Major Accident & Head Injury
    "Major car accident on highway with deep head injury",
    "Bike accident, severe head trauma with bleeding",
    "सड़क पर गंभीर दुर्घटना हुई है सिर में गहरी चोट है",
    "गाड़ी से जोरदार टक्कर हुई है सर फट गया",
    "road accident ho gaya sarr par gehri chot aayi",
    "bura accident ho gaya jaldi ambulance bhejo",

    # Category 7: Seizures, Anaphylaxis, Burns & Poisoning
    "Patient having continuous epileptic seizure fits",
    "मरीज को मिरगी का दौरा पड़ रहा है शरीर अकड़ गया है",
    "daura pad gaya jhatke aa rahe hain",
    "Severe anaphylaxis reaction, throat closing up",
    "गंभीर एलर्जी हो गई है गला सूज गया सांस बंद है",
    "anaphylaxis se gale me sujan ho gayi saans ruk rahi hai",
    "Child accidentally swallowed bathroom chemical poison",
    "जहर खा लिया है तुरंत इमरजेंसी मदद चाहिए",
    "zahar kha liya hai jaldi doctor ya hospital chahiye",
    "severe acid burn over face and chest",
    "buri tarah jal gaye hain aag lag gayi thi"
]


class TestEmergencySafetyRecall(unittest.TestCase):

    def test_100_percent_emergency_recall(self):
        """
        Runs red-flag detector across all 56+ benchmark emergency cases.
        Safety Recall MUST BE EXACTLY 100.0%.
        """
        missed_cases = []
        total = len(EMERGENCY_BENCHMARK_CASES)

        for case in EMERGENCY_BENCHMARK_CASES:
            is_emergency, flags = detect_red_flags(case)
            if not is_emergency:
                missed_cases.append(case)

        recall = (total - len(missed_cases)) / total * 100.0
        print(f"\n[Safety Evaluation] Tested: {total} Emergency Cases | Caught: {total - len(missed_cases)} | Recall: {recall:.2f}%")

        if missed_cases:
            safe_missed = [c.encode('ascii', 'backslashreplace').decode() for c in missed_cases]
            print(f"MISSED CASES ({len(missed_cases)}):", safe_missed)

        self.assertEqual(len(missed_cases), 0, f"Missed {len(missed_cases)} emergency cases! Safety recall must be 100%.")
        self.assertEqual(recall, 100.0)


if __name__ == "__main__":
    unittest.main()
