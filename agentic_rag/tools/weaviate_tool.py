"""Weaviate search tool for agent."""

from typing import List
from langchain_core.tools import BaseTool
from langchain_core.documents import Document
from pydantic import BaseModel, Field
import weaviate
from weaviate.classes.query import MetadataQuery


class WeaviateSearchInput(BaseModel):
    """Input for Weaviate search tool."""

    query: str = Field(description="The search query")
    limit: int = Field(default=5, description="Number of documents to retrieve")


class WeaviateSearchTool(BaseTool):
    """Tool for searching documents in Weaviate."""

    name: str = "search_documents"
    description: str = (
        "Search for documents in the knowledge base using semantic search. "
        "Returns relevant documents based on the query."
    )
    args_schema: type[BaseModel] = WeaviateSearchInput

    weaviate_client: weaviate.WeaviateClient

    class Config:
        arbitrary_types_allowed = True

    def _run(self, query: str, limit: int = 5) -> List[Document]:
        """Search Weaviate for documents (sync version)."""
        collection = self.weaviate_client.collections.get("Documents")

        response = collection.query.bm25(
            query=query, limit=limit, return_metadata=MetadataQuery(score=True)
        )

        # Convert to LangChain Documents
        documents = [
            Document(
                page_content=obj.properties["content"],
                metadata={
                    "doc_id": obj.properties["doc_id"],
                    "title": obj.properties["title"],
                    "department": obj.properties["department"],
                    "classification": obj.properties["classification"],
                },
            )
            for obj in response.objects
        ]

        return documents

    async def _arun(self, query: str, limit: int = 5) -> List[Document]:
        """Search Weaviate for documents (async version)."""
        # For simplicity, we'll use sync version
        # In production, use async Weaviate client
        return self._run(query, limit)


def get_weaviate_search_tool(weaviate_client: weaviate.WeaviateClient) -> WeaviateSearchTool:
    """Create a Weaviate search tool instance."""
    return WeaviateSearchTool(weaviate_client=weaviate_client)
