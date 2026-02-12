"""Planning node - agent plans retrieval strategy."""

import time
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from ..state import AgenticRAGState
from ..config import get_config
from ..logging_config import get_logger

logger = get_logger("nodes.planning")

PLANNING_PROMPT = """You are a retrieval planning agent. Your job is to plan how to retrieve documents to answer the user's query.

Consider:
1. What type of documents are needed?
2. How many documents should be retrieved?
3. What search terms should be used?

Be concise and specific in your plan.

Query: {query}
User: {subject_id}"""


def planning_node(state: AgenticRAGState) -> dict:
    """Agent plans retrieval strategy.

    For simplicity, this uses an LLM to generate a plan without tool calling.
    The plan helps the agent reason about the retrieval strategy.
    """
    start_time = time.time()

    logger.info(
        "Starting planning",
        extra={
            "subject_id": state["subject_id"],
            "query": state["query"],
            "attempt": state.get("retrieval_attempt", 0) + 1,
        },
    )

    config = get_config()

    llm = ChatOpenAI(model="gpt-4", temperature=0, api_key=config.openai_api_key)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", PLANNING_PROMPT),
        ]
    )

    chain = prompt | llm

    result = chain.invoke(
        {
            "query": state["query"],
            "subject_id": state["subject_id"],
        }
    )

    current_attempt = state.get("retrieval_attempt", 0) + 1
    reasoning = state.get("reasoning", [])
    reasoning.append(result.content)

    duration_ms = (time.time() - start_time) * 1000

    logger.info(
        "Planning complete",
        extra={
            "subject_id": state["subject_id"],
            "attempt": current_attempt,
            "plan_length": len(result.content),
            "duration_ms": duration_ms,
        },
    )

    return {
        "reasoning": reasoning,
        "retrieval_attempt": current_attempt,
        "messages": [AIMessage(content=f"Planning: {result.content}")],
    }
