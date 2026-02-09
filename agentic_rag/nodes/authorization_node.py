"""Authorization node - deterministic permission filtering via SpiceDB."""

from langchain_core.messages import SystemMessage
from ..state import AgenticRAGState
from ..config import get_config
from authzed.api.v1 import (
    CheckPermissionRequest,
    ObjectReference,
    SubjectReference,
)
from ..grpc_helpers import create_insecure_spicedb_client


def authorization_node(state: AgenticRAGState) -> dict:
    """
    Deterministic authorization node - ALWAYS runs, cannot be bypassed.

    This node filters retrieved documents based on SpiceDB permissions.
    This is a security boundary - the agent cannot bypass this check.
    """
    config = get_config()

    # Initialize SpiceDB client (insecure for local development)
    client = create_insecure_spicedb_client(
        config.spicedb_endpoint,
        config.spicedb_token,
    )

    # Filter documents by permissions
    authorized_docs = []
    for doc in state["retrieved_documents"]:
        doc_id = doc.metadata.get("doc_id")

        # Check permission via SpiceDB
        request = CheckPermissionRequest(
            resource=ObjectReference(object_type="document", object_id=doc_id),
            permission="view",
            subject=SubjectReference(
                object=ObjectReference(object_type="user", object_id=state["subject_id"])
            ),
        )

        response = client.CheckPermission(request)

        # Check if permission is granted
        # permissionship: 0=UNSPECIFIED, 1=NO_PERMISSION, 2=HAS_PERMISSION
        if response.permissionship == 2:
            authorized_docs.append(doc)

    denied_count = len(state["retrieved_documents"]) - len(authorized_docs)

    return {
        "authorized_documents": authorized_docs,
        "denied_count": denied_count,
        "authorization_passed": len(authorized_docs) > 0,
        "messages": [
            SystemMessage(
                content=f"Authorization: {len(authorized_docs)}/{len(state['retrieved_documents'])} documents authorized"
            )
        ],
    }
