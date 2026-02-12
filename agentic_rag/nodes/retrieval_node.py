"""Retrieval node - retrieve documents from Weaviate."""

import time
from langchain_core.messages import SystemMessage
from ..state import AgenticRAGState
from ..config import get_config
from langchain_core.documents import Document
from ..logging_config import get_logger
from ..weaviate_client import get_weaviate_client

logger = get_logger("nodes.retrieval")


def retrieval_node(state: AgenticRAGState) -> dict:
    """Retrieve documents from Weaviate based on query.

    This node performs keyword search in Weaviate to find
    relevant documents. Authorization happens in the next node.
    """
    start_time = time.time()

    logger.info(
        "Starting retrieval",
        extra={
            "query": state["query"],
            "subject_id": state["subject_id"],
        },
    )

    config = get_config()

    try:
        # Get or create Weaviate client (reused across requests)
        weaviate_client = get_weaviate_client(config.weaviate_url)

        # Perform BM25 keyword search using v3 API
        response = (
            weaviate_client.query.get("Documents", ["doc_id", "title", "content", "department", "classification"])
            .with_bm25(query=state["query"])
            .with_limit(5)
            .do()
        )

        # Extract results
        results = response.get("data", {}).get("Get", {}).get("Documents", [])

        # Convert to LangChain Documents
        documents = [
            Document(
                page_content=result["content"],
                metadata={
                    "doc_id": result["doc_id"],
                    "title": result["title"],
                    "department": result["department"],
                    "classification": result["classification"],
                },
            )
            for result in results
        ]

        duration_ms = (time.time() - start_time) * 1000

        logger.info(
            "Retrieval complete",
            extra={
                "query": state["query"],
                "document_count": len(documents),
                "doc_ids": [doc.metadata.get("doc_id") for doc in documents],
                "duration_ms": duration_ms,
            },
        )

        return {
            "retrieved_documents": documents,
            "messages": [
                SystemMessage(
                    content=f"Retrieved {len(documents)} documents from Weaviate"
                )
            ],
        }

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000

        logger.error(
            "Retrieval failed",
            extra={
                "query": state["query"],
                "error": str(e),
                "error_type": type(e).__name__,
                "duration_ms": duration_ms,
            },
            exc_info=True,
        )

        # Fail gracefully - return empty results
        return {
            "retrieved_documents": [],
            "messages": [
                SystemMessage(
                    content=f"Retrieval failed: {str(e)}. Unable to retrieve documents."
                )
            ],
        }
