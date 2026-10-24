/**
 * CareCompass Client Application
 * Full Multilingual Internationalization (Hindi, Hinglish, English, Auto)
 * Handles voice transcription (webkitSpeechRecognition hi-IN / en-IN),
 * speech synthesis read-aloud (No-Download Grandparent UX),
 * family proxy reporting, WhatsApp 1-tap sharing, and async trauma desk discovery.
 */

// --- I18N MULTILINGUAL DICTIONARY ---
const I18N = {
  Hindi: {
    langCode: "hi",
    speechLang: "hi-IN",
    brandSubtitle: "एआई-संचालित बहुभाषी स्वास्थ्य मार्गदर्शन एवं सुरक्षा-प्रथम देखभालकर्ता मिलान",
    observerLabel: "👮‍♂️ ऑब्जर्वर मोड",
    observerTitle: "अकेले रहने वाले बुजुर्गों के लिए पड़ोसी या गार्ड द्वारा रिपोर्टिंग",
    proxyLabel: "👨‍👩‍👧 फैमिली प्रॉक्सी",
    patientLocationLabel: "मरीज़ का स्थान:",
    locationDetecting: "📍 आपका स्थान खोजा जा रहा है...",
    locationDefault: "📍 ओखला, नई दिल्ली · पुनः प्रयास करें",
    locationVerified: "(सत्यापित जीपीएस)",
    locationDefaultTag: "(डिफ़ॉल्ट)",
    refreshGPS: "जीपीएस रिफ्रेश करें",

    // Bento Scenarios
    scenarios: {
      1: {
        title: "पापा को बुखार व खांसी",
        sub: "वाइटल्स जांच और लक्षण स्पष्टता के साथ गृह सहायता संवाद।",
        tag: "पैरामेडिक होम विजिट",
        prompt: "पापा को दो दिन से बुखार है और खांसी भी"
      },
      2: {
        title: "सीने में दर्द व सांस फूलना",
        sub: "112 आपातकालीन सेवा के साथ त्वरित जीवन-रक्षा प्रोटोकॉल।",
        tag: "आपातकालीन 112",
        prompt: "पापा को तेज सीने में दर्द है और सांस नहीं आ रही"
      },
      3: {
        title: "गार्ड / पड़ोसी अलर्ट",
        sub: "बुजुर्ग दरवाजा नहीं खोल रहे। तत्काल वेलफेयर पैरामेडिक सहायता।",
        tag: "कल्याण सहायता",
        prompt: "दादी दरवाजा नहीं खोल रही हैं और फोन नहीं उठा रहीं, पड़ोसी रिपोर्टिंग"
      },
      4: {
        title: "इंजेक्शन व ड्रेसिंग",
        sub: "घर पर घाव की ड्रेसिंग, कैथेटर व इंजेक्शन सहायता।",
        tag: "होम नर्सिंग",
        prompt: "डॉक्टर ने इंजेक्शन और ड्रेसिंग लिखी है, क्या कोई घर आ सकता है"
      },
      5: {
        title: "घर से लैब टेस्ट",
        sub: "घर से रक्त जांच एवं स्वास्थ्य चेकअप सैंपल कलेक्शन।",
        tag: "लैब टेस्ट होम",
        prompt: "फुल बॉडी चेकअप और ब्लड टेस्ट के लिए होम कलेक्शन बुक करना है"
      }
    },

    // Left Panel
    intakeTitle: "अपनी समस्या या जरूरत बताएं",
    intakeSub: "हिंदी, हिंग्लिश या अंग्रेजी में बोलें अथवा लिखें",
    voiceReady: "🎙️ वॉइस-सक्षम",
    welcomeTitle: "नमस्ते! मैं CareCompass हूँ।",
    welcomeBody: "आपको या आपके परिवार में किसको क्या तकलीफ है? आप बोलकर या लिखकर आसानी से बता सकते हैं।",
    welcomeNote: "(सुरक्षा-प्रथम ट्राइएज एवं प्रमाणित देखभालकर्ता मिलान)",
    senderLocLabel: "मैसेज भेजने का स्थान:",
    detectGPSBtn: "जीपीएस पहचानें",
    inputPlaceholder: "बोलकर या लिखकर बताएं... (जैसे: पापा को बुखार और खांसी है)",
    inputPlaceholderObserver: "पड़ोसी या गार्ड रिपोर्ट: जैसे दादी दरवाजा नहीं खोल रहीं और फोन नहीं उठा रहीं...",
    sendBtn: "भेजें",
    micListening: "🎙️ सुन रहा हूँ... कृपया हिंदी में बोलना शुरू करें",
    micHeard: "सुना गया:",
    micError: "वॉइस इनपुट में त्रुटि। कृपया लिखकर संदेश भेजें।",
    micDefaultTitle: "बोलने के लिए क्लिक करें (हिंदी)",

    // Right Panel
    resultsTitle: "क्लिनिकल ट्राइएज एवं सहायक मिलान",
    resultsSub: "सुरक्षा-सत्यापित वर्गीकरण एवं प्रमाणित स्थानीय स्वास्थ्यकर्मी",
    emptyTitle: "स्वास्थ्य समस्या का विवरण प्रतीक्षित",
    emptySub: "बाईं ओर अपनी समस्या बताएं। CareCompass गंभीरता की जांच करेगा, आपातकालीन सुरक्षा सुनिश्चित करेगा और नजदीकी प्रमाणित देखभालकर्ताओं से जोड़ेगा।",
    assessmentTitle: "क्लिनिकल मूल्यांकन एवं कारण",
    readAloudBtn: "🔊 बोलकर सुनें",
    shareWhatsAppBtn: "💬 व्हाट्सएप पर परिवार से साझा करें",
    emergencyTitle: "आपातकालीन 112 प्रोटोकॉल सक्रिय",
    dispatch112Btn: "📞 112 राष्ट्रीय हेल्पलाइन",
    call108Btn: "🚑 108 एम्बुलेंस बुलाएं",
    emergencyShareBtn: "🚨 परिवार को व्हाट्सएप पर आपातकालीन अलर्ट भेजें",
    traumaHeader: "🏥 नजदीकी प्रमाणित 24x7 इमरजेंसी ट्रॉमा केंद्र (AIIMS व NCR नेटवर्क)",
    caregiversDeckLabel: "नजदीकी अनुशंसित स्वास्थ्यकर्मी (बहु-मानदंड स्कोर अनुसार)",
    matchScoreSuffix: "मिलान",
    bookBtn: "तुरंत बुक करें",

    // Booking Modal
    modalTitle: "✅ स्वास्थ्यकर्मी भेज दिया गया है",
    modalRoutedText: (name) => `आपका अनुरोध सफलतापूर्वक स्वास्थ्यकर्मी <strong>${name}</strong> को भेज दिया गया है।`,
    modalServiceLabel: "स्वास्थ्य सेवा:",
    modalSlotLabel: "उपलब्ध समय:",
    modalLocationLabel: "मरीज़ का स्थान:",
    modalNotice: "प्रमाणित देखभालकर्ता को आपका स्थान मिल गया है और वे आगमन की पुष्टि के लिए आपसे तुरंत संपर्क करेंगे।",
    modalDoneBtn: "पूर्ण",

    // Badges & Statuses
    careTypes: {
      emergency_112: "आपातकालीन 112",
      emergency: "आपातकालीन 112",
      paramedic_home_visit: "पैरामेडिक होम विजिट",
      home_nursing: "होम नर्सिंग",
      lab_test_home: "लैब टेस्ट होम",
      teleconsultation: "डॉक्टर टेली-परामर्श"
    },
    urgencies: {
      emergency: "गंभीरता: आपातकालीन (तुरंत)",
      same_day: "गंभीरता: आज ही",
      scheduled: "गंभीरता: निर्धारित समय"
    },
    roles: {
      medic: "पैरामेडिक (Medic)",
      nurse: "प्रमाणित नर्स (Nurse)",
      phlebotomist: "लैब तकनीशियन (Phlebotomist)",
      doctor: "डॉक्टर (Doctor)"
    },
    assessmentPrefix: "मूल्यांकन पूर्ण:",
    emergencyPrefix: "आपातकालीन चेतावनी:",
    networkError: "क्षमा करें, नेटवर्क में समस्या आई है। कृपया पुनः प्रयास करें।"
  },

  Hinglish: {
    langCode: "hi",
    speechLang: "hi-IN",
    brandSubtitle: "AI-Powered Multilingual Care Guidance & Safety-First Caregiver Matching",
    observerLabel: "👮‍♂️ Observer Mode",
    observerTitle: "Akela reh rahe buzurgon ke liye padosi ya guard reporting",
    proxyLabel: "👨‍👩‍👧 Family Proxy",
    patientLocationLabel: "Patient ka Location:",
    locationDetecting: "📍 Aapka location dhoonda ja raha hai...",
    locationDefault: "📍 Okhla, New Delhi · Retry karein",
    locationVerified: "(Verified GPS)",
    locationDefaultTag: "(Default)",
    refreshGPS: "GPS Refresh Karein",

    // Bento Scenarios
    scenarios: {
      1: {
        title: "Papa ko Bukhar & Khansi",
        sub: "Smart vitals check aur symptoms follow-up ke saath.",
        tag: "Paramedic Home Visit",
        prompt: "Papa ko do din se bukhar hai aur khansi bhi"
      },
      2: {
        title: "Chest Pain & Distress",
        sub: "112 emergency routing ke saath turant safety action.",
        tag: "Emergency 112",
        prompt: "Papa ko tez seene me dard hai aur saans nahi aa rahi"
      },
      3: {
        title: "Guard / Padosi Alert",
        sub: "Elderly door nahi khol rahe. Turant welfare paramedic dispatch.",
        tag: "Welfare Dispatch",
        prompt: "Dadi darwaza nahi khol rahi hain aur phone nahi utha rahi, padosi reporting"
      },
      4: {
        title: "Injection & Dressing",
        sub: "Ghar par wound dressing aur catheter care.",
        tag: "Home Nursing",
        prompt: "Doctor ne injection aur dressing likhi hai, kya koi ghar aa sakta hai"
      },
      5: {
        title: "Ghar se Lab Test Sample",
        sub: "Doorstep blood sample collection aur health checkup.",
        tag: "Lab Test Home",
        prompt: "Full body checkup aur blood test ke liye home collection chahiye"
      }
    },

    // Left Panel
    intakeTitle: "Apni Pareshani Batayein",
    intakeSub: "Hindi, Hinglish ya English me bolein ya likhein",
    voiceReady: "🎙️ Voice-Ready",
    welcomeTitle: "Namaste! Main CareCompass hoon.",
    welcomeBody: "Aap ya aapke parivar me kisko kya takleef hai? Aap bol kar ya likh kar bata sakte hain.",
    welcomeNote: "(Safety-first triage aur certified caregiver matching)",
    senderLocLabel: "Message bhejne ka location:",
    detectGPSBtn: "Detect GPS",
    inputPlaceholder: "Bol kar ya likh kar batayein... (e.g. Papa ko bukhar hai)",
    inputPlaceholderObserver: "Padosi ya guard reporting: e.g. Dadi darwaza nahi khol rahi hain...",
    sendBtn: "Bhejein",
    micListening: "🎙️ Sun raha hoon... Bolna shuru kijiye (Hindi / English)",
    micHeard: "Heard:",
    micError: "Voice input error. Kripya type karein.",
    micDefaultTitle: "Bolne ke liye click karein",

    // Right Panel
    resultsTitle: "Clinical Triage & Provider Match",
    resultsSub: "Safety-validated classification aur certified local providers",
    emptyTitle: "Symptom Inquiry ka Intezaar hai",
    emptySub: "Left me symptoms batayein. CareCompass severity check karega aur pass ke certified caregivers se jodega.",
    assessmentTitle: "Clinical Assessment & Reasoning",
    readAloudBtn: "🔊 Awaaz me sunein",
    shareWhatsAppBtn: "💬 WhatsApp par Family ko share karein",
    emergencyTitle: "EMERGENCY 112 PROTOCOL ACTIVATED",
    dispatch112Btn: "📞 112 Helpline Call Karein",
    call108Btn: "🚑 108 Ambulance Call Karein",
    emergencyShareBtn: "🚨 Family ko WhatsApp par Emergency Alert bhejein",
    traumaHeader: "🏥 Verified 24x7 Emergency Trauma Centers (AIIMS & NCR Network)",
    caregiversDeckLabel: "Recommended Providers Nearby (Multi-Criteria Score ke anusar)",
    matchScoreSuffix: "Match",
    bookBtn: "1-Tap Book Karein",

    // Booking Modal
    modalTitle: "✅ Provider Dispatch Ho Gaya",
    modalRoutedText: (name) => `Aapka care request <strong>${name}</strong> ko assign kar diya gaya hai.`,
    modalServiceLabel: "Care Service:",
    modalSlotLabel: "Available Slot:",
    modalLocationLabel: "Patient ka Location:",
    modalNotice: "Certified provider ko aapka location mil gaya hai aur woh confirm karne ke liye turant call karenge.",
    modalDoneBtn: "Done",

    // Badges & Statuses
    careTypes: {
      emergency_112: "EMERGENCY 112",
      emergency: "EMERGENCY 112",
      paramedic_home_visit: "PARAMEDIC HOME VISIT",
      home_nursing: "HOME NURSING",
      lab_test_home: "LAB TEST HOME",
      teleconsultation: "TELECONSULTATION"
    },
    urgencies: {
      emergency: "URGENCY: EMERGENCY (TURANT)",
      same_day: "URGENCY: SAME DAY (AAJ HI)",
      scheduled: "URGENCY: SCHEDULED (SAMAY ANUSAR)"
    },
    roles: {
      medic: "Paramedic Medic",
      nurse: "Certified Nurse",
      phlebotomist: "Lab Phlebotomist",
      doctor: "Doctor Teleconsult"
    },
    assessmentPrefix: "Assessment Complete:",
    emergencyPrefix: "Emergency Alert:",
    networkError: "Kshama karein, network error aayi hai. Kripya punah prayas karein."
  },

  English: {
    langCode: "en",
    speechLang: "en-IN",
    brandSubtitle: "AI-Powered Multilingual Care Navigation & Safety-First Caregiver Matching",
    observerLabel: "👮‍♂️ Observer Mode",
    observerTitle: "Neighbor or Guard reporting for isolated elderly",
    proxyLabel: "👨‍👩‍👧 Family Proxy",
    patientLocationLabel: "Patient Location:",
    locationDetecting: "📍 Detecting your location...",
    locationDefault: "📍 Okhla, New Delhi · Click to retry",
    locationVerified: "(Verified GPS)",
    locationDefaultTag: "(Default)",
    refreshGPS: "Refresh GPS",

    // Bento Scenarios
    scenarios: {
      1: {
        title: "Papa Fever & Cough",
        sub: "Hinglish dialogue intake with smart vitals check follow-up.",
        tag: "Paramedic Home Visit",
        prompt: "My father has had fever and cough for two days"
      },
      2: {
        title: "Chest Pain & Distress",
        sub: "Zero-tolerance red-flag trigger with 112 emergency routing.",
        tag: "Emergency 112",
        prompt: "Severe chest pain and difficulty breathing"
      },
      3: {
        title: "Guard / Observer Alert",
        sub: "Unresponsive elder, door locked. Immediate welfare paramedic dispatch.",
        tag: "Welfare Dispatch",
        prompt: "Elderly neighbor is not opening the door and not answering phone, neighbor reporting"
      },
      4: {
        title: "Injections & Dressing",
        sub: "Procedural wound dressing and catheter care at home.",
        tag: "Home Nursing",
        prompt: "Doctor prescribed an injection and dressing, can someone come home"
      },
      5: {
        title: "Home Lab Sample",
        sub: "Scheduled diagnostic phlebotomy with doorstep collection.",
        tag: "Lab Test Home",
        prompt: "Book a full body checkup, home collection"
      }
    },

    // Left Panel
    intakeTitle: "Describe What You Need",
    intakeSub: "Speak or type in Hindi, Hinglish, or English",
    voiceReady: "🎙️ Voice-Ready",
    welcomeTitle: "Hello! I am CareCompass.",
    welcomeBody: "Please describe what care or symptoms you need help with. You can type or speak.",
    welcomeNote: "(Safety-first triage and caregiver matching)",
    senderLocLabel: "Sending message from:",
    detectGPSBtn: "Detect GPS",
    inputPlaceholder: "Speak or type your health need... (e.g. Papa has fever and cough)",
    inputPlaceholderObserver: "Neighbor or guard reporting: e.g. Elder is not opening door and unresponsive...",
    sendBtn: "Send",
    micListening: "🎙️ Listening... Please speak in English",
    micHeard: "Heard:",
    micError: "Voice input error. Please type your message.",
    micDefaultTitle: "Click to speak (English)",

    // Right Panel
    resultsTitle: "Clinical Triage & Provider Match",
    resultsSub: "Safety-validated routing and ranked local providers",
    emptyTitle: "Awaiting Clinical Inquiry",
    emptySub: "Describe symptoms on the left. CareCompass will analyze severity, enforce red-flag safety, and match nearby certified caregivers.",
    assessmentTitle: "Clinical Assessment & Reasoning",
    readAloudBtn: "🔊 Read Aloud",
    shareWhatsAppBtn: "💬 Share with Family on WhatsApp",
    emergencyTitle: "EMERGENCY 112 PROTOCOL ACTIVATED",
    dispatch112Btn: "📞 Dispatch 112 Helpline",
    call108Btn: "🚑 Call 108 Ambulance",
    emergencyShareBtn: "🚨 Alert Family via WhatsApp",
    traumaHeader: "🏥 Verified 24x7 Emergency Trauma Centers Nearby (AIIMS & NCR Network)",
    caregiversDeckLabel: "Recommended Providers Nearby (Ranked by Multi-Criteria Formula)",
    matchScoreSuffix: "Match",
    bookBtn: "Book 1-Tap",

    // Booking Modal
    modalTitle: "✅ Provider Dispatched",
    modalRoutedText: (name) => `Your care request has been routed to <strong>${name}</strong>.`,
    modalServiceLabel: "Care Service:",
    modalSlotLabel: "Available Slot:",
    modalLocationLabel: "Patient Location:",
    modalNotice: "The certified provider has received your location and will contact you shortly to confirm arrival.",
    modalDoneBtn: "Done",

    // Badges & Statuses
    careTypes: {
      emergency_112: "EMERGENCY 112",
      emergency: "EMERGENCY 112",
      paramedic_home_visit: "PARAMEDIC HOME VISIT",
      home_nursing: "HOME NURSING",
      lab_test_home: "LAB TEST HOME",
      teleconsultation: "TELECONSULTATION"
    },
    urgencies: {
      emergency: "URGENCY: EMERGENCY",
      same_day: "URGENCY: SAME DAY",
      scheduled: "URGENCY: SCHEDULED"
    },
    roles: {
      medic: "Paramedic Medic",
      nurse: "Certified Nurse",
      phlebotomist: "Lab Phlebotomist",
      doctor: "Doctor Teleconsult"
    },
    assessmentPrefix: "Assessment Complete:",
    emergencyPrefix: "Emergency Alert:",
    networkError: "Sorry, a network error occurred. Please try again."
  }
};

