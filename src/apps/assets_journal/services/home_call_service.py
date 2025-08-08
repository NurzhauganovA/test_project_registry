from datetime import datetime, time, date
from typing import List, Tuple, Optional
from uuid import UUID, uuid4

from src.apps.assets_journal.domain.enums import HomeCallStatusEnum, HomeCallCategoryEnum
from src.apps.assets_journal.domain.models.home_call import HomeCallDomain, HomeCallListItemDomain
from src.apps.assets_journal.infrastructure.api.schemas.requests.home_call_schemas import (
    HomeCallFilterParams,
    CreateHomeCallSchema,
    UpdateHomeCallSchema,
    CreateHomeCallByPatientIdSchema,
    CompleteHomeCallSchema,
)
from src.apps.assets_journal.infrastructure.api.schemas.responses.home_call_schemas import (
    HomeCallStatisticsSchema,
)
from src.apps.assets_journal.interfaces.home_call_repository_interfaces import (
    HomeCallRepositoryInterface,
)
from src.apps.assets_journal.interfaces.uow_interface import (
    AssetsJournalUnitOfWorkInterface,
)
from src.apps.assets_journal.mappers.home_call_mappers import map_create_schema_to_domain
from src.apps.catalogs.services.medical_organizations_catalog_service import MedicalOrganizationsCatalogService
from src.apps.patients.services.patients_service import PatientService
from src.core.i18n import _
from src.core.logger import LoggerService
from src.shared.exceptions import NoInstanceFoundError, ValidationError
from src.shared.schemas.pagination_schemas import PaginationParams


