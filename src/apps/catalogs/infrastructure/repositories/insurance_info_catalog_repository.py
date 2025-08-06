from typing import List, Optional

from sqlalchemy import and_, delete, func, select

from src.apps.catalogs.infrastructure.api.schemas.requests.filters.insurance_info_catalog_filters import (
    InsuranceInfoCatalogFilterParams,
)
from src.apps.catalogs.infrastructure.api.schemas.requests.insurance_info_catalog_request_schemas import (
    AddInsuranceInfoRecordSchema,
    UpdateInsuranceInfoRecordSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.insurance_info_catalog_response_schemas import (
    ResponseInsuranceInfoRecordSchema,
)
from src.apps.catalogs.infrastructure.db_models.insurance_info_catalogue import (
    SQLAlchemyInsuranceInfoCatalogue,
)
from src.apps.catalogs.interfaces.insurance_info_catalog_repository_interface import (
    InsuranceInfoCatalogRepositoryInterface,
)
from src.apps.catalogs.mappers import (
    map_insurance_info_create_schema_to_db_entity,
    map_insurance_info_db_entity_to_response_schema,
    map_insurance_info_update_schema_to_db_entity,
)
from src.shared.helpers.decorators import handle_unique_violation, transactional
from src.shared.infrastructure.base import BaseRepository


class SQLAlchemyInsuranceInfoCatalogRepositoryImpl(
    BaseRepository, InsuranceInfoCatalogRepositoryInterface
):
    @staticmethod
    def _apply_filters_to_query(query, filters: InsuranceInfoCatalogFilterParams):
        conditions = []

        if filters.patient_id is not None:
            conditions.append(
                SQLAlchemyInsuranceInfoCatalogue.patient_id == filters.patient_id
            )

        if filters.financing_source_id is not None:
            conditions.append(
                SQLAlchemyInsuranceInfoCatalogue.financing_source_id
                == filters.financing_source_id
            )

        if filters.policy_number is not None:
            conditions.append(
                func.lower(SQLAlchemyInsuranceInfoCatalogue.policy_number)
                == filters.policy_number.lower().strip()
            )

        if filters.company is not None:
            conditions.append(
                func.lower(SQLAlchemyInsuranceInfoCatalogue.company)
                == filters.company.lower().strip()
            )

        if filters.valid_from is not None:
            conditions.append(
                SQLAlchemyInsuranceInfoCatalogue.valid_from >= filters.valid_from
            )

        if filters.valid_till is not None:
            conditions.append(
                SQLAlchemyInsuranceInfoCatalogue.valid_till <= filters.valid_till
            )

        if conditions:
            query = query.where(and_(*conditions))

        return query

    async def get_total_number_of_insurance_info_records(self) -> int:
        query = select(func.count(SQLAlchemyInsuranceInfoCatalogue.id))
        result = await self._async_db_session.execute(query)
        return result.scalar_one()

    async def get_by_id(
        self, insurance_info_record_id: int
    ) -> Optional[ResponseInsuranceInfoRecordSchema]:
        query = select(SQLAlchemyInsuranceInfoCatalogue).where(
            SQLAlchemyInsuranceInfoCatalogue.id == insurance_info_record_id
        )
        result = await self._async_db_session.execute(query)
        obj = result.scalar_one_or_none()

        if obj:
            return map_insurance_info_db_entity_to_response_schema(obj)

        return None

    async def get_insurance_info_records(
        self,
        filters: InsuranceInfoCatalogFilterParams,
        page: int = 1,
        limit: int = 30,
    ) -> List[ResponseInsuranceInfoRecordSchema]:
        offset = (page - 1) * limit
        query = select(SQLAlchemyInsuranceInfoCatalogue)

        # Filters applying...
        query = self._apply_filters_to_query(query, filters)

        query = query.offset(offset).limit(limit)
        result = await self._async_db_session.execute(query)
        records = result.scalars().all()

        return [
            map_insurance_info_db_entity_to_response_schema(record)
            for record in records
        ]

    @transactional
    @handle_unique_violation
    async def add_insurance_info_record(
        self, request_dto: AddInsuranceInfoRecordSchema
    ) -> ResponseInsuranceInfoRecordSchema:
        obj = map_insurance_info_create_schema_to_db_entity(request_dto)
        self._async_db_session.add(obj)

        await self._async_db_session.flush()
        await self._async_db_session.refresh(obj)
        await self._async_db_session.commit()

        return map_insurance_info_db_entity_to_response_schema(obj)

    @transactional
    async def update_insurance_info_record(
        self,
        insurance_info_record_id: int,
        request_dto: UpdateInsuranceInfoRecordSchema,
    ) -> ResponseInsuranceInfoRecordSchema:
        query = select(SQLAlchemyInsuranceInfoCatalogue).where(
            SQLAlchemyInsuranceInfoCatalogue.id == insurance_info_record_id
        )
        result = await self._async_db_session.execute(query)
        obj = result.scalar_one_or_none()

        obj = map_insurance_info_update_schema_to_db_entity(obj, request_dto)

        await self._async_db_session.flush()
        await self._async_db_session.refresh(obj)
        await self._async_db_session.commit()

        return map_insurance_info_db_entity_to_response_schema(obj)

    @transactional
    async def delete_by_id(self, insurance_info_record_id: int) -> None:
        query = delete(SQLAlchemyInsuranceInfoCatalogue).where(
            SQLAlchemyInsuranceInfoCatalogue.id == insurance_info_record_id
        )

        await self._async_db_session.execute(query)
        await self._async_db_session.commit()
