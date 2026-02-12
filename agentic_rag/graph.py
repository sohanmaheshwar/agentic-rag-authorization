"""LangGraph state machine for agentic RAG with authorization."""

from langgraph.graph import StateGraph, END
from .state import AgenticRAGState
from .nodes import (
    planning_node,
    retrieval_node,
    authorization_node,
    reasoning_node,
    generation_node,
)
from .validation import validate_query, validate_subject_id, ValidationError


def should_retry_or_generate(state: AgenticRAGState) -> str:
    """Decide whether to retry retrieval or generate answer.

    After reasoning about authorization failures, decide:
    - If attempts remain and no authorized docs: retry with new strategy
    - Otherwise: generate answer (possibly explaining access denial)
    """
    if (
        state["retrieval_attempt"] < state["max_attempts"]
        and len(state["authorized_documents"]) == 0
    ):
        return "plan"
    return "generate"


def should_reason_or_generate(state: AgenticRAGState) -> str:
    """Decide whether to reason about failures or generate answer.

    After authorization:
    - If we have authorized documents: generate answer
    - If no authorized documents: reason about what to do next
    """
    if state["authorization_passed"]:
        return "generate"
    return "reason"


def build_agentic_rag_graph():
    """Build the agentic RAG graph with deterministic authorization.

    Flow:
    1. Planning: Agent plans retrieval strategy
    2. Retrieval: Fetch documents from Weaviate
    3. Authorization: Deterministic permission check (security boundary)
    4. Conditional:
       - If authorized docs exist: Generate answer
       - If no authorized docs: Reason about what to do
    5. After reasoning:
       - If attempts remain: Retry with new plan
       - Otherwise: Generate answer explaining constraints
    """
    workflow = StateGraph(AgenticRAGState)

    # Add nodes
    workflow.add_node("plan", planning_node)
    workflow.add_node("retrieve", retrieval_node)
    workflow.add_node("authorize", authorization_node)  # ALWAYS runs
    workflow.add_node("reason", reasoning_node)
    workflow.add_node("generate", generation_node)

    # Define flow
    workflow.set_entry_point("plan")
    workflow.add_edge("plan", "retrieve")
    workflow.add_edge("retrieve", "authorize")  # Deterministic auth

    # Conditional: after auth, either reason or generate
    workflow.add_conditional_edges(
        "authorize",
        should_reason_or_generate,
        {
            "reason": "reason",
            "generate": "generate",
        },
    )

    # Conditional: after reasoning, retry or generate
    workflow.add_conditional_edges(
        "reason",
        should_retry_or_generate,
        {
            "plan": "plan",
            "generate": "generate",
        },
    )

    workflow.add_edge("generate", END)

    return workflow.compile()


def run_agentic_rag(query: str, subject_id: str, max_attempts: int = 1) -> dict:
    """
    Run the agentic RAG graph with input validation.

    This is the main entry point for running the agentic RAG system.
    It validates inputs before processing to ensure security and stability.

    Args:
        query: User query string
        subject_id: User/subject identifier for authorization
        max_attempts: Maximum number of retrieval attempts (default 1)

    Returns:
        Final state dict with answer and metadata

    Raises:
        ValidationError: If inputs are invalid
    """
    # Validate inputs
    query = validate_query(query)
    subject_id = validate_subject_id(subject_id)

    # Build graph
    graph = build_agentic_rag_graph()

    # Run graph
    initial_state = {
        "query": query,
        "subject_id": subject_id,
        "max_attempts": max_attempts,
        "retrieved_documents": [],
        "authorized_documents": [],
        "denied_count": 0,
        "reasoning": [],
        "retrieval_attempt": 0,
        "authorization_passed": False,
        "messages": [],
        "answer": None,
    }

    result = graph.invoke(initial_state)
    return result
