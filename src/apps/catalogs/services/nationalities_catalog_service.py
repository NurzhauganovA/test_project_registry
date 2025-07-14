import math
from typing import Dict, List, Optional, Union

from src.apps.catalogs.infrastructure.api.schemas.requests.nationalities_catalog_request_schemas import (
    AddNationalitySchema,
    UpdateNationalitySchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.nationalities_catalog_response_schemas import (
    MultipleNationalitiesCatalogSchema,
    NationalityCatalogFullResponseSchema,
    NationalityCatalogPartialResponseSchema,
)
from src.apps.catalogs.interfaces.nationalities_catalog_repository_interface import (
    NationalitiesCatalogRepositoryInterface,
)
from src.core.i18n import _, get_locale
from src.core.logger import LoggerService
from src.core.settings import project_settings
from src.shared.exceptions import InstanceAlreadyExistsError, NoInstanceFoundError
from src.shared.schemas.pagination_schemas import (
    PaginationMetaDataSchema,
    PaginationParams,
)


class NationalitiesCatalogService:
    def __init__(
        self,
        logger: LoggerService,
        nationalities_catalog_repository: NationalitiesCatalogRepositoryInterface,
    ):
        self._logger = logger
        self._nationalities_catalog_repository = nationalities_catalog_repository

    @staticmethod
    def __get_localized_name(
        patient_context_attribute: NationalityCatalogFullResponseSchema,
    ) -> str:
        chosen_language = get_locale()
        default_language = project_settings.DEFAULT_LANGUAGE

        locales: Dict[str, str] = patient_context_attribute.name_locales or {}

        if patient_context_attribute.lang == chosen_language:
            return patient_context_attribute.name
        if translated := locales.get(chosen_language):
            return translated

        if default_language != chosen_language:
            if patient_context_attribute.lang == default_language:
                return patient_context_attribute.name
            if translated := locales.get(default_language):
                return translated

        return patient_context_attribute.name

    async def get_by_id(
        self,
        nationality_id: int,
        include_all_locales: bool = False,
    ) -> Union[
        NationalityCatalogFullResponseSchema,
        NationalityCatalogPartialResponseSchema,
    ]:
        full_schema = await self._nationalities_catalog_repository.get_by_id(
            nationality_id
        )
        if not full_schema:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Nationality with ID: %(NATIONALITY_ID)s was not found.")
                % {"NATIONALITY_ID": nationality_id},
            )

        if include_all_locales:
            return full_schema

        chosen_language = get_locale()
        localized_name = NationalitiesCatalogService.__get_localized_name(full_schema)

        return NationalityCatalogPartialResponseSchema(
            id=full_schema.id,
            lang=chosen_language,
            name=localized_name,
            created_at=full_schema.created_at,
            changed_at=full_schema.changed_at,
        )

    async def get_nationalities(
        self,
        pagination_params: PaginationParams,
        name_filter: Optional[str] = None,
        include_all_locales: bool = False,
    ) -> MultipleNationalitiesCatalogSchema:
        page: int = pagination_params.page or 1  # for mypy
        limit: int = pagination_params.limit or 30  # for mypy

        items_full_schemas = (
            await self._nationalities_catalog_repository.get_nationalities(
                page=page,
                limit=limit,
                name_filter=name_filter,
            )
        )
        total_items = (
            await self._nationalities_catalog_repository.get_total_number_of_nationalities()
        )

        if include_all_locales:
            # type ignore:
            items: List[
                Union[
                    NationalityCatalogFullResponseSchema,
                    NationalityCatalogPartialResponseSchema,
                ]
            ] = items_full_schemas  # type: ignore[assignment]
        else:
            chosen_language = get_locale()

            items = [
                NationalityCatalogPartialResponseSchema(
                    id=patient_context_attribute.id,
                    lang=chosen_language,
                    name=NationalitiesCatalogService.__get_localized_name(
                        patient_context_attribute
                    ),
                    created_at=patient_context_attribute.created_at,
                    changed_at=patient_context_attribute.changed_at,
                )
                for patient_context_attribute in items_full_schemas
            ]

        # Calculate pagination metadata
        total_pages = math.ceil(total_items / limit) if limit else 1
        has_next = page < total_pages
        has_prev = page > 1

        pagination = PaginationMetaDataSchema(
            current_page=page,
            per_page=limit,
            total_items=total_items,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
        )

        return MultipleNationalitiesCatalogSchema(
            items=items,
            pagination=pagination,
        )

    async def add_nationality(
        self, request_dto: AddNationalitySchema
    ) -> NationalityCatalogFullResponseSchema:
        # Check that 'name' field is not taken already
        if await self._nationalities_catalog_repository.get_by_default_name(
            request_dto.name
        ):
            raise InstanceAlreadyExistsError(
                status_code=409,
                detail=_("Nationality with name: '%(NAME)s' already exists.")
                % {"NAME": request_dto.name},
            )

        # Check that value in the 'name_locales' entry is not taken already
        for code, value in request_dto.name_locales.items():
            if await self._nationalities_catalog_repository.get_by_locale(code, value):
                raise InstanceAlreadyExistsError(
                    status_code=409,
                    detail=_(
                        "Nationality's '%(CODE)s' locale: '%(VALUE)s' already exists in some "
                        "record's locale. It's already taken."
                    )
                    % {"VALUE": value, "CODE": code},
                )

        return await self._nationalities_catalog_repository.add_nationality(request_dto)

    async def update_nationality(
        self,
        nationality_id: int,
        request_dto: UpdateNationalitySchema,
    ) -> NationalityCatalogFullResponseSchema:
        # Check if context attribute exists
        existing = await self._nationalities_catalog_repository.get_by_id(
            nationality_id
        )
        if not existing:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Nationality with ID: %(ID)s not found.")
                % {"ID": nationality_id},
            )

        default_language = project_settings.DEFAULT_LANGUAGE

        if request_dto.lang is not None and request_dto.lang != existing.lang:
            if request_dto.lang != default_language:
                raise ValueError(
                    _("Field 'lang' must be '%(DEFAULT_LANG)s.'")
                    % {"DEFAULT_LANG": default_language}
                )

        if request_dto.name is not None and request_dto.name != existing.name:
            if await self._nationalities_catalog_repository.get_by_default_name(
                request_dto.name
            ):
                raise InstanceAlreadyExistsError(
                    status_code=409,
                    detail=_("Nationality with name: '%(NAME)s' already exists.")
                    % {"NAME": request_dto.name},
                )

        if request_dto.name_locales is not None:
            existing_locales = existing.name_locales or {}
            for language_code, value in request_dto.name_locales.items():
                if existing_locales.get(language_code) == value:
                    continue

                if await self._nationalities_catalog_repository.get_by_locale(
                    language_code, value
                ):
                    raise InstanceAlreadyExistsError(
                        status_code=409,
                        detail=_(
                            "Nationality's '%(CODE)s' locale: '%(VALUE)s' already exists in some "
                            "record's locale. It's already taken."
                        )
                        % {"VALUE": value, "CODE": language_code},
                    )

        updated = await self._nationalities_catalog_repository.update_nationality(
            nationality_id, request_dto
        )

        return updated

    async def delete_by_id(self, nationality_id: int) -> None:
        # Check if context attribute exists
        existing = await self._nationalities_catalog_repository.get_by_id(
            nationality_id
        )
        if not existing:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Nationality with ID: %(ID)s not found.")
                % {"ID": nationality_id},
            )

        await self._nationalities_catalog_repository.delete_by_id(nationality_id)
