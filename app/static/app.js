/**
 * CareCompass Client Application
 * Handles voice transcription (webkitSpeechRecognition hi-IN),
 * speech synthesis read-aloud (No-Download Grandparent UX),
 * family proxy reporting, WhatsApp 1-tap sharing, and async trauma desk discovery.
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
const whatsappShareBtn = document.getElementById("whatsapp-share-btn");
const emergencyWhatsAppBtn = document.getElementById("emergency-whatsapp-share-btn");

// Conversation & Patient State
let conversationHistory = [];
const DEFAULT_LOCATION = { lat: 28.5445, lng: 77.2725 }; // IIIT-Delhi Okhla benchmark
let patientLocation = { ...DEFAULT_LOCATION };
let lastAssessmentText = "";
let isDetectingLocation = false;
let locationAcquired = false;
let locationStatus = "pending"; // 'pending' | 'success' | 'denied' | 'error'
let locationAddress = "";

// Geolocation UI Synchronization
function updateLocationUI(status, coords, areaName) {
  const locText = document.getElementById("location-text");
  const senderCoords = document.getElementById("sender-coords-text");
  const liveBeacon = document.getElementById("live-beacon");
  const detectBtn = document.getElementById("loc-detect-btn");

  const isProxy = document.getElementById("proxy-mode-toggle")?.checked;
  if (isProxy) {
    if (senderCoords) senderCoords.innerHTML = `<span style="color: #0369A1;">Proxy Mode (Selected Location)</span>`;
    return;
  }

  if (status === "detecting") {
    if (locText) locText.textContent = "📍 Detecting current GPS location...";
    if (senderCoords) senderCoords.textContent = "Detecting current GPS coordinates...";
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
    if (senderCoords) senderCoords.innerHTML = `<strong>${label}</strong> <span style="color:#16A34A;font-size:11px;">(Verified GPS)</span>`;
    if (liveBeacon) liveBeacon.className = "live-beacon";
  } else {
    // Fallback or permission denied
    const defaultLabel = "Okhla, New Delhi (Default Benchmark)";
    if (locText) locText.textContent = `📍 ${defaultLabel} · Click to retry`;
    if (senderCoords) senderCoords.innerHTML = `<span>${defaultLabel}</span> <span style="color:#94A3B8;font-size:11px;">(Default)</span>`;
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

// Fetch current GPS location of whoever is going to message
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

// 1. Observer & Family Proxy Mode Handlers
function toggleObserverMode() {
  const isObs = document.getElementById("observer-mode-toggle").checked;
  const senderCoords = document.getElementById("sender-coords-text");
  if (isObs) {
    if (senderCoords) {
      senderCoords.innerHTML = `<span style="color: #B45309; font-weight: 800;">👮‍♂️ Observer / Guard Mode Active (Welfare Reporting)</span>`;
    }
    userInput.placeholder = "Padosi ya guard reporting: e.g. Dadi darwaza nahi khol rahi hain aur phone nahi utha rahi...";
  } else {
    userInput.placeholder = "Bol kar ya likh kar batayein... (e.g. Papa ko bukhar hai)";
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

// 2. Browser-Native Speech Recognition (Hindi / Hinglish / English)
let recognition = null;
let isRecording = false;

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = 'hi-IN'; // Indian Hindi/Hinglish speech

  recognition.onstart = () => {
    isRecording = true;
    micBtn.classList.add("listening");
    micStatus.textContent = "🎙️ Listening... Bolna shuru kijiye (listening in Hindi / English)";
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

// 3. SpeechSynthesis Read Aloud (Grandparent Accessibility)
function speakAssessment() {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  const textToRead = lastAssessmentText || "CareCompass assessment complete.";
  const utterance = new SpeechSynthesisUtterance(textToRead);
  utterance.lang = langSelect.value === 'English' ? 'en-IN' : 'hi-IN';
  utterance.rate = 0.95; // Gentle elderly-friendly pacing
  window.speechSynthesis.speak(utterance);
}

// 4. Send Message Handler
async function handleSend() {
  const text = userInput.value.trim();
  if (!text) return;

  // Ensure current location of whoever is going to message is captured
  const isProxy = document.getElementById("proxy-mode-toggle")?.checked;
  if (!isProxy && !locationAcquired && !isDetectingLocation) {
    try {
      // Race fetchCurrentLocation with quick 1.5s timeout so send is not delayed
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
      language: langSelect.value,
      location: patientLocation,
      conversation_history: conversationHistory
    };

    // Update local history
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

// Proactively acquire current location as soon as the user interacts with input
userInput.addEventListener("focus", () => {
  const isProxy = document.getElementById("proxy-mode-toggle")?.checked;
  if (!isProxy && !locationAcquired && !isDetectingLocation) {
    fetchCurrentLocation(false);
  }
});

userInput.addEventListener("input", () => {
  const isProxy = document.getElementById("proxy-mode-toggle")?.checked;
  if (!isProxy && !locationAcquired && !isDetectingLocation) {
    fetchCurrentLocation(false);
  }
});

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

// 5. Render Response & Decoupled Async Trauma Lookup
function renderResponse(data) {
  // Case A: Follow-up question needed (Underspecified)
  if (data.follow_up_question) {
    appendMessage("assistant", data.follow_up_question);
    conversationHistory.push({ role: "assistant", content: data.follow_up_question });
    lastAssessmentText = data.follow_up_question;
    speakAssessment();
    return;
  }

  // Case B: Final Triage Reached
  emptyState.classList.add("hidden");

  // Emergency Case (Sub-10ms response: call buttons shown immediately, matching skipped)
  if (data.care_type === "emergency_112" || data.care_type === "emergency") {
    emergencyBanner.classList.remove("hidden");
    emergencyText.textContent = data.reasoning;
    triageCard.classList.add("hidden");
    caregiversContainer.classList.add("hidden");
    appendMessage("assistant", `🚨 <strong>Emergency Alert:</strong> ${data.reasoning}`);

    lastAssessmentText = `Emergency alert. ${data.reasoning}. Please call 112 or 108 immediately.`;
    speakAssessment();

    // 1-Tap WhatsApp Emergency Alert Link
    const emShareText = encodeURIComponent(
      `🚨 *URGENT MEDICAL EMERGENCY ALERT*\n` +
      `Patient Coordinates: (${patientLocation.lat}, ${patientLocation.lng})\n` +
      `Protocol: Emergency 112 / Ambulance 108\n` +
      `Details: ${data.reasoning}\n` +
      `Please check on them or dispatch help immediately!`
    );
    if (emergencyWhatsAppBtn) {
      emergencyWhatsAppBtn.href = `https://wa.me/?text=${emShareText}`;
    }

    // Decoupled Background Fetch for Live Verified Trauma Desks
    loadLiveTraumaCenters(patientLocation.lat, patientLocation.lng);
    return;
  }

  // Non-Emergency Case
  emergencyBanner.classList.add("hidden");
  triageCard.classList.remove("hidden");

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

  lastAssessmentText = `${careTypeFormatted} recommended. ${data.reasoning}`;
  speakAssessment();

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

    // 1-Tap WhatsApp Triage Share Link
    const topCg = data.matched_caregivers[0];
    const shareText = encodeURIComponent(
      `🧭 *CareCompass Health Triage Summary*\n` +
      `Service: ${careTypeFormatted}\n` +
      `Urgency: ${data.urgency.toUpperCase()}\n` +
      `Reasoning: ${data.reasoning}\n` +
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

// 6. Decoupled Live Emergency Trauma Desks Loader
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

// 7. Booking Modal Handlers
function openBookingModal(name, role, slot) {
  const modal = document.getElementById("booking-modal");
  const modalContent = document.getElementById("modal-content");
  modalContent.innerHTML = `
    <p>Your care request has been routed to <strong>${name}</strong>.</p>
    <div style="margin: 16px 0; background: #F4EFE6; padding: 14px 18px; border-radius: 12px; border: 1px solid #E8E0D2;">
      <p style="margin-bottom: 6px;">🏥 <strong>Care Service:</strong> ${role.replace(/_/g, " ").toUpperCase()}</p>
      <p style="margin-bottom: 6px;">⏰ <strong>Available Slot:</strong> Today at ${slot || "Immediate Available"}</p>
      <p>📍 <strong>Patient Location:</strong> (${patientLocation.lat.toFixed(4)}, ${patientLocation.lng.toFixed(4)})</p>
    </div>
    <p style="font-size: 12px; color: #78716C;">The certified provider has received your location and will contact you shortly to confirm arrival.</p>
  `;
  modal.classList.remove("hidden");
}

function closeModal() {
  document.getElementById("booking-modal").classList.add("hidden");
}

// Automatically acquire current location of whoever is going to message
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    fetchCurrentLocation(false);
  });
} else {
  fetchCurrentLocation(false);
}
