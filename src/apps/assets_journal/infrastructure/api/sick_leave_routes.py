import math
from datetime import datetime
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status, Query

from src.apps.assets_journal.container import AssetsJournalContainer
from src.apps.assets_journal.infrastructure.api.schemas.requests.sick_leave_schemas import (
    SickLeaveFilterParams,
    CreateSickLeaveSchema,
    UpdateSickLeaveSchema,
    CreateSickLeaveByPatientIdSchema,
    CloseSickLeaveSchema,
    ExtendSickLeaveSchema,
)
from src.apps.assets_journal.infrastructure.api.schemas.responses.sick_leave_schemas import (
    MultipleSickLeavesResponseSchema,
    SickLeaveResponseSchema,
    SickLeaveListItemSchema,
    SickLeaveStatisticsSchema,
    PatientSickLeavesResponseSchema,
    SickLeaveExtensionsResponseSchema,
    SickLeavesByOrganizationResponseSchema,
)
from src.apps.assets_journal.mappers.sick_leave_mappers import (
    map_sick_leave_domain_to_full_response,
    map_sick_leave_domain_to_list_item,
)
from src.apps.assets_journal.services.sick_leave_service import SickLeaveService
from src.apps.catalogs.services.medical_organizations_catalog_service import MedicalOrganizationsCatalogService
from src.apps.patients.services.patients_service import PatientService
from src.shared.dependencies.check_user_permissions import check_user_permissions
from src.shared.schemas.pagination_schemas import (
    PaginationMetaDataSchema,
    PaginationParams,
)
from src.apps.assets_journal.domain.enums import (
    SickLeaveStatusEnum,
    SickLeaveReasonEnum,
)

sick_leaves_router = APIRouter()


