from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class CareType(str, Enum):
    EMERGENCY = "emergency"
    PARAMEDIC_HOME_VISIT = "paramedic_home_visit"
    NURSE = "nurse"
    GP_TELECONSULT = "gp_teleconsult"
    SPECIALIST = "specialist"


class UrgencyLevel(str, Enum):
    IMMEDIATE = "immediate"
    SAME_DAY = "same_day"
    ROUTINE = "routine"


class Location(BaseModel):
    lat: float = Field(..., description="Latitude coordinate")
    lng: float = Field(..., description="Longitude coordinate")


class ConversationTurn(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text")


class TriageRequest(BaseModel):
    user_input: str = Field(..., description="Patient input in English, Hindi, or Hinglish")
    language: Optional[str] = Field("auto", description="Language preference: 'auto', 'en', 'hi', or 'hinglish'")
    location: Optional[Location] = Field(default=Location(lat=28.54, lng=77.27), description="Patient GPS coordinates")
    conversation_history: List[ConversationTurn] = Field(default_factory=list, description="Prior conversation messages")


class MatchedCaregiver(BaseModel):
    caregiver_id: str
    name: Optional[str] = None
    role: Optional[str] = None
    score: float = Field(..., ge=0.0, le=1.0, description="Match score between 0 and 1")
    reason: str = Field(..., description="Plain-language explainable reason for the match")
    distance_km: Optional[float] = None
    available_slot: Optional[str] = None
    rating: Optional[float] = None


class TriageResponse(BaseModel):
    follow_up_question: Optional[str] = Field(None, description="Next targeted question if more info is needed")
    care_type: Optional[str] = Field(None, description="One of emergency, paramedic_home_visit, nurse, gp_teleconsult, specialist")
    urgency: Optional[str] = Field(None, description="One of immediate, same_day, routine")
    red_flags: List[str] = Field(default_factory=list, description="Identified red-flag symptoms")
    reasoning: str = Field(..., description="Clinical reasoning explaining the triage decision")
    matched_caregivers: List[MatchedCaregiver] = Field(default_factory=list, description="Ranked caregivers")
