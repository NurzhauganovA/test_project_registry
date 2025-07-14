import math
from typing import List
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from src.apps.assets_journal.container import AssetsJournalContainer
from src.apps.assets_journal.infrastructure.api.schemas.requests.stationary_asset_filter_params import (
    StationaryAssetFilterParams,
)
from src.apps.assets_journal.infrastructure.api.schemas.requests.stationary_asset_schemas import (
    CreateStationaryAssetSchema,
    UpdateStationaryAssetSchema, CreateStationaryAssetByPatientIdSchema, TransferStationaryAssetSchema,
)
from src.apps.assets_journal.infrastructure.api.schemas.responses.stationary_asset_schemas import (
    MultipleStationaryAssetsResponseSchema,
    StationaryAssetResponseSchema,
    StationaryAssetListItemSchema,
    StationaryAssetStatisticsSchema, StationaryAssetsByOrganizationResponseSchema,
    PatientStationaryAssetsResponseSchema,
)
from src.apps.assets_journal.mappers import (
    map_stationary_asset_domain_to_full_response,
    map_stationary_asset_domain_to_list_item,
)
from src.apps.assets_journal.services.stationary_asset_service import (
    StationaryAssetService,
)
from src.apps.catalogs.services.medical_organizations_catalog_service import MedicalOrganizationsCatalogService
from src.apps.patients.services.patients_service import PatientService
from src.shared.dependencies.check_user_permissions import check_user_permissions
from src.shared.schemas.pagination_schemas import (
    PaginationMetaDataSchema,
    PaginationParams,
)

stationary_assets_router = APIRouter()


