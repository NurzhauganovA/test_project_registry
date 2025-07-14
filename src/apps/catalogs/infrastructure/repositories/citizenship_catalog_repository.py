from typing import List, Optional

from sqlalchemy import delete, func, or_, select

from src.apps.catalogs.infrastructure.api.schemas.requests.citizenship_catalog_request_schemas import (
    AddCitizenshipSchema,
    UpdateCitizenshipSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.citizenship_catalog_response_schemas import (
    CitizenshipCatalogFullResponseSchema,
)
from src.apps.catalogs.infrastructure.db_models.citizenship_catalogue import (
    SQLAlchemyCitizenshipCatalogue,
)
from src.apps.catalogs.interfaces.citizenship_catalog_repository_interface import (
    CitizenshipCatalogRepositoryInterface,
)
from src.core.settings import project_settings
from src.shared.infrastructure.base import BaseRepository


class SQLAlchemyCitizenshipCatalogueRepositoryImpl(
    BaseRepository, CitizenshipCatalogRepositoryInterface
):
    async def get_by_default_name(
        self, name: str
    ) -> Optional[CitizenshipCatalogFullResponseSchema]:
        stmt = select(SQLAlchemyCitizenshipCatalogue).where(
            SQLAlchemyCitizenshipCatalogue.lang == project_settings.DEFAULT_LANGUAGE,
            func.lower(SQLAlchemyCitizenshipCatalogue.name) == name.lower(),
        )
        result = await self._async_db_session.execute(stmt)
        obj = result.scalar_one_or_none()
        if not obj:
            return None

        return CitizenshipCatalogFullResponseSchema.model_validate(obj)

    async def get_by_locale(
        self, locale: str, name: str
    ) -> Optional[CitizenshipCatalogFullResponseSchema]:
        stmt = select(SQLAlchemyCitizenshipCatalogue).where(
            func.lower(SQLAlchemyCitizenshipCatalogue.name_locales[locale].astext)
            == name.lower()
        )
        result = await self._async_db_session.execute(stmt)
        obj = result.scalar_one_or_none()
        if not obj:
            return None

        return CitizenshipCatalogFullResponseSchema.model_validate(obj)

    async def get_total_number_of_citizenship_records(self) -> int:
        query = select(func.count(SQLAlchemyCitizenshipCatalogue.id))
        result = await self._async_db_session.execute(query)

        return result.scalar_one()

    async def get_by_id(
        self, citizenship_id: int
    ) -> Optional[CitizenshipCatalogFullResponseSchema]:
        query = select(SQLAlchemyCitizenshipCatalogue).where(
            SQLAlchemyCitizenshipCatalogue.id == citizenship_id
        )
        result = await self._async_db_session.execute(query)
        obj = result.scalar_one_or_none()
        if obj:
            return CitizenshipCatalogFullResponseSchema.model_validate(obj)

        return None

    async def get_by_country_code(
        self, country_code: str
    ) -> Optional[CitizenshipCatalogFullResponseSchema]:
        query = select(SQLAlchemyCitizenshipCatalogue).where(
            func.lower(SQLAlchemyCitizenshipCatalogue.country_code)
            == country_code.lower()
        )
        result = await self._async_db_session.execute(query)
        obj = result.scalar_one_or_none()
        if obj:
            return CitizenshipCatalogFullResponseSchema.model_validate(obj)

        return None

    async def get_citizenship_records(
        self,
        name_filter: Optional[str],
        country_code_filter: Optional[str],
        page: int = 1,
        limit: int = 30,
    ) -> List[CitizenshipCatalogFullResponseSchema]:
        offset = (page - 1) * limit
        query = select(SQLAlchemyCitizenshipCatalogue)

        # Filtering...
        if name_filter:
            name_filter = name_filter.lower()
            filters = [func.lower(SQLAlchemyCitizenshipCatalogue.name) == name_filter]
            for language in project_settings.LANGUAGES:
                filters.append(
                    func.lower(
                        SQLAlchemyCitizenshipCatalogue.name_locales[language].astext
                    )
                    == name_filter
                )
            query = query.where(or_(*filters))
        if country_code_filter:
            query = query.where(
                SQLAlchemyCitizenshipCatalogue.country_code == country_code_filter
            )

        query = query.offset(offset).limit(limit)

        result = await self._async_db_session.execute(query)
        records = result.scalars().all()

        return [
            CitizenshipCatalogFullResponseSchema.model_validate(obj) for obj in records
        ]

    async def add_citizenship(
        self, request_dto: AddCitizenshipSchema
    ) -> CitizenshipCatalogFullResponseSchema:
        obj = SQLAlchemyCitizenshipCatalogue(
            country_code=request_dto.country_code,
            name=request_dto.name,
            lang=request_dto.lang,
            name_locales=request_dto.name_locales,
        )
        self._async_db_session.add(obj)

        await self._async_db_session.flush()
        await self._async_db_session.refresh(obj)
        await self._async_db_session.commit()

        return CitizenshipCatalogFullResponseSchema.model_validate(obj)

    async def update_citizenship(
        self, citizenship_id: int, request_dto: UpdateCitizenshipSchema
    ) -> CitizenshipCatalogFullResponseSchema:
        query = select(SQLAlchemyCitizenshipCatalogue).where(
            SQLAlchemyCitizenshipCatalogue.id == citizenship_id
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

        return CitizenshipCatalogFullResponseSchema.model_validate(obj)

    async def delete_by_id(self, citizenship_id: int) -> None:
        query = delete(SQLAlchemyCitizenshipCatalogue).where(
            SQLAlchemyCitizenshipCatalogue.id == citizenship_id
        )
        await self._async_db_session.execute(query)
        await self._async_db_session.commit()
