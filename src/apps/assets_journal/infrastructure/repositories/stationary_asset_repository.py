from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.apps.assets_journal.domain.models.stationary_asset import StationaryAssetDomain
from src.apps.assets_journal.infrastructure.api.schemas.responses.stationary_asset_schemas import (
    StationaryAssetStatisticsSchema,
)
from src.apps.assets_journal.infrastructure.db_models.stationary_models import StationaryAsset
from src.apps.assets_journal.interfaces.stationary_repository_interfaces import (
    StationaryAssetRepositoryInterface,
)
from src.apps.assets_journal.mappers.stationary_asset_mappers import (
    map_stationary_asset_db_to_domain,
    map_stationary_asset_domain_to_db,
)
from src.apps.patients.infrastructure.db_models.patients import SQLAlchemyPatient
from src.core.logger import LoggerService
from src.shared.infrastructure.base import BaseRepository


class StationaryAssetRepositoryImpl(BaseRepository, StationaryAssetRepositoryInterface):
    """Реализация репозитория активов стационара"""

    def __init__(self, async_db_session: AsyncSession, logger: LoggerService):
        super().__init__(async_db_session, logger)

    async def get_by_id(self, asset_id: UUID) -> Optional[StationaryAssetDomain]:
        query = (
            select(StationaryAsset)
            .options(
                joinedload(StationaryAsset.patient),
            )
            .where(StationaryAsset.id == asset_id)
        )
        result = await self._async_db_session.execute(query)
        asset = result.scalar_one_or_none()

        if asset:
            return map_stationary_asset_db_to_domain(asset)
        return None

    async def get_by_bg_asset_id(self, bg_asset_id: str) -> Optional[StationaryAssetDomain]:
        query = (
            select(StationaryAsset)
            .options(
                joinedload(StationaryAsset.patient),
            )
            .where(StationaryAsset.bg_asset_id == bg_asset_id)
        )
        result = await self._async_db_session.execute(query)
        asset = result.scalar_one_or_none()

        if asset:
            return map_stationary_asset_db_to_domain(asset)
        return None

    async def get_assets(
            self,
            filters: Dict[str, any],
            page: int = 1,
            limit: int = 30,
    ) -> List[StationaryAssetDomain]:
        query = (
            select(StationaryAsset)
            .options(
                joinedload(StationaryAsset.patient),
            )
        )

        # Применяем фильтры
        query = self._apply_filters(query, filters)

        # Сортировка по дате регистрации (сначала новые)
        query = query.order_by(StationaryAsset.reg_date.desc())

        # Пагинация
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        result = await self._async_db_session.execute(query)
        assets = result.scalars().all()

        return [map_stationary_asset_db_to_domain(asset) for asset in assets]

    async def get_total_count(self, filters: Dict[str, any]) -> int:
        query = select(func.count(StationaryAsset.id))

        # Применяем фильтры
        query = self._apply_filters(query, filters)

        result = await self._async_db_session.execute(query)
        return result.scalar_one()

    async def create(self, asset: StationaryAssetDomain) -> StationaryAssetDomain:
        db_asset = map_stationary_asset_domain_to_db(asset)

        self._async_db_session.add(db_asset)
        await self._async_db_session.flush()
        await self._async_db_session.refresh(db_asset)

        # Загружаем связанные данные
        query = (
            select(StationaryAsset)
            .options(
                joinedload(StationaryAsset.patient),
            )
            .where(StationaryAsset.id == db_asset.id)
        )
        result = await self._async_db_session.execute(query)
        db_asset_with_relations = result.scalar_one()

        return map_stationary_asset_db_to_domain(db_asset_with_relations)

    async def update(self, asset: StationaryAssetDomain) -> StationaryAssetDomain:
        query = (
            select(StationaryAsset)
            .options(
                joinedload(StationaryAsset.patient),
            )
            .where(StationaryAsset.id == asset.id)
        )
        result = await self._async_db_session.execute(query)
        db_asset = result.scalar_one()

        # Обновляем поля
        for field, value in asset.__dict__.items():
            if hasattr(db_asset, field) and field not in ['id', 'created_at', 'patient_data', '_organization_data']:
                setattr(db_asset, field, value)

        await self._async_db_session.flush()
        await self._async_db_session.refresh(db_asset)

        return map_stationary_asset_db_to_domain(db_asset)

    async def delete(self, asset_id: UUID) -> None:
        query = select(StationaryAsset).where(StationaryAsset.id == asset_id)
        result = await self._async_db_session.execute(query)
        asset = result.scalar_one()

        await self._async_db_session.delete(asset)
        await self._async_db_session.flush()

    async def get_statistics(self, filters: Dict[str, any]) -> StationaryAssetStatisticsSchema:
        base_query = select(StationaryAsset)
        base_query = self._apply_filters(base_query, filters)

        # Общее количество
        total_query = select(func.count(StationaryAsset.id))
        total_query = self._apply_filters(total_query, filters)
        total_result = await self._async_db_session.execute(total_query)
        total_assets = total_result.scalar_one()

        # Подтвержденные
        confirmed_query = select(func.count(StationaryAsset.id)).where(
            StationaryAsset.has_confirm == True
        )
        confirmed_query = self._apply_filters(confirmed_query, filters)
        confirmed_result = await self._async_db_session.execute(confirmed_query)
        confirmed_assets = confirmed_result.scalar_one()

        # Отказанные
        refused_query = select(func.count(StationaryAsset.id)).where(
            StationaryAsset.has_refusal == True
        )
        refused_query = self._apply_filters(refused_query, filters)
        refused_result = await self._async_db_session.execute(refused_query)
        refused_assets = refused_result.scalar_one()

        # Ожидающие
        pending_assets = total_assets - confirmed_assets - refused_assets

        # С файлами
        files_query = select(func.count(StationaryAsset.id)).where(
            StationaryAsset.has_files == True
        )
        files_query = self._apply_filters(files_query, filters)
        files_result = await self._async_db_session.execute(files_query)
        assets_with_files = files_result.scalar_one()

        return StationaryAssetStatisticsSchema(
            total_assets=total_assets,
            confirmed_assets=confirmed_assets,
            refused_assets=refused_assets,
            pending_assets=pending_assets,
            assets_with_files=assets_with_files,
        )

    async def bulk_create(self, assets: List[StationaryAssetDomain]) -> List[StationaryAssetDomain]:
        db_assets = [map_stationary_asset_domain_to_db(asset) for asset in assets]

        self._async_db_session.add_all(db_assets)
        await self._async_db_session.flush()

        # Получаем созданные активы со связанными данными
        asset_ids = [db_asset.id for db_asset in db_assets]
        query = (
            select(StationaryAsset)
            .options(
                joinedload(StationaryAsset.patient),
            )
            .where(StationaryAsset.id.in_(asset_ids))
        )
        result = await self._async_db_session.execute(query)
        created_assets = result.scalars().all()

        return [map_stationary_asset_db_to_domain(db_asset) for db_asset in created_assets]

    async def exists_by_bg_asset_id(self, bg_asset_id: str) -> bool:
        query = select(func.count(StationaryAsset.id)).where(
            StationaryAsset.bg_asset_id == bg_asset_id
        )
        result = await self._async_db_session.execute(query)
        count = result.scalar_one()
        return count > 0

    def _apply_filters(self, query, filters: Dict[str, any]):
        """Применить фильтры к запросу"""

        # Поиск по пациенту (ФИО или ИИН)
        if filters.get("patient_search"):
            search_term = f"%{filters['patient_search']}%"
            query = query.join(SQLAlchemyPatient).where(
                or_(
                    func.lower(func.concat(SQLAlchemyPatient.last_name, ' ', SQLAlchemyPatient.first_name, ' ', SQLAlchemyPatient.middle_name)).like(search_term.lower()),
                    SQLAlchemyPatient.iin.like(search_term)
                )
            )

        # Конкретный пациент
        if filters.get("patient_id"):
            query = query.where(StationaryAsset.patient_id == filters["patient_id"])

        # ИИН пациента
        if filters.get("patient_iin"):
            query = query.join(SQLAlchemyPatient).where(SQLAlchemyPatient.iin == filters["patient_iin"])

        # Фильтр по организации через attachment_data пациента
        if filters.get("organization_id"):
            query = query.join(SQLAlchemyPatient).where(
                SQLAlchemyPatient.attachment_data['attached_clinic_id'] == filters["organization_id"]
            )

        # Период по дате регистрации
        if filters.get("date_from"):
            query = query.where(StationaryAsset.reg_date >= filters["date_from"])

        if filters.get("date_to"):
            query = query.where(StationaryAsset.reg_date <= filters["date_to"])

        # Статусы
        if filters.get("status") is not None:
            query = query.where(StationaryAsset.status == filters["status"])

        if filters.get("delivery_status") is not None:
            query = query.where(StationaryAsset.delivery_status == filters["delivery_status"])

        # Медицинские данные
        if filters.get("diagnosis"):
            query = query.where(StationaryAsset.diagnosis == filters["diagnosis"])

        # Участок и специализация
        if filters.get("area"):
            query = query.where(StationaryAsset.area == filters["area"])

        if filters.get("specialization"):
            query = query.where(
                func.lower(StationaryAsset.specialization).like(
                    f"%{filters['specialization']}%"
                )
            )

        if filters.get("specialist"):
            query = query.where(
                func.lower(StationaryAsset.specialist).like(
                    f"%{filters['specialist']}%"
                )
            )

        # Флаги
        if filters.get("has_confirm") is not None:
            query = query.where(StationaryAsset.has_confirm == filters["has_confirm"])

        if filters.get("has_files") is not None:
            query = query.where(StationaryAsset.has_files == filters["has_files"])

        if filters.get("has_refusal") is not None:
            query = query.where(StationaryAsset.has_refusal == filters["has_refusal"])

        # Дополнительные поля
        if filters.get("card_number"):
            query = query.where(StationaryAsset.card_number == filters["card_number"])

        if filters.get("bg_asset_id"):
            query = query.where(StationaryAsset.bg_asset_id == filters["bg_asset_id"])

        if filters.get("stay_outcome"):
            query = query.where(
                func.lower(StationaryAsset.stay_outcome).like(
                    f"%{filters['stay_outcome']}%"
                )
            )

        return query