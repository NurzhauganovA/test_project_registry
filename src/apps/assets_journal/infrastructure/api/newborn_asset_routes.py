import math
from datetime import datetime
from typing import List
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status, Query

from src.apps.assets_journal.container import AssetsJournalContainer
from src.apps.assets_journal.infrastructure.api.schemas.requests.newborn_asset_schemas import (
    NewbornAssetFilterParams,
    CreateNewbornAssetSchema,
    UpdateNewbornAssetSchema,
    CreateNewbornAssetByPatientIdSchema,
)
from src.apps.assets_journal.infrastructure.api.schemas.responses.newborn_asset_schemas import (
    MultipleNewbornAssetsResponseSchema,
    NewbornAssetResponseSchema,
    NewbornAssetListItemSchema,
    NewbornAssetStatisticsSchema,
    NewbornAssetsByOrganizationResponseSchema,
    PatientNewbornAssetsResponseSchema,
)
from src.apps.assets_journal.mappers.newborn_asset_mappers import (
    map_newborn_asset_domain_to_full_response,
    map_newborn_asset_domain_to_list_item,
)
from src.apps.assets_journal.services.newborn_asset_service import (
    NewbornAssetService,
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
    NewbornConditionEnum,
    DeliveryTypeEnum,
)

newborn_assets_router = APIRouter()


