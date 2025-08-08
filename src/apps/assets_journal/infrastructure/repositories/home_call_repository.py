from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.apps.assets_journal.domain.models.home_call import HomeCallDomain, HomeCallListItemDomain
from src.apps.assets_journal.domain.enums import HomeCallStatusEnum
from src.apps.assets_journal.infrastructure.db_models.home_call_models import HomeCall
from src.apps.assets_journal.interfaces.home_call_repository_interfaces import (
    HomeCallRepositoryInterface,
)
from src.apps.assets_journal.mappers.home_call_mappers import (
    map_home_call_db_to_domain,
    map_home_call_domain_to_db,
    map_home_call_db_to_list_item,
)
from src.apps.patients.infrastructure.db_models.patients import SQLAlchemyPatient
from src.core.logger import LoggerService
from src.shared.infrastructure.base import BaseRepository


class HomeCallRepositoryImpl(BaseRepository, HomeCallRepositoryInterface):
    """Реализация репозитория вызовов на дом"""

    def __init__(self, async_db_session: AsyncSession, logger: LoggerService):
        super().__init__(async_db_session, logger)

    async def get_by_id(self, home_call_id: UUID) -> Optional[HomeCallDomain]:
        query = (
            select(HomeCall)
            .options(
                joinedload(HomeCall.patient),
            )
            .where(HomeCall.id == home_call_id)
        )
        result = await self._async_db_session.execute(query)
        home_call = result.unique().scalar_one_or_none()

        if home_call:
            return map_home_call_db_to_domain(home_call)
        return None

    async def get_by_call_number(self, call_number: str) -> Optional[HomeCallDomain]:
        query = (
            select(HomeCall)
            .options(
                joinedload(HomeCall.patient),
            )
            .where(HomeCall.call_number == call_number)
        )
        result = await self._async_db_session.execute(query)
        home_call = result.unique().scalar_one_or_none()

        if home_call:
            return map_home_call_db_to_domain(home_call)
        return None

    async def get_home_calls(
            self,
            filters: Dict[str, any],
            page: int = 1,
            limit: int = 30,
    ) -> List[HomeCallListItemDomain]:
        query = (
            select(HomeCall)
            .options(
                joinedload(HomeCall.patient),
            )
        )

        # Применяем фильтры
        query = self._apply_filters(query, filters)

        # Сортировка по дате регистрации (сначала новые)
        query = query.order_by(HomeCall.registration_date.desc())

        # Пагинация
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        result = await self._async_db_session.execute(query)
        home_calls = result.unique().scalars().all()

        return [map_home_call_db_to_list_item(home_call) for home_call in home_calls]

    async def get_total_count(self, filters: Dict[str, any]) -> int:
        query = select(func.count(HomeCall.id))

        # Применяем фильтры
        query = self._apply_filters(query, filters)

        result = await self._async_db_session.execute(query)
        return result.scalar_one()

    async def create(self, home_call: HomeCallDomain) -> HomeCallDomain:
        # Генерируем номер вызова если не указан
        if not home_call.call_number:
            home_call.call_number = await self._generate_call_number()

        db_home_call = map_home_call_domain_to_db(home_call)

        self._async_db_session.add(db_home_call)
        await self._async_db_session.flush()
        await self._async_db_session.refresh(db_home_call)

        # Загружаем связанные данные
        query = (
            select(HomeCall)
            .options(
                joinedload(HomeCall.patient),
            )
            .where(HomeCall.id == db_home_call.id)
        )
        result = await self._async_db_session.execute(query)
        db_home_call_with_relations = result.unique().scalar_one()

        return map_home_call_db_to_domain(db_home_call_with_relations)

    async def update(self, home_call: HomeCallDomain) -> HomeCallDomain:
        query = (
            select(HomeCall)
            .options(
                joinedload(HomeCall.patient),
            )
            .where(HomeCall.id == home_call.id)
        )
        result = await self._async_db_session.execute(query)
        db_home_call = result.unique().scalar_one()

        # Обновляем поля
        for field, value in home_call.__dict__.items():
            if hasattr(db_home_call, field) and field not in ['id', 'created_at', 'patient_data']:
                setattr(db_home_call, field, value)

        await self._async_db_session.flush()
        await self._async_db_session.refresh(db_home_call)

        return map_home_call_db_to_domain(db_home_call)

    async def delete(self, home_call_id: UUID) -> None:
        query = select(HomeCall).where(HomeCall.id == home_call_id)
        result = await self._async_db_session.execute(query)
        home_call = result.scalar_one()

        await self._async_db_session.delete(home_call)
        await self._async_db_session.flush()

    async def get_active_home_calls_by_patient(self, patient_id: UUID) -> List[HomeCallDomain]:
        query = (
            select(HomeCall)
            .options(
                joinedload(HomeCall.patient),
            )
            .where(
                HomeCall.patient_id == patient_id,
                HomeCall.status.in_([HomeCallStatusEnum.REGISTERED, HomeCallStatusEnum.IN_PROGRESS])
            )
            .order_by(HomeCall.registration_date.desc())
        )
        result = await self._async_db_session.execute(query)
        home_calls = result.unique().scalars().all()

        return [map_home_call_db_to_domain(home_call) for home_call in home_calls]

    async def get_home_calls_by_patient(
            self,
            patient_id: UUID,
            page: int = 1,
            limit: int = 30,
    ) -> List[HomeCallDomain]:
        query = (
            select(HomeCall)
            .options(
                joinedload(HomeCall.patient),
            )
            .where(HomeCall.patient_id == patient_id)
            .order_by(HomeCall.registration_date.desc())
        )

        # Пагинация
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        result = await self._async_db_session.execute(query)
        home_calls = result.unique().scalars().all()

        return [map_home_call_db_to_domain(home_call) for home_call in home_calls]

    async def get_home_calls_by_specialist(
            self,
            specialist: str,
            page: int = 1,
            limit: int = 30,
    ) -> List[HomeCallDomain]:
        query = (
            select(HomeCall)
            .options(
                joinedload(HomeCall.patient),
            )
            .where(HomeCall.specialist == specialist)
            .order_by(HomeCall.registration_date.desc())
        )

        # Пагинация
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        result = await self._async_db_session.execute(query)
        home_calls = result.unique().scalars().all()

        return [map_home_call_db_to_domain(home_call) for home_call in home_calls]

    async def exists_by_call_number(self, call_number: str) -> bool:
        query = select(func.count(HomeCall.id)).where(
            HomeCall.call_number == call_number
        )
        result = await self._async_db_session.execute(query)
        count = result.scalar_one()
        return count > 0

    async def _generate_call_number(self) -> str:
        """Генерировать номер вызова"""
        from datetime import datetime

        # Получаем текущую дату
        today = datetime.now()
        year = today.strftime("%Y")
        month = today.strftime("%m")
        day = today.strftime("%d")

        # Ищем последний номер вызова за сегодня
        query = select(func.count(HomeCall.id)).where(
            func.date(HomeCall.registration_date) == today.date()
        )
        result = await self._async_db_session.execute(query)
        count = result.scalar_one()

        # Генерируем номер: ГГММДД + порядковый номер
        call_number = f"{year[-2:]}{month}{day}{count + 1:04d}"

        return call_number

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
            query = query.where(HomeCall.patient_id == filters["patient_id"])

        # ИИН пациента
        if filters.get("patient_iin"):
            query = query.join(SQLAlchemyPatient).where(SQLAlchemyPatient.iin == filters["patient_iin"])

        # Фильтр по организации через attachment_data пациента
        if filters.get("organization_id"):
            from sqlalchemy import Integer
            query = query.join(SQLAlchemyPatient).where(
                SQLAlchemyPatient.attachment_data['attached_clinic_id'].cast(Integer) == filters["organization_id"]
            )

        # Период по дате регистрации
        if filters.get("registration_date_from"):
            query = query.where(HomeCall.registration_date >= filters["registration_date_from"])

        if filters.get("registration_date_to"):
            query = query.where(HomeCall.registration_date <= filters["registration_date_to"])

        # Период по дате выполнения
        if filters.get("execution_date_from"):
            query = query.where(HomeCall.execution_date >= filters["execution_date_from"])

        if filters.get("execution_date_to"):
            query = query.where(HomeCall.execution_date <= filters["execution_date_to"])

        # Статус
        if filters.get("status") is not None:
            query = query.where(HomeCall.status == filters["status"])

        # Категория
        if filters.get("category") is not None:
            query = query.where(HomeCall.category == filters["category"])

        # Источник
        if filters.get("source") is not None:
            query = query.where(HomeCall.source == filters["source"])

        # Тип вызова
        if filters.get("call_type") is not None:
            query = query.where(HomeCall.call_type == filters["call_type"])

        # Врач
        if filters.get("specialist"):
            query = query.where(
                func.lower(HomeCall.specialist).like(
                    f"%{filters['specialist'].lower()}%"
                )
            )

        # Специализация врача
        if filters.get("specialization"):
            query = query.where(
                func.lower(HomeCall.specialization).like(
                    f"%{filters['specialization'].lower()}%"
                )
            )

        # Участок
        if filters.get("area"):
            query = query.where(
                func.lower(HomeCall.area).like(
                    f"%{filters['area'].lower()}%"
                )
            )

        # Номер вызова
        if filters.get("call_number"):
            query = query.where(HomeCall.call_number == filters["call_number"])

        # Только активные вызовы
        if filters.get("is_active"):
            query = query.where(HomeCall.status.in_([HomeCallStatusEnum.REGISTERED, HomeCallStatusEnum.IN_PROGRESS]))

        return query