// Aliases for "auto"
I18N.auto = { ...I18N.Hindi };

// Current Language State
let currentLanguage = localStorage.getItem("carecompass_lang") || "Hindi";
let lastTriageData = null;

// DOM Element References
const chatMessages = document.getElementById("chat-messages");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const micBtn = document.getElementById("mic-btn");
const micStatus = document.getElementById("mic-status");
const langSelect = document.getElementById("lang-select");

// Results Panel Elements
const emptyState = document.getElementById("empty-state");
const triageCard = document.getElementById("triage-card");
const careTypeBadge = document.getElementById("care-type-badge");
const urgencyBadge = document.getElementById("urgency-badge");
const triageReasoning = document.getElementById("triage-reasoning");
const emergencyBanner = document.getElementById("emergency-banner");
const emergencyText = document.getElementById("emergency-text");
const caregiversContainer = document.getElementById("caregivers-container");
const caregiverList = document.getElementById("caregiver-list");
const whatsappShareBtn = document.getElementById("whatsapp-share-btn");
const emergencyWhatsAppBtn = document.getElementById("emergency-whatsapp-share-btn");

// Conversation & Patient State
let conversationHistory = [];
const DEFAULT_LOCATION = { lat: 28.5445, lng: 77.2725 }; // IIIT-Delhi Okhla benchmark
let patientLocation = { ...DEFAULT_LOCATION };
let lastAssessmentText = "";
let isDetectingLocation = false;
let locationAcquired = false;
let locationStatus = "pending";
let locationAddress = "";

