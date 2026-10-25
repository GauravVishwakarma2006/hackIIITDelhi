from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class CareType(str, Enum):
    EMERGENCY_112 = "emergency_112"
    HOME_NURSING = "home_nursing"
    PARAMEDIC_HOME_VISIT = "paramedic_home_visit"
    TELECONSULTATION = "teleconsultation"
    LAB_TEST_HOME = "lab_test_home"


class UrgencyLevel(str, Enum):
    EMERGENCY = "emergency"
    SAME_DAY = "same_day"
    SCHEDULED = "scheduled"


class Location(BaseModel):
    lat: float = Field(..., description="Latitude coordinate")
    lng: float = Field(..., description="Longitude coordinate")


class ConversationTurn(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text")


class TriageRequest(BaseModel):
    user_input: str = Field(..., description="Patient input in English, Hindi, or Hinglish")
    language: Optional[str] = Field("auto", description="Language preference: 'auto', 'en', 'hi', or 'hinglish'")
    location: Optional[Location] = Field(default=Location(lat=28.5445, lng=77.2725), description="Patient GPS coordinates")
    conversation_history: List[ConversationTurn] = Field(default_factory=list, description="Prior conversation messages")
    proxy_mode: Optional[bool] = Field(default=False, description="Whether request is reported via family proxy")
    messenger_location: Optional[Location] = Field(default=None, description="Current coordinates of the proxy messenger")
    observer_mode: Optional[bool] = Field(default=False, description="Whether request is reported by a third-party observer / guard")


class MatchedCaregiver(BaseModel):
    caregiver_id: str
    score: float = Field(..., ge=0.0, le=1.0, description="Match score between 0 and 1")
    reason: str = Field(..., description="Plain-language explainable reason for the match")
    name: Optional[str] = None
    role: Optional[str] = None
    distance_km: Optional[float] = None
    available_slot: Optional[str] = None
    rating: Optional[float] = None


class TriageResponse(BaseModel):
    follow_up_question: Optional[str] = Field(None, description="Next targeted question if more info is needed")
    care_type: Optional[str] = Field(None, description="One of emergency_112, home_nursing, paramedic_home_visit, teleconsultation, lab_test_home")
    urgency: Optional[str] = Field(None, description="One of emergency, same_day, scheduled")
    red_flags: List[str] = Field(default_factory=list, description="Identified red-flag symptoms")
    reasoning: str = Field(..., description="Clinical reasoning explaining the triage decision")
    matched_caregivers: List[MatchedCaregiver] = Field(default_factory=list, description="Ranked caregivers")


class FeedbackRequest(BaseModel):
    user_input: str = Field(..., description="Original user message that was triaged")
    predicted_care_type: Optional[str] = Field(None, description="The care type that CareCompass predicted")
    predicted_urgency: Optional[str] = Field(None, description="The urgency that CareCompass predicted")
    rating: str = Field(..., description="'thumbs_up' or 'thumbs_down'")
    suggested_care_type: Optional[str] = Field(None, description="User or expert suggested care type if correcting")
    comment: Optional[str] = Field(None, description="User explanation of why or what to improve")
    observer_mode: Optional[bool] = Field(False, description="Whether this occurred in observer mode")


class FeedbackResponse(BaseModel):
    status: str
    message: str
    learned: bool
