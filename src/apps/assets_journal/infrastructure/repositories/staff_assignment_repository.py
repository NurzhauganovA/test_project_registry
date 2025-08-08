from datetime import date
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import func, or_, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.assets_journal.domain.models.staff_assignment import StaffAssignmentDomain, StaffAssignmentListItemDomain
from src.apps.assets_journal.domain.enums import StaffAssignmentStatusEnum
from src.apps.assets_journal.infrastructure.db_models.staff_assignment import StaffAssignment
from src.apps.assets_journal.interfaces.staff_assignment_repository_interface import (
    StaffAssignmentRepositoryInterface,
)
from src.apps.assets_journal.mappers.staff_assignment_mappers import (
    map_staff_assignment_db_to_domain,
    map_staff_assignment_domain_to_db,
    map_staff_assignment_db_to_list_item,
)
from src.core.logger import LoggerService
from src.shared.infrastructure.base import BaseRepository


class StaffAssignmentRepositoryImpl(BaseRepository, StaffAssignmentRepositoryInterface):
    """Реализация репозитория назначений медперсонала"""

    def __init__(self, async_db_session: AsyncSession, logger: LoggerService):
        super().__init__(async_db_session, logger)

    async def get_by_id(self, assignment_id: UUID) -> Optional[StaffAssignmentDomain]:
        query = select(StaffAssignment).where(StaffAssignment.id == assignment_id)
        result = await self._async_db_session.execute(query)
        assignment = result.scalar_one_or_none()

        if assignment:
            return map_staff_assignment_db_to_domain(assignment)
        return None

    async def get_staff_assignments(
            self,
            filters: Dict[str, any],
            page: int = 1,
            limit: int = 30,
    ) -> List[StaffAssignmentListItemDomain]:
        query = select(StaffAssignment)

        # Применяем фильтры
        query = self._apply_filters(query, filters)

        # Сортировка по дате начала (сначала новые)
        query = query.order_by(StaffAssignment.start_date.desc())

        # Пагинация
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        result = await self._async_db_session.execute(query)
        assignments = result.scalars().all()

        return [map_staff_assignment_db_to_list_item(assignment) for assignment in assignments]

    async def get_total_count(self, filters: Dict[str, any]) -> int:
        query = select(func.count(StaffAssignment.id))

        # Применяем фильтры
        query = self._apply_filters(query, filters)

        result = await self._async_db_session.execute(query)
        return result.scalar_one()

    async def create(self, assignment: StaffAssignmentDomain) -> StaffAssignmentDomain:
        db_assignment = map_staff_assignment_domain_to_db(assignment)

        self._async_db_session.add(db_assignment)
        await self._async_db_session.flush()
        await self._async_db_session.refresh(db_assignment)

        return map_staff_assignment_db_to_domain(db_assignment)

    async def update(self, assignment: StaffAssignmentDomain) -> StaffAssignmentDomain:
        query = select(StaffAssignment).where(StaffAssignment.id == assignment.id)
        result = await self._async_db_session.execute(query)
        db_assignment = result.scalar_one()

        # Обновляем поля
        for field, value in assignment.__dict__.items():
            if hasattr(db_assignment, field) and field not in ['id', 'created_at']:
                setattr(db_assignment, field, value)

        await self._async_db_session.flush()
        await self._async_db_session.refresh(db_assignment)

        return map_staff_assignment_db_to_domain(db_assignment)

    async def delete(self, assignment_id: UUID) -> None:
        query = select(StaffAssignment).where(StaffAssignment.id == assignment_id)
        result = await self._async_db_session.execute(query)
        assignment = result.scalar_one()

        await self._async_db_session.delete(assignment)
        await self._async_db_session.flush()

    async def get_assignments_by_specialist(
            self,
            specialist_name: str,
            page: int = 1,
            limit: int = 30,
    ) -> List[StaffAssignmentDomain]:
        query = (
            select(StaffAssignment)
            .where(
                func.lower(StaffAssignment.specialist_name).like(f"%{specialist_name.lower()}%")
            )
            .order_by(StaffAssignment.start_date.desc())
        )

        # Пагинация
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        result = await self._async_db_session.execute(query)
        assignments = result.scalars().all()

        return [map_staff_assignment_db_to_domain(assignment) for assignment in assignments]

    async def get_assignments_by_area(
            self,
            area_number: str,
            page: int = 1,
            limit: int = 30,
    ) -> List[StaffAssignmentDomain]:
        query = (
            select(StaffAssignment)
            .where(StaffAssignment.area_number == area_number)
            .order_by(StaffAssignment.start_date.desc())
        )

        # Пагинация
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        result = await self._async_db_session.execute(query)
        assignments = result.scalars().all()

        return [map_staff_assignment_db_to_domain(assignment) for assignment in assignments]

    async def get_assignments_by_department(
            self,
            department: str,
            page: int = 1,
            limit: int = 30,
    ) -> List[StaffAssignmentDomain]:
        query = (
            select(StaffAssignment)
            .where(StaffAssignment.department == department)
            .order_by(StaffAssignment.start_date.desc())
        )

        # Пагинация
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        result = await self._async_db_session.execute(query)
        assignments = result.scalars().all()

        return [map_staff_assignment_db_to_domain(assignment) for assignment in assignments]

    async def get_current_assignments(
            self,
            page: int = 1,
            limit: int = 30,
    ) -> List[StaffAssignmentDomain]:
        today = date.today()

        query = (
            select(StaffAssignment)
            .where(
                and_(
                    StaffAssignment.status == StaffAssignmentStatusEnum.ACTIVE,
                    StaffAssignment.start_date <= today,
                    or_(
                        StaffAssignment.end_date.is_(None),
                        StaffAssignment.end_date >= today
                    )
                )
            )
            .order_by(StaffAssignment.start_date.desc())
        )

        # Пагинация
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        result = await self._async_db_session.execute(query)
        assignments = result.scalars().all()

        return [map_staff_assignment_db_to_domain(assignment) for assignment in assignments]

    async def check_assignment_conflict(
            self,
            specialist_name: str,
            area_number: str,
            start_date: date,
            end_date: Optional[date] = None,
            exclude_id: Optional[UUID] = None,
    ) -> bool:
        """
        Проверить конфликт назначений
        """
        query = select(StaffAssignment).where(
            and_(
                func.lower(StaffAssignment.specialist_name) == specialist_name.lower(),
                StaffAssignment.area_number == area_number,
                StaffAssignment.status == StaffAssignmentStatusEnum.ACTIVE,
            )
        )

        # Исключаем текущее назначение при редактировании
        if exclude_id:
            query = query.where(StaffAssignment.id != exclude_id)

        # Проверяем пересечение периодов
        if end_date:
            # Новое назначение имеет конечную дату
            query = query.where(
                and_(
                    StaffAssignment.start_date <= end_date,
                    or_(
                        StaffAssignment.end_date.is_(None),
                        StaffAssignment.end_date >= start_date
                    )
                )
            )
        else:
            # Новое назначение бессрочное
            query = query.where(
                or_(
                    StaffAssignment.end_date.is_(None),
                    StaffAssignment.end_date >= start_date
                )
            )

        result = await self._async_db_session.execute(query)
        conflicting_assignment = result.scalar_one_or_none()

        return conflicting_assignment is not None

    def _apply_filters(self, query, filters: Dict[str, any]):
        """Применить фильтры к запросу"""

        # Поиск по специалисту
        if filters.get("specialist_search"):
            search_term = f"%{filters['specialist_search'].lower()}%"
            query = query.where(
                func.lower(StaffAssignment.specialist_name).like(search_term)
            )

        # Период по дате начала
        if filters.get("start_date_from"):
            query = query.where(StaffAssignment.start_date >= filters["start_date_from"])

        if filters.get("start_date_to"):
            query = query.where(StaffAssignment.start_date <= filters["start_date_to"])

        # Период по дате окончания
        if filters.get("end_date_from"):
            query = query.where(StaffAssignment.end_date >= filters["end_date_from"])

        if filters.get("end_date_to"):
            query = query.where(StaffAssignment.end_date <= filters["end_date_to"])

        # Специализация
        if filters.get("specialization"):
            query = query.where(StaffAssignment.specialization == filters["specialization"])

        # Отделение
        if filters.get("department"):
            query = query.where(StaffAssignment.department == filters["department"])

        # Номер участка
        if filters.get("area_number"):
            query = query.where(StaffAssignment.area_number == filters["area_number"])

        # Тип участка
        if filters.get("area_type"):
            query = query.where(StaffAssignment.area_type == filters["area_type"])

        # Статус
        if filters.get("status"):
            query = query.where(StaffAssignment.status == filters["status"])

        # Только активные назначения
        if filters.get("only_active"):
            query = query.where(StaffAssignment.status == StaffAssignmentStatusEnum.ACTIVE)

        # Только текущие назначения (активные на сегодня)
        if filters.get("only_current"):
            today = date.today()
            query = query.where(
                and_(
                    StaffAssignment.status == StaffAssignmentStatusEnum.ACTIVE,
                    StaffAssignment.start_date <= today,
                    or_(
                        StaffAssignment.end_date.is_(None),
                        StaffAssignment.end_date >= today
                    )
                )
            )

        return query