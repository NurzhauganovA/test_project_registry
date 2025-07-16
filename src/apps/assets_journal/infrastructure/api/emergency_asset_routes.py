import math
from typing import List
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status, Query

from src.apps.assets_journal.container import AssetsJournalContainer
from src.apps.assets_journal.infrastructure.api.schemas.requests.emergency_asset_schemas import (
    EmergencyAssetFilterParams,
    CreateEmergencyAssetSchema,
    UpdateEmergencyAssetSchema,
    CreateEmergencyAssetByPatientIdSchema,
)
from src.apps.assets_journal.infrastructure.api.schemas.responses.emergency_asset_schemas import (
    MultipleEmergencyAssetsResponseSchema,
    EmergencyAssetResponseSchema,
    EmergencyAssetListItemSchema,
    EmergencyAssetStatisticsSchema,
    EmergencyAssetsByOrganizationResponseSchema,
    PatientEmergencyAssetsResponseSchema,
)
from src.apps.assets_journal.mappers.emergency_asset_mappers import (
    map_emergency_asset_domain_to_full_response,
    map_emergency_asset_domain_to_list_item,
)
from src.apps.assets_journal.services.emergency_asset_service import (
    EmergencyAssetService,
)
from src.apps.catalogs.services.medical_organizations_catalog_service import MedicalOrganizationsCatalogService
from src.apps.patients.services.patients_service import PatientService
from src.shared.dependencies.check_user_permissions import check_user_permissions
from src.shared.schemas.pagination_schemas import (
    PaginationMetaDataSchema,
    PaginationParams,
)
from src.apps.assets_journal.domain.enums import (
    AssetDeliveryStatusEnum,
    AssetStatusEnum,
    EmergencyOutcomeEnum,
)

emergency_assets_router = APIRouter()


