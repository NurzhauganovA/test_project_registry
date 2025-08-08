# src/apps/assets_journal/services/sick_leave_service.py

from datetime import date, datetime
from typing import List, Tuple, Optional
from uuid import UUID

from src.apps.assets_journal.domain.enums import SickLeaveStatusEnum
from src.apps.assets_journal.domain.models.sick_leave import SickLeaveDomain, SickLeaveListItemDomain
from src.apps.assets_journal.infrastructure.api.schemas.requests.sick_leave_schemas import (
    SickLeaveFilterParams,
    CreateSickLeaveSchema,
    UpdateSickLeaveSchema,
    CreateSickLeaveByPatientIdSchema,
    CloseSickLeaveSchema,
    ExtendSickLeaveSchema,
)
from src.apps.assets_journal.infrastructure.api.schemas.responses.sick_leave_schemas import (
    SickLeaveStatisticsSchema,
)
from src.apps.assets_journal.interfaces.sick_leave_repository_interfaces import (
    SickLeaveRepositoryInterface,
)
from src.apps.assets_journal.interfaces.uow_interface import (
    AssetsJournalUnitOfWorkInterface,
)
from src.apps.assets_journal.mappers.sick_leave_mappers import map_create_schema_to_domain
from src.apps.catalogs.services.medical_organizations_catalog_service import MedicalOrganizationsCatalogService
from src.apps.patients.services.patients_service import PatientService
from src.core.i18n import _
from src.core.logger import LoggerService
from src.shared.exceptions import NoInstanceFoundError
from src.shared.schemas.pagination_schemas import PaginationParams


