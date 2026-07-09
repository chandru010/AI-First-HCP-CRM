from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class HCPRead(BaseModel):
    id: int
    name: str
    specialty: str
    territory: str
    segment: str
    preferred_channel: str
    last_interaction_summary: str

    model_config = {"from_attributes": True}


class InteractionCreate(BaseModel):
    hcp_id: int
    interaction_date: datetime | None = None
    channel: str = "In-person"
    products_discussed: list[str] = Field(default_factory=list)
    topics_discussed: list[str] = Field(default_factory=list)
    samples_dropped: list[str] = Field(default_factory=list)
    sentiment: str = "Neutral"
    notes: str
    follow_up_date: str = ""
    follow_up_action: str = ""


class InteractionUpdate(BaseModel):
    channel: str | None = None
    products_discussed: list[str] | None = None
    topics_discussed: list[str] | None = None
    samples_dropped: list[str] | None = None
    sentiment: str | None = None
    notes: str | None = None
    follow_up_date: str | None = None
    follow_up_action: str | None = None


class InteractionRead(BaseModel):
    id: int
    hcp_id: int
    hcp_name: str
    interaction_date: datetime
    channel: str
    products_discussed: list[str]
    topics_discussed: list[str]
    samples_dropped: list[str]
    sentiment: str
    notes: str
    summary: str
    follow_up_date: str
    follow_up_action: str
    compliance_flags: list[str]
    created_at: datetime
    updated_at: datetime


class AgentChatRequest(BaseModel):
    message: str
    hcp_id: int | None = None
    interaction_id: int | None = None


class AgentChatResponse(BaseModel):
    answer: str
    intent: str
    tool_name: str
    tool_result: dict[str, Any]
    extracted: dict[str, Any]


class ToolDemoResponse(BaseModel):
    results: list[dict[str, Any]]
