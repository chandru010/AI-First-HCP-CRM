from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class HCP(Base):
    __tablename__ = "hcps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    specialty: Mapped[str] = mapped_column(String(120), nullable=False)
    territory: Mapped[str] = mapped_column(String(120), nullable=False)
    segment: Mapped[str] = mapped_column(String(50), nullable=False, default="B")
    preferred_channel: Mapped[str] = mapped_column(String(50), nullable=False, default="In-person")
    last_interaction_summary: Mapped[str] = mapped_column(Text, nullable=False, default="")

    interactions: Mapped[list["Interaction"]] = relationship(back_populates="hcp")


class Interaction(Base):
    __tablename__ = "interactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    hcp_id: Mapped[int] = mapped_column(ForeignKey("hcps.id"), nullable=False)
    interaction_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    products_discussed: Mapped[str] = mapped_column(Text, nullable=False, default="")
    topics_discussed: Mapped[str] = mapped_column(Text, nullable=False, default="")
    samples_dropped: Mapped[str] = mapped_column(Text, nullable=False, default="")
    sentiment: Mapped[str] = mapped_column(String(30), nullable=False, default="Neutral")
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    follow_up_date: Mapped[str] = mapped_column(String(40), nullable=False, default="")
    follow_up_action: Mapped[str] = mapped_column(Text, nullable=False, default="")
    compliance_flags: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    hcp: Mapped[HCP] = relationship(back_populates="interactions")
