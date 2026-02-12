"""Authorization node - deterministic permission filtering via SpiceDB."""

import time
from langchain_core.messages import SystemMessage
from ..state import AgenticRAGState
from ..config import get_config
from ..grpc_helpers import get_spicedb_client
from ..logging_config import get_logger
from ..authorization_helpers import batch_check_permissions

logger = get_logger("nodes.authorization")


def authorization_node(state: AgenticRAGState) -> dict:
    """
    Deterministic authorization node - ALWAYS runs, cannot be bypassed.

    This node filters retrieved documents based on SpiceDB permissions.
    This is a security boundary - the agent cannot bypass this check.
    """
    start_time = time.time()

    logger.info(
        "Starting authorization",
        extra={
            "subject_id": state["subject_id"],
            "document_count": len(state["retrieved_documents"]),
        },
    )

    config = get_config()

    # Get or create SpiceDB client (reused across requests)
    client = get_spicedb_client(
        config.spicedb_endpoint,
        config.spicedb_token,
    )

    # Batch check permissions using SpiceDB's bulk API
    authorized_docs, denied_doc_ids = batch_check_permissions(
        client,
        state["subject_id"],
        state["retrieved_documents"],
    )

    denied_count = len(denied_doc_ids)
    duration_ms = (time.time() - start_time) * 1000

    logger.info(
        "Authorization complete",
        extra={
            "subject_id": state["subject_id"],
            "authorized": len(authorized_docs),
            "denied": denied_count,
            "denied_doc_ids": denied_doc_ids,
            "duration_ms": duration_ms,
        },
    )

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
