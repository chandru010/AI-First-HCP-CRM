from typing import Any, TypedDict

from langgraph.graph import END, StateGraph
from sqlalchemy.orm import Session

from app.agent.llm import extract_with_groq
from app.schemas.crm import InteractionCreate, InteractionUpdate
from app.services.tools import (
    compliance_check,
    edit_interaction,
    log_interaction,
    retrieve_hcp_profile,
    schedule_follow_up,
    suggest_next_best_action,
)


class AgentState(TypedDict, total=False):
    message: str
    hcp_id: int | None
    interaction_id: int | None
    extracted: dict[str, Any]
    intent: str
    tool_name: str
    tool_result: dict[str, Any]
    answer: str


def build_agent_graph(db: Session):
    graph = StateGraph(AgentState)

    def understand(state: AgentState) -> AgentState:
        extracted = extract_with_groq(state["message"], state.get("hcp_id"), state.get("interaction_id"))

        print("Original intent:", extracted.get("intent"))

        lowered = state["message"].lower()

        if "schedule" in lowered or "follow-up" in lowered or "follow up" in lowered:
            extracted["intent"] = "schedule_follow_up"

        elif "next best" in lowered:
             extracted["intent"] = "suggest_next_best_action"

        elif "profile" in lowered:
            extracted["intent"] = "retrieve_hcp_profile"

        elif any(x in lowered for x in ["edit", "update", "change", "actually"]):
             extracted["intent"] = "edit_interaction"

        elif "compliance" in lowered or "off-label" in lowered:
            extracted["intent"] = "compliance_check"

        print("Final intent:", extracted.get("intent"))

        print("LLM OUTPUT:", extracted)
        return {
            **state,
            "extracted": extracted,
            "intent": extracted.get("intent", "log_interaction"),
        }

    def execute_tool(state: AgentState) -> AgentState:
        extracted = state["extracted"]
        intent = state["intent"]
        hcp_id = extracted.get("hcp_id") or state.get("hcp_id") or 1

        if intent == "retrieve_hcp_profile":
            result = retrieve_hcp_profile(db, int(hcp_id))
        elif intent == "edit_interaction":
            result = edit_interaction(
                db,
                int(extracted.get("interaction_id") or state.get("interaction_id") or 0),
                InteractionUpdate(
                    channel=extracted.get("channel"),
                    products_discussed=extracted.get("products_discussed"),
                    topics_discussed=extracted.get("topics_discussed"),
                    samples_dropped=extracted.get("samples_dropped"),
                    sentiment=extracted.get("sentiment"),
                    notes=extracted.get("notes"),
                    follow_up_date=extracted.get("follow_up_date"),
                    follow_up_action=extracted.get("follow_up_action"),
                ),
            )
        elif intent == "suggest_next_best_action":
            result = suggest_next_best_action(db, int(hcp_id))
        elif intent == "schedule_follow_up":
            result = schedule_follow_up(
                db,
                int(hcp_id),
                extracted.get("follow_up_action", ""),
                extracted.get("follow_up_date", ""),
            )
        elif intent == "compliance_check":
            result = compliance_check(extracted.get("notes") or state["message"])
        else:
            result = log_interaction(
                db,
                InteractionCreate(
                    hcp_id=int(hcp_id),
                    channel=extracted.get("channel") or "In-person",
                    products_discussed=extracted.get("products_discussed") or [],
                    topics_discussed=extracted.get("topics_discussed") or [],
                    samples_dropped=extracted.get("samples_dropped") or [],
                    sentiment=extracted.get("sentiment") or "Neutral",
                    notes=extracted.get("notes") or state["message"],
                    follow_up_date=extracted.get("follow_up_date") or "",
                    follow_up_action=extracted.get("follow_up_action") or "",
                ),
                extracted.get("summary", ""),
            )
            result["draft"] = extracted

        return {
            **state,
            "tool_name": result.get("tool", intent),
            "tool_result": result,
        }

    def respond(state: AgentState) -> AgentState:
        tool_name = state.get("tool_name", "unknown_tool")
        result = state.get("tool_result", {})
        if "error" in result:
            answer = f"I tried to run {tool_name}, but {result['error']}."
        elif tool_name == "log_interaction":
            interaction = result["interaction"]
            answer = f"Logged interaction #{interaction['id']} for {interaction['hcp_name']} with {interaction['sentiment']} sentiment."
        elif tool_name == "edit_interaction":
            interaction = result["interaction"]
            answer = f"Updated interaction #{interaction['id']}."
        elif tool_name == "suggest_next_best_action":
            answer = result["recommendation"]
        elif tool_name == "schedule_follow_up":
            answer = f"Follow-up scheduled for {result['follow_up_date']}: {result['action']}"
        elif tool_name == "compliance_check":
            answer = result["message"]
        else:
            answer = "Here is the requested HCP profile."
        return {**state, "answer": answer}

    graph.add_node("understand", understand)
    graph.add_node("execute_tool", execute_tool)
    graph.add_node("respond", respond)
    graph.set_entry_point("understand")
    graph.add_edge("understand", "execute_tool")
    graph.add_edge("execute_tool", "respond")
    graph.add_edge("respond", END)
    return graph.compile()


def run_agent(db: Session, message: str, hcp_id: int | None = None, interaction_id: int | None = None) -> AgentState:
    agent = build_agent_graph(db)
    return agent.invoke({"message": message, "hcp_id": hcp_id, "interaction_id": interaction_id})
