"""Generation node - generate final answer with authorization context."""

import time
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from ..state import AgenticRAGState
from ..config import get_config
from ..logging_config import get_logger

logger = get_logger("nodes.generation")

GENERATION_PROMPT = """You are a helpful assistant that answers questions based ONLY on the provided documents.

CRITICAL INSTRUCTIONS:
1. ONLY use information explicitly stated in the documents below
2. DO NOT use any external knowledge or information from your training
3. DO NOT make inferences or extrapolations beyond what's written
4. If the documents don't contain the answer, say "The provided documents do not contain this information"
5. Quote or paraphrase directly from the documents when answering

Authorization Context:
- Query: {query}
- Authorized documents: {authorized_count}
- Denied documents: {denied_count}

{documents}

Generate an answer using ONLY the information from the documents above. If documents were denied, mention that some information was not accessible due to permissions."""


def generation_node(state: AgenticRAGState) -> dict:
    """Generate final answer incorporating authorization context.

    This node creates the final response, ensuring transparency
    about what information was accessible and what was denied.
    """
    start_time = time.time()

    logger.info(
        "Starting generation",
        extra={
            "subject_id": state["subject_id"],
            "authorized_count": len(state["authorized_documents"]),
            "denied_count": state["denied_count"],
        },
    )

    config = get_config()

    llm = ChatOpenAI(model="gpt-4", temperature=0, api_key=config.openai_api_key)

    # Format documents with clear boundaries
    if state["authorized_documents"]:
        doc_parts = []
        for i, doc in enumerate(state["authorized_documents"], 1):
            doc_parts.append(
                f"--- Document {i} ---\n"
                f"Title: {doc.metadata['title']}\n"
                f"Content: {doc.page_content}\n"
                f"--- End Document {i} ---"
            )
        docs_text = "\n\n".join(doc_parts)
    else:
        docs_text = "No authorized documents available."

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", GENERATION_PROMPT),
        ]
    )

    chain = prompt | llm

    result = chain.invoke(
        {
            "query": state["query"],
            "authorized_count": len(state["authorized_documents"]),
            "denied_count": state["denied_count"],
            "documents": docs_text,
        }
    )

    duration_ms = (time.time() - start_time) * 1000

    logger.info(
        "Generation complete",
        extra={
            "subject_id": state["subject_id"],
            "answer_length": len(result.content),
            "duration_ms": duration_ms,
        },
    )

    return {
        "answer": result.content,
        "messages": [AIMessage(content=f"Answer: {result.content}")],
    }
