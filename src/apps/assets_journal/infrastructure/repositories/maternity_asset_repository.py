from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import func, or_, select, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.apps.assets_journal.domain.models.maternity_asset import MaternityAssetDomain
from src.apps.assets_journal.infrastructure.db_models.maternity_models import MaternityAsset
from src.apps.assets_journal.interfaces.maternity_repository_interfaces import (
    MaternityAssetRepositoryInterface,
)
from src.apps.assets_journal.mappers.maternity_asset_mappers import (
    map_maternity_asset_db_to_domain,
    map_maternity_asset_domain_to_db,
)
from src.apps.patients.infrastructure.db_models.patients import SQLAlchemyPatient
from src.core.logger import LoggerService
from src.shared.infrastructure.base import BaseRepository


class MaternityAssetRepositoryImpl(BaseRepository, MaternityAssetRepositoryInterface):
    """Реализация репозитория активов роддома"""

    def __init__(self, async_db_session: AsyncSession, logger: LoggerService):
        super().__init__(async_db_session, logger)

    async def get_by_id(self, asset_id: UUID) -> Optional[MaternityAssetDomain]:
        query = (
            select(MaternityAsset)
            .options(
                joinedload(MaternityAsset.patient),
            )
            .where(MaternityAsset.id == asset_id)
        )
        result = await self._async_db_session.execute(query)
        asset = result.scalar_one_or_none()

        if asset:
            return map_maternity_asset_db_to_domain(asset)
        return None

    async def get_by_bg_asset_id(self, bg_asset_id: str) -> Optional[MaternityAssetDomain]:
        query = (
            select(MaternityAsset)
            .options(
                joinedload(MaternityAsset.patient),
            )
            .where(MaternityAsset.bg_asset_id == bg_asset_id)
        )
        result = await self._async_db_session.execute(query)
        asset = result.scalar_one_or_none()

        if asset:
            return map_maternity_asset_db_to_domain(asset)
        return None

    async def get_assets(
            self,
            filters: Dict[str, any],
            page: int = 1,
            limit: int = 30,
    ) -> List[MaternityAssetDomain]:
        query = (
            select(MaternityAsset)
            .options(
                joinedload(MaternityAsset.patient),
            )
        )

        # Применяем фильтры
        query = self._apply_filters(query, filters)

        # Сортировка по дате регистрации (сначала новые)
        query = query.order_by(MaternityAsset.reg_date.desc())

        # Пагинация
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        result = await self._async_db_session.execute(query)
        assets = result.scalars().all()

        return [map_maternity_asset_db_to_domain(asset) for asset in assets]

    async def get_total_count(self, filters: Dict[str, any]) -> int:
        query = select(func.count(MaternityAsset.id))

        # Применяем фильтры
        query = self._apply_filters(query, filters)

        result = await self._async_db_session.execute(query)
        return result.scalar_one()

    async def create(self, asset: MaternityAssetDomain) -> MaternityAssetDomain:
        db_asset = map_maternity_asset_domain_to_db(asset)

        self._async_db_session.add(db_asset)
        await self._async_db_session.flush()
        await self._async_db_session.refresh(db_asset)

        # Загружаем связанные данные
        query = (
            select(MaternityAsset)
            .options(
                joinedload(MaternityAsset.patient),
            )
            .where(MaternityAsset.id == db_asset.id)
        )
        result = await self._async_db_session.execute(query)
        db_asset_with_relations = result.scalar_one()

        return map_maternity_asset_db_to_domain(db_asset_with_relations)

    async def update(self, asset: MaternityAssetDomain) -> MaternityAssetDomain:
        query = (
            select(MaternityAsset)
            .options(
                joinedload(MaternityAsset.patient),
            )
            .where(MaternityAsset.id == asset.id)
        )
        result = await self._async_db_session.execute(query)
        db_asset = result.scalar_one()

        # Обновляем поля, специально обрабатывая diagnoses
        for field, value in asset.__dict__.items():
            if hasattr(db_asset, field) and field not in ['id', 'created_at', 'patient_data', '_organization_data']:
                if field == 'diagnoses':
                    # Преобразуем доменные объекты диагнозов в JSON
                    from src.apps.assets_journal.mappers.maternity_asset_mappers import \
                        map_maternity_diagnosis_domain_to_dict

                    diagnoses_json = []
                    if value:
                        for diagnosis in value:
                            if hasattr(diagnosis, 'diagnosis_type'):  # Это объект MaternityDiagnosis
                                diagnoses_json.append(map_maternity_diagnosis_domain_to_dict(diagnosis))
                            elif isinstance(diagnosis, dict):  # Это уже словарь
                                diagnoses_json.append(diagnosis)

                    setattr(db_asset, field, diagnoses_json)
                else:
                    setattr(db_asset, field, value)

        await self._async_db_session.flush()
        await self._async_db_session.refresh(db_asset)

        return map_maternity_asset_db_to_domain(db_asset)

    async def delete(self, asset_id: UUID) -> None:
        query = select(MaternityAsset).where(MaternityAsset.id == asset_id)
        result = await self._async_db_session.execute(query)
        asset = result.scalar_one()

        await self._async_db_session.delete(asset)
        await self._async_db_session.flush()

    async def bulk_create(self, assets: List[MaternityAssetDomain]) -> List[MaternityAssetDomain]:
        db_assets = [map_maternity_asset_domain_to_db(asset) for asset in assets]

        self._async_db_session.add_all(db_assets)
        await self._async_db_session.flush()

        # Получаем созданные активы со связанными данными
        asset_ids = [db_asset.id for db_asset in db_assets]
        query = (
            select(MaternityAsset)
            .options(
                joinedload(MaternityAsset.patient),
            )
            .where(MaternityAsset.id.in_(asset_ids))
        )
        result = await self._async_db_session.execute(query)
        created_assets = result.scalars().all()

        return [map_maternity_asset_db_to_domain(db_asset) for db_asset in created_assets]

    async def exists_by_bg_asset_id(self, bg_asset_id: str) -> bool:
        query = select(func.count(MaternityAsset.id)).where(
            MaternityAsset.bg_asset_id == bg_asset_id
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
            query = query.where(MaternityAsset.patient_id == filters["patient_id"])

        # ИИН пациента
        if filters.get("patient_iin"):
            query = query.join(SQLAlchemyPatient).where(SQLAlchemyPatient.iin == filters["patient_iin"])

        # Фильтр по организации через attachment_data пациента
        if filters.get("organization_id"):
            query = query.join(SQLAlchemyPatient).where(
                SQLAlchemyPatient.attachment_data['attached_clinic_id'].cast(Integer) == filters["organization_id"]
            )

        # Период по дате регистрации
        if filters.get("date_from"):
            query = query.where(MaternityAsset.reg_date >= filters["date_from"])

        if filters.get("date_to"):
            query = query.where(MaternityAsset.reg_date <= filters["date_to"])

        # Статусы
        if filters.get("status") is not None:
            query = query.where(MaternityAsset.status == filters["status"])

        if filters.get("delivery_status") is not None:
            query = query.where(MaternityAsset.delivery_status == filters["delivery_status"])

        # Медицинские данные
        if filters.get("stay_outcome"):
            query = query.where(MaternityAsset.stay_outcome == filters["stay_outcome"])

        if filters.get("admission_type"):
            query = query.where(MaternityAsset.admission_type == filters["admission_type"])

        if filters.get("stay_type"):
            query = query.where(MaternityAsset.stay_type == filters["stay_type"])

        if filters.get("patient_status"):
            query = query.where(MaternityAsset.patient_status == filters["patient_status"])

        # Участок и специализация
        if filters.get("area"):
            query = query.where(
                func.lower(MaternityAsset.area).like(
                    f"%{filters['area'].lower()}%"
                )
            )

        if filters.get("specialization"):
            query = query.where(
                func.lower(MaternityAsset.specialization).like(
                    f"%{filters['specialization'].lower()}%"
                )
            )

        if filters.get("specialist"):
            query = query.where(
                func.lower(MaternityAsset.specialist).like(
                    f"%{filters['specialist'].lower()}%"
                )
            )

        # Поиск по диагнозу
        if filters.get("diagnosis_code"):
            diagnosis_search = f"%{filters['diagnosis_code']}%"
            query = query.where(
                func.lower(MaternityAsset.diagnoses.astext).like(diagnosis_search.lower())
            )

        # Флаги
        if filters.get("has_confirm") is not None:
            query = query.where(MaternityAsset.has_confirm == filters["has_confirm"])

        if filters.get("has_files") is not None:
            query = query.where(MaternityAsset.has_files == filters["has_files"])

        if filters.get("has_refusal") is not None:
            query = query.where(MaternityAsset.has_refusal == filters["has_refusal"])

        # Дополнительные поля
        if filters.get("bg_asset_id"):
            query = query.where(MaternityAsset.bg_asset_id == filters["bg_asset_id"])

        return query