"""LangGraph StateGraph workflow assembly."""

import logging

from langgraph.graph import END, StateGraph

from app.langgraph.nodes import acknowledge_node, context_node, dispatcher_node, reasoning_node
from app.langgraph.state import AgentState

logger = logging.getLogger(__name__)


def build_workflow() -> StateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("acknowledge", acknowledge_node)
    workflow.add_node("context", context_node)
    workflow.add_node("reasoning", reasoning_node)
    workflow.add_node("dispatcher", dispatcher_node)

    workflow.set_entry_point("acknowledge")
    workflow.add_edge("acknowledge", "context")
    workflow.add_edge("context", "reasoning")
    workflow.add_edge("reasoning", "dispatcher")
    workflow.add_edge("dispatcher", END)

    return workflow


def compile_workflow():
    return build_workflow().compile()


async def run_agent_workflow(
    tenant_id: str,
    phone: str,
    message: str,
    message_id: str | None = None,
    customer_name: str | None = None,
    message_type: str | None = None,
    media_id: str | None = None,
    media_mime_type: str | None = None,
    caption: str | None = None,
    image_url: str | None = None,
    image_path: str | None = None,
) -> dict:
    """Execute the full LangGraph pipeline asynchronously."""
    graph = compile_workflow()
    initial_state: AgentState = {
        "tenant_id": tenant_id,
        "phone": phone,
        "message": message,
        "message_id": message_id,
        "customer_name": customer_name,
        "message_type": message_type,
        "media_id": media_id,
        "media_mime_type": media_mime_type,
        "caption": caption,
        "image_url": image_url,
        "image_path": image_path,
    }
    result = await graph.ainvoke(initial_state)
    logger.info("Workflow completed for %s", phone)
    return result
