from typing import Annotated, Any, Dict, List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from src.core.i18n import _
from src.shared.exceptions import AccessDeniedError
from src.shared.infrastructure.auth_service_adapter.container import (
    AuthServiceContainer,
)
from src.shared.infrastructure.auth_service_adapter.interfaces.auth_service_repository_interface import (
    AuthServiceRepositoryInterface,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@inject
async def get_permissions(
    auth_service_repository: Annotated[
        AuthServiceRepositoryInterface,
        Depends(Provide[AuthServiceContainer.auth_service_repository]),
    ],
    token: str = Depends(oauth2_scheme),
) -> List[Dict[str, Any]]:
    """
    Returns the list of permissions for the current user.
    """

    return await auth_service_repository.get_permissions(token)


def check_user_permissions(
    resources: Optional[List[Dict]] = None,
    require_all: bool = True,
):
    """
     Dependency factory that checks user permissions for a set of resources and scopes.

    :param resources:
        A list of resources (dicts), each containing:
            - resource_name: str (required)
            - scopes: List[str] (optional, default: [])
        Example:
            [
                {"resource_name": "schedules", "scopes": ["read", "write"]},
                {"resource_name": "patients", "scopes": ["read"]},
                {"resource_name": "analytics"} # only access to resource is required
            ]

    :param require_all:
        If True, access to ALL listed resources (with all required scopes) is required (AND).
        If False, access to ANY ONE of the listed resources
        (with all required scopes for that resource) is sufficient (OR).

    :raises AccessDeniedError: If access conditions ain't met.
    """

    @inject
    async def _dep(permitted_resources: List[Dict] = Depends(get_permissions)):
        if not resources:
            return

        permitted_resources_as_dict: Dict = {
            resource["resource_name"]: set(resource.get("scopes", []) or [])
            for resource in permitted_resources
        }

        def check_single_resource(required_resource: Dict) -> bool:
            name = required_resource.get("resource_name")
            required_scopes = set(required_resource.get("scopes", []) or [])
            granted_scopes = permitted_resources_as_dict.get(name)
            if granted_scopes is None:
                return False
            if required_scopes and not required_scopes.issubset(granted_scopes):
                return False
            return True

        # AND/OR check by require_all
        results = [check_single_resource(resource) for resource in resources]
        if require_all:
            # ALL resources required (AND)
            if not all(results):
                raise AccessDeniedError(
                    status_code=403,
                    detail=_(
                        "Access denied. You're not allowed to proceed this operation."
                    ),
                )
        else:
            # ONE resource is enough (OR)
            if not any(results):
                raise AccessDeniedError(
                    status_code=403,
                    detail=_(
                        "Access denied. You're not allowed to proceed this operation."
                    ),
                )

    return _dep
