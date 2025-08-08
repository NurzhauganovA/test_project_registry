import math
from typing import List
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status, Query
from datetime import datetime

from src.apps.assets_journal.container import AssetsJournalContainer
from src.apps.assets_journal.infrastructure.api.schemas.requests.maternity_asset_schemas import (
    MaternityAssetFilterParams,
    CreateMaternityAssetSchema,
    UpdateMaternityAssetSchema,
    CreateMaternityAssetByPatientIdSchema,
    MaternityOutcomeEnum,
    MaternityAdmissionTypeEnum,
    MaternityStayTypeEnum,
    MaternityStatusEnum,
)
from src.apps.assets_journal.infrastructure.api.schemas.responses.maternity_asset_schemas import (
    MultipleMaternityAssetsResponseSchema,
    MaternityAssetResponseSchema,
    MaternityAssetListItemSchema,
    MaternityAssetsByOrganizationResponseSchema,
    PatientMaternityAssetsResponseSchema,
)
from src.apps.assets_journal.mappers.maternity_asset_mappers import (
    map_maternity_asset_domain_to_full_response,
    map_maternity_asset_domain_to_list_item,
)
from src.apps.assets_journal.services.maternity_asset_service import (
    MaternityAssetService,
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
)

maternity_assets_router = APIRouter()


