import math
from datetime import datetime
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status, Query

from src.apps.assets_journal.container import AssetsJournalContainer
from src.apps.assets_journal.infrastructure.api.schemas.requests.home_call_schemas import (
    HomeCallFilterParams,
    CreateHomeCallSchema,
    UpdateHomeCallSchema,
    CreateHomeCallByPatientIdSchema,
    CompleteHomeCallSchema,
)
from src.apps.assets_journal.infrastructure.api.schemas.responses.home_call_schemas import (
    MultipleHomeCallsResponseSchema,
    HomeCallResponseSchema,
    HomeCallListItemSchema,
    HomeCallStatisticsSchema,
    PatientHomeCallsResponseSchema,
    HomeCallsByOrganizationResponseSchema,
    HomeCallsBySpecialistResponseSchema,
)
from src.apps.assets_journal.mappers.home_call_mappers import (
    map_home_call_domain_to_full_response,
    map_home_call_domain_to_list_item,
)
from src.apps.assets_journal.services.home_call_service import HomeCallService
from src.apps.catalogs.services.medical_organizations_catalog_service import MedicalOrganizationsCatalogService
from src.apps.patients.services.patients_service import PatientService
from src.shared.dependencies.check_user_permissions import check_user_permissions
from src.shared.schemas.pagination_schemas import (
    PaginationMetaDataSchema,
    PaginationParams,
)
from src.apps.assets_journal.domain.enums import (
    HomeCallStatusEnum,
    HomeCallCategoryEnum,
    HomeCallSourceEnum,
    HomeCallTypeEnum,
)

home_calls_router = APIRouter()


