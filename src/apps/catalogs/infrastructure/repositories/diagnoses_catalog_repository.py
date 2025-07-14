from typing import List, Optional

from sqlalchemy import delete, func, or_, select

from src.apps.catalogs.infrastructure.api.schemas.requests.diagnoses_catalog_request_schemas import (
    AddDiagnosisRequestSchema,
    UpdateDiagnosisRequestSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.diagnoses_catalog_response_schemas import (
    DiagnosesCatalogResponseSchema,
)
from src.apps.catalogs.infrastructure.db_models.diagnoses_catalogue import (
    SQLAlchemyDiagnosesCatalogue,
)
from src.apps.catalogs.interfaces.diagnoses_catalogue_repository_interface import (
    DiagnosesCatalogRepositoryInterface,
)
from src.apps.catalogs.mappers import (
    map_diagnosis_catalog_create_schema_to_db_entity,
    map_diagnosis_catalog_db_entity_to_response_schema,
)
from src.shared.infrastructure.base import BaseRepository


class SQLAlchemyDiagnosesCatalogRepositoryImpl(
    BaseRepository, DiagnosesCatalogRepositoryInterface
):
    @staticmethod
    def _apply_filters_to_query(diagnosis_code_filter: str, query):
        diagnosis_code_filter = diagnosis_code_filter.lower()
        filters = [
            func.lower(SQLAlchemyDiagnosesCatalogue.diagnosis_code)
            == diagnosis_code_filter
        ]
        query = query.where(or_(*filters))

        return query

    async def get_total_number_of_diagnoses(self) -> int:
        query = select(func.count(SQLAlchemyDiagnosesCatalogue.id))
        result = await self._async_db_session.execute(query)

        return result.scalar_one()

    async def get_by_id(
        self, diagnosis_id: int
    ) -> Optional[DiagnosesCatalogResponseSchema]:
        query = select(SQLAlchemyDiagnosesCatalogue).where(
            SQLAlchemyDiagnosesCatalogue.id == diagnosis_id
        )
        result = await self._async_db_session.execute(query)
        obj = result.scalar_one_or_none()
        if obj:
            return map_diagnosis_catalog_db_entity_to_response_schema(obj)

        return None

    async def get_by_code(
        self, diagnosis_code: str
    ) -> Optional[DiagnosesCatalogResponseSchema]:
        query = select(SQLAlchemyDiagnosesCatalogue).where(
            func.lower(SQLAlchemyDiagnosesCatalogue.diagnosis_code)
            == diagnosis_code.lower()
        )
        result = await self._async_db_session.execute(query)
        obj = result.scalar_one_or_none()
        if obj:
            return map_diagnosis_catalog_db_entity_to_response_schema(obj)

        return None

    async def get_diagnoses(
        self,
        diagnosis_code_filter: Optional[str],
        page: int = 1,
        limit: int = 30,
    ) -> List[DiagnosesCatalogResponseSchema]:
        offset = (page - 1) * limit
        query = select(SQLAlchemyDiagnosesCatalogue)

        # Filtering...
        if diagnosis_code_filter:
            query = self._apply_filters_to_query(
                diagnosis_code_filter=diagnosis_code_filter, query=query
            )

        query = query.offset(offset).limit(limit)

        result = await self._async_db_session.execute(query)
        records = result.scalars().all()

        return [
            map_diagnosis_catalog_db_entity_to_response_schema(obj) for obj in records
        ]

    async def add_diagnosis(
        self, request_dto: AddDiagnosisRequestSchema
    ) -> DiagnosesCatalogResponseSchema:
        obj: SQLAlchemyDiagnosesCatalogue = (
            map_diagnosis_catalog_create_schema_to_db_entity(request_dto)
        )
        self._async_db_session.add(obj)

        await self._async_db_session.flush()
        await self._async_db_session.refresh(obj)
        await self._async_db_session.commit()

        return map_diagnosis_catalog_db_entity_to_response_schema(obj)

    async def update_diagnosis(
        self, diagnosis_id: int, request_dto: UpdateDiagnosisRequestSchema
    ) -> DiagnosesCatalogResponseSchema:
        query = select(SQLAlchemyDiagnosesCatalogue).where(
            SQLAlchemyDiagnosesCatalogue.id == diagnosis_id
        )
        result = await self._async_db_session.execute(query)
        obj = result.scalar_one_or_none()

        # Updating fields...
        update_data = request_dto.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(obj, key, value)

        await self._async_db_session.flush()
        await self._async_db_session.refresh(obj)
        await self._async_db_session.commit()

        return map_diagnosis_catalog_db_entity_to_response_schema(obj)

    async def delete_by_id(self, diagnosis_id: int) -> None:
        query = delete(SQLAlchemyDiagnosesCatalogue).where(
            SQLAlchemyDiagnosesCatalogue.id == diagnosis_id
        )
        await self._async_db_session.execute(query)
        await self._async_db_session.commit()
