"""Retrieval node - retrieve documents from Weaviate."""

from langchain_core.messages import SystemMessage
from ..state import AgenticRAGState
from ..config import get_config
import weaviate
from langchain_core.documents import Document


def retrieval_node(state: AgenticRAGState) -> dict:
    """Retrieve documents from Weaviate based on query.

    This node performs keyword search in Weaviate to find
    relevant documents. Authorization happens in the next node.
    """
    config = get_config()

    # Connect to Weaviate v3 (uses REST API, no gRPC issues)
    weaviate_client = weaviate.Client("http://127.0.0.1:8080")

    try:
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

        return {
            "retrieved_documents": documents,
            "messages": [
                SystemMessage(
                    content=f"Retrieved {len(documents)} documents from Weaviate"
                )
            ],
        }

    finally:
        pass  # v3 client doesn't need explicit close