@sick_leaves_router.get(
    "/sick-leaves/{sick_leave_id}",
    response_model=SickLeaveResponseSchema,
    summary="Получить больничный лист по ID (детальный просмотр)",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "sick_leaves", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_sick_leave_by_id(
        sick_leave_id: UUID,
        sick_leave_service: SickLeaveService = Depends(
            Provide[AssetsJournalContainer.sick_leave_service]
        ),
) -> SickLeaveResponseSchema:
    """Получить больничный лист по ID"""
    sick_leave = await sick_leave_service.get_by_id(sick_leave_id)
    return map_sick_leave_domain_to_full_response(sick_leave)


@sick_leaves_router.get(
    "/sick-leaves",
    response_model=MultipleSickLeavesResponseSchema,
    summary="Получить список больничных листов с фильтрацией",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "sick_leaves", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_sick_leaves(
        pagination_params: PaginationParams = Depends(),
        # Параметры фильтрации
        patient_search: str = Query(None, description="Поиск по ФИО или ИИН пациента"),
        patient_id: UUID = Query(None, description="ID пациента"),
        patient_iin: str = Query(None, description="ИИН пациента"),
        receive_date_from: datetime = Query(None, description="Дата получения от"),
        receive_date_to: datetime = Query(None, description="Дата получения до"),
        disability_start_date_from: datetime = Query(None, description="Начало нетрудоспособности от"),
        disability_start_date_to: datetime = Query(None, description="Начало нетрудоспособности до"),
        status: SickLeaveStatusEnum = Query(None, description="Статус больничного листа"),
        sick_leave_reason: SickLeaveReasonEnum = Query(None, description="Причина выдачи"),
        specialist: str = Query(None, description="Специалист"),
        specialization: str = Query(None, description="Специализация"),
        area: str = Query(None, description="Участок"),
        workplace_name: str = Query(None, description="Место работы"),
        is_primary: bool = Query(None, description="Только первичные (true) или продления (false)"),
        is_active: bool = Query(None, description="Только активные больничные листы"),
        organization_id: int = Query(None, description="ID организации"),
        sick_leave_service: SickLeaveService = Depends(
            Provide[AssetsJournalContainer.sick_leave_service]
        ),
) -> MultipleSickLeavesResponseSchema:
    """Получить список больничных листов с фильтрацией и пагинацией"""

    # Создаем объект фильтров
    filter_params = SickLeaveFilterParams(
        patient_search=patient_search,
        patient_id=patient_id,
        patient_iin=patient_iin,
        receive_date_from=receive_date_from,
        receive_date_to=receive_date_to,
        disability_start_date_from=disability_start_date_from,
        disability_start_date_to=disability_start_date_to,
        status=status,
        sick_leave_reason=sick_leave_reason,
        specialist=specialist,
        specialization=specialization,
        area=area,
        workplace_name=workplace_name,
        is_primary=is_primary,
        is_active=is_active,
        organization_id=organization_id,
    )

    sick_leaves, total_count = await sick_leave_service.get_sick_leaves(
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

    return MultipleSickLeavesResponseSchema(
        items=[map_sick_leave_domain_to_list_item(sick_leave) for sick_leave in sick_leaves],
        pagination=pagination_metadata,
    )


@sick_leaves_router.get(
    "/organizations/{organization_id}/sick-leaves",
    response_model=SickLeavesByOrganizationResponseSchema,
    summary="Получить больничные листы по организации",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "sick_leaves", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_sick_leaves_by_organization(
        organization_id: int,
        pagination_params: PaginationParams = Depends(),
        sick_leave_service: SickLeaveService = Depends(
            Provide[AssetsJournalContainer.sick_leave_service]
        ),
        medical_org_service: MedicalOrganizationsCatalogService = Depends(
            Provide[AssetsJournalContainer.medical_organizations_catalog_service]
        ),
) -> SickLeavesByOrganizationResponseSchema:
    """Получить больничные листы по организации"""

    # Получаем информацию об организации
    organization = await medical_org_service.get_by_id(organization_id)

    # Создаем фильтры вручную, включая organization_id
    filter_params = SickLeaveFilterParams(organization_id=organization_id)

    sick_leaves, total_count = await sick_leave_service.get_sick_leaves_by_organization(
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

    return SickLeavesByOrganizationResponseSchema(
        organization_id=organization.id,
        organization_name=organization.name,
        organization_code=organization.organization_code,
        total_sick_leaves=total_count,
        items=[map_sick_leave_domain_to_list_item(sick_leave) for sick_leave in sick_leaves],
        pagination=pagination_metadata,
    )


@sick_leaves_router.get(
    "/patients/{patient_id}/sick-leaves",
    response_model=PatientSickLeavesResponseSchema,
    summary="Получить больничные листы пациента",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "sick_leaves", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_sick_leaves_by_patient(
        patient_id: UUID,
        pagination_params: PaginationParams = Depends(),
        sick_leave_service: SickLeaveService = Depends(
            Provide[AssetsJournalContainer.sick_leave_service]
        ),
        patients_service: PatientService = Depends(
            Provide[AssetsJournalContainer.patients_service]
        ),
) -> PatientSickLeavesResponseSchema:
    """Получить больничные листы пациента"""

    # Получаем информацию о пациенте
    patient = await patients_service.get_by_id(patient_id)

    sick_leaves, total_count = await sick_leave_service.get_sick_leaves_by_patient(
        patient_id=patient_id,
        pagination_params=pagination_params,
    )

    # Получаем активные больничные листы
    active_sick_leaves = await sick_leave_service.get_active_sick_leaves_by_patient(patient_id)

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

    return PatientSickLeavesResponseSchema(
        patient_id=patient.id,
        patient_full_name=f"{patient.last_name} {patient.first_name} {patient.middle_name or ''}".strip(),
        patient_iin=patient.iin,
        total_sick_leaves=total_count,
        active_sick_leaves=len(active_sick_leaves),
        items=[map_sick_leave_domain_to_list_item(sick_leave) for sick_leave in sick_leaves],
        pagination=pagination_metadata,
    )


@sick_leaves_router.get(
    "/sick-leaves/{parent_sick_leave_id}/extensions",
    response_model=SickLeaveExtensionsResponseSchema,
    summary="Получить продления больничного листа",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "sick_leaves", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_sick_leave_extensions(
        parent_sick_leave_id: UUID,
        sick_leave_service: SickLeaveService = Depends(
            Provide[AssetsJournalContainer.sick_leave_service]
        ),
) -> SickLeaveExtensionsResponseSchema:
    """Получить продления больничного листа"""

    # Получаем продления
    extensions = await sick_leave_service.get_extensions(parent_sick_leave_id)

    return SickLeaveExtensionsResponseSchema(
        parent_sick_leave_id=parent_sick_leave_id,
        extensions=[map_sick_leave_domain_to_full_response(ext) for ext in extensions],
        total_extensions=len(extensions),
    )


@sick_leaves_router.post(
    "/sick-leaves",
    response_model=SickLeaveListItemSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый больничный лист",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "sick_leaves", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def create_sick_leave(
        create_schema: CreateSickLeaveSchema,
        sick_leave_service: SickLeaveService = Depends(
            Provide[AssetsJournalContainer.sick_leave_service]
        ),
) -> SickLeaveListItemSchema:
    """Создать новый больничный лист"""
    sick_leave = await sick_leave_service.create_sick_leave(create_schema)
    return map_sick_leave_domain_to_list_item(sick_leave)


@sick_leaves_router.post(
    "/sick-leaves/by-patient-id",
    response_model=SickLeaveListItemSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый больничный лист по ID пациента",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "sick_leaves", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def create_sick_leave_by_patient_id(
        create_schema: CreateSickLeaveByPatientIdSchema,
        sick_leave_service: SickLeaveService = Depends(
            Provide[AssetsJournalContainer.sick_leave_service]
        ),
        patients_service: PatientService = Depends(
            Provide[AssetsJournalContainer.patients_service]
        ),
) -> SickLeaveListItemSchema:
    """Создать новый больничный лист по ID пациента"""
    patient = await patients_service.get_by_id(create_schema.patient_id)

    # Создаем больничный лист
    sick_leave = await sick_leave_service.create_sick_leave_by_patient_id(create_schema, patient.id)
    return map_sick_leave_domain_to_list_item(sick_leave)


@sick_leaves_router.patch(
    "/sick-leaves/{sick_leave_id}",
    response_model=SickLeaveResponseSchema,
    summary="Обновить больничный лист",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "sick_leaves", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def update_sick_leave(
        sick_leave_id: UUID,
        update_schema: UpdateSickLeaveSchema,
        sick_leave_service: SickLeaveService = Depends(
            Provide[AssetsJournalContainer.sick_leave_service]
        ),
) -> SickLeaveResponseSchema:
    """Обновить больничный лист"""
    sick_leave = await sick_leave_service.update_sick_leave(sick_leave_id, update_schema)
    return map_sick_leave_domain_to_full_response(sick_leave)


@sick_leaves_router.post(
    "/sick-leaves/{sick_leave_id}/close",
    response_model=SickLeaveResponseSchema,
    summary="Закрыть больничный лист",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "sick_leaves", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def close_sick_leave(
        sick_leave_id: UUID,
        close_schema: CloseSickLeaveSchema,
        sick_leave_service: SickLeaveService = Depends(
            Provide[AssetsJournalContainer.sick_leave_service]
        ),
) -> SickLeaveResponseSchema:
    """Закрыть больничный лист"""
    sick_leave = await sick_leave_service.close_sick_leave(sick_leave_id, close_schema)
    return map_sick_leave_domain_to_full_response(sick_leave)


@sick_leaves_router.post(
    "/sick-leaves/{sick_leave_id}/extend",
    response_model=SickLeaveResponseSchema,
    summary="Продлить больничный лист",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "sick_leaves", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def extend_sick_leave(
        sick_leave_id: UUID,
        extend_schema: ExtendSickLeaveSchema,
        sick_leave_service: SickLeaveService = Depends(
            Provide[AssetsJournalContainer.sick_leave_service]
        ),
) -> SickLeaveResponseSchema:
    """Продлить больничный лист"""
    sick_leave = await sick_leave_service.extend_sick_leave(sick_leave_id, extend_schema)
    return map_sick_leave_domain_to_full_response(sick_leave)


@sick_leaves_router.post(
    "/sick-leaves/{sick_leave_id}/cancel",
    response_model=SickLeaveResponseSchema,
    summary="Отменить больничный лист",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "sick_leaves", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def cancel_sick_leave(
        sick_leave_id: UUID,
        reason: str = Query(None, description="Причина отмены"),
        sick_leave_service: SickLeaveService = Depends(
            Provide[AssetsJournalContainer.sick_leave_service]
        ),
) -> SickLeaveResponseSchema:
    """Отменить больничный лист"""
    sick_leave = await sick_leave_service.cancel_sick_leave(sick_leave_id, reason)
    return map_sick_leave_domain_to_full_response(sick_leave)


@sick_leaves_router.post(
    "/sick-leaves/{sick_leave_id}/transfer",
    response_model=SickLeaveResponseSchema,
    summary="Передать больничный лист другой организации",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "sick_leaves", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def transfer_sick_leave(
        sick_leave_id: UUID,
        new_organization_id: int = Query(..., description="ID новой организации"),
        transfer_reason: str = Query(None, description="Причина передачи"),
        update_patient_attachment: bool = Query(True, description="Обновить attachment_data пациента"),
        sick_leave_service: SickLeaveService = Depends(
            Provide[AssetsJournalContainer.sick_leave_service]
        ),
) -> SickLeaveResponseSchema:
    """Передать больничный лист другой организации"""
    sick_leave = await sick_leave_service.transfer_to_organization(
        sick_leave_id=sick_leave_id,
        new_organization_id=new_organization_id,
        transfer_reason=transfer_reason,
        update_patient_attachment=update_patient_attachment,
    )
    return map_sick_leave_domain_to_full_response(sick_leave)


@sick_leaves_router.delete(
    "/sick-leaves/{sick_leave_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить больничный лист",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "sick_leaves", "scopes": ["delete"]}]
    #         )
    #     )
    # ],
)
@inject
async def delete_sick_leave(
        sick_leave_id: UUID,
        sick_leave_service: SickLeaveService = Depends(
            Provide[AssetsJournalContainer.sick_leave_service]
        ),
) -> None:
    """Удалить больничный лист"""
    await sick_leave_service.delete_sick_leave(sick_leave_id)


@sick_leaves_router.get(
    "/sick-leaves/statistics",
    response_model=SickLeaveStatisticsSchema,
    summary="Получить статистику больничных листов",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "sick_leaves", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_sick_leaves_statistics(
        patient_search: str = Query(None, description="Поиск по ФИО или ИИН пациента"),
        patient_id: UUID = Query(None, description="ID пациента"),
        patient_iin: str = Query(None, description="ИИН пациента"),
        receive_date_from: datetime = Query(None, description="Дата получения от"),
        receive_date_to: datetime = Query(None, description="Дата получения до"),
        status: SickLeaveStatusEnum = Query(None, description="Статус больничного листа"),
        sick_leave_reason: SickLeaveReasonEnum = Query(None, description="Причина выдачи"),
        specialist: str = Query(None, description="Специалист"),
        organization_id: int = Query(None, description="ID организации"),
        sick_leave_service: SickLeaveService = Depends(
            Provide[AssetsJournalContainer.sick_leave_service]
        ),
) -> SickLeaveStatisticsSchema:
    """Получить статистику больничных листов"""

    filter_params = SickLeaveFilterParams(
        patient_search=patient_search,
        patient_id=patient_id,
        patient_iin=patient_iin,
        receive_date_from=receive_date_from,
        receive_date_to=receive_date_to,
        status=status,
        sick_leave_reason=sick_leave_reason,
        specialist=specialist,
        organization_id=organization_id,
    )

    return await sick_leave_service.get_statistics(filter_params)