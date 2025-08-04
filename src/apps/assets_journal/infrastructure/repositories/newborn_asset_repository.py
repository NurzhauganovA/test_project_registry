from typing import Dict, List, Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import func, or_, select, case, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.apps.assets_journal.domain.models.newborn_asset import NewbornAssetDomain
from src.apps.assets_journal.domain.enums import NewbornConditionEnum, DeliveryTypeEnum
from src.apps.assets_journal.infrastructure.api.schemas.responses.newborn_asset_schemas import (
    NewbornAssetStatisticsSchema,
)
from src.apps.assets_journal.infrastructure.db_models.newborn_models import NewbornAsset
from src.apps.assets_journal.interfaces.newborn_repository_interfaces import (
    NewbornAssetRepositoryInterface,
)
from src.apps.assets_journal.mappers.newborn_asset_mappers import (
    map_newborn_asset_db_to_domain,
    map_newborn_asset_domain_to_db,
)
from src.apps.patients.infrastructure.db_models.patients import SQLAlchemyPatient
from src.core.logger import LoggerService
from src.shared.infrastructure.base import BaseRepository


class NewbornAssetRepositoryImpl(BaseRepository, NewbornAssetRepositoryInterface):
    """Реализация репозитория активов новорожденных"""

    def __init__(self, async_db_session: AsyncSession, logger: LoggerService):
        super().__init__(async_db_session, logger)

    async def get_by_id(self, asset_id: UUID) -> Optional[NewbornAssetDomain]:
        query = (
            select(NewbornAsset)
            .options(
                joinedload(NewbornAsset.patient),
            )
            .where(NewbornAsset.id == asset_id)
        )
        result = await self._async_db_session.execute(query)
        asset = result.scalar_one_or_none()

        if asset:
            return map_newborn_asset_db_to_domain(asset)
        return None

    async def get_by_bg_asset_id(self, bg_asset_id: str) -> Optional[NewbornAssetDomain]:
        query = (
            select(NewbornAsset)
            .options(
                joinedload(NewbornAsset.patient),
            )
            .where(NewbornAsset.bg_asset_id == bg_asset_id)
        )
        result = await self._async_db_session.execute(query)
        asset = result.scalar_one_or_none()

        if asset:
            return map_newborn_asset_db_to_domain(asset)
        return None

    async def get_assets(
            self,
            filters: Dict[str, any],
            page: int = 1,
            limit: int = 30,
    ) -> List[NewbornAssetDomain]:
        query = (
            select(NewbornAsset)
            .options(
                joinedload(NewbornAsset.patient),
            )
        )

        # Применяем фильтры
        query = self._apply_filters(query, filters)

        # Сортировка по дате регистрации (сначала новые)
        query = query.order_by(NewbornAsset.reg_date.desc())

        # Пагинация
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        result = await self._async_db_session.execute(query)
        assets = result.scalars().all()

        return [map_newborn_asset_db_to_domain(asset) for asset in assets]

    async def get_total_count(self, filters: Dict[str, any]) -> int:
        query = select(func.count(NewbornAsset.id))

        # Применяем фильтры
        query = self._apply_filters(query, filters)

        result = await self._async_db_session.execute(query)
        return result.scalar_one()

    async def create(self, asset: NewbornAssetDomain) -> NewbornAssetDomain:
        db_asset = map_newborn_asset_domain_to_db(asset)

        self._async_db_session.add(db_asset)
        await self._async_db_session.flush()
        await self._async_db_session.refresh(db_asset)

        # Загружаем связанные данные
        query = (
            select(NewbornAsset)
            .options(
                joinedload(NewbornAsset.patient),
            )
            .where(NewbornAsset.id == db_asset.id)
        )
        result = await self._async_db_session.execute(query)
        db_asset_with_relations = result.scalar_one()

        return map_newborn_asset_db_to_domain(db_asset_with_relations)

    async def update(self, asset: NewbornAssetDomain) -> NewbornAssetDomain:
        query = (
            select(NewbornAsset)
            .options(
                joinedload(NewbornAsset.patient),
            )
            .where(NewbornAsset.id == asset.id)
        )
        result = await self._async_db_session.execute(query)
        db_asset = result.scalar_one()

        # Обновляем поля, но специально обрабатываем diagnoses, mother_data, newborn_data
        for field, value in asset.__dict__.items():
            if hasattr(db_asset, field) and field not in ['id', 'created_at', 'patient_data', '_organization_data']:
                if field == 'diagnoses':
                    # Преобразуем доменные объекты диагнозов в JSON
                    from src.apps.assets_journal.mappers.newborn_asset_mappers import \
                        map_newborn_diagnosis_domain_to_dict

                    diagnoses_json = []
                    if value:
                        for diagnosis in value:
                            if hasattr(diagnosis, 'diagnosis_type'):  # Это объект NewbornDiagnosis
                                diagnoses_json.append(map_newborn_diagnosis_domain_to_dict(diagnosis))
                            elif isinstance(diagnosis, dict):  # Это уже словарь
                                diagnoses_json.append(diagnosis)

                    setattr(db_asset, field, diagnoses_json)
                elif field == 'mother_data':
                    # Преобразуем данные матери в JSON
                    from src.apps.assets_journal.mappers.newborn_asset_mappers import map_mother_data_domain_to_dict

                    mother_data_json = {}
                    if value:
                        if hasattr(value, 'iin'):  # Это объект MotherData
                            mother_data_json = map_mother_data_domain_to_dict(value)
                        elif isinstance(value, dict):  # Это уже словарь
                            mother_data_json = value

                    setattr(db_asset, field, mother_data_json)
                elif field == 'newborn_data':
                    # Преобразуем данные новорожденного в JSON
                    from src.apps.assets_journal.mappers.newborn_asset_mappers import map_newborn_data_domain_to_dict

                    newborn_data_json = {}
                    if value:
                        if hasattr(value, 'birth_date'):  # Это объект NewbornData
                            newborn_data_json = map_newborn_data_domain_to_dict(value)
                        elif isinstance(value, dict):  # Это уже словарь
                            newborn_data_json = value

                    setattr(db_asset, field, newborn_data_json)
                else:
                    setattr(db_asset, field, value)

        await self._async_db_session.flush()
        await self._async_db_session.refresh(db_asset)

        return map_newborn_asset_db_to_domain(db_asset)

    async def delete(self, asset_id: UUID) -> None:
        query = select(NewbornAsset).where(NewbornAsset.id == asset_id)
        result = await self._async_db_session.execute(query)
        asset = result.scalar_one()

        await self._async_db_session.delete(asset)
        await self._async_db_session.flush()

    async def get_statistics(self, filters: Dict[str, any]) -> NewbornAssetStatisticsSchema:
        base_query = select(NewbornAsset)
        base_query = self._apply_filters(base_query, filters)

        # Общее количество
        total_query = select(func.count(NewbornAsset.id))
        total_query = self._apply_filters(total_query, filters)
        total_result = await self._async_db_session.execute(total_query)
        total_assets = total_result.scalar_one()

        # Подтвержденные
        confirmed_query = select(func.count(NewbornAsset.id)).where(
            NewbornAsset.has_confirm == True
        )
        confirmed_query = self._apply_filters(confirmed_query, filters)
        confirmed_result = await self._async_db_session.execute(confirmed_query)
        confirmed_assets = confirmed_result.scalar_one()

        # Отказанные
        refused_query = select(func.count(NewbornAsset.id)).where(
            NewbornAsset.has_refusal == True
        )
        refused_query = self._apply_filters(refused_query, filters)
        refused_result = await self._async_db_session.execute(refused_query)
        refused_assets = refused_result.scalar_one()

        # Ожидающие
        pending_assets = total_assets - confirmed_assets - refused_assets

        # С файлами
        files_query = select(func.count(NewbornAsset.id)).where(
            NewbornAsset.has_files == True
        )
        files_query = self._apply_filters(files_query, filters)
        files_result = await self._async_db_session.execute(files_query)
        assets_with_files = files_result.scalar_one()

        # Статистика по состоянию новорожденных
        condition_stats_query = select(
            func.count(case((
                func.json_extract_path_text(NewbornAsset.newborn_data, 'condition') == NewbornConditionEnum.EXCELLENT.value, 1
            ))).label('excellent'),
            func.count(case((
                func.json_extract_path_text(NewbornAsset.newborn_data, 'condition') == NewbornConditionEnum.GOOD.value, 1
            ))).label('good'),
            func.count(case((
                func.json_extract_path_text(NewbornAsset.newborn_data, 'condition') == NewbornConditionEnum.SATISFACTORY.value, 1
            ))).label('satisfactory'),
            func.count(case((
                func.json_extract_path_text(NewbornAsset.newborn_data, 'condition') == NewbornConditionEnum.SEVERE.value, 1
            ))).label('severe'),
            func.count(case((
                func.json_extract_path_text(NewbornAsset.newborn_data, 'condition') == NewbornConditionEnum.CRITICAL.value, 1
            ))).label('critical'),
        )
        condition_stats_query = self._apply_filters(condition_stats_query, filters)
        condition_result = await self._async_db_session.execute(condition_stats_query)
        condition_stats = condition_result.first()

        # Статистика по типу родов
        delivery_stats_query = select(
            func.count(case((
                func.json_extract_path_text(NewbornAsset.mother_data, 'delivery_type') == DeliveryTypeEnum.NATURAL.value, 1
            ))).label('natural'),
            func.count(case((
                func.json_extract_path_text(NewbornAsset.mother_data, 'delivery_type') == DeliveryTypeEnum.CESAREAN.value, 1
            ))).label('cesarean'),
            func.count(case((
                func.json_extract_path_text(NewbornAsset.mother_data, 'delivery_type') == DeliveryTypeEnum.FORCEPS.value, 1
            ))).label('forceps'),
            func.count(case((
                func.json_extract_path_text(NewbornAsset.mother_data, 'delivery_type') == DeliveryTypeEnum.VACUUM.value, 1
            ))).label('vacuum'),
        )
        delivery_stats_query = self._apply_filters(delivery_stats_query, filters)
        delivery_result = await self._async_db_session.execute(delivery_stats_query)
        delivery_stats = delivery_result.first()

        return NewbornAssetStatisticsSchema(
            total_assets=total_assets,
            confirmed_assets=confirmed_assets,
            refused_assets=refused_assets,
            pending_assets=pending_assets,
            assets_with_files=assets_with_files,
            excellent_condition_count=condition_stats.excellent or 0,
            good_condition_count=condition_stats.good or 0,
            satisfactory_condition_count=condition_stats.satisfactory or 0,
            severe_condition_count=condition_stats.severe or 0,
            critical_condition_count=condition_stats.critical or 0,
            natural_delivery_count=delivery_stats.natural or 0,
            cesarean_delivery_count=delivery_stats.cesarean or 0,
            forceps_delivery_count=delivery_stats.forceps or 0,
            vacuum_delivery_count=delivery_stats.vacuum or 0,
        )

    async def bulk_create(self, assets: List[NewbornAssetDomain]) -> List[NewbornAssetDomain]:
        db_assets = [map_newborn_asset_domain_to_db(asset) for asset in assets]

        self._async_db_session.add_all(db_assets)
        await self._async_db_session.flush()

        # Получаем созданные активы со связанными данными
        asset_ids = [db_asset.id for db_asset in db_assets]
        query = (
            select(NewbornAsset)
            .options(
                joinedload(NewbornAsset.patient),
            )
            .where(NewbornAsset.id.in_(asset_ids))
        )
        result = await self._async_db_session.execute(query)
        created_assets = result.scalars().all()

        return [map_newborn_asset_db_to_domain(db_asset) for db_asset in created_assets]

    async def exists_by_bg_asset_id(self, bg_asset_id: str) -> bool:
        query = select(func.count(NewbornAsset.id)).where(
            NewbornAsset.bg_asset_id == bg_asset_id
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
                    SQLAlchemyPatient.iin.like(search_term),
                    func.lower(NewbornAsset.patient_full_name_if_not_registered).like(search_term.lower())
                )
            )

        # Поиск по матери
        if filters.get("mother_search"):
            search_term = f"%{filters['mother_search']}%"
            query = query.where(
                func.lower(func.json_extract_path_text(NewbornAsset.mother_data, 'full_name')).like(search_term.lower())
            )

        # ИИН матери
        if filters.get("mother_iin"):
            query = query.where(
                func.json_extract_path_text(NewbornAsset.mother_data, 'iin') == filters["mother_iin"]
            )

        # Конкретный пациент
        if filters.get("patient_id"):
            query = query.where(NewbornAsset.patient_id == filters["patient_id"])

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
            query = query.where(NewbornAsset.reg_date >= filters["date_from"])

        if filters.get("date_to"):
            query = query.where(NewbornAsset.reg_date <= filters["date_to"])

        # Статусы
        if filters.get("status") is not None:
            query = query.where(NewbornAsset.status == filters["status"])

        if filters.get("delivery_status") is not None:
            query = query.where(NewbornAsset.delivery_status == filters["delivery_status"])

        # Состояние новорожденного
        if filters.get("newborn_condition") is not None:
            query = query.where(
                func.json_extract_path_text(NewbornAsset.newborn_data, 'condition') == filters["newborn_condition"].value
            )

        # Тип родов
        if filters.get("delivery_type") is not None:
            query = query.where(
                func.json_extract_path_text(NewbornAsset.mother_data, 'delivery_type') == filters["delivery_type"].value
            )

        # Поиск по диагнозу
        if filters.get("diagnosis_code"):
            diagnosis_search = f"%{filters['diagnosis_code']}%"
            query = query.where(
                func.lower(NewbornAsset.diagnoses.astext).like(diagnosis_search.lower())
            )

        # Флаги
        if filters.get("has_confirm") is not None:
            query = query.where(NewbornAsset.has_confirm == filters["has_confirm"])

        if filters.get("has_files") is not None:
            query = query.where(NewbornAsset.has_files == filters["has_files"])

        if filters.get("has_refusal") is not None:
            query = query.where(NewbornAsset.has_refusal == filters["has_refusal"])

        # Дополнительные поля
        if filters.get("bg_asset_id"):
            query = query.where(NewbornAsset.bg_asset_id == filters["bg_asset_id"])

        return query