// Helper to get active I18N pack
function getDict() {
  return I18N[currentLanguage] || I18N.Hindi;
}

// Helper: Translate reasoning dynamically if helpful
function getLocalizedReasoning(data, lang) {
  if (!data || !data.reasoning) return "";
  const d = I18N[lang] || I18N.Hindi;

  if (lang === "English") {
    return data.reasoning;
  }

  // If already Hindi / Hinglish in reasoning, preserve it
  if (data.care_type === "emergency_112" || data.care_type === "emergency") {
    if (lang === "Hindi") {
      return `आपातकालीन लक्षण पाए गए हैं; मरीज की सुरक्षा के लिए तुरंत राष्ट्रीय आपातकालीन सेवा (हेल्पलाइन 112 / एम्बुलेंस 108) को निर्देशित किया गया है। होम केयर को रोक दिया गया है।`;
    } else {
      return `Emergency red-flag symptoms detect huye hain; patient safety ke liye turant National Helpline 112 ya Ambulance 108 ko call karein. Home care skip kiya gaya hai.`;
    }
  }

  if (data.care_type === "paramedic_home_visit") {
    if (lang === "Hindi") {
      return `मरीज के लिए घर पर वाइटल्स एवं स्वास्थ्य जांच की आवश्यकता है; पैरामेडिक होम विजिट निर्धारित की गई है।`;
    } else {
      return `Ghar par vitals check aur acute care zaroori hai; paramedic home visit assign kiya gaya hai.`;
    }
  }

  if (data.care_type === "home_nursing") {
    if (lang === "Hindi") {
      return `इंजेक्शन, घाव की ड्रेसिंग या कैथेटर देखभाल हेतु प्रमाणित होम नर्सिंग सेवा निर्धारित की गई है।`;
    } else {
      return `Ghar par injection, wound dressing ya nursing care ke liye home nurse recommend kiya gaya hai.`;
    }
  }

  if (data.care_type === "lab_test_home") {
    if (lang === "Hindi") {
      return `घर से ब्लड टेस्ट एवं स्वास्थ्य सैंपल कलेक्शन के लिए लैब तकनीशियन सेवा निर्धारित की गई है।`;
    } else {
      return `Ghar se blood sample collection aur health checkup ke liye lab test home service recommend ki gayi hai.`;
    }
  }

  if (data.care_type === "teleconsultation") {
    if (lang === "Hindi") {
      return `लक्षणों एवं रिपोर्ट्स विश्लेषण हेतु प्रमाणित डॉक्टर से टेली-परामर्श की अनुशंसा की गई है।`;
    } else {
      return `Reports review ya routine complaints ke liye doctor teleconsultation recommend kiya gaya hai.`;
    }
  }

  return data.reasoning;
}

