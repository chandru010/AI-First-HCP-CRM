from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.crm import Interaction
from app.schemas.crm import InteractionCreate, InteractionRead, InteractionUpdate
from app.services.serializers import interaction_to_read
from app.services.tools import edit_interaction, log_interaction

router = APIRouter()


@router.get("", response_model=list[InteractionRead])
def list_interactions(db: Session = Depends(get_db)):
    interactions = db.query(Interaction).order_by(Interaction.interaction_date.desc()).all()
    return [interaction_to_read(item) for item in interactions]


@router.post("", response_model=InteractionRead)
def create_interaction(payload: InteractionCreate, db: Session = Depends(get_db)):
    result = log_interaction(db, payload)
    return result["interaction"]


@router.patch("/{interaction_id}", response_model=InteractionRead)
def update_interaction(interaction_id: int, payload: InteractionUpdate, db: Session = Depends(get_db)):
    result = edit_interaction(db, interaction_id, payload)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result["interaction"]