@home_calls_router.get(
    "/home-calls/{home_call_id}",
    response_model=HomeCallResponseSchema,
    summary="Получить вызов на дом по ID (детальный просмотр)",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "home_calls", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_home_call_by_id(
        home_call_id: UUID,
        home_call_service: HomeCallService = Depends(
            Provide[AssetsJournalContainer.home_call_service]
        ),
) -> HomeCallResponseSchema:
    """Получить вызов на дом по ID"""
    home_call = await home_call_service.get_by_id(home_call_id)
    return map_home_call_domain_to_full_response(home_call)


@home_calls_router.get(
    "/home-calls/by-number/{call_number}",
    response_model=HomeCallResponseSchema,
    summary="Получить вызов на дом по номеру",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "home_calls", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_home_call_by_number(
        call_number: str,
        home_call_service: HomeCallService = Depends(
            Provide[AssetsJournalContainer.home_call_service]
        ),
) -> HomeCallResponseSchema:
    """Получить вызов на дом по номеру"""
    home_call = await home_call_service.get_by_call_number(call_number)
    return map_home_call_domain_to_full_response(home_call)


@home_calls_router.get(
    "/home-calls",
    response_model=MultipleHomeCallsResponseSchema,
    summary="Получить список вызовов на дом с фильтрацией",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "home_calls", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_home_calls(
        pagination_params: PaginationParams = Depends(),
        # Параметры фильтрации
        patient_search: str = Query(None, description="Поиск по ФИО или ИИН пациента"),
        patient_id: UUID = Query(None, description="ID пациента"),
        patient_iin: str = Query(None, description="ИИН пациента"),
        registration_date_from: datetime = Query(None, description="Дата регистрации от"),
        registration_date_to: datetime = Query(None, description="Дата регистрации до"),
        execution_date_from: datetime = Query(None, description="Дата выполнения от"),
        execution_date_to: datetime = Query(None, description="Дата выполнения до"),
        status: HomeCallStatusEnum = Query(None, description="Статус вызова"),
        category: HomeCallCategoryEnum = Query(None, description="Категория вызова"),
        source: HomeCallSourceEnum = Query(None, description="Источник вызова"),
        call_type: HomeCallTypeEnum = Query(None, description="Тип вызова"),
        specialist: str = Query(None, description="Специалист"),
        specialization: str = Query(None, description="Специализация"),
        area: str = Query(None, description="Участок"),
        is_active: bool = Query(None, description="Только активные вызовы"),
        organization_id: int = Query(None, description="ID организации"),
        call_number: str = Query(None, description="Номер вызова"),
        home_call_service: HomeCallService = Depends(
            Provide[AssetsJournalContainer.home_call_service]
        ),
) -> MultipleHomeCallsResponseSchema:
    """Получить список вызовов на дом с фильтрацией и пагинацией"""

    # Создаем объект фильтров
    filter_params = HomeCallFilterParams(
        patient_search=patient_search,
        patient_id=patient_id,
        patient_iin=patient_iin,
        registration_date_from=registration_date_from,
        registration_date_to=registration_date_to,
        execution_date_from=execution_date_from,
        execution_date_to=execution_date_to,
        status=status,
        category=category,
        source=source,
        call_type=call_type,
        specialist=specialist,
        specialization=specialization,
        area=area,
        is_active=is_active,
        organization_id=organization_id,
        call_number=call_number,
    )

    home_calls, total_count = await home_call_service.get_home_calls(
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

    return MultipleHomeCallsResponseSchema(
        items=[map_home_call_domain_to_list_item(home_call) for home_call in home_calls],
        pagination=pagination_metadata,
    )


@home_calls_router.get(
    "/organizations/{organization_id}/home-calls",
    response_model=HomeCallsByOrganizationResponseSchema,
    summary="Получить вызовы на дом по организации",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "home_calls", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_home_calls_by_organization(
        organization_id: int,
        pagination_params: PaginationParams = Depends(),
        home_call_service: HomeCallService = Depends(
            Provide[AssetsJournalContainer.home_call_service]
        ),
        medical_org_service: MedicalOrganizationsCatalogService = Depends(
            Provide[AssetsJournalContainer.medical_organizations_catalog_service]
        ),
) -> HomeCallsByOrganizationResponseSchema:
    """Получить вызовы на дом по организации"""

    # Получаем информацию об организации
    organization = await medical_org_service.get_by_id(organization_id)

    # Создаем фильтры вручную, включая organization_id
    filter_params = HomeCallFilterParams(organization_id=organization_id)

    home_calls, total_count = await home_call_service.get_home_calls_by_organization(
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

    return HomeCallsByOrganizationResponseSchema(
        organization_id=organization.id,
        organization_name=organization.name,
        organization_code=organization.organization_code,
        total_calls=total_count,
        items=[map_home_call_domain_to_list_item(home_call) for home_call in home_calls],
        pagination=pagination_metadata,
    )


@home_calls_router.get(
    "/patients/{patient_id}/home-calls",
    response_model=PatientHomeCallsResponseSchema,
    summary="Получить вызовы на дом пациента",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "home_calls", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_home_calls_by_patient(
        patient_id: UUID,
        pagination_params: PaginationParams = Depends(),
        home_call_service: HomeCallService = Depends(
            Provide[AssetsJournalContainer.home_call_service]
        ),
        patients_service: PatientService = Depends(
            Provide[AssetsJournalContainer.patients_service]
        ),
) -> PatientHomeCallsResponseSchema:
    """Получить вызовы на дом пациента"""

    # Получаем информацию о пациенте
    patient = await patients_service.get_by_id(patient_id)

    home_calls, total_count = await home_call_service.get_home_calls_by_patient(
        patient_id=patient_id,
        pagination_params=pagination_params,
    )

    # Получаем активные вызовы на дом
    active_home_calls = await home_call_service.get_active_home_calls_by_patient(patient_id)

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

    return PatientHomeCallsResponseSchema(
        patient_id=patient.id,
        patient_full_name=f"{patient.last_name} {patient.first_name} {patient.middle_name or ''}".strip(),
        patient_iin=patient.iin,
        total_calls=total_count,
        active_calls=len(active_home_calls),
        items=[map_home_call_domain_to_list_item(home_call) for home_call in home_calls],
        pagination=pagination_metadata,
    )


@home_calls_router.get(
    "/specialists/{specialist}/home-calls",
    response_model=HomeCallsBySpecialistResponseSchema,
    summary="Получить вызовы на дом по специалисту",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "home_calls", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_home_calls_by_specialist(
        specialist: str,
        pagination_params: PaginationParams = Depends(),
        home_call_service: HomeCallService = Depends(
            Provide[AssetsJournalContainer.home_call_service]
        ),
) -> HomeCallsBySpecialistResponseSchema:
    """Получить вызовы на дом по специалисту"""

    home_calls, total_count = await home_call_service.get_home_calls_by_specialist(
        specialist=specialist,
        pagination_params=pagination_params,
    )

    # Подсчитываем активные и завершенные вызовы
    active_calls = len([call for call in home_calls if call.is_active])
    completed_calls = len([call for call in home_calls if call.is_completed])

    # Получаем данные первого вызова для определения специализации и участка
    specialization = ""
    area = ""
    if home_calls:
        specialization = home_calls[0].specialization
        area = home_calls[0].area

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

    return HomeCallsBySpecialistResponseSchema(
        specialist=specialist,
        specialization=specialization,
        area=area,
        total_calls=total_count,
        active_calls=active_calls,
        completed_calls=completed_calls,
        items=[map_home_call_domain_to_list_item(home_call) for home_call in home_calls],
        pagination=pagination_metadata,
    )


@home_calls_router.post(
    "/home-calls",
    response_model=HomeCallListItemSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый вызов на дом",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "home_calls", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def create_home_call(
        create_schema: CreateHomeCallSchema,
        home_call_service: HomeCallService = Depends(
            Provide[AssetsJournalContainer.home_call_service]
        ),
) -> HomeCallListItemSchema:
    """Создать новый вызов на дом"""
    home_call = await home_call_service.create_home_call(create_schema)
    return map_home_call_domain_to_list_item(home_call)


@home_calls_router.post(
    "/home-calls/by-patient-id",
    response_model=HomeCallListItemSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый вызов на дом по ID пациента",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "home_calls", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def create_home_call_by_patient_id(
        create_schema: CreateHomeCallByPatientIdSchema,
        home_call_service: HomeCallService = Depends(
            Provide[AssetsJournalContainer.home_call_service]
        ),
        patients_service: PatientService = Depends(
            Provide[AssetsJournalContainer.patients_service]
        ),
) -> HomeCallListItemSchema:
    """Создать новый вызов на дом по ID пациента"""
    patient = await patients_service.get_by_id(create_schema.patient_id)

    # Создаем вызов на дом
    home_call = await home_call_service.create_home_call_by_patient_id(create_schema, patient.id)
    return map_home_call_domain_to_list_item(home_call)


@home_calls_router.patch(
    "/home-calls/{home_call_id}",
    response_model=HomeCallResponseSchema,
    summary="Обновить вызов на дом",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "home_calls", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def update_home_call(
        home_call_id: UUID,
        update_schema: UpdateHomeCallSchema,
        home_call_service: HomeCallService = Depends(
            Provide[AssetsJournalContainer.home_call_service]
        ),
) -> HomeCallResponseSchema:
    """Обновить вызов на дом"""
    home_call = await home_call_service.update_home_call(home_call_id, update_schema)
    return map_home_call_domain_to_full_response(home_call)


@home_calls_router.post(
    "/home-calls/{home_call_id}/complete",
    response_model=HomeCallResponseSchema,
    summary="Завершить вызов на дом",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "home_calls", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def complete_home_call(
        home_call_id: UUID,
        complete_schema: CompleteHomeCallSchema,
        home_call_service: HomeCallService = Depends(
            Provide[AssetsJournalContainer.home_call_service]
        ),
) -> HomeCallResponseSchema:
    """Завершить вызов на дом"""
    home_call = await home_call_service.complete_home_call(home_call_id, complete_schema)
    return map_home_call_domain_to_full_response(home_call)


@home_calls_router.post(
    "/home-calls/{home_call_id}/start-processing",
    response_model=HomeCallResponseSchema,
    summary="Взять вызов на дом в работу",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "home_calls", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def start_processing_home_call(
        home_call_id: UUID,
        home_call_service: HomeCallService = Depends(
            Provide[AssetsJournalContainer.home_call_service]
        ),
) -> HomeCallResponseSchema:
    """Взять вызов на дом в работу"""
    home_call = await home_call_service.start_processing_home_call(home_call_id)
    return map_home_call_domain_to_full_response(home_call)


@home_calls_router.post(
    "/home-calls/{home_call_id}/cancel",
    response_model=HomeCallResponseSchema,
    summary="Отменить вызов на дом",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "home_calls", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def cancel_home_call(
        home_call_id: UUID,
        reason: str = Query(None, description="Причина отмены"),
        home_call_service: HomeCallService = Depends(
            Provide[AssetsJournalContainer.home_call_service]
        ),
) -> HomeCallResponseSchema:
    """Отменить вызов на дом"""
    home_call = await home_call_service.cancel_home_call(home_call_id, reason)
    return map_home_call_domain_to_full_response(home_call)


@home_calls_router.post(
    "/home-calls/{home_call_id}/transfer",
    response_model=HomeCallResponseSchema,
    summary="Передать вызов на дом другой организации",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "home_calls", "scopes": ["write"]}]
    #         )
    #     )
    # ],
)
@inject
async def transfer_home_call(
        home_call_id: UUID,
        new_organization_id: int = Query(..., description="ID новой организации"),
        transfer_reason: str = Query(None, description="Причина передачи"),
        update_patient_attachment: bool = Query(True, description="Обновить attachment_data пациента"),
        home_call_service: HomeCallService = Depends(
            Provide[AssetsJournalContainer.home_call_service]
        ),
) -> HomeCallResponseSchema:
    """Передать вызов на дом другой организации"""
    home_call = await home_call_service.transfer_to_organization(
        home_call_id=home_call_id,
        new_organization_id=new_organization_id,
        transfer_reason=transfer_reason,
        update_patient_attachment=update_patient_attachment,
    )
    return map_home_call_domain_to_full_response(home_call)


@home_calls_router.delete(
    "/home-calls/{home_call_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить вызов на дом",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "home_calls", "scopes": ["delete"]}]
    #         )
    #     )
    # ],
)
@inject
async def delete_home_call(
        home_call_id: UUID,
        home_call_service: HomeCallService = Depends(
            Provide[AssetsJournalContainer.home_call_service]
        ),
) -> None:
    """Удалить вызов на дом"""
    await home_call_service.delete_home_call(home_call_id)


@home_calls_router.get(
    "/home-calls/statistics",
    response_model=HomeCallStatisticsSchema,
    summary="Получить статистику вызовов на дом",
    # dependencies=[
    #     Depends(
    #         check_user_permissions(
    #             resources=[{"resource_name": "home_calls", "scopes": ["read"]}]
    #         )
    #     )
    # ],
)
@inject
async def get_home_calls_statistics(
        patient_search: str = Query(None, description="Поиск по ФИО или ИИН пациента"),
        patient_id: UUID = Query(None, description="ID пациента"),
        patient_iin: str = Query(None, description="ИИН пациента"),
        registration_date_from: datetime = Query(None, description="Дата регистрации от"),
        registration_date_to: datetime = Query(None, description="Дата регистрации до"),
        status: HomeCallStatusEnum = Query(None, description="Статус вызова"),
        category: HomeCallCategoryEnum = Query(None, description="Категория вызова"),
        source: HomeCallSourceEnum = Query(None, description="Источник вызова"),
        specialist: str = Query(None, description="Специалист"),
        organization_id: int = Query(None, description="ID организации"),
        home_call_service: HomeCallService = Depends(
            Provide[AssetsJournalContainer.home_call_service]
        ),
) -> HomeCallStatisticsSchema:
    """Получить статистику вызовов на дом"""

    filter_params = HomeCallFilterParams(
        patient_search=patient_search,
        patient_id=patient_id,
        patient_iin=patient_iin,
        registration_date_from=registration_date_from,
        registration_date_to=registration_date_to,
        status=status,
        category=category,
        source=source,
        specialist=specialist,
        organization_id=organization_id,
    )

    return await home_call_service.get_statistics(filter_params)