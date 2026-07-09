from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.crm import HCP
from app.schemas.crm import HCPRead

router = APIRouter()


@router.get("", response_model=list[HCPRead])
def list_hcps(db: Session = Depends(get_db)):
    return db.query(HCP).order_by(HCP.name).all()