@maternity_assets_router.get(
    "/maternity-assets/{asset_id}",
    response_model=MaternityAssetResponseSchema,
    summary="Получить актив роддома по ID (детальный просмотр)",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "maternity_assets", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_maternity_asset_by_id(
        asset_id: UUID,
        maternity_asset_service: MaternityAssetService = Depends(
            Provide[AssetsJournalContainer.maternity_asset_service]
        ),
) -> MaternityAssetResponseSchema:
    """Получить актив роддома по ID"""
    asset = await maternity_asset_service.get_by_id(asset_id)
    return map_maternity_asset_domain_to_full_response(asset)


@maternity_assets_router.get(
    "/maternity-assets",
    response_model=MultipleMaternityAssetsResponseSchema,
    summary="Получить список активов роддома с фильтрацией",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "maternity_assets", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_maternity_assets(
        pagination_params: PaginationParams = Depends(),
        # Параметры фильтрации
        patient_search: str = Query(None, description="Поиск по ФИО пациента"),
        patient_id: UUID = Query(None, description="ID пациента"),
        patient_iin: str = Query(None, description="ИИН пациента"),
        date_from: datetime = Query(None, description="Дата начала периода"),
        date_to: datetime = Query(None, description="Дата окончания периода"),
        status: AssetStatusEnum = Query(None, description="Статус актива"),
        delivery_status: AssetDeliveryStatusEnum = Query(None, description="Статус доставки"),
        stay_outcome: MaternityOutcomeEnum = Query(None, description="Исход пребывания"),
        admission_type: MaternityAdmissionTypeEnum = Query(None, description="Тип госпитализации"),
        stay_type: MaternityStayTypeEnum = Query(None, description="Тип пребывания"),
        patient_status: MaternityStatusEnum = Query(None, description="Статус пациентки"),
        area: str = Query(None, description="Участок"),
        specialization: str = Query(None, description="Специализация"),
        specialist: str = Query(None, description="Специалист"),
        diagnosis_code: str = Query(None, description="Код диагноза"),
        organization_id: int = Query(None, description="ID организации"),
        maternity_asset_service: MaternityAssetService = Depends(
            Provide[AssetsJournalContainer.maternity_asset_service]
        ),
) -> MultipleMaternityAssetsResponseSchema:
    """Получить список активов роддома с фильтрацией и пагинацией"""

    # Создаем объект фильтров
    filter_params = MaternityAssetFilterParams(
        patient_search=patient_search,
        patient_id=patient_id,
        patient_iin=patient_iin,
        date_from=date_from,
        date_to=date_to,
        status=status,
        delivery_status=delivery_status,
        stay_outcome=stay_outcome,
        admission_type=admission_type,
        stay_type=stay_type,
        patient_status=patient_status,
        area=area,
        specialization=specialization,
        specialist=specialist,
        diagnosis_code=diagnosis_code,
        organization_id=organization_id,
    )

    assets, total_count = await maternity_asset_service.get_assets(
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

    return MultipleMaternityAssetsResponseSchema(
        items=[map_maternity_asset_domain_to_list_item(asset) for asset in assets],
        pagination=pagination_metadata,
    )


@maternity_assets_router.get(
    "/organizations/{organization_id}/maternity-assets",
    response_model=MaternityAssetsByOrganizationResponseSchema,
    summary="Получить активы роддома по организации",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "maternity_assets", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_maternity_assets_by_organization(
        organization_id: int,  # Это path-параметр
        pagination_params: PaginationParams = Depends(),
        maternity_asset_service: MaternityAssetService = Depends(
            Provide[AssetsJournalContainer.maternity_asset_service]
        ),
        medical_org_service: MedicalOrganizationsCatalogService = Depends(
            Provide[AssetsJournalContainer.medical_organizations_catalog_service]
        ),
) -> MaternityAssetsByOrganizationResponseSchema:
    """Получить активы роддома по организации"""

    # Получаем информацию об организации
    organization = await medical_org_service.get_by_id(organization_id)

    # Создаем фильтры вручную, включая organization_id
    filter_params = MaternityAssetFilterParams(organization_id=organization_id)

    assets, total_count = await maternity_asset_service.get_assets_by_organization(
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

    return MaternityAssetsByOrganizationResponseSchema(
        organization_id=organization.id,
        organization_name=organization.name,
        organization_code=organization.organization_code,
        total_assets=total_count,
        items=[map_maternity_asset_domain_to_list_item(asset) for asset in assets],
        pagination=pagination_metadata,
    )


@maternity_assets_router.get(
    "/patients/{patient_id}/maternity-assets",
    response_model=PatientMaternityAssetsResponseSchema,
    summary="Получить активы роддома пациента",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "maternity_assets", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_maternity_assets_by_patient(
        patient_id: UUID,
        pagination_params: PaginationParams = Depends(),
        maternity_asset_service: MaternityAssetService = Depends(
            Provide[AssetsJournalContainer.maternity_asset_service]
        ),
        patients_service: PatientService = Depends(
            Provide[AssetsJournalContainer.patients_service]
        ),
) -> PatientMaternityAssetsResponseSchema:
    """Получить активы роддома пациента"""

    # Получаем информацию о пациенте
    patient = await patients_service.get_by_id(patient_id)

    assets, total_count = await maternity_asset_service.get_assets_by_patient(
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

    return PatientMaternityAssetsResponseSchema(
        patient_id=patient.id,
        patient_full_name=f"{patient.last_name} {patient.first_name} {patient.middle_name or ''}".strip(),
        patient_iin=patient.iin,
        total_assets=total_count,
        items=[map_maternity_asset_domain_to_list_item(asset) for asset in assets],
        pagination=pagination_metadata,
    )


@maternity_assets_router.post(
    "/maternity-assets",
    response_model=MaternityAssetListItemSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый актив роддома",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "maternity_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def create_maternity_asset(
        create_schema: CreateMaternityAssetSchema,
        maternity_asset_service: MaternityAssetService = Depends(
            Provide[AssetsJournalContainer.maternity_asset_service]
        ),
) -> MaternityAssetListItemSchema:
    """Создать новый актив роддома"""
    asset = await maternity_asset_service.create_asset(create_schema)
    return map_maternity_asset_domain_to_list_item(asset)


@maternity_assets_router.post(
    "/maternity-assets/by-patient-id",
    response_model=MaternityAssetListItemSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый актив роддома по ID пациента",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "maternity_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def create_maternity_asset_by_patient_id(
        create_schema: CreateMaternityAssetByPatientIdSchema,
        maternity_asset_service: MaternityAssetService = Depends(
            Provide[AssetsJournalContainer.maternity_asset_service]
        ),
        patients_service: PatientService = Depends(
            Provide[AssetsJournalContainer.patients_service]
        ),
) -> MaternityAssetListItemSchema:
    """Создать новый актив роддома по ID пациента"""
    patient = await patients_service.get_by_id(create_schema.patient_id)

    # Создаем актив роддома
    asset = await maternity_asset_service.create_asset_by_patient_id(create_schema, patient.id)
    return map_maternity_asset_domain_to_list_item(asset)


@maternity_assets_router.patch(
    "/maternity-assets/{asset_id}",
    response_model=MaternityAssetResponseSchema,
    summary="Обновить актив роддома",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "maternity_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def update_maternity_asset(
        asset_id: UUID,
        update_schema: UpdateMaternityAssetSchema,
        maternity_asset_service: MaternityAssetService = Depends(
            Provide[AssetsJournalContainer.maternity_asset_service]
        ),
) -> MaternityAssetResponseSchema:
    """Обновить актив роддома"""
    asset = await maternity_asset_service.update_asset(asset_id, update_schema)
    return map_maternity_asset_domain_to_full_response(asset)


@maternity_assets_router.delete(
    "/maternity-assets/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить актив роддома",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "maternity_assets", "scopes": ["delete"]}]
    #         )
    #     )
    # ],
)
@inject
async def delete_maternity_asset(
        asset_id: UUID,
        maternity_asset_service: MaternityAssetService = Depends(
            Provide[AssetsJournalContainer.maternity_asset_service]
        ),
) -> None:
    """Удалить актив роддома"""
    await maternity_asset_service.delete_asset(asset_id)


@maternity_assets_router.post(
    "/maternity-assets/{asset_id}/confirm",
    response_model=MaternityAssetResponseSchema,
    summary="Подтвердить актив роддома",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "maternity_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def confirm_maternity_asset(
        asset_id: UUID,
        maternity_asset_service: MaternityAssetService = Depends(
            Provide[AssetsJournalContainer.maternity_asset_service]
        ),
) -> MaternityAssetResponseSchema:
    """Подтвердить актив роддома"""
    asset = await maternity_asset_service.confirm_asset(asset_id)
    return map_maternity_asset_domain_to_full_response(asset)


@maternity_assets_router.post(
    "/maternity-assets/load-from-bg",
    response_model=List[MaternityAssetListItemSchema],
    summary="Загрузить активы роддома из файла BG (временно)",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "maternity_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def load_maternity_assets_from_bg(
        maternity_asset_service: MaternityAssetService = Depends(
            Provide[AssetsJournalContainer.maternity_asset_service]
        ),
) -> List[MaternityAssetListItemSchema]:
    """
    Загрузить активы роддома из файла BG (временная функция для тестирования)
    Позже будет заменена на интеграцию с BG API
    """
    assets = await maternity_asset_service.load_assets_from_bg_file()
    return [map_maternity_asset_domain_to_list_item(asset) for asset in assets]