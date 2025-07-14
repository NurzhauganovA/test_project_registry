from typing import List, Optional

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.catalogs.infrastructure.api.schemas.requests.nationalities_catalog_request_schemas import (
    AddNationalitySchema,
    UpdateNationalitySchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.nationalities_catalog_response_schemas import (
    NationalityCatalogFullResponseSchema,
)
from src.apps.catalogs.infrastructure.db_models.nationalities_catalogue import (
    SQLAlchemyNationalitiesCatalogue,
)
from src.apps.catalogs.interfaces.nationalities_catalog_repository_interface import (
    NationalitiesCatalogRepositoryInterface,
)
from src.core.logger import LoggerService
from src.core.settings import project_settings
from src.shared.infrastructure.base import BaseRepository


class SQLAlchemyNationalitiesCatalogRepositoryImpl(
    BaseRepository, NationalitiesCatalogRepositoryInterface
):
    def __init__(self, async_db_session: AsyncSession, logger: LoggerService):
        self._async_db_session = async_db_session
        self._logger = logger

    async def get_by_default_name(
        self, name: str
    ) -> Optional[NationalityCatalogFullResponseSchema]:
        stmt = select(SQLAlchemyNationalitiesCatalogue).where(
            SQLAlchemyNationalitiesCatalogue.lang == project_settings.DEFAULT_LANGUAGE,
            func.lower(SQLAlchemyNationalitiesCatalogue.name) == name.lower(),
        )
        result = await self._async_db_session.execute(stmt)
        obj = result.scalar_one_or_none()
        if not obj:
            return None

        return NationalityCatalogFullResponseSchema.model_validate(obj)

    async def get_by_locale(
        self, locale: str, name: str
    ) -> Optional[NationalityCatalogFullResponseSchema]:
        stmt = select(SQLAlchemyNationalitiesCatalogue).where(
            func.lower(SQLAlchemyNationalitiesCatalogue.name_locales[locale].astext)
            == name.lower()
        )
        result = await self._async_db_session.execute(stmt)
        obj = result.scalar_one_or_none()
        if not obj:
            return None

        return NationalityCatalogFullResponseSchema.model_validate(obj)

    async def get_by_id(
        self, nationality_id: int
    ) -> Optional[NationalityCatalogFullResponseSchema]:
        query = select(SQLAlchemyNationalitiesCatalogue).where(
            SQLAlchemyNationalitiesCatalogue.id == nationality_id
        )
        result = await self._async_db_session.execute(query)
        obj = result.scalar_one_or_none()
        if obj:
            return NationalityCatalogFullResponseSchema.model_validate(obj)

        return None

    async def get_total_number_of_nationalities(self) -> int:
        query = select(func.count(SQLAlchemyNationalitiesCatalogue.id))
        result = await self._async_db_session.execute(query)

        return result.scalar_one()

    async def get_nationalities(
        self,
        name_filter: Optional[str],
        page: int = 1,
        limit: int = 30,
    ) -> List[NationalityCatalogFullResponseSchema]:
        offset = (page - 1) * limit

        query = select(SQLAlchemyNationalitiesCatalogue)

        # Filtering...
        if name_filter:
            name_filter = name_filter.lower()
            filters = [func.lower(SQLAlchemyNationalitiesCatalogue.name) == name_filter]
            for language in project_settings.LANGUAGES:
                filters.append(
                    func.lower(
                        SQLAlchemyNationalitiesCatalogue.name_locales[language].astext
                    )
                    == name_filter
                )
            query = query.where(or_(*filters))

        query = query.offset(offset).limit(limit)

        result = await self._async_db_session.execute(query)
        records = result.scalars().all()

        return [
            NationalityCatalogFullResponseSchema.model_validate(record)
            for record in records
        ]

    async def add_nationality(
        self, request_dto: AddNationalitySchema
    ) -> NationalityCatalogFullResponseSchema:
        obj = SQLAlchemyNationalitiesCatalogue(
            name=request_dto.name,
            lang=request_dto.lang,
            name_locales=request_dto.name_locales,
        )
        self._async_db_session.add(obj)

        await self._async_db_session.flush()
        await self._async_db_session.refresh(obj)
        await self._async_db_session.commit()

        return NationalityCatalogFullResponseSchema.model_validate(obj)

    async def update_nationality(
        self, nationality_id: int, request_dto: UpdateNationalitySchema
    ) -> NationalityCatalogFullResponseSchema:
        query = select(SQLAlchemyNationalitiesCatalogue).where(
            SQLAlchemyNationalitiesCatalogue.id == nationality_id
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

        return NationalityCatalogFullResponseSchema.model_validate(obj)

    async def delete_by_id(self, nationality_id: int) -> None:
        query = delete(SQLAlchemyNationalitiesCatalogue).where(
            SQLAlchemyNationalitiesCatalogue.id == nationality_id
        )
        await self._async_db_session.execute(query)
        await self._async_db_session.commit()
