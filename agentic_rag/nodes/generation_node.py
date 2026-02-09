"""Generation node - generate final answer with authorization context."""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from ..state import AgenticRAGState
from ..config import get_config

GENERATION_PROMPT = """You are a helpful assistant that answers questions based on provided documents.

Generate a clear, accurate answer to the user's question based on the authorized documents.

IMPORTANT: Be transparent about authorization:
- If documents were denied, mention this in your answer
- If you don't have access to certain information, say so
- Explain what information you CAN provide

Context:
- Query: {query}
- Authorized documents: {authorized_count}
- Denied documents: {denied_count}
- Reasoning: {reasoning}

Documents:
{documents}

Generate a helpful answer that incorporates the authorization context."""


def generation_node(state: AgenticRAGState) -> dict:
    """Generate final answer incorporating authorization context.

    This node creates the final response, ensuring transparency
    about what information was accessible and what was denied.
    """
    config = get_config()

    llm = ChatOpenAI(model="gpt-4", temperature=0, api_key=config.openai_api_key)

    # Format documents
    if state["authorized_documents"]:
        docs_text = "\n\n".join(
            [
                f"Title: {doc.metadata['title']}\nContent: {doc.page_content}"
                for doc in state["authorized_documents"]
            ]
        )
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
            "reasoning": "\n".join(state.get("reasoning", [])),
            "documents": docs_text,
        }
    )

    return {
        "answer": result.content,
        "messages": [AIMessage(content=f"Answer: {result.content}")],
    }
