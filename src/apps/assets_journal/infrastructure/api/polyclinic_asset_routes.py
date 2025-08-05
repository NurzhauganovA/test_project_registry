from datetime import datetime
import math
from typing import List
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status, Query

from src.apps.assets_journal.container import AssetsJournalContainer
from src.apps.assets_journal.infrastructure.api.schemas.requests.polyclinic_asset_schemas import (
    PolyclinicAssetFilterParams,
    CreatePolyclinicAssetSchema,
    UpdatePolyclinicAssetSchema,
    CreatePolyclinicAssetByPatientIdSchema,
    RejectPolyclinicAssetSchema,
    TransferPolyclinicAssetSchema,
)
from src.apps.assets_journal.infrastructure.api.schemas.responses.polyclinic_asset_schemas import (
    MultiplePolyclinicAssetsResponseSchema,
    PolyclinicAssetResponseSchema,
    PolyclinicAssetListItemSchema,
    PolyclinicAssetStatisticsSchema,
    PolyclinicAssetsByOrganizationResponseSchema,
    PatientPolyclinicAssetsResponseSchema,
)
from src.apps.assets_journal.mappers.polyclinic_asset_mappers import (
    map_polyclinic_asset_domain_to_full_response,
    map_polyclinic_asset_domain_to_list_item,
)
from src.apps.assets_journal.services.polyclinic_asset_service import (
    PolyclinicAssetService,
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
    PolyclinicVisitTypeEnum,
    PolyclinicServiceTypeEnum,
    PolyclinicOutcomeEnum, PolyclinicReasonAppeal, PolyclinicTypeActiveVisit,
)

polyclinic_assets_router = APIRouter()


