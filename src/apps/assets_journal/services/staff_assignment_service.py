from datetime import datetime, date
from typing import List, Tuple, Optional
from uuid import UUID, uuid4

from src.apps.assets_journal.domain.enums import StaffAssignmentStatusEnum
from src.apps.assets_journal.domain.models.staff_assignment import StaffAssignmentDomain, StaffAssignmentListItemDomain
from src.apps.assets_journal.infrastructure.api.schemas.requests.staff_assignment_schemas import (
    StaffAssignmentFilterParams,
    CreateStaffAssignmentSchema,
    UpdateStaffAssignmentSchema,
    CompleteStaffAssignmentSchema,
    ExtendStaffAssignmentSchema,
)
from src.apps.assets_journal.infrastructure.api.schemas.responses.staff_assignment_schemas import (
    StaffAssignmentStatisticsSchema,
)
from src.apps.assets_journal.interfaces.staff_assignment_repository_interface import (
    StaffAssignmentRepositoryInterface,
)
from src.apps.assets_journal.interfaces.uow_interface import (
    AssetsJournalUnitOfWorkInterface,
)
from src.apps.assets_journal.mappers.staff_assignment_mappers import map_create_schema_to_domain
from src.core.i18n import _
from src.core.logger import LoggerService
from src.shared.exceptions import NoInstanceFoundError, ValidationError
from src.shared.schemas.pagination_schemas import PaginationParams


