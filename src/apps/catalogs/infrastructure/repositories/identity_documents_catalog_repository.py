from datetime import date
from typing import Any, Dict, List, Optional

from sqlalchemy import delete, func, or_, select

from src.apps.catalogs.infrastructure.api.schemas.requests.identity_documents_catalog_request_schemas import (
    AddIdentityDocumentRequestSchema,
    UpdateIdentityDocumentRequestSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.identity_documents_catalog_response_schemas import (
    IdentityDocumentResponseSchema,
)
from src.apps.catalogs.infrastructure.db_models.identity_documents_catalogue import (
    SQLAlchemyIdentityDocumentsCatalogue,
)
from src.apps.catalogs.interfaces.identity_documents_repository_interface import (
    IdentityDocumentsCatalogRepositoryInterface,
)
from src.apps.catalogs.mappers import (
    map_identity_document_create_schema_to_db_entity,
    map_identity_document_db_entity_to_response_schema,
    map_identity_document_update_schema_to_db_entity,
)
from src.shared.helpers.decorators import handle_unique_violation, transactional
from src.shared.infrastructure.base import BaseRepository


class SQLAlchemyIdentityDocumentsCatalogRepositoryImpl(
    BaseRepository, IdentityDocumentsCatalogRepositoryInterface
):
    @staticmethod
    def _apply_filters_to_query(filters: Dict[str, Any], query):
        patient_id = filters.get("patient_id")
        if patient_id:
            query = query.where(
                SQLAlchemyIdentityDocumentsCatalogue.patient_id == patient_id
            )

        doc_type = filters.get("type")
        if doc_type:
            query = query.where(SQLAlchemyIdentityDocumentsCatalogue.type == doc_type)

        series = filters.get("series")
        if series:
            query = query.where(SQLAlchemyIdentityDocumentsCatalogue.series == series)

        number = filters.get("number")
        if number:
            query = query.where(SQLAlchemyIdentityDocumentsCatalogue.number == number)

        # Filter by document validity (active if expiration_date is not set or is greater than or equal to today's date)
        only_active = filters.get("only_active")
        if only_active:
            today = date.today()
            query = query.where(
                or_(
                    SQLAlchemyIdentityDocumentsCatalogue.expiration_date is None,
                    SQLAlchemyIdentityDocumentsCatalogue.expiration_date >= today,
                )
            )

        return query

    async def get_total_number_of_identity_documents(self) -> int:
        query = select(func.count(SQLAlchemyIdentityDocumentsCatalogue.id))
        result = await self._async_db_session.execute(query)

        return result.scalar_one()

    async def get_by_id(
        self, document_id: int
    ) -> Optional[IdentityDocumentResponseSchema]:
        query = select(SQLAlchemyIdentityDocumentsCatalogue).where(
            SQLAlchemyIdentityDocumentsCatalogue.id == document_id
        )
        result = await self._async_db_session.execute(query)
        obj = result.scalar_one_or_none()
        if obj:
            return map_identity_document_db_entity_to_response_schema(obj)

        return None

    async def get_identity_documents(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        limit: int = 30,
    ) -> List[IdentityDocumentResponseSchema]:
        offset = (page - 1) * limit
        query = select(SQLAlchemyIdentityDocumentsCatalogue)

        if filters:
            query = self._apply_filters_to_query(filters=filters, query=query)

        query = query.offset(offset).limit(limit)

        result = await self._async_db_session.execute(query)
        records = result.scalars().all()

        return [
            map_identity_document_db_entity_to_response_schema(obj) for obj in records
        ]

    @transactional
    @handle_unique_violation
    async def add_identity_document(
        self, request_dto: AddIdentityDocumentRequestSchema
    ) -> IdentityDocumentResponseSchema:
        obj: SQLAlchemyIdentityDocumentsCatalogue = (
            map_identity_document_create_schema_to_db_entity(request_dto)
        )
        self._async_db_session.add(obj)

        await self._async_db_session.flush()
        await self._async_db_session.refresh(obj)
        await self._async_db_session.commit()

        return map_identity_document_db_entity_to_response_schema(obj)

    @transactional
    async def update_identity_document(
        self,
        document_id: int,
        request_dto: UpdateIdentityDocumentRequestSchema,
    ) -> IdentityDocumentResponseSchema:
        query = select(SQLAlchemyIdentityDocumentsCatalogue).where(
            SQLAlchemyIdentityDocumentsCatalogue.id == document_id
        )
        result = await self._async_db_session.execute(query)
        obj = result.scalar_one_or_none()

        updated_obj = map_identity_document_update_schema_to_db_entity(
            db_entity=obj,
            update_schema=request_dto,
        )

        await self._async_db_session.flush()
        await self._async_db_session.refresh(obj)
        await self._async_db_session.commit()

        return map_identity_document_db_entity_to_response_schema(updated_obj)

    @transactional
    async def delete_by_id(self, document_id: int) -> None:
        query = delete(SQLAlchemyIdentityDocumentsCatalogue).where(
            SQLAlchemyIdentityDocumentsCatalogue.id == document_id
        )
        await self._async_db_session.execute(query)
        await self._async_db_session.commit()
