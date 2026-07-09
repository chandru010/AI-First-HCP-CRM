from app.core.database import SessionLocal
from app.models.crm import HCP


def seed_demo_data() -> None:
    db = SessionLocal()
    try:
        demo_hcps = [
            HCP(
                name="Dr. Smith",
                specialty="General Physician",
                territory="Demo Territory",
                segment="B",
                preferred_channel="In-person",
                last_interaction_summary="Demo HCP for AI-filled interaction logging.",
            ),
            HCP(
                name="Dr. John",
                specialty="General Physician",
                territory="Demo Territory",
                segment="B",
                preferred_channel="In-person",
                last_interaction_summary="Demo HCP for edit-interaction correction flow.",
            ),
            HCP(
                name="Dr. Meera Patel",
                specialty="Cardiologist",
                territory="Mumbai Central",
                segment="A",
                preferred_channel="In-person",
                last_interaction_summary="Asked for comparative adherence data for CardioMax.",
            ),
            HCP(
                name="Dr. Arjun Rao",
                specialty="Endocrinologist",
                territory="Bengaluru East",
                segment="A",
                preferred_channel="WhatsApp",
                last_interaction_summary="Interested in diabetes patient education kits.",
            ),
            HCP(
                name="Dr. Nisha Shah",
                specialty="Pulmonologist",
                territory="Delhi South",
                segment="B",
                preferred_channel="Email",
                last_interaction_summary="Prefers concise clinical summaries before visits.",
            ),
        ]
        existing_names = {name for (name,) in db.query(HCP.name).all()}
        db.add_all([hcp for hcp in demo_hcps if hcp.name not in existing_names])
        db.commit()
    finally:
        db.close()