class HomeCallService:
    """Сервис для работы с вызовами на дом"""

    def __init__(
            self,
            uow: AssetsJournalUnitOfWorkInterface,
            home_call_repository: HomeCallRepositoryInterface,
            patients_service: PatientService,
            medical_organizations_catalog_service: MedicalOrganizationsCatalogService,
            logger: LoggerService,
    ):
        self._uow = uow
        self._home_call_repository = home_call_repository
        self._patients_service = patients_service
        self._medical_organizations_catalog_service = medical_organizations_catalog_service
        self._logger = logger

    async def get_by_id(self, home_call_id: UUID) -> HomeCallDomain:
        """
        Получить вызов на дом по ID с загрузкой данных организации

        :param home_call_id: ID вызова на дом
        :return: Доменная модель вызова на дом
        :raises NoInstanceFoundError: Если вызов на дом не найден
        """
        home_call = await self._home_call_repository.get_by_id(home_call_id)
        if not home_call:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Вызов на дом с ID: %(ID)s не найден.") % {"ID": home_call_id}
            )

        # Загружаем данные организации если есть organization_id
        await self._load_organization_data(home_call)

        return home_call

    async def get_by_call_number(self, call_number: str) -> HomeCallDomain:
        """
        Получить вызов на дом по номеру

        :param call_number: Номер вызова
        :return: Доменная модель вызова на дом
        :raises NoInstanceFoundError: Если вызов на дом не найден
        """
        home_call = await self._home_call_repository.get_by_call_number(call_number)
        if not home_call:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Вызов на дом с номером: %(NUMBER)s не найден.") % {"NUMBER": call_number}
            )

        # Загружаем данные организации если есть organization_id
        await self._load_organization_data(home_call)

        return home_call

    async def get_home_calls(
            self,
            pagination_params: PaginationParams,
            filter_params: HomeCallFilterParams,
    ) -> Tuple[List[HomeCallListItemDomain], int]:
        """
        Получить список вызовов на дом с фильтрацией и пагинацией

        :param pagination_params: Параметры пагинации
        :param filter_params: Параметры фильтрации
        :return: Кортеж из списка вызовов на дом и общего количества
        """
        filters = filter_params.to_dict(exclude_none=True)

        home_calls = await self._home_call_repository.get_home_calls(
            filters=filters,
            page=pagination_params.page or 1,
            limit=pagination_params.limit or 30,
        )

        # Загружаем данные организаций для каждого вызова на дом
        await self._load_organization_data_for_home_calls(home_calls)

        total_count = await self._home_call_repository.get_total_count(filters)

        return home_calls, total_count

    async def get_home_calls_by_organization(
            self,
            organization_id: int,
            pagination_params: PaginationParams,
            filter_params: Optional[HomeCallFilterParams] = None,
    ) -> Tuple[List[HomeCallListItemDomain], int]:
        """
        Получить список вызовов на дом по организации

        :param organization_id: ID организации
        :param pagination_params: Параметры пагинации
        :param filter_params: Параметры фильтрации по организации
        :return: Кортеж из списка вызовов на дом и общего количества
        """
        if filter_params is None:
            filter_params = HomeCallFilterParams()

        filters = filter_params.to_dict(exclude_none=True)
        filters['organization_id'] = organization_id  # Добавляем фильтр по организации

        home_calls = await self._home_call_repository.get_home_calls(
            filters=filters,
            page=pagination_params.page or 1,
            limit=pagination_params.limit or 30,
        )

        # Загружаем данные организаций для каждого вызова на дом
        await self._load_organization_data_for_home_calls(home_calls)

        total_count = await self._home_call_repository.get_total_count(filters)

        return home_calls, total_count

    async def get_home_calls_by_patient(
            self,
            patient_id: UUID,
            pagination_params: PaginationParams,
    ) -> Tuple[List[HomeCallDomain], int]:
        """
        Получить список вызовов на дом пациента

        :param patient_id: ID пациента
        :param pagination_params: Параметры пагинации
        :return: Кортеж из списка вызовов на дом и общего количества
        """
        home_calls = await self._home_call_repository.get_home_calls_by_patient(
            patient_id=patient_id,
            page=pagination_params.page or 1,
            limit=pagination_params.limit or 30,
        )

        # Загружаем данные организаций для каждого вызова на дом
        await self._load_organization_data_for_home_calls(home_calls)

        # Для подсчета общего количества используем фильтр по пациенту
        filters = {'patient_id': patient_id}
        total_count = await self._home_call_repository.get_total_count(filters)

        return home_calls, total_count

    async def get_home_calls_by_specialist(
            self,
            specialist: str,
            pagination_params: PaginationParams,
    ) -> Tuple[List[HomeCallDomain], int]:
        """
        Получить список вызовов на дом по специалисту

        :param specialist: Имя специалиста
        :param pagination_params: Параметры пагинации
        :return: Кортеж из списка вызовов на дом и общего количества
        """
        home_calls = await self._home_call_repository.get_home_calls_by_specialist(
            specialist=specialist,
            page=pagination_params.page or 1,
            limit=pagination_params.limit or 30,
        )

        # Загружаем данные организаций для каждого вызова на дом
        await self._load_organization_data_for_home_calls(home_calls)

        # Для подсчета общего количества используем фильтр по специалисту
        filters = {'specialist': specialist}
        total_count = await self._home_call_repository.get_total_count(filters)

        return home_calls, total_count

    async def get_active_home_calls_by_patient(self, patient_id: UUID) -> List[HomeCallDomain]:
        """
        Получить активные вызовы на дом пациента

        :param patient_id: ID пациента
        :return: Список активных вызовов на дом
        """
        return await self._home_call_repository.get_active_home_calls_by_patient(patient_id)

    async def create_home_call(self, create_schema: CreateHomeCallSchema) -> HomeCallDomain:
        """
        Создать новый вызов на дом

        :param create_schema: Схема создания вызова на дом
        :return: Созданная доменная модель вызова на дом
        """
        # Находим пациента по ИИН
        patient = await self._patients_service.get_by_iin(create_schema.patient_iin)
        if not patient:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Пациент с ИИН %(IIN)s не найден.") % {"IIN": create_schema.patient_iin}
            )

        # Валидация данных
        await self._validate_home_call_data(create_schema)

        # Создаем доменную модель
        home_call_domain = HomeCallDomain(
            id=uuid4(),
            patient_id=patient.id,
            patient_address=create_schema.patient_address,
            patient_phone=create_schema.patient_phone,
            registration_date=create_schema.registration_date,
            registration_time=create_schema.registration_time,
            registration_datetime=create_schema.registration_datetime or create_schema.registration_date,
            execution_date=create_schema.execution_date,
            execution_time=create_schema.execution_time,
            area=create_schema.area,
            specialization=create_schema.specialization,
            specialist=create_schema.specialist,
            is_insured=create_schema.is_insured,
            has_oms=create_schema.has_oms,
            source=create_schema.source,
            category=create_schema.category,
            reason=create_schema.reason,
            call_type=create_schema.call_type,
            reason_patient_words=create_schema.reason_patient_words,
            visit_type=create_schema.visit_type,
            notes=create_schema.notes,
        )

        async with self._uow:
            created_home_call = await self._uow.home_call_repository.create(home_call_domain)
            await self._uow.commit()

        # Загружаем данные организации
        await self._load_organization_data(created_home_call)

        self._logger.info(f"Создан вызов на дом {created_home_call.call_number} для пациента {patient.iin}")
        return created_home_call

    async def create_home_call_by_patient_id(
            self,
            create_schema: CreateHomeCallByPatientIdSchema,
            patient_id: UUID
    ) -> HomeCallDomain:
        """
        Создать новый вызов на дом по ID пациента

        :param create_schema: Схема создания вызова на дом с ID пациента
        :param patient_id: ID пациента
        :return: Созданная доменная модель вызова на дом
        """
        # Проверяем существование пациента
        patient = await self._patients_service.get_by_id(patient_id)

        # Валидация данных
        await self._validate_home_call_data(create_schema)

        # Создаем доменную модель
        home_call_domain = HomeCallDomain(
            id=uuid4(),
            patient_id=patient_id,
            patient_address=create_schema.patient_address,
            patient_phone=create_schema.patient_phone,
            registration_date=create_schema.registration_date,
            registration_time=create_schema.registration_time,
            registration_datetime=create_schema.registration_datetime or create_schema.registration_date,
            execution_date=create_schema.execution_date,
            execution_time=create_schema.execution_time,
            area=create_schema.area,
            specialization=create_schema.specialization,
            specialist=create_schema.specialist,
            is_insured=create_schema.is_insured,
            has_oms=create_schema.has_oms,
            source=create_schema.source,
            category=create_schema.category,
            reason=create_schema.reason,
            call_type=create_schema.call_type,
            reason_patient_words=create_schema.reason_patient_words,
            visit_type=create_schema.visit_type,
            notes=create_schema.notes,
        )

        async with self._uow:
            created_home_call = await self._uow.home_call_repository.create(home_call_domain)
            await self._uow.commit()

        # Загружаем данные организации
        await self._load_organization_data(created_home_call)

        self._logger.info(f"Создан вызов на дом {created_home_call.call_number} для пациента {patient_id}")
        return created_home_call

    async def update_home_call(
            self,
            home_call_id: UUID,
            update_schema: UpdateHomeCallSchema
    ) -> HomeCallDomain:
        """
        Обновить вызов на дом

        :param home_call_id: ID вызова на дом
        :param update_schema: Схема обновления вызова на дом
        :return: Обновленная доменная модель вызова на дом
        """
        # Получаем существующий вызов на дом
        home_call = await self.get_by_id(home_call_id)

        # Проверяем возможность обновления
        if home_call.status == HomeCallStatusEnum.COMPLETED:
            raise ValidationError("Нельзя изменять завершенный вызов на дом.")

        # Обновляем поля
        update_data = update_schema.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(home_call, field) and value is not None:
                setattr(home_call, field, value)

        # Валидация дат после обновления
        if home_call.execution_date and home_call.registration_date:
            if home_call.execution_date.date() < home_call.registration_date.date():
                raise ValidationError(_("Дата выполнения не может быть раньше даты регистрации."))

        home_call.updated_at = datetime.utcnow()

        async with self._uow:
            updated_home_call = await self._uow.home_call_repository.update(home_call)
            await self._uow.commit()

        # Загружаем данные организации
        await self._load_organization_data(updated_home_call)

        self._logger.info(f"Обновлен вызов на дом {home_call.call_number}")
        return updated_home_call

    async def complete_home_call(
            self,
            home_call_id: UUID,
            complete_schema: CompleteHomeCallSchema
    ) -> HomeCallDomain:
        """
        Завершить вызов на дом

        :param home_call_id: ID вызова на дом
        :param complete_schema: Схема завершения вызова на дом
        :return: Обновленная доменная модель вызова на дом
        """
        home_call = await self.get_by_id(home_call_id)

        if home_call.status == HomeCallStatusEnum.COMPLETED:
            raise ValidationError(_("Вызов на дом уже завершен."))

        if home_call.status == HomeCallStatusEnum.CANCELLED:
            raise ValidationError(_("Нельзя завершить отмененный вызов на дом."))

        # Валидация даты выполнения
        if complete_schema.execution_date.date() < home_call.registration_date.date():
            raise ValidationError(_("Дата выполнения не может быть раньше даты регистрации."))

        home_call.complete_call(
            complete_schema.execution_date,
            complete_schema.execution_time,
            complete_schema.notes
        )

        async with self._uow:
            updated_home_call = await self._uow.home_call_repository.update(home_call)
            await self._uow.commit()

        # Загружаем данные организации
        await self._load_organization_data(updated_home_call)

        self._logger.info(f"Завершен вызов на дом {home_call.call_number}")
        return updated_home_call

    async def start_processing_home_call(self, home_call_id: UUID) -> HomeCallDomain:
        """
        Взять вызов на дом в работу

        :param home_call_id: ID вызова на дом
        :return: Обновленная доменная модель вызова на дом
        """
        home_call = await self.get_by_id(home_call_id)

        if home_call.status != HomeCallStatusEnum.REGISTERED:
            raise ValidationError(_("Можно взять в работу только зарегистрированные вызовы."))

        home_call.start_processing()

        async with self._uow:
            updated_home_call = await self._uow.home_call_repository.update(home_call)
            await self._uow.commit()

        # Загружаем данные организации
        await self._load_organization_data(updated_home_call)

        self._logger.info(f"Вызов на дом {home_call.call_number} взят в работу")
        return updated_home_call

    async def cancel_home_call(
            self,
            home_call_id: UUID,
            reason: Optional[str] = None
    ) -> HomeCallDomain:
        """
        Отменить вызов на дом

        :param home_call_id: ID вызова на дом
        :param reason: Причина отмены
        :return: Обновленная доменная модель вызова на дом
        """
        home_call = await self.get_by_id(home_call_id)

        if home_call.status == HomeCallStatusEnum.CANCELLED:
            raise ValidationError(_("Вызов на дом уже отменен."))

        if home_call.status == HomeCallStatusEnum.COMPLETED:
            raise ValidationError(_("Нельзя отменить завершенный вызов на дом."))

        home_call.cancel_call(reason)

        async with self._uow:
            updated_home_call = await self._uow.home_call_repository.update(home_call)
            await self._uow.commit()

        # Загружаем данные организации
        await self._load_organization_data(updated_home_call)

        self._logger.info(f"Отменен вызов на дом {home_call.call_number}. Причина: {reason or 'Не указана'}")
        return updated_home_call

    async def delete_home_call(self, home_call_id: UUID) -> None:
        """
        Удалить вызов на дом

        :param home_call_id: ID вызова на дом
        """
        # Проверяем существование вызова на дом
        home_call = await self.get_by_id(home_call_id)

        # Проверяем возможность удаления
        if home_call.status == HomeCallStatusEnum.COMPLETED:
            raise ValidationError(_("Нельзя удалить завершенный вызов на дом."))

        async with self._uow:
            await self._uow.home_call_repository.delete(home_call_id)
            await self._uow.commit()

        self._logger.info(f"Удален вызов на дом {home_call.call_number}")

    async def get_statistics(
            self,
            filter_params: HomeCallFilterParams
    ) -> HomeCallStatisticsSchema:
        """
        Получить статистику вызовов на дом

        :param filter_params: Параметры фильтрации
        :return: Статистика вызовов на дом
        """
        filters = filter_params.to_dict(exclude_none=True)
        total_count = await self._home_call_repository.get_total_count(filters)

        # Получаем статистику по статусам
        status_stats = {}
        for status in HomeCallStatusEnum:
            status_filters = filters.copy()
            status_filters['status'] = status
            count = await self._home_call_repository.get_total_count(status_filters)
            status_stats[status.value] = count

        # Получаем статистику по категориям
        category_stats = {}
        for category in HomeCallCategoryEnum:
            category_filters = filters.copy()
            category_filters['category'] = category
            count = await self._home_call_repository.get_total_count(category_filters)
            category_stats[category.value] = count

        return HomeCallStatisticsSchema(
            total_calls=total_count,
            registered_calls=status_stats.get('registered', 0),
            in_progress_calls=status_stats.get('in_progress', 0),
            completed_calls=status_stats.get('completed', 0),
            cancelled_calls=status_stats.get('cancelled', 0),
            emergency_calls=category_stats.get('emergency', 0),
            urgent_calls=category_stats.get('urgent', 0),
            planned_calls=category_stats.get('planned', 0),
            patient_calls=0,
            relatives_calls=0,
            egov_calls=0,
            call_center_calls=0,
            other_source_calls=0,
            therapeutic_calls=0,
            pediatric_calls=0,
            specialist_calls=0,
        )

    async def _validate_home_call_data(self, schema) -> None:
        """
        Валидация данных вызова на дом

        :param schema: Схема с данными для валидации
        """
        # Проверка дат
        if hasattr(schema, 'execution_date') and schema.execution_date and schema.registration_date:
            if schema.execution_date.date() < schema.registration_date.date():
                raise ValidationError(_("Дата выполнения не может быть раньше даты регистрации."))

        # Проверка обязательных полей
        if not schema.area or not schema.area.strip():
            raise ValidationError(_("Поле 'Участок' обязательно для заполнения."))

        if not schema.specialization or not schema.specialization.strip():
            raise ValidationError(_("Поле 'Специализация' обязательно для заполнения."))

        if not schema.specialist or not schema.specialist.strip():
            raise ValidationError(_("Поле 'Специалист' обязательно для заполнения."))

        # Валидация телефона если указан
        if hasattr(schema, 'patient_phone') and schema.patient_phone:
            if not self._is_valid_phone(schema.patient_phone):
                raise ValidationError(_("Некорректный формат номера телефона."))

    def _is_valid_phone(self, phone: str) -> bool:
        """
        Проверка корректности номера телефона

        :param phone: Номер телефона
        :return: True если номер корректен
        """
        import re
        # Простая проверка формата телефона
        phone_pattern = r'^[\+]?[1-9][\d]{0,15}$'
        return bool(re.match(phone_pattern, phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')))

    async def _load_organization_data(self, home_call: HomeCallDomain) -> None:
        """
        Загрузить данные организации для вызова на дом

        :param home_call: Доменная модель вызова на дом
        """
        if home_call.organization_id:
            try:
                organization = await self._medical_organizations_catalog_service.get_by_id(home_call.organization_id)
                home_call.organization_data = {
                    'id': organization.id,
                    'name': organization.name,
                    'code': organization.organization_code,
                    'address': organization.address,
                }
            except NoInstanceFoundError:
                self._logger.warning(f"Организация с ID {home_call.organization_id} не найдена")
                home_call.organization_data = None

    async def _load_organization_data_for_home_calls(self, home_calls: List[HomeCallDomain]) -> None:
        """
        Загрузить данные организаций для списка вызовов на дом

        :param home_calls: Список доменных моделей вызовов на дом
        """
        # Собираем уникальные ID организаций
        organization_ids = set()
        for home_call in home_calls:
            if home_call.organization_id:
                organization_ids.add(home_call.organization_id)

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

        # Устанавливаем данные организаций для вызовов на дом
        for home_call in home_calls:
            if home_call.organization_id and home_call.organization_id in organizations_data:
                home_call.organization_data = organizations_data[home_call.organization_id]