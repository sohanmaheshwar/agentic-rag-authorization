"""Basic example showing agentic RAG with authorization."""

import sys
import os

# Add parent directory to path so we can import from agentic_rag
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from agentic_rag.graph import build_agentic_rag_graph
from agentic_rag.config import get_config


async def run_query(graph, query: str, subject_id: str):
    """Run a single query through the agentic RAG system."""
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"User: {subject_id}")
    print('='*60)

    result = await graph.ainvoke(
        {
            "query": query,
            "subject_id": subject_id,
            "max_attempts": 3,
            "retrieval_attempt": 0,
            "messages": [],
            "reasoning": [],
            "retrieved_documents": [],
            "authorized_documents": [],
            "denied_count": 0,
            "authorization_passed": False,
            "answer": "",
        }
    )

    print(f"\n📊 Results:")
    print(f"  - Retrieved: {len(result['retrieved_documents'])} documents")
    print(f"  - Authorized: {len(result['authorized_documents'])} documents")
    print(f"  - Denied: {result['denied_count']} documents")
    print(f"  - Attempts: {result['retrieval_attempt']}")

    if result['authorized_documents']:
        print(f"\n📄 Authorized Documents:")
        for doc in result['authorized_documents']:
            print(f"  - {doc.metadata['doc_id']}: {doc.metadata['title']}")

    print(f"\n💭 Agent Reasoning:")
    for i, reasoning in enumerate(result['reasoning'], 1):
        print(f"  {i}. {reasoning[:100]}...")

    print(f"\n✨ Answer:")
    print(f"{result['answer']}")
    print()

    return result


async def main():
    """Run basic examples."""
    config = get_config()

    if not config.openai_api_key:
        print("❌ Error: OPENAI_API_KEY not set")
        print("Please set it in your .env file or environment")
        return

    print("\n" + "="*60)
    print("Agentic RAG with Authorization - Basic Examples")
    print("="*60)

    # Build graph
    graph = build_agentic_rag_graph()

    # Example 1: Alice (engineering) queries engineering documents
    await run_query(
        graph,
        "What are our system architecture best practices?",
        "alice"
    )

    # Example 2: Bob (not in engineering) queries engineering documents
    await run_query(
        graph,
        "What are the engineering system architecture details?",
        "bob"
    )

    # Example 3: Alice queries HR documents (should be denied)
    await run_query(
        graph,
        "What are the employee compensation guidelines?",
        "alice"
    )

    # Example 4: HR manager queries HR documents
    await run_query(
        graph,
        "What are the employee compensation guidelines?",
        "hr_manager"
    )


if __name__ == "__main__":
    asyncio.run(main())