class StaffAssignmentService:
    """Сервис для работы с назначениями медперсонала"""

    def __init__(
            self,
            uow: AssetsJournalUnitOfWorkInterface,
            staff_assignment_repository: StaffAssignmentRepositoryInterface,
            logger: LoggerService,
    ):
        self._uow = uow
        self._staff_assignment_repository = staff_assignment_repository
        self._logger = logger

    async def get_by_id(self, assignment_id: UUID) -> StaffAssignmentDomain:
        """
        Получить назначение медперсонала по ID

        :param assignment_id: ID назначения
        :return: Доменная модель назначения медперсонала
        :raises NoInstanceFoundError: Если назначение не найдено
        """
        assignment = await self._staff_assignment_repository.get_by_id(assignment_id)
        if not assignment:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Назначение медперсонала с ID: %(ID)s не найдено.") % {"ID": assignment_id}
            )

        return assignment

    async def get_staff_assignments(
            self,
            pagination_params: PaginationParams,
            filter_params: StaffAssignmentFilterParams,
    ) -> Tuple[List[StaffAssignmentListItemDomain], int]:
        """
        Получить список назначений медперсонала с фильтрацией и пагинацией

        :param pagination_params: Параметры пагинации
        :param filter_params: Параметры фильтрации
        :return: Кортеж из списка назначений медперсонала и общего количества
        """
        filters = filter_params.to_dict(exclude_none=True)

        assignments = await self._staff_assignment_repository.get_staff_assignments(
            filters=filters,
            page=pagination_params.page or 1,
            limit=pagination_params.limit or 30,
        )

        total_count = await self._staff_assignment_repository.get_total_count(filters)

        return assignments, total_count

    async def get_assignments_by_specialist(
            self,
            specialist_name: str,
            pagination_params: PaginationParams,
    ) -> Tuple[List[StaffAssignmentDomain], int]:
        """
        Получить список назначений конкретного специалиста

        :param specialist_name: Имя специалиста
        :param pagination_params: Параметры пагинации
        :return: Кортеж из списка назначений и общего количества
        """
        assignments = await self._staff_assignment_repository.get_assignments_by_specialist(
            specialist_name=specialist_name,
            page=pagination_params.page or 1,
            limit=pagination_params.limit or 30,
        )

        # Для подсчета общего количества используем фильтр по специалисту
        filters = {'specialist_search': specialist_name}
        total_count = await self._staff_assignment_repository.get_total_count(filters)

        return assignments, total_count

    async def get_assignments_by_area(
            self,
            area_number: str,
            pagination_params: PaginationParams,
    ) -> Tuple[List[StaffAssignmentDomain], int]:
        """
        Получить список назначений на конкретный участок

        :param area_number: Номер участка
        :param pagination_params: Параметры пагинации
        :return: Кортеж из списка назначений и общего количества
        """
        assignments = await self._staff_assignment_repository.get_assignments_by_area(
            area_number=area_number,
            page=pagination_params.page or 1,
            limit=pagination_params.limit or 30,
        )

        # Для подсчета общего количества используем фильтр по участку
        filters = {'area_number': area_number}
        total_count = await self._staff_assignment_repository.get_total_count(filters)

        return assignments, total_count

    async def get_assignments_by_department(
            self,
            department: str,
            pagination_params: PaginationParams,
    ) -> Tuple[List[StaffAssignmentDomain], int]:
        """
        Получить список назначений по отделению

        :param department: Отделение
        :param pagination_params: Параметры пагинации
        :return: Кортеж из списка назначений и общего количества
        """
        assignments = await self._staff_assignment_repository.get_assignments_by_department(
            department=department,
            page=pagination_params.page or 1,
            limit=pagination_params.limit or 30,
        )

        # Для подсчета общего количества используем фильтр по отделению
        filters = {'department': department}
        total_count = await self._staff_assignment_repository.get_total_count(filters)

        return assignments, total_count

    async def get_current_assignments(
            self,
            pagination_params: PaginationParams,
    ) -> Tuple[List[StaffAssignmentDomain], int]:
        """
        Получить список текущих активных назначений

        :param pagination_params: Параметры пагинации
        :return: Кортеж из списка назначений и общего количества
        """
        assignments = await self._staff_assignment_repository.get_current_assignments(
            page=pagination_params.page or 1,
            limit=pagination_params.limit or 30,
        )

        # Для подсчета общего количества используем фильтр текущих назначений
        filters = {'only_current': True}
        total_count = await self._staff_assignment_repository.get_total_count(filters)

        return assignments, total_count

    async def create_staff_assignment(self, create_schema: CreateStaffAssignmentSchema) -> StaffAssignmentDomain:
        """
        Создать новое назначение медперсонала

        :param create_schema: Схема создания назначения медперсонала
        :return: Созданная доменная модель назначения медперсонала
        """
        # Валидация данных
        await self._validate_assignment_data(create_schema)

        # Проверяем конфликты назначений
        has_conflict = await self._staff_assignment_repository.check_assignment_conflict(
            specialist_name=create_schema.specialist_name,
            area_number=create_schema.area_number,
            start_date=create_schema.start_date,
            end_date=create_schema.end_date,
        )

        if has_conflict:
            raise ValidationError(
                _("Специалист %(specialist)s уже назначен на участок %(area)s в указанный период.") %
                {"specialist": create_schema.specialist_name, "area": create_schema.area_number}
            )

        # Создаем доменную модель
        assignment_domain = StaffAssignmentDomain(
            id=uuid4(),
            specialist_name=create_schema.specialist_name,
            specialization=create_schema.specialization,
            area_number=create_schema.area_number,
            area_type=create_schema.area_type,
            department=create_schema.department,
            start_date=create_schema.start_date,
            end_date=create_schema.end_date,
            reception_hours_per_day=create_schema.reception_hours_per_day,
            reception_minutes_per_day=create_schema.reception_minutes_per_day,
            area_hours_per_day=create_schema.area_hours_per_day,
            area_minutes_per_day=create_schema.area_minutes_per_day,
            notes=create_schema.notes,
        )

        async with self._uow:
            created_assignment = await self._uow.staff_assignment_repository.create(assignment_domain)
            await self._uow.commit()

        self._logger.info(
            f"Создано назначение медперсонала: {create_schema.specialist_name} "
            f"на участок {create_schema.area_number} с {create_schema.start_date}"
        )
        return created_assignment

    async def update_staff_assignment(
            self,
            assignment_id: UUID,
            update_schema: UpdateStaffAssignmentSchema
    ) -> StaffAssignmentDomain:
        """
        Обновить назначение медперсонала

        :param assignment_id: ID назначения медперсонала
        :param update_schema: Схема обновления назначения медперсонала
        :return: Обновленная доменная модель назначения медперсонала
        """
        # Получаем существующее назначение
        assignment = await self.get_by_id(assignment_id)

        # Проверяем возможность обновления
        if assignment.status == StaffAssignmentStatusEnum.COMPLETED:
            raise ValidationError("Нельзя изменять завершенное назначение.")

        # Обновляем поля
        update_data = update_schema.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(assignment, field) and value is not None:
                setattr(assignment, field, value)

        # Валидация данных после обновления
        await self._validate_assignment_data(assignment, is_update=True)

        # Проверяем конфликты при изменении ключевых полей
        if any(field in update_data for field in ['specialist_name', 'area_number', 'start_date', 'end_date']):
            has_conflict = await self._staff_assignment_repository.check_assignment_conflict(
                specialist_name=assignment.specialist_name,
                area_number=assignment.area_number,
                start_date=assignment.start_date,
                end_date=assignment.end_date,
                exclude_id=assignment_id,
            )

            if has_conflict:
                raise ValidationError(
                    _("Специалист %(specialist)s уже назначен на участок %(area)s в указанный период.") %
                    {"specialist": assignment.specialist_name, "area": assignment.area_number}
                )

        assignment.updated_at = datetime.utcnow()

        async with self._uow:
            updated_assignment = await self._uow.staff_assignment_repository.update(assignment)
            await self._uow.commit()

        self._logger.info(f"Обновлено назначение медперсонала {assignment_id}")
        return updated_assignment

    async def complete_staff_assignment(
            self,
            assignment_id: UUID,
            complete_schema: CompleteStaffAssignmentSchema
    ) -> StaffAssignmentDomain:
        """
        Завершить назначение медперсонала

        :param assignment_id: ID назначения медперсонала
        :param complete_schema: Схема завершения назначения медперсонала
        :return: Обновленная доменная модель назначения медперсонала
        """
        assignment = await self.get_by_id(assignment_id)

        if assignment.status == StaffAssignmentStatusEnum.COMPLETED:
            raise ValidationError(_("Назначение медперсонала уже завершено."))

        # Валидация даты завершения
        if complete_schema.end_date < assignment.start_date:
            raise ValidationError(_("Дата завершения не может быть раньше даты начала назначения."))

        assignment.complete_assignment(complete_schema.end_date, complete_schema.notes)

        async with self._uow:
            updated_assignment = await self._uow.staff_assignment_repository.update(assignment)
            await self._uow.commit()

        self._logger.info(f"Завершено назначение медперсонала {assignment_id}")
        return updated_assignment

    async def extend_staff_assignment(
            self,
            assignment_id: UUID,
            extend_schema: ExtendStaffAssignmentSchema
    ) -> StaffAssignmentDomain:
        """
        Продлить назначение медперсонала

        :param assignment_id: ID назначения медперсонала
        :param extend_schema: Схема продления назначения медперсонала
        :return: Обновленная доменная модель назначения медперсонала
        """
        assignment = await self.get_by_id(assignment_id)

        if assignment.status not in [StaffAssignmentStatusEnum.ACTIVE, StaffAssignmentStatusEnum.SUSPENDED]:
            raise ValidationError(_("Можно продлевать только активные или приостановленные назначения."))

        if extend_schema.new_end_date <= assignment.start_date:
            raise ValidationError(_("Новая дата окончания должна быть позже даты начала назначения."))

        # Проверяем конфликты при продлении
        has_conflict = await self._staff_assignment_repository.check_assignment_conflict(
            specialist_name=assignment.specialist_name,
            area_number=assignment.area_number,
            start_date=assignment.start_date,
            end_date=extend_schema.new_end_date,
            exclude_id=assignment_id,
        )

        if has_conflict:
            raise ValidationError(
                _("Нельзя продлить назначение до %(date)s из-за конфликта с другими назначениями.") %
                {"date": extend_schema.new_end_date}
            )

        assignment.extend_assignment(extend_schema.new_end_date, extend_schema.reason)

        async with self._uow:
            updated_assignment = await self._uow.staff_assignment_repository.update(assignment)
            await self._uow.commit()

        self._logger.info(f"Продлено назначение медперсонала {assignment_id} до {extend_schema.new_end_date}")
        return updated_assignment

    async def suspend_staff_assignment(
            self,
            assignment_id: UUID,
            reason: Optional[str] = None
    ) -> StaffAssignmentDomain:
        """
        Приостановить назначение медперсонала

        :param assignment_id: ID назначения медперсонала
        :param reason: Причина приостановки
        :return: Обновленная доменная модель назначения медперсонала
        """
        assignment = await self.get_by_id(assignment_id)

        if assignment.status != StaffAssignmentStatusEnum.ACTIVE:
            raise ValidationError(_("Можно приостанавливать только активные назначения."))

        assignment.suspend_assignment(reason)

        async with self._uow:
            updated_assignment = await self._uow.staff_assignment_repository.update(assignment)
            await self._uow.commit()

        self._logger.info(f"Приостановлено назначение медперсонала {assignment_id}. Причина: {reason or 'Не указана'}")
        return updated_assignment

    async def activate_staff_assignment(self, assignment_id: UUID) -> StaffAssignmentDomain:
        """
        Активировать назначение медперсонала

        :param assignment_id: ID назначения медперсонала
        :return: Обновленная доменная модель назначения медперсонала
        """
        assignment = await self.get_by_id(assignment_id)

        if assignment.status not in [StaffAssignmentStatusEnum.INACTIVE, StaffAssignmentStatusEnum.SUSPENDED]:
            raise ValidationError(_("Можно активировать только неактивные или приостановленные назначения."))

        assignment.activate_assignment()

        async with self._uow:
            updated_assignment = await self._uow.staff_assignment_repository.update(assignment)
            await self._uow.commit()

        self._logger.info(f"Активировано назначение медперсонала {assignment_id}")
        return updated_assignment

    async def delete_staff_assignment(self, assignment_id: UUID) -> None:
        """
        Удалить назначение медперсонала

        :param assignment_id: ID назначения медперсонала
        """
        # Проверяем существование назначения
        assignment = await self.get_by_id(assignment_id)

        # Проверяем возможность удаления
        if assignment.status == StaffAssignmentStatusEnum.ACTIVE and assignment.is_current:
            raise ValidationError(_("Нельзя удалить текущее активное назначение."))

        async with self._uow:
            await self._uow.staff_assignment_repository.delete(assignment_id)
            await self._uow.commit()

        self._logger.info(f"Удалено назначение медперсонала {assignment_id}")

    async def get_statistics(
            self,
            filter_params: StaffAssignmentFilterParams
    ) -> StaffAssignmentStatisticsSchema:
        """
        Получить статистику назначений медперсонала

        :param filter_params: Параметры фильтрации
        :return: Статистика назначений медперсонала
        """
        filters = filter_params.to_dict(exclude_none=True)
        total_count = await self._staff_assignment_repository.get_total_count(filters)

        # Получаем статистику по статусам
        status_stats = {}
        for status in StaffAssignmentStatusEnum:
            status_filters = filters.copy()
            status_filters['status'] = status
            count = await self._staff_assignment_repository.get_total_count(status_filters)
            status_stats[status.value] = count

        return StaffAssignmentStatisticsSchema(
            total_assignments=total_count,
            active_assignments=status_stats.get('active', 0),
            inactive_assignments=status_stats.get('inactive', 0),
            suspended_assignments=status_stats.get('suspended', 0),
            completed_assignments=status_stats.get('completed', 0),
            therapists_count=0,
            pediatricians_count=0,
            surgeons_count=0,
            cardiologists_count=0,
            neurologists_count=0,
            other_specialists_count=0,
            therapeutic_department_count=0,
            pediatric_department_count=0,
            surgical_department_count=0,
            other_departments_count=0,
            total_areas_covered=0,
            therapeutic_areas_count=0,
            pediatric_areas_count=0,
            general_practice_areas_count=0,
        )

    async def _validate_assignment_data(self, schema, is_update: bool = False) -> None:
        """
        Валидация данных назначения медперсонала

        :param schema: Схема с данными для валидации
        :param is_update: Флаг обновления (для схем обновления)
        """
        # Проверка дат
        if hasattr(schema, 'end_date') and schema.end_date and hasattr(schema, 'start_date') and schema.start_date:
            if schema.end_date < schema.start_date:
                raise ValidationError(_("Дата окончания не может быть раньше даты начала."))

        # Проверка обязательных полей (только для создания)
        if not is_update:
            if not schema.specialist_name or not schema.specialist_name.strip():
                raise ValidationError(_("ФИО специалиста обязательно для заполнения."))

            if not schema.area_number or not schema.area_number.strip():
                raise ValidationError(_("Номер участка обязателен для заполнения."))

        # Проверка времени работы
        if hasattr(schema, 'reception_hours_per_day') and hasattr(schema, 'area_hours_per_day'):
            total_hours = (schema.reception_hours_per_day or 0) + (schema.area_hours_per_day or 0)
            if total_hours > 24:
                raise ValidationError(_("Общее время работы не может превышать 24 часа в день."))

        # Проверка разумности времени работы
        if hasattr(schema, 'reception_hours_per_day') and (schema.reception_hours_per_day or 0) > 12:
            raise ValidationError(_("Время работы на приёме не может превышать 12 часов в день."))

        if hasattr(schema, 'area_hours_per_day') and (schema.area_hours_per_day or 0) > 12:
            raise ValidationError(_("Время работы на участке не может превышать 12 часов в день."))