@polyclinic_assets_router.get(
    "/polyclinic-assets/{asset_id}",
    response_model=PolyclinicAssetResponseSchema,
    summary="Получить актив поликлиники по ID (детальный просмотр)",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "polyclinic_assets", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_polyclinic_asset_by_id(
        asset_id: UUID,
        polyclinic_asset_service: PolyclinicAssetService = Depends(
            Provide[AssetsJournalContainer.polyclinic_asset_service]
        ),
) -> PolyclinicAssetResponseSchema:
    """Получить актив поликлиники по ID"""
    asset = await polyclinic_asset_service.get_by_id(asset_id)
    return map_polyclinic_asset_domain_to_full_response(asset)


@polyclinic_assets_router.get(
    "/polyclinic-assets",
    response_model=MultiplePolyclinicAssetsResponseSchema,
    summary="Получить список активов поликлиники с фильтрацией",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "polyclinic_assets", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_polyclinic_assets(
        pagination_params: PaginationParams = Depends(),
        # Параметры фильтрации
        patient_search: str = Query(None, description="Поиск по ФИО пациента"),
        patient_id: UUID = Query(None, description="ID пациента"),
        patient_iin: str = Query(None, description="ИИН пациента"),
        date_from: datetime = Query(None, description="Дата начала периода"),
        date_to: datetime = Query(None, description="Дата окончания периода"),
        status: AssetStatusEnum = Query(None, description="Статус актива"),
        delivery_status: AssetDeliveryStatusEnum = Query(None, description="Статус доставки"),
        area: str = Query(None, description="Участок"),
        specialization: str = Query(None, description="Специализация"),
        specialist: str = Query(None, description="Специалист"),
        service: PolyclinicServiceTypeEnum = Query(None, description="Услуга"),
        reason_appeal: PolyclinicReasonAppeal = Query(None, description="Повод обращения"),
        type_active_visit: PolyclinicTypeActiveVisit = Query(None, description="Тип активного посещения"),
        visit_type: PolyclinicVisitTypeEnum = Query(None, description="Тип посещения"),
        visit_outcome: PolyclinicOutcomeEnum = Query(None, description="Исход посещения"),
        organization_id: int = Query(None, description="ID организации"),
        polyclinic_asset_service: PolyclinicAssetService = Depends(
            Provide[AssetsJournalContainer.polyclinic_asset_service]
        ),
) -> MultiplePolyclinicAssetsResponseSchema:
    """Получить список активов поликлиники с фильтрацией и пагинацией"""

    # Создаем объект фильтров
    filter_params = PolyclinicAssetFilterParams(
        patient_search=patient_search,
        patient_id=patient_id,
        patient_iin=patient_iin,
        date_from=date_from,
        date_to=date_to,
        status=status,
        delivery_status=delivery_status,
        area=area,
        specialization=specialization,
        specialist=specialist,
        service=service,
        reason_appeal=reason_appeal,
        type_active_visit=type_active_visit,
        visit_type=visit_type,
        visit_outcome=visit_outcome,
        organization_id=organization_id,
    )

    assets, total_count = await polyclinic_asset_service.get_assets(
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

    return MultiplePolyclinicAssetsResponseSchema(
        items=[map_polyclinic_asset_domain_to_list_item(asset) for asset in assets],
        pagination=pagination_metadata,
    )


@polyclinic_assets_router.get(
    "/organizations/{organization_id}/polyclinic-assets",
    response_model=PolyclinicAssetsByOrganizationResponseSchema,
    summary="Получить активы поликлиники по организации",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "polyclinic_assets", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_polyclinic_assets_by_organization(
        organization_id: int,  # Это path-параметр
        pagination_params: PaginationParams = Depends(),
        polyclinic_asset_service: PolyclinicAssetService = Depends(
            Provide[AssetsJournalContainer.polyclinic_asset_service]
        ),
        medical_org_service: MedicalOrganizationsCatalogService = Depends(
            Provide[AssetsJournalContainer.medical_organizations_catalog_service]
        ),
) -> PolyclinicAssetsByOrganizationResponseSchema:
    """Получить активы поликлиники по организации"""

    # Получаем информацию об организации
    organization = await medical_org_service.get_by_id(organization_id)

    # Создаем фильтры вручную, включая organization_id
    filter_params = PolyclinicAssetFilterParams(organization_id=organization_id)

    assets, total_count = await polyclinic_asset_service.get_assets_by_organization(
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

    return PolyclinicAssetsByOrganizationResponseSchema(
        organization_id=organization.id,
        organization_name=organization.name,
        organization_code=organization.organization_code,
        total_assets=total_count,
        items=[map_polyclinic_asset_domain_to_list_item(asset) for asset in assets],
        pagination=pagination_metadata,
    )


@polyclinic_assets_router.get(
    "/patients/{patient_id}/polyclinic-assets",
    response_model=PatientPolyclinicAssetsResponseSchema,
    summary="Получить активы поликлиники пациента",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "polyclinic_assets", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_polyclinic_assets_by_patient(
        patient_id: UUID,
        pagination_params: PaginationParams = Depends(),
        polyclinic_asset_service: PolyclinicAssetService = Depends(
            Provide[AssetsJournalContainer.polyclinic_asset_service]
        ),
        patients_service: PatientService = Depends(
            Provide[AssetsJournalContainer.patients_service]
        ),
) -> PatientPolyclinicAssetsResponseSchema:
    """Получить активы поликлиники пациента"""

    # Получаем информацию о пациенте
    patient = await patients_service.get_by_id(patient_id)

    assets, total_count = await polyclinic_asset_service.get_assets_by_patient(
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

    return PatientPolyclinicAssetsResponseSchema(
        patient_id=patient.id,
        patient_full_name=f"{patient.last_name} {patient.first_name} {patient.middle_name or ''}".strip(),
        patient_iin=patient.iin,
        total_assets=total_count,
        items=[map_polyclinic_asset_domain_to_list_item(asset) for asset in assets],
        pagination=pagination_metadata,
    )


@polyclinic_assets_router.post(
    "/polyclinic-assets",
    response_model=PolyclinicAssetListItemSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый актив поликлиники",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "polyclinic_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def create_polyclinic_asset(
        create_schema: CreatePolyclinicAssetSchema,
        polyclinic_asset_service: PolyclinicAssetService = Depends(
            Provide[AssetsJournalContainer.polyclinic_asset_service]
        ),
) -> PolyclinicAssetListItemSchema:
    """Создать новый актив поликлиники"""
    asset = await polyclinic_asset_service.create_asset(create_schema)
    return map_polyclinic_asset_domain_to_list_item(asset)


@polyclinic_assets_router.post(
    "/polyclinic-assets/by-patient-id",
    response_model=PolyclinicAssetListItemSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый актив поликлиники по ID пациента",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "polyclinic_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def create_polyclinic_asset_by_patient_id(
        create_schema: CreatePolyclinicAssetByPatientIdSchema,
        polyclinic_asset_service: PolyclinicAssetService = Depends(
            Provide[AssetsJournalContainer.polyclinic_asset_service]
        ),
        patients_service: PatientService = Depends(
            Provide[AssetsJournalContainer.patients_service]
        ),
) -> PolyclinicAssetListItemSchema:
    """Создать новый актив поликлиники по ID пациента"""
    patient = await patients_service.get_by_id(create_schema.patient_id)

    # Создаем актив поликлиники
    asset = await polyclinic_asset_service.create_asset_by_patient_id(create_schema, patient.id)
    return map_polyclinic_asset_domain_to_list_item(asset)


@polyclinic_assets_router.patch(
    "/polyclinic-assets/{asset_id}",
    response_model=PolyclinicAssetResponseSchema,
    summary="Обновить актив поликлиники",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "polyclinic_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def update_polyclinic_asset(
        asset_id: UUID,
        update_schema: UpdatePolyclinicAssetSchema,
        polyclinic_asset_service: PolyclinicAssetService = Depends(
            Provide[AssetsJournalContainer.polyclinic_asset_service]
        ),
) -> PolyclinicAssetResponseSchema:
    """Обновить актив поликлиники"""
    asset = await polyclinic_asset_service.update_asset(asset_id, update_schema)
    return map_polyclinic_asset_domain_to_full_response(asset)


@polyclinic_assets_router.delete(
    "/polyclinic-assets/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить актив поликлиники",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "polyclinic_assets", "scopes": ["delete"]}]
    #         )
    #     )
    # ],
)
@inject
async def delete_polyclinic_asset(
        asset_id: UUID,
        polyclinic_asset_service: PolyclinicAssetService = Depends(
            Provide[AssetsJournalContainer.polyclinic_asset_service]
        ),
) -> None:
    """Удалить актив поликлиники"""
    await polyclinic_asset_service.delete_asset(asset_id)


@polyclinic_assets_router.post(
    "/polyclinic-assets/{asset_id}/confirm",
    response_model=PolyclinicAssetResponseSchema,
    summary="Подтвердить актив поликлиники",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "polyclinic_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def confirm_polyclinic_asset(
        asset_id: UUID,
        polyclinic_asset_service: PolyclinicAssetService = Depends(
            Provide[AssetsJournalContainer.polyclinic_asset_service]
        ),
) -> PolyclinicAssetResponseSchema:
    """Подтвердить актив поликлиники"""
    asset = await polyclinic_asset_service.confirm_asset(asset_id)
    return map_polyclinic_asset_domain_to_full_response(asset)


@polyclinic_assets_router.post(
    "/polyclinic-assets/{asset_id}/reject",
    response_model=PolyclinicAssetResponseSchema,
    summary="Отклонить актив поликлиники",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "polyclinic_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def reject_polyclinic_asset(
        asset_id: UUID,
        reject_schema: RejectPolyclinicAssetSchema,
        polyclinic_asset_service: PolyclinicAssetService = Depends(
            Provide[AssetsJournalContainer.polyclinic_asset_service]
        ),
) -> PolyclinicAssetResponseSchema:
    """Отклонить актив поликлиники"""
    asset = await polyclinic_asset_service.reject_asset(asset_id, reject_schema)
    return map_polyclinic_asset_domain_to_full_response(asset)


@polyclinic_assets_router.post(
    "/polyclinic-assets/{asset_id}/transfer",
    response_model=PolyclinicAssetResponseSchema,
    summary="Передать актив поликлиники другой организации",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "polyclinic_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def transfer_polyclinic_asset(
        asset_id: UUID,
        transfer_data: TransferPolyclinicAssetSchema,
        polyclinic_asset_service: PolyclinicAssetService = Depends(
            Provide[AssetsJournalContainer.polyclinic_asset_service]
        ),
) -> PolyclinicAssetResponseSchema:
    """Передать актив поликлиники другой организации"""
    asset = await polyclinic_asset_service.transfer_to_organization(
        asset_id=asset_id,
        new_organization_id=transfer_data.new_organization_id,
        transfer_reason=transfer_data.transfer_reason,
        update_patient_attachment=transfer_data.update_patient_attachment
    )
    return map_polyclinic_asset_domain_to_full_response(asset)


@polyclinic_assets_router.post(
    "/polyclinic-assets/load-from-bg",
    response_model=List[PolyclinicAssetListItemSchema],
    summary="Загрузить активы поликлиники из файла BG (временно)",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "polyclinic_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def load_polyclinic_assets_from_bg(
        polyclinic_asset_service: PolyclinicAssetService = Depends(
            Provide[AssetsJournalContainer.polyclinic_asset_service]
        ),
) -> List[PolyclinicAssetListItemSchema]:
    """
    Загрузить активы поликлиники из файла BG (временная функция для тестирования)
    Позже будет заменена на интеграцию с BG API
    """
    assets = await polyclinic_asset_service.load_assets_from_bg_file()
    return [map_polyclinic_asset_domain_to_list_item(asset) for asset in assets]


# @polyclinic_assets_router.get(
#     "/polyclinic-assets/statistics",
#     response_model=PolyclinicAssetStatisticsSchema,
#     summary="Получить статистику активов поликлиники",
#     # dependencies=[
#     #     Depends(
#     #         check_user_permissions(
#     #             resources=[{"resource_name": "polyclinic_assets", "scopes": ["read"]}]
#     #         )
#     #     )
#     # ],
# )
# @inject
# async def get_polyclinic_assets_statistics(
#         patient_search: str = Query(None, description="Поиск по ФИО пациента"),
#         patient_id: UUID = Query(None, description="ID пациента"),
#         patient_iin: str = Query(None, description="ИИН пациента"),
#         date_from: str = Query(None, description="Дата начала периода"),
#         date_to: str = Query(None, description="Дата окончания периода"),
#         status: AssetStatusEnum = Query(None, description="Статус актива"),
#         delivery_status: AssetDeliveryStatusEnum = Query(None, description="Статус доставки"),
#         area: str = Query(None, description="Участок"),
#         specialization: str = Query(None, description="Специализация"),
#         specialist: str = Query(None, description="Специалист"),
#         visit_type: PolyclinicVisitTypeEnum = Query(None, description="Тип посещения"),
#         service_type: PolyclinicServiceTypeEnum = Query(None, description="Тип услуги"),
#         visit_outcome: PolyclinicOutcomeEnum = Query(None, description="Исход посещения"),
#         organization_id: int = Query(None, description="ID организации"),
#         polyclinic_asset_service: PolyclinicAssetService = Depends(
#             Provide[AssetsJournalContainer.polyclinic_asset_service]
#         ),
# ) -> PolyclinicAssetStatisticsSchema:
#     """Получить статистику активов поликлиники"""
#
#     filter_params = PolyclinicAssetFilterParams(
#         patient_search=patient_search,
#         patient_id=patient_id,
#         patient_iin=patient_iin,
#         date_from=date_from,
#         date_to=date_to,
#         status=status,
#         delivery_status=delivery_status,
#         area=area,
#         specialization=specialization,
#         specialist=specialist,
#         visit_type=visit_type,
#         service_type=service_type,
#         visit_outcome=visit_outcome,
#         organization_id=organization_id,
#     )
#
#     return await polyclinic_asset_service.get_statistics(filter_params)