// Localized Follow-Up questions
function getLocalizedFollowUp(originalQuestion, lang) {
  if (!originalQuestion) return "";
  if (lang === "English") return originalQuestion;
  if (lang === "Hindi") {
    return "नमस्ते! मैं आपकी सहायता के लिए तैयार हूँ। यह सेवा किसके लिए चाहिए और मुख्य समस्या क्या है — बुखार, नर्सिंग जरूरत, लैब टेस्ट, या डॉक्टर से परामर्श?";
  }
  if (lang === "Hinglish") {
    return "Namaste! Main help karne ke liye ready hoon. Ye kiske liye chahiye aur kya problem hai — bukhar, nursing need, lab test, ya doctor consult?";
  }
  return originalQuestion;
}

// --- LANGUAGE SWITCHING ENGINE ---
function changeLanguage(selectedLang) {
  currentLanguage = selectedLang;
  localStorage.setItem("carecompass_lang", selectedLang);

  if (langSelect && langSelect.value !== selectedLang) {
    langSelect.value = selectedLang;
  }

  const dict = getDict();
  document.documentElement.lang = dict.langCode;

  // 1. Header & Modes
  const brandSub = document.getElementById("brand-subtitle");
  if (brandSub) brandSub.textContent = dict.brandSubtitle;

  const obsLabel = document.getElementById("observer-label");
  if (obsLabel) obsLabel.textContent = dict.observerLabel;

  const obsBox = document.getElementById("observer-mode-box");
  if (obsBox) obsBox.title = dict.observerTitle;

  const proxyLabel = document.getElementById("proxy-label");
  if (proxyLabel) proxyLabel.textContent = dict.proxyLabel;

  const proxyLocLabel = document.getElementById("proxy-location-label");
  if (proxyLocLabel) proxyLocLabel.textContent = dict.patientLocationLabel;

  const pillRefresh = document.getElementById("pill-refresh-btn");
  if (pillRefresh) pillRefresh.title = dict.refreshGPS;

  // 2. Bento Scenario Cards
  for (let i = 1; i <= 5; i++) {
    const sc = dict.scenarios[i];
    if (sc) {
      const titleEl = document.getElementById(`sc${i}-title`);
      const subEl = document.getElementById(`sc${i}-sub`);
      const tagEl = document.getElementById(`sc${i}-tag`);
      if (titleEl) titleEl.textContent = sc.title;
      if (subEl) subEl.textContent = sc.sub;
      if (tagEl) tagEl.textContent = sc.tag;
    }
  }

  // 3. Left Panel (Intake & Input)
  const intakeTitle = document.getElementById("intake-title");
  if (intakeTitle) intakeTitle.textContent = dict.intakeTitle;

  const intakeSub = document.getElementById("intake-sub");
  if (intakeSub) intakeSub.textContent = dict.intakeSub;

  const voiceReadyBadge = document.getElementById("voice-ready-badge");
  if (voiceReadyBadge) voiceReadyBadge.textContent = dict.voiceReady;

  const welcomeTitle = document.getElementById("welcome-title");
  if (welcomeTitle) welcomeTitle.textContent = dict.welcomeTitle;

  const welcomeBody = document.getElementById("welcome-body");
  if (welcomeBody) welcomeBody.textContent = dict.welcomeBody;

  const welcomeNote = document.getElementById("welcome-note");
  if (welcomeNote) welcomeNote.textContent = dict.welcomeNote;

  const senderLocLabel = document.getElementById("sender-loc-label");
  if (senderLocLabel) senderLocLabel.textContent = dict.senderLocLabel;

  const locDetectBtnText = document.getElementById("loc-detect-btn-text");
  if (locDetectBtnText) locDetectBtnText.textContent = dict.detectGPSBtn;

  const locDetectBtn = document.getElementById("loc-detect-btn");
  if (locDetectBtn) locDetectBtn.title = dict.detectGPSBtn;

  // Placeholder depends on observer mode
  const isObs = document.getElementById("observer-mode-toggle")?.checked;
  if (userInput) {
    userInput.placeholder = isObs ? dict.inputPlaceholderObserver : dict.inputPlaceholder;
  }

  const sendBtnText = document.getElementById("send-btn-text");
  if (sendBtnText) sendBtnText.textContent = dict.sendBtn;

  if (micBtn) micBtn.title = dict.micDefaultTitle;

  // 4. Right Panel (Clinical Triage & Providers)
  const resultsTitle = document.getElementById("results-title");
  if (resultsTitle) resultsTitle.textContent = dict.resultsTitle;

  const resultsSub = document.getElementById("results-sub");
  if (resultsSub) resultsSub.textContent = dict.resultsSub;

  const emptyTitle = document.getElementById("empty-title");
  if (emptyTitle) emptyTitle.textContent = dict.emptyTitle;

  const emptySub = document.getElementById("empty-sub");
  if (emptySub) emptySub.textContent = dict.emptySub;

  const assessmentTitle = document.getElementById("assessment-title");
  if (assessmentTitle) assessmentTitle.textContent = dict.assessmentTitle;

  const ttsBtnText = document.getElementById("tts-btn-text");
  if (ttsBtnText) ttsBtnText.textContent = dict.readAloudBtn;

  const whatsappShareText = document.getElementById("whatsapp-share-text");
  if (whatsappShareText) whatsappShareText.textContent = dict.shareWhatsAppBtn;

  const emergencyTitle = document.getElementById("emergency-title");
  if (emergencyTitle) emergencyTitle.textContent = dict.emergencyTitle;

  const dispatch112Btn = document.getElementById("dispatch-112-btn");
  if (dispatch112Btn) dispatch112Btn.textContent = dict.dispatch112Btn;

  const call108Btn = document.getElementById("call-108-btn");
  if (call108Btn) call108Btn.textContent = dict.call108Btn;

  const emergencyWhatsAppText = document.getElementById("emergency-whatsapp-text");
  if (emergencyWhatsAppText) emergencyWhatsAppText.textContent = dict.emergencyShareBtn;

  const liveTraumaHeader = document.getElementById("live-trauma-header");
  if (liveTraumaHeader) liveTraumaHeader.textContent = dict.traumaHeader;

  const caregiversDeckLabel = document.getElementById("caregivers-deck-label");
  if (caregiversDeckLabel) caregiversDeckLabel.textContent = dict.caregiversDeckLabel;

  const modalTitle = document.getElementById("modal-title");
  if (modalTitle) modalTitle.textContent = dict.modalTitle;

  const modalDoneBtn = document.getElementById("modal-done-btn");
  if (modalDoneBtn) modalDoneBtn.textContent = dict.modalDoneBtn;

  // Update speech recognition language
  if (recognition) {
    recognition.lang = dict.speechLang;
  }

  // Refresh Location UI in active language
  updateLocationUI(locationStatus, patientLocation, locationAddress);

  // If a triage result is already displayed, re-render it in the new language!
  if (lastTriageData) {
    renderResponse(lastTriageData);
  }
}