@emergency_assets_router.get(
    "/emergency-assets/{asset_id}",
    response_model=EmergencyAssetResponseSchema,
    summary="Получить актив скорой помощи по ID (детальный просмотр)",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "emergency_assets", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_emergency_asset_by_id(
        asset_id: UUID,
        emergency_asset_service: EmergencyAssetService = Depends(
            Provide[AssetsJournalContainer.emergency_asset_service]
        ),
) -> EmergencyAssetResponseSchema:
    """Получить актив скорой помощи по ID"""
    asset = await emergency_asset_service.get_by_id(asset_id)
    return map_emergency_asset_domain_to_full_response(asset)


@emergency_assets_router.get(
    "/emergency-assets",
    response_model=MultipleEmergencyAssetsResponseSchema,
    summary="Получить список активов скорой помощи с фильтрацией",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "emergency_assets", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_emergency_assets(
        pagination_params: PaginationParams = Depends(),
        # Параметры фильтрации
        patient_search: str = Query(None, description="Поиск по ФИО или ИИН пациента"),
        patient_id: UUID = Query(None, description="ID пациента"),
        patient_iin: str = Query(None, description="ИИН пациента"),
        date_from: str = Query(None, description="Дата начала периода"),
        date_to: str = Query(None, description="Дата окончания периода"),
        status: AssetStatusEnum = Query(None, description="Статус актива"),
        delivery_status: AssetDeliveryStatusEnum = Query(None, description="Статус доставки"),
        outcome: EmergencyOutcomeEnum = Query(None, description="Исход обращения"),
        diagnosis_code: str = Query(None, description="Код диагноза"),
        organization_id: UUID = Query(None, description="ID организации"),
        emergency_asset_service: EmergencyAssetService = Depends(
            Provide[AssetsJournalContainer.emergency_asset_service]
        ),
) -> MultipleEmergencyAssetsResponseSchema:
    """Получить список активов скорой помощи с фильтрацией и пагинацией"""

    # Создаем объект фильтров
    filter_params = EmergencyAssetFilterParams(
        patient_search=patient_search,
        patient_id=patient_id,
        patient_iin=patient_iin,
        date_from=date_from,
        date_to=date_to,
        status=status,
        delivery_status=delivery_status,
        outcome=outcome,
        diagnosis_code=diagnosis_code,
        organization_id=organization_id,
    )

    assets, total_count = await emergency_asset_service.get_assets(
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

    return MultipleEmergencyAssetsResponseSchema(
        items=[map_emergency_asset_domain_to_list_item(asset) for asset in assets],
        pagination=pagination_metadata,
    )


@emergency_assets_router.get(
    "/organizations/{organization_id}/emergency-assets",
    response_model=EmergencyAssetsByOrganizationResponseSchema,
    summary="Получить активы скорой помощи по организации",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "emergency_assets", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_emergency_assets_by_organization(
        organization_id: int,  # Это path-параметр
        pagination_params: PaginationParams = Depends(),
        emergency_asset_service: EmergencyAssetService = Depends(
            Provide[AssetsJournalContainer.emergency_asset_service]
        ),
        medical_org_service: MedicalOrganizationsCatalogService = Depends(
            Provide[AssetsJournalContainer.medical_organizations_catalog_service]
        ),
) -> EmergencyAssetsByOrganizationResponseSchema:
    """Получить активы скорой помощи по организации"""

    # Получаем информацию об организации
    organization = await medical_org_service.get_by_id(organization_id)

    # Создаем фильтры вручную, включая organization_id
    filter_params = EmergencyAssetFilterParams(organization_id=organization_id)

    assets, total_count = await emergency_asset_service.get_assets_by_organization(
        organization_id=organization_id,
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

    return EmergencyAssetsByOrganizationResponseSchema(
        organization_id=organization.id,
        organization_name=organization.name,
        organization_code=organization.organization_code,
        total_assets=total_count,
        items=[map_emergency_asset_domain_to_list_item(asset) for asset in assets],
        pagination=pagination_metadata,
    )


@emergency_assets_router.get(
    "/patients/{patient_id}/emergency-assets",
    response_model=PatientEmergencyAssetsResponseSchema,
    summary="Получить активы скорой помощи пациента",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "emergency_assets", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_emergency_assets_by_patient(
        patient_id: UUID,
        pagination_params: PaginationParams = Depends(),
        emergency_asset_service: EmergencyAssetService = Depends(
            Provide[AssetsJournalContainer.emergency_asset_service]
        ),
        patients_service: PatientService = Depends(
            Provide[AssetsJournalContainer.patients_service]
        ),
) -> PatientEmergencyAssetsResponseSchema:
    """Получить активы скорой помощи пациента"""

    # Получаем информацию о пациенте
    patient = await patients_service.get_by_id(patient_id)

    assets, total_count = await emergency_asset_service.get_assets_by_patient(
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

    return PatientEmergencyAssetsResponseSchema(
        patient_id=patient.id,
        patient_full_name=f"{patient.last_name} {patient.first_name} {patient.middle_name or ''}".strip(),
        patient_iin=patient.iin,
        total_assets=total_count,
        items=[map_emergency_asset_domain_to_list_item(asset) for asset in assets],
        pagination=pagination_metadata,
    )


@emergency_assets_router.post(
    "/emergency-assets",
    response_model=EmergencyAssetListItemSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый актив скорой помощи",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "emergency_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def create_emergency_asset(
        create_schema: CreateEmergencyAssetSchema,
        emergency_asset_service: EmergencyAssetService = Depends(
            Provide[AssetsJournalContainer.emergency_asset_service]
        ),
) -> EmergencyAssetListItemSchema:
    """Создать новый актив скорой помощи"""
    asset = await emergency_asset_service.create_asset(create_schema)
    return map_emergency_asset_domain_to_list_item(asset)


@emergency_assets_router.post(
    "/emergency-assets/by-patient-id",
    response_model=EmergencyAssetListItemSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый актив скорой помощи по ID пациента",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "emergency_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def create_emergency_asset_by_patient_id(
        create_schema: CreateEmergencyAssetByPatientIdSchema,
        emergency_asset_service: EmergencyAssetService = Depends(
            Provide[AssetsJournalContainer.emergency_asset_service]
        ),
        patients_service: PatientService = Depends(
            Provide[AssetsJournalContainer.patients_service]
        ),
) -> EmergencyAssetListItemSchema:
    """Создать новый актив скорой помощи по ID пациента"""
    patient = await patients_service.get_by_id(create_schema.patient_id)

    # Создаем актив скорой помощи
    asset = await emergency_asset_service.create_asset_by_patient_id(create_schema, patient.id)
    return map_emergency_asset_domain_to_list_item(asset)


@emergency_assets_router.patch(
    "/emergency-assets/{asset_id}",
    response_model=EmergencyAssetResponseSchema,
    summary="Обновить актив скорой помощи",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "emergency_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def update_emergency_asset(
        asset_id: UUID,
        update_schema: UpdateEmergencyAssetSchema,
        emergency_asset_service: EmergencyAssetService = Depends(
            Provide[AssetsJournalContainer.emergency_asset_service]
        ),
) -> EmergencyAssetResponseSchema:
    """Обновить актив скорой помощи"""
    asset = await emergency_asset_service.update_asset(asset_id, update_schema)
    return map_emergency_asset_domain_to_full_response(asset)


@emergency_assets_router.delete(
    "/emergency-assets/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить актив скорой помощи",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "emergency_assets", "scopes": ["delete"]}]
    #         )
    #     )
    # ],
)
@inject
async def delete_emergency_asset(
        asset_id: UUID,
        emergency_asset_service: EmergencyAssetService = Depends(
            Provide[AssetsJournalContainer.emergency_asset_service]
        ),
) -> None:
    """Удалить актив скорой помощи"""
    await emergency_asset_service.delete_asset(asset_id)


@emergency_assets_router.get(
    "/emergency-assets/statistics",
    response_model=EmergencyAssetStatisticsSchema,
    summary="Получить статистику активов скорой помощи",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "emergency_assets", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_emergency_assets_statistics(
        patient_search: str = Query(None, description="Поиск по ФИО или ИИН пациента"),
        patient_id: UUID = Query(None, description="ID пациента"),
        patient_iin: str = Query(None, description="ИИН пациента"),
        date_from: str = Query(None, description="Дата начала периода"),
        date_to: str = Query(None, description="Дата окончания периода"),
        status: AssetStatusEnum = Query(None, description="Статус актива"),
        delivery_status: AssetDeliveryStatusEnum = Query(None, description="Статус доставки"),
        outcome: EmergencyOutcomeEnum = Query(None, description="Исход обращения"),
        diagnosis_code: str = Query(None, description="Код диагноза"),
        organization_id: UUID = Query(None, description="ID организации"),
        emergency_asset_service: EmergencyAssetService = Depends(
            Provide[AssetsJournalContainer.emergency_asset_service]
        ),
) -> EmergencyAssetStatisticsSchema:
    """Получить статистику активов скорой помощи"""

    filter_params = EmergencyAssetFilterParams(
        patient_search=patient_search,
        patient_id=patient_id,
        patient_iin=patient_iin,
        date_from=date_from,
        date_to=date_to,
        status=status,
        delivery_status=delivery_status,
        outcome=outcome,
        diagnosis_code=diagnosis_code,
        organization_id=organization_id,
    )

    return await emergency_asset_service.get_statistics(filter_params)


@emergency_assets_router.post(
    "/emergency-assets/{asset_id}/confirm",
    response_model=EmergencyAssetResponseSchema,
    summary="Подтвердить актив скорой помощи",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "emergency_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def confirm_emergency_asset(
        asset_id: UUID,
        emergency_asset_service: EmergencyAssetService = Depends(
            Provide[AssetsJournalContainer.emergency_asset_service]
        ),
) -> EmergencyAssetResponseSchema:
    """Подтвердить актив скорой помощи"""
    asset = await emergency_asset_service.confirm_asset(asset_id)
    return map_emergency_asset_domain_to_full_response(asset)


@emergency_assets_router.post(
    "/emergency-assets/load-from-bg",
    response_model=List[EmergencyAssetListItemSchema],
    summary="Загрузить активы скорой помощи из файла BG (временно)",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "emergency_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def load_emergency_assets_from_bg(
        emergency_asset_service: EmergencyAssetService = Depends(
            Provide[AssetsJournalContainer.emergency_asset_service]
        ),
) -> List[EmergencyAssetListItemSchema]:
    """
    Загрузить активы скорой помощи из файла BG (временная функция для тестирования)
    Позже будет заменена на интеграцию с BG API
    """
    assets = await emergency_asset_service.load_assets_from_bg_file()
    return [map_emergency_asset_domain_to_list_item(asset) for asset in assets]