@stationary_assets_router.get(
    "/stationary-assets/{asset_id}",
    response_model=StationaryAssetResponseSchema,
    summary="Получить актив стационара по ID (детальный просмотр)",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "stationary_assets", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_stationary_asset_by_id(
    asset_id: UUID,
    stationary_asset_service: StationaryAssetService = Depends(
        Provide[AssetsJournalContainer.stationary_asset_service]
    ),
) -> StationaryAssetResponseSchema:
    """Получить актив стационара по ID"""
    asset = await stationary_asset_service.get_by_id(asset_id)
    return map_stationary_asset_domain_to_full_response(asset)


@stationary_assets_router.get(
    "/stationary-assets",
    response_model=MultipleStationaryAssetsResponseSchema,
    summary="Получить список активов стационара с фильтрацией",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "stationary_assets", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_stationary_assets(
    pagination_params: PaginationParams = Depends(),
    filter_params: StationaryAssetFilterParams = Depends(),
    stationary_asset_service: StationaryAssetService = Depends(
        Provide[AssetsJournalContainer.stationary_asset_service]
    ),
) -> MultipleStationaryAssetsResponseSchema:
    """Получить список активов стационара с фильтрацией и пагинацией"""
    assets, total_count = await stationary_asset_service.get_assets(
        pagination_params=pagination_params,
        filter_params=filter_params,
    )

    # Вычисляем метаданные пагинации
    page: int = pagination_params.page or 1
    limit: int = pagination_params.limit or 30
    total_pages = math.ceil(total_count / limit) if limit else 1
    has_next = page < total_pages
    has_prev = page > 1

    pagination_metadata = PaginationMetaDataSchema(
        current_page=page,
        per_page=limit,
        total_items=total_count,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev,
    )

    return MultipleStationaryAssetsResponseSchema(
        items=[map_stationary_asset_domain_to_list_item(asset) for asset in assets],
        pagination=pagination_metadata,
    )


@stationary_assets_router.get(
    "/organizations/{organization_id}/stationary-assets",
    response_model=StationaryAssetsByOrganizationResponseSchema,
    summary="Получить активы стационара по организации",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "stationary_assets", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_stationary_assets_by_organization(
        organization_id: int,  # Это path-параметр
        pagination_params: PaginationParams = Depends(),
        stationary_asset_service: StationaryAssetService = Depends(
            Provide[AssetsJournalContainer.stationary_asset_service]
        ),
        medical_org_service: MedicalOrganizationsCatalogService = Depends(
            Provide[AssetsJournalContainer.medical_organizations_catalog_service]
        ),
) -> StationaryAssetsByOrganizationResponseSchema:
    """Получить активы стационара по организации"""

    # Получаем информацию об организации
    organization = await medical_org_service.get_by_id(organization_id)

    # Создаем фильтры вручную, включая organization_id
    filters = {"organization_id": organization_id}

    assets, total_count = await stationary_asset_service.get_assets(
        pagination_params=pagination_params,
        filter_params=StationaryAssetFilterParams(**filters),
    )
    print("ASSETS:", assets)

    # Вычисляем метаданные пагинации
    page: int = pagination_params.page or 1
    limit: int = pagination_params.limit or 30
    total_pages = math.ceil(total_count / limit) if limit else 1
    has_next = page < total_pages
    has_prev = page > 1

    pagination_metadata = PaginationMetaDataSchema(
        current_page=page,
        per_page=limit,
        total_items=total_count,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev,
    )

    return StationaryAssetsByOrganizationResponseSchema(
        organization_id=organization.id,
        organization_name=organization.name,
        organization_code=organization.organization_code,
        total_assets=total_count,
        items=[map_stationary_asset_domain_to_list_item(asset) for asset in assets],
        pagination=pagination_metadata,
    )


@stationary_assets_router.get(
    "/patients/{patient_id}/stationary-assets",
    response_model=PatientStationaryAssetsResponseSchema,
    summary="Получить активы стационара пациента",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "stationary_assets", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_stationary_assets_by_patient(
        patient_id: UUID,
        pagination_params: PaginationParams = Depends(),
        stationary_asset_service: StationaryAssetService = Depends(
            Provide[AssetsJournalContainer.stationary_asset_service]
        ),
        patients_service: PatientService = Depends(
            Provide[AssetsJournalContainer.patients_service]
        ),
) -> PatientStationaryAssetsResponseSchema:
    """Получить активы стационара пациента"""

    # Получаем информацию о пациенте
    patient = await patients_service.get_by_id(patient_id)

    assets, total_count = await stationary_asset_service.get_assets_by_patient(
        patient_id=patient_id,
        pagination_params=pagination_params,
    )

    # Вычисляем метаданные пагинации
    page: int = pagination_params.page or 1
    limit: int = pagination_params.limit or 30
    total_pages = math.ceil(total_count / limit) if limit else 1
    has_next = page < total_pages
    has_prev = page > 1

    pagination_metadata = PaginationMetaDataSchema(
        current_page=page,
        per_page=limit,
        total_items=total_count,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev,
    )

    return PatientStationaryAssetsResponseSchema(
        patient_id=patient.id,
        patient_full_name=f"{patient.last_name} {patient.first_name} {patient.middle_name or ''}".strip(),
        patient_iin=patient.iin,
        total_assets=total_count,
        items=[map_stationary_asset_domain_to_list_item(asset) for asset in assets],
        pagination=pagination_metadata,
    )


@stationary_assets_router.post(
    "/stationary-assets",
    response_model=StationaryAssetListItemSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый актив стационара",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "stationary_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def create_stationary_asset(
    create_schema: CreateStationaryAssetSchema,
    stationary_asset_service: StationaryAssetService = Depends(
        Provide[AssetsJournalContainer.stationary_asset_service]
    ),
) -> StationaryAssetListItemSchema:
    """Создать новый актив стационара"""
    asset = await stationary_asset_service.create_asset(create_schema)
    return map_stationary_asset_domain_to_list_item(asset)


@stationary_assets_router.post(
    "/stationary-assets/by-patient-id",
    response_model=StationaryAssetListItemSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый актив стационара по ID пациента",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "stationary_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def create_stationary_asset_by_patient_id(
    create_schema: CreateStationaryAssetByPatientIdSchema,
    stationary_asset_service: StationaryAssetService = Depends(
        Provide[AssetsJournalContainer.stationary_asset_service]
    ),
    patients_service: PatientService = Depends(
        Provide[AssetsJournalContainer.patients_service]
    ),
) -> StationaryAssetListItemSchema:
    """Создать новый актив стационара по ID пациента"""
    patient = await patients_service.get_by_id(create_schema.patient_id)

    # Создаем актив стационара
    asset = await stationary_asset_service.create_asset_by_patient_id(create_schema, patient.id)
    return map_stationary_asset_domain_to_list_item(asset)


@stationary_assets_router.patch(
    "/stationary-assets/{asset_id}",
    response_model=StationaryAssetResponseSchema,
    summary="Обновить актив стационара",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "stationary_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def update_stationary_asset(
    asset_id: UUID,
    update_schema: UpdateStationaryAssetSchema,
    stationary_asset_service: StationaryAssetService = Depends(
        Provide[AssetsJournalContainer.stationary_asset_service]
    ),
) -> StationaryAssetResponseSchema:
    """Обновить актив стационара"""
    asset = await stationary_asset_service.update_asset(asset_id, update_schema)
    return map_stationary_asset_domain_to_full_response(asset)


@stationary_assets_router.delete(
    "/stationary-assets/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить актив стационара",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "stationary_assets", "scopes": ["delete"]}]
    #         )
    #     )
    # ],
)
@inject
async def delete_stationary_asset(
    asset_id: UUID,
    stationary_asset_service: StationaryAssetService = Depends(
        Provide[AssetsJournalContainer.stationary_asset_service]
    ),
) -> None:
    """Удалить актив стационара"""
    await stationary_asset_service.delete_asset(asset_id)


@stationary_assets_router.get(
    "/stationary-assets/statistics",
    response_model=StationaryAssetStatisticsSchema,
    summary="Получить статистику активов стационара",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "stationary_assets", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_stationary_assets_statistics(
    filter_params: StationaryAssetFilterParams = Depends(),
    stationary_asset_service: StationaryAssetService = Depends(
        Provide[AssetsJournalContainer.stationary_asset_service]
    ),
) -> StationaryAssetStatisticsSchema:
    """Получить статистику активов стационара"""
    return await stationary_asset_service.get_statistics(filter_params)


@stationary_assets_router.post(
    "/stationary-assets/{asset_id}/confirm",
    response_model=StationaryAssetResponseSchema,
    summary="Подтвердить актив стационара",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "stationary_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def confirm_stationary_asset(
    asset_id: UUID,
    stationary_asset_service: StationaryAssetService = Depends(
        Provide[AssetsJournalContainer.stationary_asset_service]
    ),
) -> StationaryAssetResponseSchema:
    """Подтвердить актив стационара"""
    asset = await stationary_asset_service.confirm_asset(asset_id)
    return map_stationary_asset_domain_to_full_response(asset)


@stationary_assets_router.post(
    "/stationary-assets/load-from-bg",
    response_model=List[StationaryAssetListItemSchema],
    summary="Загрузить активы из файла BG (временно)",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "stationary_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def load_stationary_assets_from_bg(
    stationary_asset_service: StationaryAssetService = Depends(
        Provide[AssetsJournalContainer.stationary_asset_service]
    ),
) -> List[StationaryAssetListItemSchema]:
    """
    Загрузить активы из файла BG (временная функция для тестирования)
    Позже будет заменена на интеграцию с BG API
    """
    assets = await stationary_asset_service.load_assets_from_bg_file()
    return [map_stationary_asset_domain_to_list_item(asset) for asset in assets]


@stationary_assets_router.post(
    "/stationary-assets/{asset_id}/transfer",
    response_model=StationaryAssetResponseSchema,
    summary="Передать актив стационара другой организации",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "stationary_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def transfer_stationary_asset(
    asset_id: UUID,
    transfer_data: TransferStationaryAssetSchema,
    stationary_asset_service: StationaryAssetService = Depends(
        Provide[AssetsJournalContainer.stationary_asset_service]
    ),
) -> StationaryAssetResponseSchema:
    """Передать актив стационара другой организации"""
    asset = await stationary_asset_service.transfer_to_organization(
        asset_id=asset_id,
        new_organization_id=transfer_data.new_organization_id,
        transfer_reason=transfer_data.transfer_reason
    )
    return map_stationary_asset_domain_to_full_response(asset)