// Bento scenario click handler: feeds localized prompt
function applyScenario(index) {
  const dict = getDict();
  const sc = dict.scenarios[index];
  if (sc && sc.prompt) {
    userInput.value = sc.prompt;
    handleSend();
  }
}

// Geolocation UI Synchronization
function updateLocationUI(status, coords, areaName) {
  const dict = getDict();
  const locText = document.getElementById("location-text");
  const senderCoords = document.getElementById("sender-coords-text");
  const liveBeacon = document.getElementById("live-beacon");
  const detectBtn = document.getElementById("loc-detect-btn");

  const isProxy = document.getElementById("proxy-mode-toggle")?.checked;
  if (isProxy) {
    if (senderCoords) {
      senderCoords.innerHTML = `<span style="color: #0369A1;">${dict.proxyLabel} (${document.getElementById("proxy-location-select")?.selectedOptions[0]?.text || "Selected"})</span>`;
    }
    return;
  }

  if (status === "detecting") {
    if (locText) locText.textContent = dict.locationDetecting;
    if (senderCoords) senderCoords.textContent = dict.locationDetecting;
    if (liveBeacon) liveBeacon.className = "live-beacon searching";
    if (detectBtn) detectBtn.classList.add("loading");
    return;
  }

  if (detectBtn) detectBtn.classList.remove("loading");

  if (status === "success" && coords) {
    const latStr = coords.lat.toFixed(4);
    const lngStr = coords.lng.toFixed(4);
    const label = areaName ? `${areaName} (${latStr}, ${lngStr})` : `GPS: ${latStr}, ${lngStr}`;

    if (locText) locText.textContent = `📍 ${label}`;
    if (senderCoords) senderCoords.innerHTML = `<strong>${label}</strong> <span style="color:#16A34A;font-size:11px;">${dict.locationVerified}</span>`;
    if (liveBeacon) liveBeacon.className = "live-beacon";
  } else {
    if (locText) locText.textContent = dict.locationDefault;
    if (senderCoords) senderCoords.innerHTML = `<span>Okhla, New Delhi</span> <span style="color:#94A3B8;font-size:11px;">${dict.locationDefaultTag}</span>`;
    if (liveBeacon) liveBeacon.className = "live-beacon fallback";
  }
}

