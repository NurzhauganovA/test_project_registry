import math

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.apps.platform_rules.container import PlatformRulesContainer
from src.apps.platform_rules.infrastructure.api.schemas.requests.platform_rules_filter_params import (
    PlatformRulesFilterParams,
)
from src.apps.platform_rules.infrastructure.api.schemas.requests.platform_rules_schemas import (
    CreatePlatformRuleSchema,
    UpdatePlatformRuleSchema,
)
from src.apps.platform_rules.infrastructure.api.schemas.responses.platform_rules_schemas import (
    MultiplePlatformRulesResponseSchema,
    ResponsePlatformRuleSchema,
)
from src.apps.platform_rules.interfaces.platform_rules_repository_interface import (
    PlatformRulesRepositoryInterface,
)
from src.apps.registry.exceptions import NoInstanceFoundError
from src.core.i18n import _
from src.shared.exceptions import InstanceAlreadyExistsError
from src.shared.schemas.pagination_schemas import (
    PaginationMetaDataSchema,
    PaginationParams,
)

platform_rules_router = APIRouter()


@platform_rules_router.get(
    "/platform-rules/{platform_rule_id}",
    response_model=ResponsePlatformRuleSchema,
    summary="Retrieve a platform rule by ID",
)
@inject
async def get_by_id(
    platform_rule_id: int,
    repository: PlatformRulesRepositoryInterface = Depends(
        Provide[PlatformRulesContainer.platform_rules_repository]
    ),
):
    platform_rule = await repository.get_by_id(platform_rule_id)
    if not platform_rule:
        raise NoInstanceFoundError(
            status_code=404,
            detail=_("Platform rule with ID: '%(ID)s' not found.")
            % {"ID": platform_rule_id},
        )

    return platform_rule


@platform_rules_router.get(
    "/platform-rules",
    response_model=MultiplePlatformRulesResponseSchema,
    summary="Retrieve a list of platform rules with optional filtering and pagination",
)
@inject
async def get_platform_rules(
    pagination_params: PaginationParams = Depends(),
    filter_params: PlatformRulesFilterParams = Depends(),
    repository: PlatformRulesRepositoryInterface = Depends(
        Provide[PlatformRulesContainer.platform_rules_repository]
    ),
) -> MultiplePlatformRulesResponseSchema:
    filters: dict = filter_params.to_dict()

    platform_rules = await repository.get_platform_rules(
        filters=filters,
        page=pagination_params.page or 1,
        limit=pagination_params.limit or 30,
    )

    total_amount_of_records: int = await repository.get_total_number_of_platform_rules()

    # Calculate pagination metadata
    page: int = pagination_params.page or 1  # for mypy
    limit: int = pagination_params.limit or 30  # for mypy
    total_pages = math.ceil(total_amount_of_records / limit) if limit else 1
    has_next = page < total_pages
    has_prev = page > 1

    pagination_metadata = PaginationMetaDataSchema(
        current_page=page,
        per_page=limit,
        total_items=total_amount_of_records,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev,
    )

    return MultiplePlatformRulesResponseSchema(
        items=platform_rules, pagination=pagination_metadata
    )


@platform_rules_router.post(
    "/platform-rules",
    response_model=ResponsePlatformRuleSchema,
    status_code=201,
    summary="Create a new platform rule",
)
@inject
async def create_platform_rule(
    request_dto: CreatePlatformRuleSchema,
    repository: PlatformRulesRepositoryInterface = Depends(
        Provide[PlatformRulesContainer.platform_rules_repository]
    ),
):
    # Check if this 'key' is already taken
    existing_rule = await repository.get_by_key(request_dto.key)
    if existing_rule:
        raise InstanceAlreadyExistsError(
            status_code=409,
            detail=_("Platform rule with key: '%(KEY)s' already exists.")
            % {"KEY": request_dto.key},
        )

    created_rule = await repository.create_platform_rule(request_dto)
    return created_rule


@platform_rules_router.put(
    "/platform-rules/{platform_rule_id}",
    response_model=ResponsePlatformRuleSchema,
    summary="Update an existing platform rule",
)
@inject
async def update_platform_rule(
    platform_rule_id: int,
    request_dto: UpdatePlatformRuleSchema,
    repository: PlatformRulesRepositoryInterface = Depends(
        Provide[PlatformRulesContainer.platform_rules_repository]
    ),
):
    # Check if target platform rule exists
    platform_rule = await repository.get_by_id(platform_rule_id)
    if not platform_rule:
        raise NoInstanceFoundError(
            status_code=404,
            detail=_("Platform rule with ID: '%(ID)s' not found.")
            % {"ID": platform_rule_id},
        )

    updated_platform_rule = await repository.update_platform_rule(
        platform_rule_id=platform_rule_id, request_dto=request_dto
    )

    return updated_platform_rule


@platform_rules_router.delete(
    "/platform-rules/{platform_rule_id}",
    status_code=204,
    summary="Delete a platform rule by ID",
)
@inject
async def delete_platform_rule_endpoint(
    platform_rule_id: int,
    repository: PlatformRulesRepositoryInterface = Depends(
        Provide[PlatformRulesContainer.platform_rules_repository]
    ),
):
    # Check if target platform rule exists
    platform_rule = await repository.get_by_id(platform_rule_id)
    if not platform_rule:
        raise NoInstanceFoundError(
            status_code=404,
            detail=_("Platform rule with ID: '%(ID)s' not found.")
            % {"ID": platform_rule_id},
        )

    await repository.delete_by_id(platform_rule_id)
