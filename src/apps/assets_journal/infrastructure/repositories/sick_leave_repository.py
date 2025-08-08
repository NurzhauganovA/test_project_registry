# src/apps/assets_journal/infrastructure/repositories/sick_leave_repository.py

from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import func, or_, select, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.apps.assets_journal.domain.models.sick_leave import SickLeaveDomain, SickLeaveListItemDomain
from src.apps.assets_journal.domain.enums import SickLeaveStatusEnum
from src.apps.assets_journal.infrastructure.db_models.sick_leave_models import SickLeave
from src.apps.assets_journal.interfaces.sick_leave_repository_interfaces import (
    SickLeaveRepositoryInterface,
)
from src.apps.assets_journal.mappers.sick_leave_mappers import (
    map_sick_leave_db_to_domain,
    map_sick_leave_domain_to_db,
    map_sick_leave_db_to_list_item,
)
from src.apps.patients.infrastructure.db_models.patients import SQLAlchemyPatient
from src.core.logger import LoggerService
from src.shared.infrastructure.base import BaseRepository


class SickLeaveRepositoryImpl(BaseRepository, SickLeaveRepositoryInterface):
    """Реализация репозитория больничных листов"""

    def __init__(self, async_db_session: AsyncSession, logger: LoggerService):
        super().__init__(async_db_session, logger)

    async def get_by_id(self, sick_leave_id: UUID) -> Optional[SickLeaveDomain]:
        query = (
            select(SickLeave)
            .options(
                joinedload(SickLeave.patient),
                joinedload(SickLeave.parent_sick_leave),
                joinedload(SickLeave.extensions),
            )
            .where(SickLeave.id == sick_leave_id)
        )
        result = await self._async_db_session.execute(query)
        sick_leave = result.scalar_one_or_none()

        if sick_leave:
            return map_sick_leave_db_to_domain(sick_leave)
        return None

    async def get_by_number(self, sick_leave_number: str) -> Optional[SickLeaveDomain]:
        query = (
            select(SickLeave)
            .options(
                joinedload(SickLeave.patient),
                joinedload(SickLeave.parent_sick_leave),
                joinedload(SickLeave.extensions),
            )
            .where(SickLeave.sick_leave_number == sick_leave_number)
        )
        result = await self._async_db_session.execute(query)
        sick_leave = result.scalar_one_or_none()

        if sick_leave:
            return map_sick_leave_db_to_domain(sick_leave)
        return None

    async def get_sick_leaves(
            self,
            filters: Dict[str, any],
            page: int = 1,
            limit: int = 30,
    ) -> List[SickLeaveListItemDomain]:
        query = (
            select(SickLeave)
            .options(
                joinedload(SickLeave.patient),
            )
        )

        # Применяем фильтры
        query = self._apply_filters(query, filters)

        # Сортировка по дате создания (сначала новые)
        query = query.order_by(SickLeave.created_at.desc())

        # Пагинация
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        result = await self._async_db_session.execute(query)
        sick_leaves = result.scalars().all()

        return [map_sick_leave_db_to_list_item(sick_leave) for sick_leave in sick_leaves]

    async def get_total_count(self, filters: Dict[str, any]) -> int:
        query = select(func.count(SickLeave.id))

        # Применяем фильтры
        query = self._apply_filters(query, filters)

        result = await self._async_db_session.execute(query)
        return result.scalar_one()

    async def create(self, sick_leave: SickLeaveDomain) -> SickLeaveDomain:
        db_sick_leave = map_sick_leave_domain_to_db(sick_leave)

        self._async_db_session.add(db_sick_leave)
        await self._async_db_session.flush()
        await self._async_db_session.refresh(db_sick_leave)

        # Загружаем связанные данные
        query = (
            select(SickLeave)
            .options(
                joinedload(SickLeave.patient),
                joinedload(SickLeave.parent_sick_leave),
                joinedload(SickLeave.extensions),
            )
            .where(SickLeave.id == db_sick_leave.id)
        )
        result = await self._async_db_session.execute(query)
        db_sick_leave_with_relations = result.scalar_one()

        return map_sick_leave_db_to_domain(db_sick_leave_with_relations)

    async def update(self, sick_leave: SickLeaveDomain) -> SickLeaveDomain:
        query = (
            select(SickLeave)
            .options(
                joinedload(SickLeave.patient),
                joinedload(SickLeave.parent_sick_leave),
                joinedload(SickLeave.extensions),
            )
            .where(SickLeave.id == sick_leave.id)
        )
        result = await self._async_db_session.execute(query)
        db_sick_leave = result.scalar_one()

        # Обновляем поля
        for field, value in sick_leave.__dict__.items():
            if hasattr(db_sick_leave, field) and field not in ['id', 'created_at', 'patient_data']:
                setattr(db_sick_leave, field, value)

        await self._async_db_session.flush()
        await self._async_db_session.refresh(db_sick_leave)

        return map_sick_leave_db_to_domain(db_sick_leave)

    async def delete(self, sick_leave_id: UUID) -> None:
        query = select(SickLeave).where(SickLeave.id == sick_leave_id)
        result = await self._async_db_session.execute(query)
        sick_leave = result.scalar_one()

        await self._async_db_session.delete(sick_leave)
        await self._async_db_session.flush()

    async def get_active_sick_leaves_by_patient(self, patient_id: UUID) -> List[SickLeaveDomain]:
        query = (
            select(SickLeave)
            .options(
                joinedload(SickLeave.patient),
                joinedload(SickLeave.parent_sick_leave),
                joinedload(SickLeave.extensions),
            )
            .where(
                SickLeave.patient_id == patient_id,
                SickLeave.status == SickLeaveStatusEnum.OPEN
            )
            .order_by(SickLeave.disability_start_date.desc())
        )
        result = await self._async_db_session.execute(query)
        sick_leaves = result.scalars().all()

        return [map_sick_leave_db_to_domain(sick_leave) for sick_leave in sick_leaves]

    async def get_sick_leaves_by_patient(
            self,
            patient_id: UUID,
            page: int = 1,
            limit: int = 30,
    ) -> List[SickLeaveDomain]:
        query = (
            select(SickLeave)
            .options(
                joinedload(SickLeave.patient),
                joinedload(SickLeave.parent_sick_leave),
                joinedload(SickLeave.extensions),
            )
            .where(SickLeave.patient_id == patient_id)
            .order_by(SickLeave.disability_start_date.desc())
        )

        # Пагинация
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        result = await self._async_db_session.execute(query)
        sick_leaves = result.scalars().all()

        return [map_sick_leave_db_to_domain(sick_leave) for sick_leave in sick_leaves]

    async def exists_by_number(self, sick_leave_number: str) -> bool:
        query = select(func.count(SickLeave.id)).where(
            SickLeave.sick_leave_number == sick_leave_number
        )
        result = await self._async_db_session.execute(query)
        count = result.scalar_one()
        return count > 0

    async def get_extensions(self, parent_sick_leave_id: UUID) -> List[SickLeaveDomain]:
        query = (
            select(SickLeave)
            .options(
                joinedload(SickLeave.patient),
                joinedload(SickLeave.parent_sick_leave),
            )
            .where(SickLeave.parent_sick_leave_id == parent_sick_leave_id)
            .order_by(SickLeave.disability_start_date.asc())
        )
        result = await self._async_db_session.execute(query)
        extensions = result.scalars().all()

        return [map_sick_leave_db_to_domain(extension) for extension in extensions]

    def _apply_filters(self, query, filters: Dict[str, any]):
        """Применить фильтры к запросу"""

        # Поиск по пациенту (ФИО или ИИН)
        if filters.get("patient_search"):
            search_term = f"%{filters['patient_search']}%"
            query = query.join(SQLAlchemyPatient).where(
                or_(
                    func.lower(func.concat(
                        SQLAlchemyPatient.last_name, ' ',
                        SQLAlchemyPatient.first_name, ' ',
                        SQLAlchemyPatient.middle_name
                    )).like(search_term.lower()),
                    SQLAlchemyPatient.iin.like(search_term)
                )
            )

        # Конкретный пациент
        if filters.get("patient_id"):
            query = query.where(SickLeave.patient_id == filters["patient_id"])

        # ИИН пациента
        if filters.get("patient_iin"):
            query = query.join(SQLAlchemyPatient).where(
                SQLAlchemyPatient.iin == filters["patient_iin"]
            )

        # Период по дате выдачи
        if filters.get("issue_date_from"):
            query = query.where(SickLeave.issue_date >= filters["issue_date_from"])

        if filters.get("issue_date_to"):
            query = query.where(SickLeave.issue_date <= filters["issue_date_to"])

        # Период нетрудоспособности
        if filters.get("disability_start_date_from"):
            query = query.where(SickLeave.disability_start_date >= filters["disability_start_date_from"])

        if filters.get("disability_start_date_to"):
            query = query.where(SickLeave.disability_start_date <= filters["disability_start_date_to"])

        # Статус
        if filters.get("status") is not None:
            query = query.where(SickLeave.status == filters["status"])

        # Тип больничного листа
        if filters.get("sick_leave_type") is not None:
            query = query.where(SickLeave.sick_leave_type == filters["sick_leave_type"])

        # Причина
        if filters.get("sick_leave_reason") is not None:
            query = query.where(SickLeave.sick_leave_reason == filters["sick_leave_reason"])

        # Врач
        if filters.get("doctor_name"):
            query = query.where(
                func.lower(SickLeave.doctor_full_name).like(
                    f"%{filters['doctor_name'].lower()}%"
                )
            )

        # Специализация врача
        if filters.get("doctor_specialization"):
            query = query.where(
                func.lower(SickLeave.doctor_specialization).like(
                    f"%{filters['doctor_specialization'].lower()}%"
                )
            )

        # Диагноз
        if filters.get("diagnosis"):
            query = query.where(
                func.lower(SickLeave.diagnosis).like(
                    f"%{filters['diagnosis'].lower()}%"
                )
            )

        # Код диагноза
        if filters.get("diagnosis_code"):
            query = query.where(SickLeave.diagnosis_code == filters["diagnosis_code"])

        # Номер больничного листа
        if filters.get("sick_leave_number"):
            query = query.where(SickLeave.sick_leave_number == filters["sick_leave_number"])

        # Место работы
        if filters.get("workplace_name"):
            query = query.where(
                func.lower(SickLeave.workplace_name).like(
                    f"%{filters['workplace_name'].lower()}%"
                )
            )

        # Только первичные или продления
        if filters.get("is_primary") is not None:
            query = query.where(SickLeave.is_primary == filters["is_primary"])

        # Активные больничные листы
        if filters.get("is_active"):
            query = query.where(SickLeave.status == SickLeaveStatusEnum.OPEN)

    def _apply_filters(self, query, filters: Dict[str, any]):
        """Применить фильтры к запросу"""

        # Поиск по пациенту (ФИО или ИИН)
        if filters.get("patient_search"):
            search_term = f"%{filters['patient_search']}%"
            query = query.join(SQLAlchemyPatient).where(
                or_(
                    func.lower(func.concat(
                        SQLAlchemyPatient.last_name, ' ',
                        SQLAlchemyPatient.first_name, ' ',
                        SQLAlchemyPatient.middle_name
                    )).like(search_term.lower()),
                    SQLAlchemyPatient.iin.like(search_term)
                )
            )

        # Конкретный пациент
        if filters.get("patient_id"):
            query = query.where(SickLeave.patient_id == filters["patient_id"])

        # ИИН пациента
        if filters.get("patient_iin"):
            query = query.join(SQLAlchemyPatient).where(SQLAlchemyPatient.iin == filters["patient_iin"])

        # Фильтр по организации через attachment_data пациента
        if filters.get("organization_id"):
            from sqlalchemy import Integer
            query = query.join(SQLAlchemyPatient).where(
                SQLAlchemyPatient.attachment_data['attached_clinic_id'].cast(Integer) == filters["organization_id"]
            )

        # Период по дате получения
        if filters.get("receive_date_from"):
            query = query.where(SickLeave.receive_date >= filters["receive_date_from"])

        if filters.get("receive_date_to"):
            query = query.where(SickLeave.receive_date <= filters["receive_date_to"])

        # Период нетрудоспособности
        if filters.get("disability_start_date_from"):
            query = query.where(SickLeave.disability_start_date >= filters["disability_start_date_from"])

        if filters.get("disability_start_date_to"):
            query = query.where(SickLeave.disability_start_date <= filters["disability_start_date_to"])

        # Статус
        if filters.get("status") is not None:
            query = query.where(SickLeave.status == filters["status"])

        # Причина больничного листа
        if filters.get("sick_leave_reason") is not None:
            query = query.where(SickLeave.sick_leave_reason == filters["sick_leave_reason"])

        # Врач
        if filters.get("specialist"):
            query = query.where(
                func.lower(SickLeave.specialist).like(
                    f"%{filters['specialist'].lower()}%"
                )
            )

        # Специализация врача
        if filters.get("specialization"):
            query = query.where(
                func.lower(SickLeave.specialization).like(
                    f"%{filters['specialization'].lower()}%"
                )
            )

        # Участок
        if filters.get("area"):
            query = query.where(
                func.lower(SickLeave.area).like(
                    f"%{filters['area'].lower()}%"
                )
            )

        # Место работы
        if filters.get("workplace_name"):
            query = query.where(
                func.lower(SickLeave.workplace_name).like(
                    f"%{filters['workplace_name'].lower()}%"
                )
            )

        # Только первичные или продления
        if filters.get("is_primary") is not None:
            query = query.where(SickLeave.is_primary == filters["is_primary"])

        # Активные больничные листы
        if filters.get("is_active"):
            query = query.where(SickLeave.status == SickLeaveStatusEnum.OPEN)

        return query