// Reverse Geocoding helper (OpenStreetMap Nominatim with 2s timeout)
async function reverseGeocode(lat, lng) {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000);
    const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=14`, {
      signal: controller.signal,
      headers: { "Accept": "application/json" }
    });
    clearTimeout(timeoutId);
    if (!res.ok) return null;
    const data = await res.json();
    const address = data.address || {};
    const locality = address.suburb || address.neighbourhood || address.residential || address.city_district || address.town || address.city;
    const state = address.state;
    if (locality) {
      return state ? `${locality}, ${state}` : locality;
    }
    return data.name || null;
  } catch {
    return null;
  }
}

// Fetch current GPS location
async function fetchCurrentLocation(userInitiated = false) {
  const isProxy = document.getElementById("proxy-mode-toggle")?.checked;
  if (isProxy) {
    changePatientLocation();
    return patientLocation;
  }

  if (!navigator.geolocation) {
    if (userInitiated) {
      alert("Geolocation is not supported by your browser. Using default Delhi coordinates.");
    }
    locationStatus = "error";
    updateLocationUI("error", null);
    return patientLocation;
  }

  updateLocationUI("detecting");
  isDetectingLocation = true;

  return new Promise((resolve) => {
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        patientLocation = { lat, lng };
        locationAcquired = true;
        locationStatus = "success";
        isDetectingLocation = false;

        try {
          const area = await reverseGeocode(lat, lng);
          locationAddress = area || "";
          updateLocationUI("success", patientLocation, area);
        } catch {
          updateLocationUI("success", patientLocation, null);
        }
        resolve(patientLocation);
      },
      (err) => {
        console.warn("Geolocation permission or timeout:", err.message);
        locationStatus = "denied";
        isDetectingLocation = false;
        updateLocationUI("denied", null);
        resolve(patientLocation);
      },
      {
        enableHighAccuracy: true,
        timeout: 8000,
        maximumAge: 30000
      }
    );
  });
}

// Observer & Family Proxy Mode Handlers
function toggleObserverMode() {
  const isObs = document.getElementById("observer-mode-toggle").checked;
  const senderCoords = document.getElementById("sender-coords-text");
  const dict = getDict();

  if (isObs) {
    if (senderCoords) {
      senderCoords.innerHTML = `<span style="color: #B45309; font-weight: 800;">${dict.observerLabel} Active (Welfare Reporting)</span>`;
    }
    userInput.placeholder = dict.inputPlaceholderObserver;
  } else {
    userInput.placeholder = dict.inputPlaceholder;
    if (locationAcquired) {
      updateLocationUI("success", patientLocation, locationAddress);
    } else {
      fetchCurrentLocation(false);
    }
  }
}

function toggleProxyMode() {
  const isProxy = document.getElementById("proxy-mode-toggle").checked;
  const drawer = document.getElementById("proxy-location-container");
  const locPill = document.getElementById("location-pill");

  if (isProxy) {
    drawer.classList.remove("hidden");
    locPill.classList.add("hidden");
    changePatientLocation();
  } else {
    drawer.classList.add("hidden");
    locPill.classList.remove("hidden");
    if (locationAcquired) {
      updateLocationUI("success", patientLocation, locationAddress);
    } else {
      fetchCurrentLocation(false);
    }
  }
}

function changePatientLocation() {
  const select = document.getElementById("proxy-location-select");
  const val = select.value;
  const [lat, lng] = val.split(",").map(Number);
  patientLocation = { lat, lng };

  const senderCoords = document.getElementById("sender-coords-text");
  if (senderCoords) {
    const text = select.selectedOptions[0]?.text || "Selected Location";
    senderCoords.innerHTML = `<span style="color: #0369A1;">${text}</span>`;
  }
}

// Browser-Native Speech Recognition
let recognition = null;
let isRecording = false;

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = getDict().speechLang;

  recognition.onstart = () => {
    isRecording = true;
    micBtn.classList.add("listening");
    micStatus.textContent = getDict().micListening;
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    userInput.value = transcript;
    micStatus.textContent = `${getDict().micHeard} "${transcript}"`;
  };

  recognition.onerror = (event) => {
    console.error("Speech recognition error:", event.error);
    isRecording = false;
    micBtn.classList.remove("listening");
    micStatus.textContent = getDict().micError;
  };

  recognition.onend = () => {
    isRecording = false;
    micBtn.classList.remove("listening");
  };
} else {
  micBtn.style.display = "none";
}

micBtn.addEventListener("click", () => {
  if (!recognition) return;
  if (isRecording) {
    recognition.stop();
  } else {
    recognition.lang = getDict().speechLang;
    recognition.start();
  }
});

// SpeechSynthesis Read Aloud (Grandparent Accessibility)
function speakAssessment() {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  const textToRead = lastAssessmentText || "CareCompass assessment complete.";
  const utterance = new SpeechSynthesisUtterance(textToRead);
  utterance.lang = getDict().speechLang;
  utterance.rate = 0.95; // Gentle elderly-friendly pacing
  window.speechSynthesis.speak(utterance);
}

// Send Message Handler
async function handleSend() {
  const text = userInput.value.trim();
  if (!text) return;
  const dict = getDict();

  // Ensure current location of whoever is going to message is captured
  const isProxy = document.getElementById("proxy-mode-toggle")?.checked;
  if (!isProxy && !locationAcquired && !isDetectingLocation) {
    try {
      await Promise.race([
        fetchCurrentLocation(false),
        new Promise((resolve) => setTimeout(resolve, 1500))
      ]);
    } catch (e) {
      console.warn("Location capture timeout:", e);
    }
  }

  // Add User Message to UI
  appendMessage("user", text);
  userInput.value = "";
  micStatus.textContent = "";

  // Call CareCompass Triage API (/triage)
  try {
    const payload = {
      user_input: text,
      language: currentLanguage,
      location: patientLocation,
      conversation_history: conversationHistory
    };

    conversationHistory.push({ role: "user", content: text });

    const res = await fetch("/triage", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      throw new Error(`API error: ${res.statusText}`);
    }

    const data = await res.json();
    renderResponse(data);
  } catch (err) {
    console.error(err);
    appendMessage("assistant", dict.networkError);
  }
}

sendBtn.addEventListener("click", handleSend);
userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    handleSend();
  }
});

userInput.addEventListener("focus", () => {
  const isProxy = document.getElementById("proxy-mode-toggle")?.checked;
  if (!isProxy && !locationAcquired && !isDetectingLocation) {
    fetchCurrentLocation(false);
  }
});

function appendMessage(role, text) {
  const row = document.createElement("div");
  row.className = `bubble-row ${role}`;

  const avatar = document.createElement("div");
  avatar.className = `avatar ${role === "user" ? "patient" : "bot"}`;
  avatar.textContent = role === "user" ? "👤" : "🤖";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = text.replace(/\n/g, "<br>");

  row.appendChild(avatar);
  row.appendChild(bubble);
  chatMessages.appendChild(row);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Render Response & Decoupled Async Trauma Lookup
function renderResponse(data) {
  lastTriageData = data;
  const dict = getDict();

  // Case A: Follow-up question needed (Underspecified)
  if (data.follow_up_question) {
    const localizedFollowUp = getLocalizedFollowUp(data.follow_up_question, currentLanguage);
    appendMessage("assistant", localizedFollowUp);
    conversationHistory.push({ role: "assistant", content: localizedFollowUp });
    lastAssessmentText = localizedFollowUp;
    speakAssessment();
    return;
  }

  // Case B: Final Triage Reached
  emptyState.classList.add("hidden");
  const localizedReasoning = getLocalizedReasoning(data, currentLanguage);

  // Emergency Case
  if (data.care_type === "emergency_112" || data.care_type === "emergency") {
    emergencyBanner.classList.remove("hidden");
    emergencyText.textContent = localizedReasoning;
    triageCard.classList.add("hidden");
    caregiversContainer.classList.add("hidden");
    appendMessage("assistant", `🚨 <strong>${dict.emergencyPrefix}</strong> ${localizedReasoning}`);

    lastAssessmentText = `${dict.emergencyPrefix} ${localizedReasoning}`;
    speakAssessment();

    // 1-Tap WhatsApp Emergency Alert Link in Active Language
    const emShareText = encodeURIComponent(
      `🚨 *${dict.emergencyTitle}*\n` +
      `GPS: (${patientLocation.lat.toFixed(4)}, ${patientLocation.lng.toFixed(4)})\n` +
      `Protocol: Helpline 112 / Ambulance 108\n` +
      `Details: ${localizedReasoning}\n` +
      `Please check on them or dispatch help immediately!`
    );
    if (emergencyWhatsAppBtn) {
      emergencyWhatsAppBtn.href = `https://wa.me/?text=${emShareText}`;
    }

    loadLiveTraumaCenters(patientLocation.lat, patientLocation.lng);
    return;
  }

  // Non-Emergency Case
  emergencyBanner.classList.add("hidden");
  triageCard.classList.remove("hidden");

  // Localized Care Type Badge
  const careTypeLabel = dict.careTypes[data.care_type] || data.care_type.replace(/_/g, " ").toUpperCase();
  careTypeBadge.textContent = careTypeLabel;
  careTypeBadge.className = "badge-pill badge-care";

  // Localized Urgency Badge
  const urgencyLabel = dict.urgencies[data.urgency] || `Urgency: ${data.urgency.toUpperCase()}`;
  urgencyBadge.textContent = urgencyLabel;
  urgencyBadge.className = `badge-pill ${
    data.urgency === "emergency" ? "badge-urgency-emergency" :
    data.urgency === "same_day" ? "badge-urgency-sameday" : "badge-urgency-scheduled"
  }`;

  triageReasoning.textContent = localizedReasoning;
  appendMessage("assistant", `✅ <strong>${dict.assessmentPrefix}</strong> ${careTypeLabel} recommended. ${localizedReasoning}`);

  lastAssessmentText = `${careTypeLabel}. ${localizedReasoning}`;
  speakAssessment();

  // Render Caregivers
  if (data.matched_caregivers && data.matched_caregivers.length > 0) {
    caregiversContainer.classList.remove("hidden");
    caregiverList.innerHTML = "";

    data.matched_caregivers.forEach((cg) => {
      const card = document.createElement("div");
      card.className = "caregiver-item";
      const scorePct = Math.round(cg.score * 100);
      const roleLabel = dict.roles[cg.role] || cg.role || careTypeLabel;

      card.innerHTML = `
        <div class="cg-profile">
          <h4>${cg.name || cg.caregiver_id} <span class="match-score">${scorePct}% ${dict.matchScoreSuffix}</span></h4>
          <p class="cg-justification">${cg.reason}</p>
        </div>
        <button class="action-book" onclick="openBookingModal('${cg.name || cg.caregiver_id}', '${roleLabel}', '${cg.available_slot}')">
          ${dict.bookBtn}
        </button>
      `;
      caregiverList.appendChild(card);
    });

    // 1-Tap WhatsApp Triage Share Link in active language
    const topCg = data.matched_caregivers[0];
    const shareText = encodeURIComponent(
      `🧭 *CareCompass Health Triage Summary*\n` +
      `Service: ${careTypeLabel}\n` +
      `Urgency: ${urgencyLabel}\n` +
      `Reasoning: ${localizedReasoning}\n` +
      `Top Provider: ${topCg.name || topCg.caregiver_id} (${topCg.reason})\n` +
      `Slot: ${topCg.available_slot || "Available Today"}`
    );
    if (whatsappShareBtn) {
      whatsappShareBtn.href = `https://wa.me/?text=${shareText}`;
      whatsappShareBtn.classList.remove("hidden");
    }
  } else {
    caregiversContainer.classList.add("hidden");
    if (whatsappShareBtn) whatsappShareBtn.classList.add("hidden");
  }
}

