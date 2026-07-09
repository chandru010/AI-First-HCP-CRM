from app.models.crm import Interaction


def split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def join_csv(value: list[str] | None) -> str:
    return ", ".join(value or [])


def interaction_to_read(interaction: Interaction) -> dict:
    return {
        "id": interaction.id,
        "hcp_id": interaction.hcp_id,
        "hcp_name": interaction.hcp.name,
        "interaction_date": interaction.interaction_date,
        "channel": interaction.channel,
        "products_discussed": split_csv(interaction.products_discussed),
        "topics_discussed": split_csv(interaction.topics_discussed),
        "samples_dropped": split_csv(interaction.samples_dropped),
        "sentiment": interaction.sentiment,
        "notes": interaction.notes,
        "summary": interaction.summary,
        "follow_up_date": interaction.follow_up_date,
        "follow_up_action": interaction.follow_up_action,
        "compliance_flags": split_csv(interaction.compliance_flags),
        "created_at": interaction.created_at,
        "updated_at": interaction.updated_at,
    }
