/**
 * CareCompass Client Application
 * Handles voice transcription, multi-turn clinical intake, triage rendering, and 1-tap booking.
 */

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

// Conversation State
let conversationHistory = [];
const patientLocation = { lat: 28.5445, lng: 77.2725 }; // IIIT-Delhi Okhla coordinates

// Voice Recognition Setup
let recognition = null;
let isRecording = false;

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = 'hi-IN'; // Default to Indian Hindi/Hinglish speech

  recognition.onstart = () => {
    isRecording = true;
    micBtn.classList.add("listening");
    micStatus.textContent = "🎙️ Listening... Bolna shuru kijiye (listening in Hindi/English)";
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    userInput.value = transcript;
    micStatus.textContent = `Heard: "${transcript}"`;
  };

  recognition.onerror = (event) => {
    console.error("Speech recognition error:", event.error);
    isRecording = false;
    micBtn.classList.remove("listening");
    micStatus.textContent = "Voice input error. Please type your message.";
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
    recognition.lang = langSelect.value === "English" ? "en-IN" : "hi-IN";
    recognition.start();
  }
});

// Send Message Handler
async function handleSend() {
  const text = userInput.value.trim();
  if (!text) return;

  // Add User Message to UI
  appendMessage("user", text);
  userInput.value = "";
  micStatus.textContent = "";

  // Call CareCompass Triage API
  try {
    const payload = {
      user_input: text,
      language: langSelect.value,
      location: patientLocation,
      conversation_history: conversationHistory
    };

    // Update local history
    conversationHistory.push({ role: "user", content: text });

    const res = await fetch("/api/v1/triage", {
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
    appendMessage("assistant", "Kshama karein, network error aayi hai. Kripya punah prayas karein. (Network error, please try again.)");
  }
}

sendBtn.addEventListener("click", handleSend);
userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    handleSend();
  }
});

// Quick Scenarios click
function applyPrompt(text) {
  userInput.value = text;
  handleSend();
}

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

function renderResponse(data) {
  // Case A: Follow-up question needed (Underspecified)
  if (data.follow_up_question) {
    appendMessage("assistant", data.follow_up_question);
    conversationHistory.push({ role: "assistant", content: data.follow_up_question });
    return;
  }

  // Case B: Final Triage & Matching Reached
  emptyState.classList.add("hidden");

  // Emergency Case
  if (data.care_type === "emergency_112" || data.care_type === "emergency") {
    emergencyBanner.classList.remove("hidden");
    emergencyText.textContent = data.reasoning;
    triageCard.classList.add("hidden");
    caregiversContainer.classList.add("hidden");
    appendMessage("assistant", `🚨 <strong>Emergency Alert:</strong> ${data.reasoning}`);
    return;
  }

  // Non-Emergency Triage Card
  emergencyBanner.classList.add("hidden");
  triageCard.classList.remove("hidden");

  // Format Badges
  const careTypeFormatted = data.care_type.replace(/_/g, " ").toUpperCase();
  careTypeBadge.textContent = careTypeFormatted;
  careTypeBadge.className = "badge-pill badge-care";

  urgencyBadge.textContent = `Urgency: ${data.urgency.toUpperCase()}`;
  urgencyBadge.className = `badge-pill ${
    data.urgency === "emergency" ? "badge-urgency-emergency" :
    data.urgency === "same_day" ? "badge-urgency-sameday" : "badge-urgency-scheduled"
  }`;

  triageReasoning.textContent = data.reasoning;
  appendMessage("assistant", `✅ <strong>Assessment Complete:</strong> ${careTypeFormatted} recommended. ${data.reasoning}`);

  // Render Caregivers
  if (data.matched_caregivers && data.matched_caregivers.length > 0) {
    caregiversContainer.classList.remove("hidden");
    caregiverList.innerHTML = "";

    data.matched_caregivers.forEach((cg) => {
      const card = document.createElement("div");
      card.className = "caregiver-item";
      const scorePct = Math.round(cg.score * 100);

      card.innerHTML = `
        <div class="cg-profile">
          <h4>${cg.name || cg.caregiver_id} <span class="match-score">${scorePct}% Match</span></h4>
          <p class="cg-justification">${cg.reason}</p>
        </div>
        <button class="action-book" onclick="openBookingModal('${cg.name || cg.caregiver_id}', '${cg.role || data.care_type}', '${cg.available_slot}')">
          Book 1-Tap
        </button>
      `;
      caregiverList.appendChild(card);
    });
  } else {
    caregiversContainer.classList.add("hidden");
  }
}

// Modal Handlers
function openBookingModal(name, role, slot) {
  const modal = document.getElementById("booking-modal");
  const modalContent = document.getElementById("modal-content");
  modalContent.innerHTML = `
    <p>Your care request has been routed to <strong>${name}</strong>.</p>
    <div style="margin: 16px 0; background: #F4EFE6; padding: 14px 18px; border-radius: 12px; border: 1px solid #E8E0D2;">
      <p style="margin-bottom: 6px;">🏥 <strong>Care Service:</strong> ${role.replace(/_/g, " ").toUpperCase()}</p>
      <p style="margin-bottom: 6px;">⏰ <strong>Available Slot:</strong> Today at ${slot || "Immediate Available"}</p>
      <p>📍 <strong>Patient Location:</strong> Okhla Phase III, New Delhi</p>
    </div>
    <p style="font-size: 12px; color: #78716C;">The certified provider has received your location and will contact you shortly to confirm arrival.</p>
  `;
  modal.classList.remove("hidden");
}

function closeModal() {
  document.getElementById("booking-modal").classList.add("hidden");
}
