from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import func, or_, select, case, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.apps.assets_journal.domain.models.polyclinic_asset import PolyclinicAssetDomain
from src.apps.assets_journal.domain.enums import (
    PolyclinicVisitTypeEnum,
    PolyclinicServiceTypeEnum,
    PolyclinicOutcomeEnum,
)
from src.apps.assets_journal.infrastructure.api.schemas.responses.polyclinic_asset_schemas import (
    PolyclinicAssetStatisticsSchema,
)
from src.apps.assets_journal.infrastructure.db_models.polyclinic_models import PolyclinicAsset
from src.apps.assets_journal.interfaces.polyclinic_repository_interfaces import (
    PolyclinicAssetRepositoryInterface,
)
from src.apps.assets_journal.mappers.polyclinic_asset_mappers import (
    map_polyclinic_asset_db_to_domain,
    map_polyclinic_asset_domain_to_db,
)
from src.apps.patients.infrastructure.db_models.patients import SQLAlchemyPatient
from src.core.logger import LoggerService
from src.shared.infrastructure.base import BaseRepository


class PolyclinicAssetRepositoryImpl(BaseRepository, PolyclinicAssetRepositoryInterface):
    """Реализация репозитория активов поликлиники"""

    def __init__(self, async_db_session: AsyncSession, logger: LoggerService):
        super().__init__(async_db_session, logger)

    async def get_by_id(self, asset_id: UUID) -> Optional[PolyclinicAssetDomain]:
        query = (
            select(PolyclinicAsset)
            .options(
                joinedload(PolyclinicAsset.patient),
            )
            .where(PolyclinicAsset.id == asset_id)
        )
        result = await self._async_db_session.execute(query)
        asset = result.scalar_one_or_none()

        if asset:
            return map_polyclinic_asset_db_to_domain(asset)
        return None

    async def get_by_bg_asset_id(self, bg_asset_id: str) -> Optional[PolyclinicAssetDomain]:
        query = (
            select(PolyclinicAsset)
            .options(
                joinedload(PolyclinicAsset.patient),
            )
            .where(PolyclinicAsset.bg_asset_id == bg_asset_id)
        )
        result = await self._async_db_session.execute(query)
        asset = result.scalar_one_or_none()

        if asset:
            return map_polyclinic_asset_db_to_domain(asset)
        return None

    async def get_assets(
            self,
            filters: Dict[str, any],
            page: int = 1,
            limit: int = 30,
    ) -> List[PolyclinicAssetDomain]:
        query = (
            select(PolyclinicAsset)
            .options(
                joinedload(PolyclinicAsset.patient),
            )
        )

        # Применяем фильтры
        query = self._apply_filters(query, filters)

        # Сортировка по дате регистрации (сначала новые)
        query = query.order_by(PolyclinicAsset.reg_date.desc())

        # Пагинация
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        result = await self._async_db_session.execute(query)
        assets = result.scalars().all()

        return [map_polyclinic_asset_db_to_domain(asset) for asset in assets]

    async def get_total_count(self, filters: Dict[str, any]) -> int:
        query = select(func.count(PolyclinicAsset.id))

        # Применяем фильтры
        query = self._apply_filters(query, filters)

        result = await self._async_db_session.execute(query)
        return result.scalar_one()

    async def create(self, asset: PolyclinicAssetDomain) -> PolyclinicAssetDomain:
        db_asset = map_polyclinic_asset_domain_to_db(asset)

        self._async_db_session.add(db_asset)
        await self._async_db_session.flush()
        await self._async_db_session.refresh(db_asset)

        # Загружаем связанные данные
        query = (
            select(PolyclinicAsset)
            .options(
                joinedload(PolyclinicAsset.patient),
            )
            .where(PolyclinicAsset.id == db_asset.id)
        )
        result = await self._async_db_session.execute(query)
        db_asset_with_relations = result.scalar_one()

        return map_polyclinic_asset_db_to_domain(db_asset_with_relations)

    async def update(self, asset: PolyclinicAssetDomain) -> PolyclinicAssetDomain:
        query = (
            select(PolyclinicAsset)
            .options(
                joinedload(PolyclinicAsset.patient),
            )
            .where(PolyclinicAsset.id == asset.id)
        )
        result = await self._async_db_session.execute(query)
        db_asset = result.scalar_one()

        # Обновляем поля, специально обрабатывая weekly_schedule
        for field, value in asset.__dict__.items():
            if hasattr(db_asset, field) and field not in ['id', 'created_at', 'patient_data', '_organization_data']:
                if field == 'weekly_schedule':
                    # Преобразуем доменную модель расписания в JSON
                    from src.apps.assets_journal.mappers.polyclinic_asset_mappers import \
                        map_weekly_schedule_domain_to_dict

                    schedule_json = {}
                    if value:
                        if hasattr(value, 'monday_enabled'):  # Это объект WeeklySchedule
                            schedule_json = map_weekly_schedule_domain_to_dict(value)
                        elif isinstance(value, dict):  # Это уже словарь
                            schedule_json = value

                    setattr(db_asset, field, schedule_json)
                else:
                    setattr(db_asset, field, value)

        await self._async_db_session.flush()
        await self._async_db_session.refresh(db_asset)

        return map_polyclinic_asset_db_to_domain(db_asset)

    async def delete(self, asset_id: UUID) -> None:
        query = select(PolyclinicAsset).where(PolyclinicAsset.id == asset_id)
        result = await self._async_db_session.execute(query)
        asset = result.scalar_one()

        await self._async_db_session.delete(asset)
        await self._async_db_session.flush()

    async def get_statistics(self, filters: Dict[str, any]) -> PolyclinicAssetStatisticsSchema:
        base_query = select(PolyclinicAsset)
        base_query = self._apply_filters(base_query, filters)

        # Общее количество
        total_query = select(func.count(PolyclinicAsset.id))
        total_query = self._apply_filters(total_query, filters)
        total_result = await self._async_db_session.execute(total_query)
        total_assets = total_result.scalar_one()

        # Подтвержденные
        confirmed_query = select(func.count(PolyclinicAsset.id)).where(
            PolyclinicAsset.has_confirm == True
        )
        confirmed_query = self._apply_filters(confirmed_query, filters)
        confirmed_result = await self._async_db_session.execute(confirmed_query)
        confirmed_assets = confirmed_result.scalar_one()

        # Отказанные
        refused_query = select(func.count(PolyclinicAsset.id)).where(
            PolyclinicAsset.has_refusal == True
        )
        refused_query = self._apply_filters(refused_query, filters)
        refused_result = await self._async_db_session.execute(refused_query)
        refused_assets = refused_result.scalar_one()

        # Ожидающие
        pending_assets = total_assets - confirmed_assets - refused_assets

        # С файлами
        files_query = select(func.count(PolyclinicAsset.id)).where(
            PolyclinicAsset.has_files == True
        )
        files_query = self._apply_filters(files_query, filters)
        files_result = await self._async_db_session.execute(files_query)
        assets_with_files = files_result.scalar_one()

        # Статистика по типу посещения
        visit_type_stats_query = select(
            func.count(case((PolyclinicAsset.visit_type == PolyclinicVisitTypeEnum.FIRST_VISIT, 1))).label('first_visit'),
            func.count(case((PolyclinicAsset.visit_type == PolyclinicVisitTypeEnum.REPEAT_VISIT, 1))).label('repeat_visit'),
        )
        visit_type_stats_query = self._apply_filters(visit_type_stats_query, filters)
        visit_type_result = await self._async_db_session.execute(visit_type_stats_query)
        visit_type_stats = visit_type_result.first()

        # Статистика по типу услуги
        service_type_stats_query = select(
            func.count(case((PolyclinicAsset.service == PolyclinicServiceTypeEnum.CONSULTATION, 1))).label('consultation'),
            func.count(case((PolyclinicAsset.service == PolyclinicServiceTypeEnum.PROCEDURE, 1))).label('procedure'),
            func.count(case((PolyclinicAsset.service == PolyclinicServiceTypeEnum.DIAGNOSTIC, 1))).label('diagnostic'),
            func.count(case((PolyclinicAsset.service == PolyclinicServiceTypeEnum.VACCINATION, 1))).label('vaccination'),
            func.count(case((PolyclinicAsset.service == PolyclinicServiceTypeEnum.LABORATORY, 1))).label('laboratory'),
        )
        service_type_stats_query = self._apply_filters(service_type_stats_query, filters)
        service_type_result = await self._async_db_session.execute(service_type_stats_query)
        service_type_stats = service_type_result.first()

        # Статистика по исходу посещения
        outcome_stats_query = select(
            func.count(case((PolyclinicAsset.visit_outcome == PolyclinicOutcomeEnum.RECOVERED, 1))).label('recovered'),
            func.count(case((PolyclinicAsset.visit_outcome == PolyclinicOutcomeEnum.IMPROVED, 1))).label('improved'),
            func.count(case((PolyclinicAsset.visit_outcome == PolyclinicOutcomeEnum.WITHOUT_CHANGES, 1))).label('without_changes'),
            func.count(case((PolyclinicAsset.visit_outcome == PolyclinicOutcomeEnum.WORSENED, 1))).label('worsened'),
            func.count(case((PolyclinicAsset.visit_outcome == PolyclinicOutcomeEnum.REFERRED, 1))).label('referred'),
            func.count(case((PolyclinicAsset.visit_outcome == PolyclinicOutcomeEnum.HOSPITALIZED, 1))).label('hospitalized'),
        )
        outcome_stats_query = self._apply_filters(outcome_stats_query, filters)
        outcome_result = await self._async_db_session.execute(outcome_stats_query)
        outcome_stats = outcome_result.first()

        return PolyclinicAssetStatisticsSchema(
            total_assets=total_assets,
            confirmed_assets=confirmed_assets,
            refused_assets=refused_assets,
            pending_assets=pending_assets,
            assets_with_files=assets_with_files,
            first_visit_count=visit_type_stats.first_visit or 0,
            repeat_visit_count=visit_type_stats.repeat_visit or 0,
            consultation_count=service_type_stats.consultation or 0,
            procedure_count=service_type_stats.procedure or 0,
            diagnostic_count=service_type_stats.diagnostic or 0,
            vaccination_count=service_type_stats.vaccination or 0,
            laboratory_count=service_type_stats.laboratory or 0,
            recovered_count=outcome_stats.recovered or 0,
            improved_count=outcome_stats.improved or 0,
            without_changes_count=outcome_stats.without_changes or 0,
            worsened_count=outcome_stats.worsened or 0,
            referred_count=outcome_stats.referred or 0,
            hospitalized_count=outcome_stats.hospitalized or 0,
        )

    async def bulk_create(self, assets: List[PolyclinicAssetDomain]) -> List[PolyclinicAssetDomain]:
        db_assets = [map_polyclinic_asset_domain_to_db(asset) for asset in assets]

        self._async_db_session.add_all(db_assets)
        await self._async_db_session.flush()

        # Получаем созданные активы со связанными данными
        asset_ids = [db_asset.id for db_asset in db_assets]
        query = (
            select(PolyclinicAsset)
            .options(
                joinedload(PolyclinicAsset.patient),
            )
            .where(PolyclinicAsset.id.in_(asset_ids))
        )
        result = await self._async_db_session.execute(query)
        created_assets = result.scalars().all()

        return [map_polyclinic_asset_db_to_domain(db_asset) for db_asset in created_assets]

    async def exists_by_bg_asset_id(self, bg_asset_id: str) -> bool:
        query = select(func.count(PolyclinicAsset.id)).where(
            PolyclinicAsset.bg_asset_id == bg_asset_id
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
            query = query.where(PolyclinicAsset.patient_id == filters["patient_id"])

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
            query = query.where(PolyclinicAsset.reg_date >= filters["date_from"])

        if filters.get("date_to"):
            query = query.where(PolyclinicAsset.reg_date <= filters["date_to"])

        # Статусы
        if filters.get("status") is not None:
            query = query.where(PolyclinicAsset.status == filters["status"])

        if filters.get("delivery_status") is not None:
            query = query.where(PolyclinicAsset.delivery_status == filters["delivery_status"])

        # Медицинские данные
        if filters.get("visit_type") is not None:
            query = query.where(PolyclinicAsset.visit_type == filters["visit_type"])

        if filters.get("visit_outcome") is not None:
            query = query.where(PolyclinicAsset.visit_outcome == filters["visit_outcome"])

        # Участок и специализация
        if filters.get("area"):
            query = query.where(
                func.lower(PolyclinicAsset.area).like(
                    f"%{filters['area'].lower()}%"
                )
            )

        if filters.get("specialization"):
            query = query.where(
                func.lower(PolyclinicAsset.specialization).like(
                    f"%{filters['specialization'].lower()}%"
                )
            )

        if filters.get("specialist"):
            query = query.where(
                func.lower(PolyclinicAsset.specialist).like(
                    f"%{filters['specialist'].lower()}%"
                )
            )

        # Флаги
        if filters.get("has_confirm") is not None:
            query = query.where(PolyclinicAsset.has_confirm == filters["has_confirm"])

        if filters.get("has_files") is not None:
            query = query.where(PolyclinicAsset.has_files == filters["has_files"])

        if filters.get("has_refusal") is not None:
            query = query.where(PolyclinicAsset.has_refusal == filters["has_refusal"])

        # Дополнительные поля
        if filters.get("bg_asset_id"):
            query = query.where(PolyclinicAsset.bg_asset_id == filters["bg_asset_id"])

        if filters.get("service"):
            query = query.where(
                func.lower(PolyclinicAsset.service).like(
                    f"%{filters['service'].lower()}%"
                )
            )

        if filters.get("reason_appeal"):
            query = query.where(
                func.lower(PolyclinicAsset.reason_appeal).like(
                    f"%{filters['reason_appeal'].lower()}%"
                )
            )

        if filters.get("type_active_visit"):
            query = query.where(
                func.lower(PolyclinicAsset.type_active_visit).like(
                    f"%{filters['type_active_visit'].lower()}%"
                )
            )

        # Планирование активов
        if filters.get("schedule_enabled") is not None:
            query = query.where(PolyclinicAsset.schedule_enabled == filters["schedule_enabled"])

        return query