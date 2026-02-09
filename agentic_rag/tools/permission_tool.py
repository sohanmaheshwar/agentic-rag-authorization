"""Permission checking tool for agent."""

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from authzed.api.v1 import (
    CheckPermissionRequest,
    ObjectReference,
    SubjectReference,
)
from ..grpc_helpers import create_insecure_spicedb_client


class PermissionCheckInput(BaseModel):
    """Input for permission check tool."""

    subject_id: str = Field(description="The user ID to check permissions for")
    resource_id: str = Field(description="The document ID to check permissions on")
    permission: str = Field(
        default="view", description="The permission to check (default: view)"
    )


class PermissionCheckTool(BaseTool):
    """Tool for checking permissions via SpiceDB."""

    name: str = "check_permission"
    description: str = (
        "Check if a user has permission to access a specific document. "
        "Returns True if the user has the permission, False otherwise."
    )
    args_schema: type[BaseModel] = PermissionCheckInput

    spicedb_endpoint: str
    spicedb_token: str

    def _run(
        self, subject_id: str, resource_id: str, permission: str = "view"
    ) -> bool:
        """Check permission (sync version)."""
        client = create_insecure_spicedb_client(
            self.spicedb_endpoint,
            self.spicedb_token,
        )

        request = CheckPermissionRequest(
            resource=ObjectReference(object_type="document", object_id=resource_id),
            permission=permission,
            subject=SubjectReference(
                object=ObjectReference(object_type="user", object_id=subject_id)
            ),
        )

        response = client.CheckPermission(request)
        # permissionship: 0=UNSPECIFIED, 1=NO_PERMISSION, 2=HAS_PERMISSION
        return response.permissionship == 2

    async def _arun(
        self, subject_id: str, resource_id: str, permission: str = "view"
    ) -> bool:
        """Check permission (async version)."""
        # For simplicity, use sync version
        return self._run(subject_id, resource_id, permission)


def get_permission_tool(spicedb_endpoint: str, spicedb_token: str) -> PermissionCheckTool:
    """Create a permission check tool instance."""
    return PermissionCheckTool(
        spicedb_endpoint=spicedb_endpoint, spicedb_token=spicedb_token
    )