class SickLeaveService:
    """Сервис для работы с больничными листами"""

    def __init__(
            self,
            uow: AssetsJournalUnitOfWorkInterface,
            sick_leave_repository: SickLeaveRepositoryInterface,
            patients_service: PatientService,
            medical_organizations_catalog_service: MedicalOrganizationsCatalogService,
            logger: LoggerService,
    ):
        self._uow = uow
        self._sick_leave_repository = sick_leave_repository
        self._patients_service = patients_service
        self._medical_organizations_catalog_service = medical_organizations_catalog_service
        self._logger = logger

    async def get_by_id(self, sick_leave_id: UUID) -> SickLeaveDomain:
        """
        Получить больничный лист по ID с загрузкой данных организации

        :param sick_leave_id: ID больничного листа
        :return: Доменная модель больничного листа
        :raises NoInstanceFoundError: Если больничный лист не найден
        """
        sick_leave = await self._sick_leave_repository.get_by_id(sick_leave_id)
        if not sick_leave:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Больничный лист с ID: %(ID)s не найден.") % {"ID": sick_leave_id}
            )

        # Загружаем данные организации если есть organization_id
        await self._load_organization_data(sick_leave)

        return sick_leave

    async def get_sick_leaves(
            self,
            pagination_params: PaginationParams,
            filter_params: SickLeaveFilterParams,
    ) -> Tuple[List[SickLeaveListItemDomain], int]:
        """
        Получить список больничных листов с фильтрацией и пагинацией

        :param pagination_params: Параметры пагинации
        :param filter_params: Параметры фильтрации
        :return: Кортеж из списка больничных листов и общего количества
        """
        filters = filter_params.to_dict(exclude_none=True)

        sick_leaves = await self._sick_leave_repository.get_sick_leaves(
            filters=filters,
            page=pagination_params.page,
            limit=pagination_params.limit,
        )

        # Загружаем данные организаций для каждого больничного листа
        await self._load_organization_data_for_sick_leaves(sick_leaves)

        total_count = await self._sick_leave_repository.get_total_count(filters)

        return sick_leaves, total_count

    async def get_sick_leaves_by_organization(
            self,
            organization_id: int,
            pagination_params: PaginationParams,
            filter_params: SickLeaveFilterParams,
    ) -> Tuple[List[SickLeaveListItemDomain], int]:
        """
        Получить список больничных листов по организации

        :param organization_id: ID организации
        :param pagination_params: Параметры пагинации
        :param filter_params: Параметры фильтрации по организации
        :return: Кортеж из списка больничных листов и общего количества
        """
        filters = filter_params.to_dict(exclude_none=True)
        filters['organization_id'] = organization_id  # Добавляем фильтр по организации

        sick_leaves = await self._sick_leave_repository.get_sick_leaves(
            filters=filters,
            page=pagination_params.page,
            limit=pagination_params.limit,
        )

        # Загружаем данные организаций для каждого больничного листа
        await self._load_organization_data_for_sick_leaves(sick_leaves)

        total_count = await self._sick_leave_repository.get_total_count(filters)

        return sick_leaves, total_count

    async def get_sick_leaves_by_patient(
            self,
            patient_id: UUID,
            pagination_params: PaginationParams,
    ) -> Tuple[List[SickLeaveDomain], int]:
        """
        Получить список больничных листов пациента

        :param patient_id: ID пациента
        :param pagination_params: Параметры пагинации
        :return: Кортеж из списка больничных листов и общего количества
        """
        sick_leaves = await self._sick_leave_repository.get_sick_leaves_by_patient(
            patient_id=patient_id,
            page=pagination_params.page,
            limit=pagination_params.limit,
        )

        # Загружаем данные организаций для каждого больничного листа
        await self._load_organization_data_for_sick_leaves(sick_leaves)

        # Для подсчета общего количества используем фильтр по пациенту
        filters = {'patient_id': patient_id}
        total_count = await self._sick_leave_repository.get_total_count(filters)

        return sick_leaves, total_count

    async def get_active_sick_leaves_by_patient(self, patient_id: UUID) -> List[SickLeaveDomain]:
        """
        Получить активные больничные листы пациента

        :param patient_id: ID пациента
        :return: Список активных больничных листов
        """
        return await self._sick_leave_repository.get_active_sick_leaves_by_patient(patient_id)

    async def create_sick_leave(self, create_schema: CreateSickLeaveSchema) -> SickLeaveDomain:
        """
        Создать новый больничный лист

        :param create_schema: Схема создания больничного листа
        :return: Созданная доменная модель больничного листа
        """
        # Находим пациента по ИИН
        patient = await self._patients_service.get_by_iin(create_schema.patient_iin)
        if not patient:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Пациент с ИИН %(IIN)s не найден.") % {"IIN": create_schema.patient_iin}
            )

        # Валидация дат
        if create_schema.disability_end_date and create_schema.disability_end_date < create_schema.disability_start_date:
            raise ValueError(_("Дата окончания нетрудоспособности не может быть раньше даты начала."))

        # Создаем доменную модель
        sick_leave_domain = map_create_schema_to_domain(create_schema, patient.id)

        async with self._uow:
            created_sick_leave = await self._uow.sick_leave_repository.create(sick_leave_domain)

        # Загружаем данные организации
        await self._load_organization_data(created_sick_leave)

        self._logger.info(f"Создан больничный лист {created_sick_leave.id} для пациента {patient.iin}")
        return created_sick_leave

    async def create_sick_leave_by_patient_id(
            self,
            create_schema: CreateSickLeaveByPatientIdSchema,
            patient_id: UUID
    ) -> SickLeaveDomain:
        """
        Создать новый больничный лист по ID пациента

        :param create_schema: Схема создания больничного листа с ID пациента
        :param patient_id: ID пациента
        :return: Созданная доменная модель больничного листа
        """
        # Валидация дат
        if create_schema.disability_end_date and create_schema.disability_end_date < create_schema.disability_start_date:
            raise ValueError(_("Дата окончания нетрудоспособности не может быть раньше даты начала."))

        # Создаем доменную модель
        sick_leave_domain = SickLeaveDomain(
            patient_id=patient_id,
            patient_location_address=create_schema.patient_location_address,
            receive_date=create_schema.receive_date,
            receive_time=create_schema.receive_time,
            actual_datetime=create_schema.actual_datetime or create_schema.receive_date,
            received_from=create_schema.received_from,
            is_repeat=create_schema.is_repeat,
            workplace_name=create_schema.workplace_name,
            disability_start_date=create_schema.disability_start_date,
            disability_end_date=create_schema.disability_end_date,
            sick_leave_reason=create_schema.sick_leave_reason,
            work_capacity=create_schema.work_capacity,
            area=create_schema.area,
            specialization=create_schema.specialization,
            specialist=create_schema.specialist,
            notes=create_schema.notes,
            is_primary=create_schema.is_primary,
            parent_sick_leave_id=create_schema.parent_sick_leave_id,
        )

        async with self._uow:
            created_sick_leave = await self._uow.sick_leave_repository.create(sick_leave_domain)

        # Загружаем данные организации
        await self._load_organization_data(created_sick_leave)

        self._logger.info(f"Создан больничный лист {created_sick_leave.id} для пациента {patient_id}")
        return created_sick_leave

    async def update_sick_leave(
            self,
            sick_leave_id: UUID,
            update_schema: UpdateSickLeaveSchema
    ) -> SickLeaveDomain:
        """
        Обновить больничный лист

        :param sick_leave_id: ID больничного листа
        :param update_schema: Схема обновления больничного листа
        :return: Обновленная доменная модель больничного листа
        """
        # Получаем существующий больничный лист
        sick_leave = await self.get_by_id(sick_leave_id)

        # Обновляем поля
        update_data = update_schema.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(sick_leave, field) and value is not None:
                setattr(sick_leave, field, value)

        # Валидация дат после обновления
        if sick_leave.disability_end_date and sick_leave.disability_end_date < sick_leave.disability_start_date:
            raise ValueError(_("Дата окончания нетрудоспособности не может быть раньше даты начала."))

        sick_leave.updated_at = datetime.utcnow()

        async with self._uow:
            updated_sick_leave = await self._uow.sick_leave_repository.update(sick_leave)

        # Загружаем данные организации
        await self._load_organization_data(updated_sick_leave)

        self._logger.info(f"Обновлен больничный лист {sick_leave_id}")
        return updated_sick_leave

    async def close_sick_leave(
            self,
            sick_leave_id: UUID,
            close_schema: CloseSickLeaveSchema
    ) -> SickLeaveDomain:
        """
        Закрыть больничный лист

        :param sick_leave_id: ID больничного листа
        :param close_schema: Схема закрытия больничного листа
        :return: Обновленная доменная модель больничного листа
        """
        sick_leave = await self.get_by_id(sick_leave_id)

        if sick_leave.status != SickLeaveStatusEnum.OPEN:
            raise ValueError(_("Можно закрывать только открытые больничные листы."))

        sick_leave.close_sick_leave(close_schema.disability_end_date)

        if close_schema.notes:
            sick_leave.add_note(close_schema.notes)

        async with self._uow:
            updated_sick_leave = await self._uow.sick_leave_repository.update(sick_leave)

        # Загружаем данные организации
        await self._load_organization_data(updated_sick_leave)

        self._logger.info(f"Закрыт больничный лист {sick_leave_id}")
        return updated_sick_leave

    async def extend_sick_leave(
            self,
            sick_leave_id: UUID,
            extend_schema: ExtendSickLeaveSchema
    ) -> SickLeaveDomain:
        """
        Продлить больничный лист

        :param sick_leave_id: ID больничного листа
        :param extend_schema: Схема продления больничного листа
        :return: Обновленная доменная модель больничного листа
        """
        sick_leave = await self.get_by_id(sick_leave_id)

        if sick_leave.status not in [SickLeaveStatusEnum.OPEN, SickLeaveStatusEnum.EXTENSION]:
            raise ValueError(_("Можно продлевать только открытые больничные листы или продления."))

        if extend_schema.new_end_date <= sick_leave.disability_start_date:
            raise ValueError(_("Новая дата окончания должна быть позже даты начала нетрудоспособности."))

        sick_leave.extend_sick_leave(extend_schema.new_end_date)

        if extend_schema.reason:
            sick_leave.add_note(f"Продление до {extend_schema.new_end_date}: {extend_schema.reason}")

        async with self._uow:
            updated_sick_leave = await self._uow.sick_leave_repository.update(sick_leave)

        # Загружаем данные организации
        await self._load_organization_data(updated_sick_leave)

        self._logger.info(f"Продлен больничный лист {sick_leave_id} до {extend_schema.new_end_date}")
        return updated_sick_leave

    async def cancel_sick_leave(
            self,
            sick_leave_id: UUID,
            reason: Optional[str] = None
    ) -> SickLeaveDomain:
        """
        Отменить больничный лист

        :param sick_leave_id: ID больничного листа
        :param reason: Причина отмены
        :return: Обновленная доменная модель больничного листа
        """
        sick_leave = await self.get_by_id(sick_leave_id)

        if sick_leave.status == SickLeaveStatusEnum.CANCELLED:
            raise ValueError(_("Больничный лист уже отменен."))

        sick_leave.cancel_sick_leave(reason)

        async with self._uow:
            updated_sick_leave = await self._uow.sick_leave_repository.update(sick_leave)

        # Загружаем данные организации
        await self._load_organization_data(updated_sick_leave)

        self._logger.info(f"Отменен больничный лист {sick_leave_id}. Причина: {reason or 'Не указана'}")
        return updated_sick_leave

    async def delete_sick_leave(self, sick_leave_id: UUID) -> None:
        """
        Удалить больничный лист

        :param sick_leave_id: ID больничного листа
        """
        # Проверяем существование больничного листа
        await self.get_by_id(sick_leave_id)

        async with self._uow:
            await self._uow.sick_leave_repository.delete(sick_leave_id)

        self._logger.info(f"Удален больничный лист {sick_leave_id}")

    async def get_extensions(self, parent_sick_leave_id: UUID) -> List[SickLeaveDomain]:
        """
        Получить продления больничного листа

        :param parent_sick_leave_id: ID родительского больничного листа
        :return: Список продлений
        """
        return await self._sick_leave_repository.get_extensions(parent_sick_leave_id)

    async def transfer_to_organization(
            self,
            sick_leave_id: UUID,
            new_organization_id: int,
            transfer_reason: Optional[str] = None,
            update_patient_attachment: bool = True
    ) -> SickLeaveDomain:
        """
        Передать больничный лист другой организации

        :param sick_leave_id: ID больничного листа
        :param new_organization_id: ID новой организации
        :param transfer_reason: Причина передачи
        :param update_patient_attachment: Обновить attachment_data пациента
        :return: Обновленная доменная модель больничного листа
        """
        # Получаем существующий больничный лист
        sick_leave = await self.get_by_id(sick_leave_id)

        # Проверяем, что это не та же организация
        if sick_leave.organization_id == new_organization_id:
            raise ValueError(_("Больничный лист уже принадлежит указанной организации."))

        # Проверяем существование новой организации
        try:
            new_organization = await self._medical_organizations_catalog_service.get_by_id(new_organization_id)
        except NoInstanceFoundError:
            raise ValueError(_("Организация с ID %(ID)s не найдена.") % {"ID": new_organization_id})

        # Логируем передачу
        old_org_name = sick_leave.organization_data.get('name', 'Неизвестно') if sick_leave.organization_data else 'Неизвестно'
        self._logger.info(
            f"Передача больничного листа {sick_leave_id} из организации '{old_org_name}' "
            f"в организацию '{new_organization.name}'. Причина: {transfer_reason or 'Не указана'}"
        )

        # Обновляем attachment_data пациента если требуется
        if update_patient_attachment:
            patient = await self._patients_service.get_by_id(sick_leave.patient_id)

            # Обновляем attachment_data пациента
            attachment_data = patient.attachment_data or {}
            attachment_data['attached_clinic_id'] = new_organization_id

            # Обновляем пациента
            await self._patients_service.update_patient_attachment_data(
                patient_id=patient.id,
                attachment_data=attachment_data
            )

        # Добавляем примечание о передаче
        transfer_note = f"Больничный лист передан организации '{new_organization.name}'"
        if transfer_reason:
            transfer_note += f". Причина: {transfer_reason}"

        sick_leave.add_note(transfer_note)
        sick_leave.updated_at = datetime.utcnow()

        async with self._uow:
            updated_sick_leave = await self._uow.sick_leave_repository.update(sick_leave)

        # Загружаем обновленные данные организации
        await self._load_organization_data(updated_sick_leave)

        return updated_sick_leave

    async def get_statistics(
            self,
            filter_params: SickLeaveFilterParams
    ) -> SickLeaveStatisticsSchema:
        """
        Получить статистику больничных листов

        :param filter_params: Параметры фильтрации
        :return: Статистика больничных листов
        """
        # Эта функция требует дополнительной реализации в репозитории
        # Пока возвращаем базовую статистику
        filters = filter_params.to_dict(exclude_none=True)
        total_count = await self._sick_leave_repository.get_total_count(filters)

        # Можно добавить более детальную статистику позже
        return SickLeaveStatisticsSchema(
            total_sick_leaves=total_count,
            open_sick_leaves=0,
            closed_sick_leaves=0,
            cancelled_sick_leaves=0,
            extended_sick_leaves=0,
            acute_illness_count=0,
            chronic_illness_count=0,
            work_injury_count=0,
            domestic_injury_count=0,
            pregnancy_complications_count=0,
            child_care_count=0,
            family_member_care_count=0,
        )

    async def _load_organization_data(self, sick_leave: SickLeaveDomain) -> None:
        """
        Загрузить данные организации для больничного листа

        :param sick_leave: Доменная модель больничного листа
        """
        if sick_leave.organization_id:
            try:
                organization = await self._medical_organizations_catalog_service.get_by_id(sick_leave.organization_id)
                sick_leave.organization_data = {
                    'id': organization.id,
                    'name': organization.name,
                    'code': organization.organization_code,
                    'address': organization.address,
                }
            except NoInstanceFoundError:
                self._logger.warning(f"Организация с ID {sick_leave.organization_id} не найдена")
                sick_leave.organization_data = None

    async def _load_organization_data_for_sick_leaves(self, sick_leaves: List[SickLeaveDomain]) -> None:
        """
        Загрузить данные организаций для списка больничных листов

        :param sick_leaves: Список доменных моделей больничных листов
        """
        # Собираем уникальные ID организаций
        organization_ids = set()
        for sick_leave in sick_leaves:
            if sick_leave.organization_id:
                organization_ids.add(sick_leave.organization_id)

        # Загружаем все организации одним запросом
        organizations_data = {}
        for org_id in organization_ids:
            try:
                organization = await self._medical_organizations_catalog_service.get_by_id(org_id)
                organizations_data[org_id] = {
                    'id': organization.id,
                    'name': organization.name,
                    'code': organization.organization_code,
                    'address': organization.address,
                }
            except NoInstanceFoundError:
                self._logger.warning(f"Организация с ID {org_id} не найдена")

        # Устанавливаем данные организаций для больничных листов
        for sick_leave in sick_leaves:
            if sick_leave.organization_id and sick_leave.organization_id in organizations_data:
                sick_leave.organization_data = organizations_data[sick_leave.organization_id]