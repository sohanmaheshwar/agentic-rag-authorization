"""Initialize Weaviate and SpiceDB with sample data."""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path so we can import from agentic_rag
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import weaviate
from authzed.api.v1 import (
    WriteSchemaRequest,
    WriteRelationshipsRequest,
    Relationship,
    RelationshipUpdate,
    ObjectReference,
    SubjectReference,
)
from agentic_rag.grpc_helpers import create_insecure_spicedb_client
import json


def setup_spicedb():
    """Setup SpiceDB schema and relationships."""
    print("Setting up SpiceDB...")

    client = create_insecure_spicedb_client("localhost:50051", "devtoken")

    # Load schema
    schema_path = os.path.join(os.path.dirname(__file__), "..", "data", "schema.zed")
    with open(schema_path) as f:
        schema = f.read()

    client.WriteSchema(WriteSchemaRequest(schema=schema))
    print("  ✅ Schema loaded")

    # Create sample relationships
    updates = [
        # Alice is in engineering department
        RelationshipUpdate(
            operation=RelationshipUpdate.Operation.OPERATION_TOUCH,
            relationship=Relationship(
                resource=ObjectReference(
                    object_type="department", object_id="engineering"
                ),
                relation="member",
                subject=SubjectReference(
                    object=ObjectReference(object_type="user", object_id="alice")
                ),
            ),
        ),
        # Engineering documents are viewable by engineering department
        RelationshipUpdate(
            operation=RelationshipUpdate.Operation.OPERATION_TOUCH,
            relationship=Relationship(
                resource=ObjectReference(object_type="document", object_id="eng-001"),
                relation="viewer",
                subject=SubjectReference(
                    object=ObjectReference(
                        object_type="department",
                        object_id="engineering",
                    ),
                    optional_relation="member",
                ),
            ),
        ),
        RelationshipUpdate(
            operation=RelationshipUpdate.Operation.OPERATION_TOUCH,
            relationship=Relationship(
                resource=ObjectReference(object_type="document", object_id="eng-002"),
                relation="viewer",
                subject=SubjectReference(
                    object=ObjectReference(
                        object_type="department",
                        object_id="engineering",
                    ),
                    optional_relation="member",
                ),
            ),
        ),
        # HR document is only viewable by hr_manager
        RelationshipUpdate(
            operation=RelationshipUpdate.Operation.OPERATION_TOUCH,
            relationship=Relationship(
                resource=ObjectReference(object_type="document", object_id="hr-001"),
                relation="viewer",
                subject=SubjectReference(
                    object=ObjectReference(object_type="user", object_id="hr_manager")
                ),
            ),
        ),
    ]

    client.WriteRelationships(WriteRelationshipsRequest(updates=updates))
    print("  ✅ Relationships configured")
    print("  - alice: member of engineering department")
    print("  - eng-001, eng-002: viewable by engineering department")
    print("  - hr-001: viewable by hr_manager only")


def setup_weaviate():
    """Setup Weaviate with sample documents."""
    print("\nSetting up Weaviate...")

    # Connect to Weaviate v3 (REST API)
    client = weaviate.Client("http://127.0.0.1:8080")

    try:
        # Check if class exists and delete it
        try:
            client.schema.delete_class("Documents")
            print("  ✅ Deleted existing Documents class")
        except:
            pass

        # Create schema using v3 API (no vectorizer since we're using BM25 keyword search)
        schema = {
            "class": "Documents",
            "vectorizer": "none",  # Disable vectorization for BM25 keyword search
            "properties": [
                {"name": "doc_id", "dataType": ["text"]},
                {"name": "title", "dataType": ["text"]},
                {"name": "content", "dataType": ["text"]},
                {"name": "department", "dataType": ["text"]},
                {"name": "classification", "dataType": ["text"]},
            ],
        }
        client.schema.create_class(schema)
        print("  ✅ Documents class created")

        # Load sample documents
        docs_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "sample_docs.json"
        )
        with open(docs_path) as f:
            docs = json.load(f)

        # Insert documents using v3 API
        with client.batch as batch:
            for doc in docs:
                batch.add_data_object(
                    data_object=doc,
                    class_name="Documents",
                )

        print(f"  ✅ Inserted {len(docs)} documents:")
        for doc in docs:
            print(f"    - {doc['doc_id']}: {doc['title']} ({doc['department']})")

    finally:
        pass  # v3 client doesn't need explicit close


def main():
    """Run setup."""
    print("=" * 60)
    print("Agentic RAG with Authorization - Environment Setup")
    print("=" * 60)

    setup_spicedb()
    setup_weaviate()

    print("\n" + "=" * 60)
    print("✅ Setup complete!")
    print("=" * 60)
    print("\nYou can now run: python examples/basic_example.py")


if __name__ == "__main__":
    main()
