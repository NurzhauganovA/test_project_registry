from typing import List, Optional

from sqlalchemy import and_, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.catalogs.infrastructure.api.schemas.requests.citizenship_catalog_request_schemas import (
    UpdateCitizenshipSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.requests.medical_organizations_catalog_schemas import (
    AddMedicalOrganizationSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.medical_organizations_catalog_schemas import (
    MedicalOrganizationCatalogFullResponseSchema,
)
from src.apps.catalogs.infrastructure.db_models.medical_organizations_catalogue import (
    SQLAlchemyMedicalOrganizationsCatalogue,
)
from src.apps.catalogs.interfaces.medical_organizations_catalog_repository_interface import (
    MedicalOrganizationsCatalogRepositoryInterface,
)
from src.core.logger import LoggerService
from src.core.settings import project_settings
from src.shared.infrastructure.base import BaseRepository


class SQLAlchemyMedicalOrganizationsCatalogCatalogueRepositoryImpl(
    BaseRepository, MedicalOrganizationsCatalogRepositoryInterface
):
    def __init__(self, async_db_session: AsyncSession, logger: LoggerService):
        self._async_db_session = async_db_session
        self._logger = logger

    async def get_by_default_name(
        self, name: str
    ) -> Optional[MedicalOrganizationCatalogFullResponseSchema]:
        stmt = select(SQLAlchemyMedicalOrganizationsCatalogue).where(
            SQLAlchemyMedicalOrganizationsCatalogue.lang
            == project_settings.DEFAULT_LANGUAGE,
            func.lower(SQLAlchemyMedicalOrganizationsCatalogue.name) == name.lower(),
        )
        result = await self._async_db_session.execute(stmt)
        obj = result.scalar_one_or_none()
        if not obj:
            return None

        return MedicalOrganizationCatalogFullResponseSchema.model_validate(obj)

    async def get_by_organization_code(
        self, organization_code: str
    ) -> Optional[MedicalOrganizationCatalogFullResponseSchema]:
        query = select(SQLAlchemyMedicalOrganizationsCatalogue).where(
            SQLAlchemyMedicalOrganizationsCatalogue.code == organization_code
        )
        result = await self._async_db_session.execute(query)
        obj = result.scalar_one_or_none()
        if obj:
            return MedicalOrganizationCatalogFullResponseSchema.model_validate(obj)

        return None

    async def get_by_name_locale(
        self, locale: str, name: str
    ) -> Optional[MedicalOrganizationCatalogFullResponseSchema]:
        stmt = select(SQLAlchemyMedicalOrganizationsCatalogue).where(
            func.lower(
                SQLAlchemyMedicalOrganizationsCatalogue.name_locales[locale].astext
            )
            == name.lower()
        )
        result = await self._async_db_session.execute(stmt)
        obj = result.scalar_one_or_none()
        if not obj:
            return None

        return MedicalOrganizationCatalogFullResponseSchema.model_validate(obj)

    async def get_by_address_locale(
        self, locale: str, address: str
    ) -> Optional[MedicalOrganizationCatalogFullResponseSchema]:
        stmt = select(SQLAlchemyMedicalOrganizationsCatalogue).where(
            func.lower(
                SQLAlchemyMedicalOrganizationsCatalogue.address_locales[locale].astext
            )
            == address.lower()
        )
        result = await self._async_db_session.execute(stmt)
        obj = result.scalar_one_or_none()
        if not obj:
            return None

        return MedicalOrganizationCatalogFullResponseSchema.model_validate(obj)

    async def get_total_number_of_medical_organizations(self) -> int:
        query = select(func.count(SQLAlchemyMedicalOrganizationsCatalogue.id))
        result = await self._async_db_session.execute(query)

        return result.scalar_one()

    async def get_by_id(
        self, medical_organization_id: int
    ) -> Optional[MedicalOrganizationCatalogFullResponseSchema]:
        query = select(SQLAlchemyMedicalOrganizationsCatalogue).where(
            SQLAlchemyMedicalOrganizationsCatalogue.id == medical_organization_id
        )
        result = await self._async_db_session.execute(query)
        obj = result.scalar_one_or_none()
        if obj:
            return MedicalOrganizationCatalogFullResponseSchema.model_validate(obj)

        return None

    async def get_medical_organizations(
        self,
        name_filter: Optional[str],
        organization_code_filter: Optional[str],
        address_filter: Optional[str],
        page: int = 1,
        limit: int = 30,
    ) -> List[MedicalOrganizationCatalogFullResponseSchema]:
        offset = (page - 1) * limit

        query = select(SQLAlchemyMedicalOrganizationsCatalogue)

        # Filtering...
        filters = []

        if name_filter:
            name_filter = name_filter.lower()
            name_conditions = [
                func.lower(SQLAlchemyMedicalOrganizationsCatalogue.name).ilike(
                    f"%{name_filter}%"
                )
            ]
            for language in project_settings.LANGUAGES:
                name_conditions.append(
                    func.lower(
                        SQLAlchemyMedicalOrganizationsCatalogue.name_locales[
                            language
                        ].astext
                    ).ilike(f"%{name_filter}%")
                )
            filters.append(or_(*name_conditions))

        if organization_code_filter:
            filters.append(
                SQLAlchemyMedicalOrganizationsCatalogue.code == organization_code_filter
            )

        if address_filter:
            address_filter = address_filter.lower()
            address_conditions = [
                func.lower(SQLAlchemyMedicalOrganizationsCatalogue.address).ilike(
                    f"%{address_filter}%"
                )
            ]
            for language in project_settings.LANGUAGES:
                address_conditions.append(
                    func.lower(
                        SQLAlchemyMedicalOrganizationsCatalogue.address_locales[
                            language
                        ].astext
                    ).ilike(f"%{address_filter}%")
                )
            filters.append(or_(*address_conditions))

        if filters:
            query = query.where(and_(*filters))

        query = query.offset(offset).limit(limit)
        result = await self._async_db_session.execute(query)
        records = result.scalars().all()

        return [
            MedicalOrganizationCatalogFullResponseSchema.model_validate(record)
            for record in records
        ]

    async def add_medical_organization(
        self, request_dto: AddMedicalOrganizationSchema
    ) -> MedicalOrganizationCatalogFullResponseSchema:
        obj = SQLAlchemyMedicalOrganizationsCatalogue(
            name=request_dto.name,
            code=request_dto.organization_code,
            address=request_dto.address,
            lang=request_dto.lang,
            name_locales=request_dto.name_locales,
            address_locales=request_dto.address_locales,
        )
        self._async_db_session.add(obj)

        await self._async_db_session.flush()
        await self._async_db_session.refresh(obj)
        await self._async_db_session.commit()

        return MedicalOrganizationCatalogFullResponseSchema.model_validate(obj)

    async def update_medical_organization(
        self, medical_organization_id: int, request_dto: UpdateCitizenshipSchema
    ) -> MedicalOrganizationCatalogFullResponseSchema:
        query = select(SQLAlchemyMedicalOrganizationsCatalogue).where(
            SQLAlchemyMedicalOrganizationsCatalogue.id == medical_organization_id
        )
        result = await self._async_db_session.execute(query)
        obj = result.scalar_one_or_none()

        # Updating fields...
        update_data = request_dto.model_dump(exclude_unset=True)
        if "name_locales" in update_data and update_data["name_locales"] == {}:
            update_data["name_locales"] = None
        if "address_locales" in update_data and update_data["address_locales"] == {}:
            update_data["address_locales"] = None

        for key, value in update_data.items():
            setattr(obj, key, value)

        await self._async_db_session.flush()
        await self._async_db_session.refresh(obj)
        await self._async_db_session.commit()

        return MedicalOrganizationCatalogFullResponseSchema.model_validate(obj)

    async def delete_by_id(self, medical_organization_id: int) -> None:
        query = delete(SQLAlchemyMedicalOrganizationsCatalogue).where(
            SQLAlchemyMedicalOrganizationsCatalogue.id == medical_organization_id
        )
        await self._async_db_session.execute(query)
        await self._async_db_session.commit()
