from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.models.crm import HCP, Interaction
from app.schemas.crm import InteractionCreate, InteractionUpdate
from app.services.serializers import interaction_to_read, join_csv


COMPLIANCE_TERMS = {
    "off-label": "Potential off-label discussion detected.",
    "guarantee": "Avoid guaranteed outcome claims.",
    "cash": "Potential improper inducement language detected.",
    "gift": "Gift language may need compliance review.",
}


def make_summary(notes: str, topics: list[str], products: list[str]) -> str:
    topic_text = ", ".join(topics) if topics else "general practice needs"
    product_text = ", ".join(products) if products else "portfolio"
    return f"Discussed {product_text} with focus on {topic_text}. Notes: {notes[:180]}"


def compliance_check(text: str) -> dict[str, Any]:
    lowered = text.lower()
    flags = [message for term, message in COMPLIANCE_TERMS.items() if term in lowered]
    return {
        "tool": "compliance_check",
        "status": "review" if flags else "clear",
        "flags": flags,
        "message": "Compliance review recommended." if flags else "No obvious compliance flags found.",
    }


def retrieve_hcp_profile(db: Session, hcp_id: int) -> dict[str, Any]:
    hcp = db.get(HCP, hcp_id)
    if not hcp:
        return {"tool": "retrieve_hcp_profile", "error": "HCP not found"}
    return {
        "tool": "retrieve_hcp_profile",
        "hcp": {
            "id": hcp.id,
            "name": hcp.name,
            "specialty": hcp.specialty,
            "territory": hcp.territory,
            "segment": hcp.segment,
            "preferred_channel": hcp.preferred_channel,
            "last_interaction_summary": hcp.last_interaction_summary,
        },
    }


def log_interaction(db: Session, payload: InteractionCreate, extracted_summary: str = "") -> dict[str, Any]:
    compliance = compliance_check(payload.notes)
    summary = extracted_summary or make_summary(
        payload.notes,
        payload.topics_discussed,
        payload.products_discussed,
    )
    interaction = Interaction(
        hcp_id=payload.hcp_id,
        interaction_date=payload.interaction_date or datetime.utcnow(),
        channel=payload.channel,
        products_discussed=join_csv(payload.products_discussed),
        topics_discussed=join_csv(payload.topics_discussed),
        samples_dropped=join_csv(payload.samples_dropped),
        sentiment=payload.sentiment,
        notes=payload.notes,
        summary=summary,
        follow_up_date=payload.follow_up_date,
        follow_up_action=payload.follow_up_action,
        compliance_flags=join_csv(compliance["flags"]),
    )
    db.add(interaction)
    hcp = db.get(HCP, payload.hcp_id)
    if hcp:
        hcp.last_interaction_summary = summary
    db.commit()
    db.refresh(interaction)
    return {
        "tool": "log_interaction",
        "interaction": interaction_to_read(interaction),
        "compliance": compliance,
    }


def edit_interaction(db: Session, interaction_id: int, patch: InteractionUpdate) -> dict[str, Any]:
    interaction = db.get(Interaction, interaction_id)
    if not interaction:
        return {"tool": "edit_interaction", "error": "Interaction not found"}

    data = patch.model_dump(exclude_unset=True)
    for key, value in data.items():
        if value is None:
            continue
        if key in {"products_discussed", "topics_discussed", "samples_dropped"}:
            setattr(interaction, key, join_csv(value))
        else:
            setattr(interaction, key, value)

    interaction.updated_at = datetime.utcnow()
    interaction.compliance_flags = join_csv(compliance_check(interaction.notes)["flags"])
    interaction.summary = make_summary(
        interaction.notes,
        interaction.topics_discussed.split(", ") if interaction.topics_discussed else [],
        interaction.products_discussed.split(", ") if interaction.products_discussed else [],
    )
    db.commit()
    db.refresh(interaction)
    return {"tool": "edit_interaction", "interaction": interaction_to_read(interaction)}


def suggest_next_best_action(db: Session, hcp_id: int) -> dict[str, Any]:
    hcp = db.get(HCP, hcp_id)
    if not hcp:
        return {"tool": "suggest_next_best_action", "error": "HCP not found"}
    latest = (
        db.query(Interaction)
        .filter(Interaction.hcp_id == hcp_id)
        .order_by(Interaction.interaction_date.desc())
        .first()
    )
    if latest and "positive" in latest.sentiment.lower():
        action = "Send requested clinical evidence and ask for patient profile fit in the next visit."
    elif latest and "negative" in latest.sentiment.lower():
        action = "Schedule a short objection-handling follow-up with approved medical information."
    else:
        action = f"Use {hcp.preferred_channel} to share a concise specialty-relevant value message."
    return {"tool": "suggest_next_best_action", "hcp_id": hcp_id, "recommendation": action}


def schedule_follow_up(db: Session, hcp_id: int, action: str, date_text: str = "") -> dict[str, Any]:
    hcp = db.get(HCP, hcp_id)
    if not hcp:
        return {"tool": "schedule_follow_up", "error": "HCP not found"}
    follow_up_date = date_text or (datetime.utcnow() + timedelta(days=7)).date().isoformat()
    return {
        "tool": "schedule_follow_up",
        "hcp_id": hcp_id,
        "hcp_name": hcp.name,
        "follow_up_date": follow_up_date,
        "action": action or "Follow up with approved clinical material.",
    }