// Decoupled Live Emergency Trauma Desks Loader
async function loadLiveTraumaCenters(lat, lng) {
  try {
    const res = await fetch(`/api/v1/emergency/facilities?lat=${lat}&lng=${lng}`);
    if (!res.ok) return;
    const json = await res.json();
    const container = document.getElementById("live-trauma-container");
    const list = document.getElementById("live-trauma-list");
    if (json.facilities && json.facilities.length > 0 && container && list) {
      list.innerHTML = "";
      json.facilities.forEach((f) => {
        const div = document.createElement("div");
        div.className = "trauma-item";
        div.innerHTML = `
          <div>
            <div class="trauma-title">${f.name}</div>
            <div style="font-size: 11px; color: #78716C;">${f.area} (${f.distance_km} km) · ${f.type}</div>
          </div>
          <a href="tel:${f.phone}" class="trauma-phone">📞 ${f.phone}</a>
        `;
        list.appendChild(div);
      });
      container.classList.remove("hidden");
    }
  } catch (err) {
    console.warn("Trauma centers fetch error:", err);
  }
}

// Booking Modal Handlers
function openBookingModal(name, role, slot) {
  const dict = getDict();
  const modal = document.getElementById("booking-modal");
  const modalContent = document.getElementById("modal-content");
  modalContent.innerHTML = `
    <p>${dict.modalRoutedText(name)}</p>
    <div style="margin: 16px 0; background: #F4EFE6; padding: 14px 18px; border-radius: 12px; border: 1px solid #E8E0D2;">
      <p style="margin-bottom: 6px;">🏥 <strong>${dict.modalServiceLabel}</strong> ${role}</p>
      <p style="margin-bottom: 6px;">⏰ <strong>${dict.modalSlotLabel}</strong> ${slot || "Immediate Available"}</p>
      <p>📍 <strong>${dict.modalLocationLabel}</strong> (${patientLocation.lat.toFixed(4)}, ${patientLocation.lng.toFixed(4)})</p>
    </div>
    <p style="font-size: 12px; color: #78716C;">${dict.modalNotice}</p>
  `;
  modal.classList.remove("hidden");
}

function closeModal() {
  document.getElementById("booking-modal").classList.add("hidden");
}

// Initialization on load
document.addEventListener("DOMContentLoaded", () => {
  changeLanguage(currentLanguage);
  fetchCurrentLocation(false);
});