@newborn_assets_router.get(
    "/newborn-assets/{asset_id}",
    response_model=NewbornAssetResponseSchema,
    summary="Получить актив новорожденного по ID (детальный просмотр)",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "newborn_assets", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_newborn_asset_by_id(
        asset_id: UUID,
        newborn_asset_service: NewbornAssetService = Depends(
            Provide[AssetsJournalContainer.newborn_asset_service]
        ),
) -> NewbornAssetResponseSchema:
    """Получить актив новорожденного по ID"""
    asset = await newborn_asset_service.get_by_id(asset_id)
    return map_newborn_asset_domain_to_full_response(asset)


@newborn_assets_router.get(
    "/newborn-assets",
    response_model=MultipleNewbornAssetsResponseSchema,
    summary="Получить список активов новорожденных с фильтрацией",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "newborn_assets", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_newborn_assets(
        pagination_params: PaginationParams = Depends(),
        # Параметры фильтрации
        patient_search: str = Query(None, description="Поиск по ФИО пациента"),
        patient_id: UUID = Query(None, description="ID пациента"),
        patient_iin: str = Query(None, description="ИИН пациента"),
        mother_search: str = Query(None, description="Поиск по ФИО матери"),
        mother_iin: str = Query(None, description="ИИН матери"),
        date_from: datetime = Query(None, description="Дата начала периода"),
        date_to: datetime = Query(None, description="Дата окончания периода"),
        status: AssetStatusEnum = Query(None, description="Статус актива"),
        delivery_status: AssetDeliveryStatusEnum = Query(None, description="Статус доставки"),
        newborn_condition: NewbornConditionEnum = Query(None, description="Состояние новорожденного"),
        delivery_type: DeliveryTypeEnum = Query(None, description="Тип родов"),
        diagnosis_code: str = Query(None, description="Код диагноза"),
        organization_id: UUID = Query(None, description="ID организации"),
        newborn_asset_service: NewbornAssetService = Depends(
            Provide[AssetsJournalContainer.newborn_asset_service]
        ),
) -> MultipleNewbornAssetsResponseSchema:
    """Получить список активов новорожденных с фильтрацией и пагинацией"""

    # Создаем объект фильтров
    filter_params = NewbornAssetFilterParams(
        patient_search=patient_search,
        patient_id=patient_id,
        patient_iin=patient_iin,
        mother_search=mother_search,
        mother_iin=mother_iin,
        date_from=date_from,
        date_to=date_to,
        status=status,
        delivery_status=delivery_status,
        newborn_condition=newborn_condition,
        delivery_type=delivery_type,
        diagnosis_code=diagnosis_code,
        organization_id=organization_id,
    )

    assets, total_count = await newborn_asset_service.get_assets(
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

    return MultipleNewbornAssetsResponseSchema(
        items=[map_newborn_asset_domain_to_list_item(asset) for asset in assets],
        pagination=pagination_metadata,
    )


@newborn_assets_router.get(
    "/organizations/{organization_id}/newborn-assets",
    response_model=NewbornAssetsByOrganizationResponseSchema,
    summary="Получить активы новорожденных по организации",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "newborn_assets", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_newborn_assets_by_organization(
        organization_id: int,  # Это path-параметр
        pagination_params: PaginationParams = Depends(),
        newborn_asset_service: NewbornAssetService = Depends(
            Provide[AssetsJournalContainer.newborn_asset_service]
        ),
        medical_org_service: MedicalOrganizationsCatalogService = Depends(
            Provide[AssetsJournalContainer.medical_organizations_catalog_service]
        ),
) -> NewbornAssetsByOrganizationResponseSchema:
    """Получить активы новорожденных по организации"""

    # Получаем информацию об организации
    organization = await medical_org_service.get_by_id(organization_id)

    # Создаем фильтры вручную, включая organization_id
    filter_params = NewbornAssetFilterParams(organization_id=organization_id)

    assets, total_count = await newborn_asset_service.get_assets_by_organization(
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

    return NewbornAssetsByOrganizationResponseSchema(
        organization_id=organization.id,
        organization_name=organization.name,
        organization_code=organization.organization_code,
        total_assets=total_count,
        items=[map_newborn_asset_domain_to_list_item(asset) for asset in assets],
        pagination=pagination_metadata,
    )


@newborn_assets_router.get(
    "/patients/{patient_id}/newborn-assets",
    response_model=PatientNewbornAssetsResponseSchema,
    summary="Получить активы новорожденных пациента",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "newborn_assets", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_newborn_assets_by_patient(
        patient_id: UUID,
        pagination_params: PaginationParams = Depends(),
        newborn_asset_service: NewbornAssetService = Depends(
            Provide[AssetsJournalContainer.newborn_asset_service]
        ),
        patients_service: PatientService = Depends(
            Provide[AssetsJournalContainer.patients_service]
        ),
) -> PatientNewbornAssetsResponseSchema:
    """Получить активы новорожденных пациента"""

    # Получаем информацию о пациенте
    patient = await patients_service.get_by_id(patient_id)

    assets, total_count = await newborn_asset_service.get_assets_by_patient(
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

    return PatientNewbornAssetsResponseSchema(
        patient_id=patient.id,
        patient_full_name=f"{patient.last_name} {patient.first_name} {patient.middle_name or ''}".strip(),
        patient_iin=patient.iin,
        total_assets=total_count,
        items=[map_newborn_asset_domain_to_list_item(asset) for asset in assets],
        pagination=pagination_metadata,
    )


@newborn_assets_router.post(
    "/newborn-assets",
    response_model=NewbornAssetListItemSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый актив новорожденного",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "newborn_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def create_newborn_asset(
        create_schema: CreateNewbornAssetSchema,
        newborn_asset_service: NewbornAssetService = Depends(
            Provide[AssetsJournalContainer.newborn_asset_service]
        ),
) -> NewbornAssetListItemSchema:
    """Создать новый актив новорожденного"""
    asset = await newborn_asset_service.create_asset(create_schema)
    return map_newborn_asset_domain_to_list_item(asset)


@newborn_assets_router.post(
    "/newborn-assets/by-patient-id",
    response_model=NewbornAssetListItemSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый актив новорожденного по ID пациента",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "newborn_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def create_newborn_asset_by_patient_id(
        create_schema: CreateNewbornAssetByPatientIdSchema,
        newborn_asset_service: NewbornAssetService = Depends(
            Provide[AssetsJournalContainer.newborn_asset_service]
        ),
        patients_service: PatientService = Depends(
            Provide[AssetsJournalContainer.patients_service]
        ),
) -> NewbornAssetListItemSchema:
    """Создать новый актив новорожденного по ID пациента"""
    patient = await patients_service.get_by_id(create_schema.patient_id)

    # Создаем актив новорожденного
    asset = await newborn_asset_service.create_asset_by_patient_id(create_schema, patient.id)
    return map_newborn_asset_domain_to_list_item(asset)


@newborn_assets_router.patch(
    "/newborn-assets/{asset_id}",
    response_model=NewbornAssetResponseSchema,
    summary="Обновить актив новорожденного",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "newborn_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def update_newborn_asset(
        asset_id: UUID,
        update_schema: UpdateNewbornAssetSchema,
        newborn_asset_service: NewbornAssetService = Depends(
            Provide[AssetsJournalContainer.newborn_asset_service]
        ),
) -> NewbornAssetResponseSchema:
    """Обновить актив новорожденного"""
    asset = await newborn_asset_service.update_asset(asset_id, update_schema)
    return map_newborn_asset_domain_to_full_response(asset)


@newborn_assets_router.delete(
    "/newborn-assets/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить актив новорожденного",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "newborn_assets", "scopes": ["delete"]}]
    #         )
    #     )
    # ],
)
@inject
async def delete_newborn_asset(
        asset_id: UUID,
        newborn_asset_service: NewbornAssetService = Depends(
            Provide[AssetsJournalContainer.newborn_asset_service]
        ),
) -> None:
    """Удалить актив новорожденного"""
    await newborn_asset_service.delete_asset(asset_id)


# @newborn_assets_router.get(
#     "/newborn-assets/statistics",
#     response_model=NewbornAssetStatisticsSchema,
#     summary="Получить статистику активов новорожденных",
#     # dependencies=[
#     #     Depends(
#     #         check_user_permissions(
#     #             resources=[{"resource_name": "newborn_assets", "scopes": ["read"]}]
#     #         )
#     #     )
#     # ],
# )
# @inject
# async def get_newborn_assets_statistics(
#         patient_search: str = Query(None, description="Поиск по ФИО пациента"),
#         patient_id: UUID = Query(None, description="ID пациента"),
#         patient_iin: str = Query(None, description="ИИН пациента"),
#         mother_search: str = Query(None, description="Поиск по ФИО матери"),
#         mother_iin: str = Query(None, description="ИИН матери"),
#         date_from: str = Query(None, description="Дата начала периода"),
#         date_to: str = Query(None, description="Дата окончания периода"),
#         status: AssetStatusEnum = Query(None, description="Статус актива"),
#         delivery_status: AssetDeliveryStatusEnum = Query(None, description="Статус доставки"),
#         newborn_condition: NewbornConditionEnum = Query(None, description="Состояние новорожденного"),
#         delivery_type: DeliveryTypeEnum = Query(None, description="Тип родов"),
#         diagnosis_code: str = Query(None, description="Код диагноза"),
#         organization_id: UUID = Query(None, description="ID организации"),
#         newborn_asset_service: NewbornAssetService = Depends(
#             Provide[AssetsJournalContainer.newborn_asset_service]
#         ),
# ) -> NewbornAssetStatisticsSchema:
#     """Получить статистику активов новорожденных"""
#
#     filter_params = NewbornAssetFilterParams(
#         patient_search=patient_search,
#         patient_id=patient_id,
#         patient_iin=patient_iin,
#         mother_search=mother_search,
#         mother_iin=mother_iin,
#         date_from=date_from,
#         date_to=date_to,
#         status=status,
#         delivery_status=delivery_status,
#         newborn_condition=newborn_condition,
#         delivery_type=delivery_type,
#         diagnosis_code=diagnosis_code,
#         organization_id=organization_id,
#     )
#
#     return await newborn_asset_service.get_statistics(filter_params)


@newborn_assets_router.post(
    "/newborn-assets/{asset_id}/confirm",
    response_model=NewbornAssetResponseSchema,
    summary="Подтвердить актив новорожденного",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "newborn_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def confirm_newborn_asset(
        asset_id: UUID,
        newborn_asset_service: NewbornAssetService = Depends(
            Provide[AssetsJournalContainer.newborn_asset_service]
        ),
) -> NewbornAssetResponseSchema:
    """Подтвердить актив новорожденного"""
    asset = await newborn_asset_service.confirm_asset(asset_id)
    return map_newborn_asset_domain_to_full_response(asset)


@newborn_assets_router.post(
    "/newborn-assets/load-from-bg",
    response_model=List[NewbornAssetListItemSchema],
    summary="Загрузить активы новорожденных из файла BG (временно)",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "newborn_assets", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def load_newborn_assets_from_bg(
        newborn_asset_service: NewbornAssetService = Depends(
            Provide[AssetsJournalContainer.newborn_asset_service]
        ),
) -> List[NewbornAssetListItemSchema]:
    """
    Загрузить активы новорожденных из файла BG (временная функция для тестирования)
    Позже будет заменена на интеграцию с BG API
    """
    assets = await newborn_asset_service.load_assets_from_bg_file()
    return [map_newborn_asset_domain_to_list_item(asset) for asset in assets]