import json
import re
from datetime import date
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.core.config import settings


SYSTEM_PROMPT = """You are an AI assistant for a life sciences CRM used by field representatives.
Return only JSON with keys: intent, hcp_id, interaction_id, hcp_name, interaction_date,
interaction_time, interaction_type, attendees, channel, products_discussed, topics_discussed,
samples_dropped, materials_shared, discussion_outcomes, sentiment, notes, follow_up_date,
follow_up_action, summary.
Allowed intents: log_interaction, edit_interaction, retrieve_hcp_profile, suggest_next_best_action,
schedule_follow_up, compliance_check."""


def fallback_extract(message: str, hcp_id: int | None = None, interaction_id: int | None = None) -> dict[str, Any]:
    lowered = message.lower()
    if "sorry" in lowered or "actually" in lowered or "change" in lowered or "edit" in lowered or "update" in lowered or interaction_id:
        intent = "edit_interaction"
    elif "log" in lowered or "visit" in lowered or "met with" in lowered or "today i met" in lowered:
        intent = "log_interaction"
    elif "profile" in lowered:
        intent = "retrieve_hcp_profile"
    elif "next best" in lowered or "recommend" in lowered:
        intent = "suggest_next_best_action"
    elif "follow" in lowered or "schedule" in lowered:
        intent = "schedule_follow_up"
    elif any(
        phrase in lowered
        for phrase in [
            "compliance",
            "off-label",
            "off label",
            "unapproved",
            "unapproved indication",
            "promote",
            "promotion",
            "label",
        ]
    ):
        intent = "compliance_check"
    else:
        intent = "log_interaction"

    products = re.findall(r"\b(CardioMax|GlucoFree|Respira|NeuroCalm|Product X)\b", message, flags=re.I)
    hcp_match = re.search(r"\bDr\.?\s+([A-Z][a-zA-Z]+)\b", message)
    hcp_name = f"Dr. {hcp_match.group(1)}" if hcp_match else None
    sentiment = "Positive" if "positive" in lowered or "interested" in lowered else "Neutral"
    if "negative" in lowered or "concern" in lowered:
        sentiment = "Negative"
    materials = []
    if "brochure" in lowered:
        materials.append("Brochures")
    if "sample" in lowered or "starter kit" in lowered:
        materials.append("Samples")
    if "evidence" in lowered or "data" in lowered:
        materials.append("Clinical evidence")

    topics = []
    if "efficacy" in lowered:
        topics.append("efficacy")
    if "adherence" in lowered:
        topics.append("adherence")
    if "renal" in lowered:
        topics.append("renal safety")
    if "data" in lowered or "evidence" in lowered:
        topics.append("clinical evidence")
    if not topics:
        topics.append("practice needs")

    today = date.today().isoformat() if "today" in lowered else ""
    is_edit = intent == "edit_interaction"

    extracted = {
        "intent": intent,
        "hcp_id": hcp_id,
        "interaction_id": interaction_id,
        "hcp_name": hcp_name,
        "interaction_date": today,
        "interaction_time": "",
        "interaction_type": "Meeting",
        "attendees": "",
        "channel": "In-person" if "call" not in lowered and "email" not in lowered else "Call",
        "products_discussed": list(dict.fromkeys(products)),
        "topics_discussed": topics,
        "samples_dropped": [],
        "materials_shared": materials,
        "discussion_outcomes": "HCP requested follow-up material." if "requested" in lowered else "",
        "sentiment": sentiment,
        "notes": message,
        "follow_up_date": "",
        "follow_up_action": "Send approved clinical materials" if "data" in lowered or "evidence" in lowered else "",
        "summary": message[:220],
    }
    if is_edit:
        editable_keys = {"intent", "hcp_name", "sentiment", "interaction_id"}
        if "date" in lowered or "today" in lowered:
            editable_keys.add("interaction_date")
        if "brochure" in lowered:
            editable_keys.add("materials_shared")
        return {key: value for key, value in extracted.items() if key in editable_keys and value not in (None, "", [])}
    return extracted


def extract_with_groq(message: str, hcp_id: int | None = None, interaction_id: int | None = None) -> dict[str, Any]:
    if not settings.groq_api_key:
        return fallback_extract(message, hcp_id, interaction_id)

    model = ChatGroq(api_key=settings.groq_api_key, model=settings.groq_model, temperature=0)
    try:
        response = model.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=message)])
        content = str(response.content).strip()
        if content.startswith("```"):
            content = content.strip("`").replace("json", "", 1).strip()
        parsed = json.loads(content)

        print("=" * 50)
        print("Groq returned:", parsed)
        print("Original intent:", parsed.get("intent"))

        lowered = message.lower()

        # Override obvious intents if the LLM misclassifies them
        if "schedule" in lowered or "follow-up" in lowered or "follow up" in lowered:
            parsed["intent"] = "schedule_follow_up"

        elif "next best" in lowered:
            parsed["intent"] = "suggest_next_best_action"

        elif "profile" in lowered:
            parsed["intent"] = "retrieve_hcp_profile"

        elif any(word in lowered for word in ["edit", "update", "change", "actually"]):
            parsed["intent"] = "edit_interaction"

        elif any(
            phrase in lowered
            for phrase in [
                "compliance",
                "off-label",
                "off label",
                "unapproved",
                "unapproved indication",
                "promote",
                "promotion",
                "label",
            ]
        ):
            parsed["intent"] = "compliance_check"

        parsed.setdefault("hcp_id", hcp_id)
        parsed.setdefault("interaction_id", interaction_id)
        parsed.setdefault("notes", message)
        
        print("Final intent:", parsed.get("intent"))
        print("=" * 50)

        return parsed

    except Exception:
        if settings.groq_fallback_model and settings.groq_fallback_model != settings.groq_model:
            try:
                fallback_model = ChatGroq(
                    api_key=settings.groq_api_key,
                    model=settings.groq_fallback_model,
                    temperature=0,
                )
                response = fallback_model.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=message)])
                return json.loads(str(response.content).strip())
            except Exception:
                pass
        return fallback_extract(message, hcp_id, interaction_id)
