"""Simplified demo using mock documents to demonstrate authorization flow."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentic_rag.grpc_helpers import create_insecure_spicedb_client
from authzed.api.v1 import CheckPermissionRequest, ObjectReference, SubjectReference
from langchain_core.documents import Document

# Mock documents (same as in Weaviate)
MOCK_DOCS = {
    "eng-001": Document(
        page_content="Our system uses microservices architecture with event-driven patterns. We use Kubernetes for orchestration and PostgreSQL for primary data storage. Key principles: loose coupling, high cohesion, and clear service boundaries.",
        metadata={
            "doc_id": "eng-001",
            "title": "System Architecture Overview",
            "department": "engineering",
            "classification": "internal"
        }
    ),
    "eng-002": Document(
        page_content="Code review is mandatory for all changes. We use trunk-based development with feature flags. Testing pyramid: unit tests for logic, integration tests for APIs, E2E for critical paths.",
        metadata={
            "doc_id": "eng-002",
            "title": "Engineering Best Practices",
            "department": "engineering",
            "classification": "internal"
        }
    ),
    "hr-001": Document(
        page_content="Salary bands are reviewed quarterly. Performance reviews happen bi-annually. Benefits include health insurance, 401k matching, and unlimited PTO.",
        metadata={
            "doc_id": "hr-001",
            "title": "Employee Compensation Guidelines",
            "department": "hr",
            "classification": "confidential"
        }
    )
}


def check_authorization(subject_id: str, query: str):
    """Demonstrate authorization flow."""
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"User: {subject_id}")
    print('='*60)

    # Create SpiceDB client
    client = create_insecure_spicedb_client("localhost:50051", "devtoken")

    # Simulate retrieval - all documents match the query
    retrieved_docs = list(MOCK_DOCS.values())
    print(f"\n📥 Retrieved {len(retrieved_docs)} documents from search")

    # Authorization phase
    authorized_docs = []
    denied_docs = []

    for doc in retrieved_docs:
        doc_id = doc.metadata["doc_id"]

        # Check permission via SpiceDB
        request = CheckPermissionRequest(
            resource=ObjectReference(object_type="document", object_id=doc_id),
            permission="view",
            subject=SubjectReference(
                object=ObjectReference(object_type="user", object_id=subject_id)
            ),
        )

        response = client.CheckPermission(request)

        # Check if permission is granted
        # permissionship: 0=UNSPECIFIED, 1=NO_PERMISSION, 2=HAS_PERMISSION
        if response.permissionship == 2:
            authorized_docs.append(doc)
            print(f"  ✅ {doc_id}: {doc.metadata['title']} - AUTHORIZED")
        else:
            denied_docs.append(doc)
            print(f"  ❌ {doc_id}: {doc.metadata['title']} - DENIED")

    # Results
    print(f"\n📊 Authorization Results:")
    print(f"  - Total retrieved: {len(retrieved_docs)}")
    print(f"  - Authorized: {len(authorized_docs)}")
    print(f"  - Denied: {len(denied_docs)}")

    # Generate answer
    if authorized_docs:
        print(f"\n✨ Answer (based on {len(authorized_docs)} authorized documents):")
        print(f"  Based on the documents I have access to:")
        for doc in authorized_docs:
            print(f"  - {doc.metadata['title']}: {doc.page_content[:80]}...")
        if denied_docs:
            print(f"\n  Note: {len(denied_docs)} document(s) were not accessible due to permissions.")
    else:
        print(f"\n✨ Answer:")
        print(f"  I don't have access to any documents for this query.")
        print(f"  {len(denied_docs)} document(s) were denied due to permissions.")


def main():
    """Run authorization demo."""
    print("\n" + "="*60)
    print("Agentic RAG Authorization Demo (Simplified)")
    print("="*60)
    print("\nThis demo shows how SpiceDB enforces document-level permissions")
    print("without relying on Weaviate (using mock documents instead).\n")

    # Scenario 1: Alice (engineering) queries documents
    check_authorization("alice", "What are our system architecture best practices?")

    # Scenario 2: Bob (sales, not in engineering) queries documents
    check_authorization("bob", "What are the engineering system architecture details?")

    # Scenario 3: Alice queries HR documents
    check_authorization("alice", "What are the employee compensation guidelines?")

    # Scenario 4: HR manager queries HR documents
    check_authorization("hr_manager", "What are the employee compensation guidelines?")

    print("\n" + "="*60)
    print("✅ Demo Complete!")
    print("="*60)
    print("\nKey Takeaways:")
    print("  1. SpiceDB enforces permissions deterministically")
    print("  2. alice (engineering) can access eng-* documents")
    print("  3. bob (sales) cannot access engineering documents")
    print("  4. alice cannot access HR documents")
    print("  5. hr_manager can access HR documents")
    print("\nThe authorization logic is identical to what would run")
    print("in the full system - this just bypasses Weaviate's gRPC issues.")


if __name__ == "__main__":
    main()
