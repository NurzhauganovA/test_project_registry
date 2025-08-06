from typing import List, Optional

from sqlalchemy import delete, func, or_, select

from src.apps.catalogs.infrastructure.api.schemas.requests.financing_sources_catalog_request_schemas import (
    AddFinancingSourceSchema,
    UpdateFinancingSourceSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.financing_sources_catalog_response_schemas import (
    FinancingSourceFullResponseSchema,
)
from src.apps.catalogs.infrastructure.db_models.financing_sources_catalogue import (
    SQLAlchemyFinancingSourcesCatalog,
)
from src.apps.catalogs.interfaces.financing_sources_catalog_repository_interface import (
    FinancingSourcesCatalogRepositoryInterface,
)
from src.core.settings import project_settings
from src.shared.helpers.decorators import handle_unique_violation, transactional
from src.shared.infrastructure.base import BaseRepository


class SQLAlchemyFinancingSourcesCatalogRepositoryImpl(
    BaseRepository, FinancingSourcesCatalogRepositoryInterface
):
    async def get_by_default_name(
        self, name: str
    ) -> Optional[FinancingSourceFullResponseSchema]:
        stmt = select(SQLAlchemyFinancingSourcesCatalog).where(
            SQLAlchemyFinancingSourcesCatalog.lang == project_settings.DEFAULT_LANGUAGE,
            func.lower(SQLAlchemyFinancingSourcesCatalog.name) == name.lower(),
        )
        result = await self._async_db_session.execute(stmt)
        obj = result.scalar_one_or_none()
        if not obj:
            return None

        return FinancingSourceFullResponseSchema.model_validate(obj)

    async def get_by_name_locale(
        self, locale: str, name: str
    ) -> Optional[FinancingSourceFullResponseSchema]:
        stmt = select(SQLAlchemyFinancingSourcesCatalog).where(
            func.lower(SQLAlchemyFinancingSourcesCatalog.name_locales[locale].astext)
            == name.lower()
        )
        result = await self._async_db_session.execute(stmt)
        obj = result.scalar_one_or_none()
        if not obj:
            return None

        return FinancingSourceFullResponseSchema.model_validate(obj)

    async def get_by_financing_source_code(
        self, financing_source_code: str
    ) -> Optional[FinancingSourceFullResponseSchema]:
        query = select(SQLAlchemyFinancingSourcesCatalog).where(
            SQLAlchemyFinancingSourcesCatalog.code == financing_source_code
        )
        result = await self._async_db_session.execute(query)
        obj = result.scalar_one_or_none()
        if obj:
            return FinancingSourceFullResponseSchema.model_validate(obj)

        return None

    async def get_total_number_of_financing_sources(self) -> int:
        query = select(func.count(SQLAlchemyFinancingSourcesCatalog.id))
        result = await self._async_db_session.execute(query)

        return result.scalar_one()

    async def get_by_id(
        self, financing_source_id: int
    ) -> Optional[FinancingSourceFullResponseSchema]:
        query = select(SQLAlchemyFinancingSourcesCatalog).where(
            SQLAlchemyFinancingSourcesCatalog.id == financing_source_id
        )
        result = await self._async_db_session.execute(query)
        obj = result.scalar_one_or_none()
        if obj:
            return FinancingSourceFullResponseSchema.model_validate(obj)

        return None

    async def get_financing_sources(
        self,
        name_filter: Optional[str],
        code_filter: Optional[str],
        page: int = 1,
        limit: int = 30,
    ) -> List[FinancingSourceFullResponseSchema]:
        offset = (page - 1) * limit

        query = select(SQLAlchemyFinancingSourcesCatalog)

        # Filtering...
        if name_filter:
            name_filter = name_filter.lower()
            filters = [
                func.lower(SQLAlchemyFinancingSourcesCatalog.name) == name_filter
            ]
            for language in project_settings.LANGUAGES:
                filters.append(
                    func.lower(
                        SQLAlchemyFinancingSourcesCatalog.name_locales[language].astext
                    )
                    == name_filter
                )
            query = query.where(or_(*filters))

        if code_filter:
            code_filter = code_filter.lower()
            query = query.where(
                func.lower(SQLAlchemyFinancingSourcesCatalog.code) == code_filter
            )

        query = query.offset(offset).limit(limit)

        result = await self._async_db_session.execute(query)
        records = result.scalars().all()

        return [
            FinancingSourceFullResponseSchema.model_validate(record)
            for record in records
        ]

    @transactional
    @handle_unique_violation
    async def add_financing_source(
        self, request_dto: AddFinancingSourceSchema
    ) -> FinancingSourceFullResponseSchema:
        obj = SQLAlchemyFinancingSourcesCatalog(
            id=request_dto.id,
            name=request_dto.name,
            code=request_dto.financing_source_code,
            lang=request_dto.lang,
            name_locales=request_dto.name_locales,
        )
        self._async_db_session.add(obj)

        await self._async_db_session.flush()
        await self._async_db_session.refresh(obj)
        await self._async_db_session.commit()

        return FinancingSourceFullResponseSchema.model_validate(obj)

    @transactional
    async def update_financing_source(
        self, financing_source_id: int, request_dto: UpdateFinancingSourceSchema
    ) -> FinancingSourceFullResponseSchema:
        query = select(SQLAlchemyFinancingSourcesCatalog).where(
            SQLAlchemyFinancingSourcesCatalog.id == financing_source_id
        )
        result = await self._async_db_session.execute(query)
        obj = result.scalar_one_or_none()

        # Updating fields...
        update_data = request_dto.model_dump(exclude_unset=True)
        if "name_locales" in update_data and update_data["name_locales"] == {}:
            update_data["name_locales"] = None

        for key, value in update_data.items():
            if key == "financing_source_code":
                setattr(obj, "code", value)
            else:
                setattr(obj, key, value)

        await self._async_db_session.flush()
        await self._async_db_session.refresh(obj)
        await self._async_db_session.commit()

        return FinancingSourceFullResponseSchema.model_validate(obj)

    @transactional
    async def delete_by_id(self, financing_source_id: int) -> None:
        query = delete(SQLAlchemyFinancingSourcesCatalog).where(
            SQLAlchemyFinancingSourcesCatalog.id == financing_source_id
        )
        await self._async_db_session.execute(query)
        await self._async_db_session.commit()
