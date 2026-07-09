from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agent.graph import run_agent
from app.core.database import get_db
from app.schemas.crm import AgentChatRequest, AgentChatResponse, InteractionCreate, InteractionUpdate, ToolDemoResponse
from app.services.tools import (
    compliance_check,
    edit_interaction,
    log_interaction,
    retrieve_hcp_profile,
    schedule_follow_up,
    suggest_next_best_action,
)

router = APIRouter()


@router.post("/chat", response_model=AgentChatResponse)
def chat_with_agent(payload: AgentChatRequest, db: Session = Depends(get_db)):
    result = run_agent(db, payload.message, payload.hcp_id, payload.interaction_id)
    return {
        "answer": result["answer"],
        "intent": result["intent"],
        "tool_name": result["tool_name"],
        "tool_result": result["tool_result"],
        "extracted": result["extracted"],
    }


@router.post("/tools/demo", response_model=ToolDemoResponse)
def demo_all_tools(db: Session = Depends(get_db)):
    log_result = log_interaction(
        db,
        InteractionCreate(
            hcp_id=1,
            channel="In-person",
            products_discussed=["CardioMax"],
            topics_discussed=["adherence", "renal safety"],
            samples_dropped=["Starter kit"],
            sentiment="Positive",
            notes="Dr. Patel asked for renal safety data and agreed to review approved CardioMax material.",
            follow_up_action="Send renal safety summary",
            follow_up_date="Next Tuesday",
        ),
    )
    interaction_id = log_result["interaction"]["id"]
    results = [
        retrieve_hcp_profile(db, 1),
        log_result,
        edit_interaction(db, interaction_id, InteractionUpdate(sentiment="Positive", topics_discussed=["adherence", "renal safety", "patient selection"])),
        suggest_next_best_action(db, 1),
        schedule_follow_up(db, 1, "Send approved renal safety data", "Next Tuesday"),
        compliance_check("No off-label claims were made. Do not guarantee outcomes."),
    ]
    return {"results": results}
