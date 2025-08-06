from typing import List, Optional

from sqlalchemy import delete, func, or_, select

from src.apps.catalogs.infrastructure.api.schemas.requests.patient_context_attributes_catalog_request_schemas import (
    AddPatientContextAttributeSchema,
    UpdatePatientContextAttributeSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.patient_context_attributes_catalog_response_schemas import (
    PatientContextAttributeCatalogFullResponseSchema,
)
from src.apps.catalogs.infrastructure.db_models.patient_context_attributes_catalogue import (
    SQLAlchemyPatientContextAttributesCatalogue,
)
from src.apps.catalogs.interfaces.patient_context_attributes_repository_interface import (
    PatientContextAttributesCatalogRepositoryInterface,
)
from src.core.settings import project_settings
from src.shared.helpers.decorators import handle_unique_violation, transactional
from src.shared.infrastructure.base import BaseRepository


class SQLAlchemyPatientContextAttributesCatalogueRepositoryImpl(
    BaseRepository, PatientContextAttributesCatalogRepositoryInterface
):
    async def get_by_default_name(
        self, name: str
    ) -> Optional[PatientContextAttributeCatalogFullResponseSchema]:
        stmt = select(SQLAlchemyPatientContextAttributesCatalogue).where(
            SQLAlchemyPatientContextAttributesCatalogue.lang
            == project_settings.DEFAULT_LANGUAGE,
            func.lower(SQLAlchemyPatientContextAttributesCatalogue.name)
            == name.lower(),
        )
        result = await self._async_db_session.execute(stmt)
        obj = result.scalar_one_or_none()
        if not obj:
            return None

        return PatientContextAttributeCatalogFullResponseSchema.model_validate(obj)

    async def get_by_locale(
        self, locale: str, name: str
    ) -> Optional[PatientContextAttributeCatalogFullResponseSchema]:
        stmt = select(SQLAlchemyPatientContextAttributesCatalogue).where(
            func.lower(
                SQLAlchemyPatientContextAttributesCatalogue.name_locales[locale].astext
            )
            == name.lower()
        )
        result = await self._async_db_session.execute(stmt)
        obj = result.scalar_one_or_none()
        if not obj:
            return None

        return PatientContextAttributeCatalogFullResponseSchema.model_validate(obj)

    async def get_total_number_of_patient_context_attributes(self) -> int:
        query = select(func.count(SQLAlchemyPatientContextAttributesCatalogue.id))
        result = await self._async_db_session.execute(query)

        return result.scalar_one()

    async def get_by_id(
        self, context_attribute_id: int
    ) -> Optional[PatientContextAttributeCatalogFullResponseSchema]:
        query = select(SQLAlchemyPatientContextAttributesCatalogue).where(
            SQLAlchemyPatientContextAttributesCatalogue.id == context_attribute_id
        )
        result = await self._async_db_session.execute(query)
        obj = result.scalar_one_or_none()
        if obj:
            return PatientContextAttributeCatalogFullResponseSchema.model_validate(obj)

        return None

    async def get_patient_context_attributes(
        self,
        name_filter: Optional[str],
        page: int = 1,
        limit: int = 30,
    ) -> List[PatientContextAttributeCatalogFullResponseSchema]:
        offset = (page - 1) * limit

        query = select(SQLAlchemyPatientContextAttributesCatalogue)

        # Filtering...
        if name_filter:
            name_filter = name_filter.lower()
            filters = [
                func.lower(SQLAlchemyPatientContextAttributesCatalogue.name)
                == name_filter
            ]
            for language in project_settings.LANGUAGES:
                filters.append(
                    func.lower(
                        SQLAlchemyPatientContextAttributesCatalogue.name_locales[
                            language
                        ].astext
                    )
                    == name_filter
                )
            query = query.where(or_(*filters))

        query = query.offset(offset).limit(limit)

        result = await self._async_db_session.execute(query)
        records = result.scalars().all()

        return [
            PatientContextAttributeCatalogFullResponseSchema.model_validate(record)
            for record in records
        ]

    @transactional
    @handle_unique_violation
    async def add_patient_context_attribute(
        self, request_dto: AddPatientContextAttributeSchema
    ) -> PatientContextAttributeCatalogFullResponseSchema:
        obj = SQLAlchemyPatientContextAttributesCatalogue(
            id=request_dto.id,
            name=request_dto.name,
            lang=request_dto.lang,
            name_locales=request_dto.name_locales,
        )
        self._async_db_session.add(obj)

        await self._async_db_session.flush()
        await self._async_db_session.refresh(obj)
        await self._async_db_session.commit()

        return PatientContextAttributeCatalogFullResponseSchema.model_validate(obj)

    @transactional
    async def update_patient_context_attribute(
        self,
        context_attribute_id: int,
        request_dto: UpdatePatientContextAttributeSchema,
    ) -> PatientContextAttributeCatalogFullResponseSchema:
        query = select(SQLAlchemyPatientContextAttributesCatalogue).where(
            SQLAlchemyPatientContextAttributesCatalogue.id == context_attribute_id
        )
        result = await self._async_db_session.execute(query)
        obj = result.scalar_one_or_none()

        # Updating fields...
        update_data = request_dto.model_dump(exclude_unset=True)
        if "name_locales" in update_data and update_data["name_locales"] == {}:
            update_data["name_locales"] = None

        for key, value in update_data.items():
            setattr(obj, key, value)

        await self._async_db_session.flush()
        await self._async_db_session.refresh(obj)
        await self._async_db_session.commit()

        return PatientContextAttributeCatalogFullResponseSchema.model_validate(obj)

    @transactional
    async def delete_by_id(self, context_attribute_id: int) -> None:
        query = delete(SQLAlchemyPatientContextAttributesCatalogue).where(
            SQLAlchemyPatientContextAttributesCatalogue.id == context_attribute_id
        )
        await self._async_db_session.execute(query)
        await self._async_db_session.commit()
