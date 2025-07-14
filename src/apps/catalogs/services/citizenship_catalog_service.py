import math
from typing import Dict, List, Optional, Union

from src.apps.catalogs.infrastructure.api.schemas.requests.citizenship_catalog_request_schemas import (
    AddCitizenshipSchema,
    UpdateCitizenshipSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.citizenship_catalog_response_schemas import (
    CitizenshipCatalogFullResponseSchema,
    CitizenshipCatalogPartialResponseSchema,
    MultipleCitizenshipSchema,
)
from src.apps.catalogs.interfaces.citizenship_catalog_repository_interface import (
    CitizenshipCatalogRepositoryInterface,
)
from src.core.i18n import _, get_locale
from src.core.logger import LoggerService
from src.core.settings import project_settings
from src.shared.exceptions import InstanceAlreadyExistsError, NoInstanceFoundError
from src.shared.schemas.pagination_schemas import (
    PaginationMetaDataSchema,
    PaginationParams,
)


class CitizenshipCatalogService:
    def __init__(
        self,
        logger: LoggerService,
        citizenship_catalog_repository: CitizenshipCatalogRepositoryInterface,
    ):
        self._logger = logger
        self._citizenship_catalog_repository = citizenship_catalog_repository

    @staticmethod
    def __get_localized_name(
        citizenship: CitizenshipCatalogFullResponseSchema,
    ) -> str:
        chosen_language = get_locale()
        default_language = project_settings.DEFAULT_LANGUAGE

        locales: Dict[str, str] = citizenship.name_locales or {}

        if citizenship.lang == chosen_language:
            return citizenship.name
        if translated := locales.get(chosen_language):
            return translated

        if default_language != chosen_language:
            if citizenship.lang == default_language:
                return citizenship.name
            if translated := locales.get(default_language):
                return translated

        return citizenship.name

    async def get_by_id(
        self,
        citizenship_id: int,
        include_all_locales: bool = False,
    ) -> Union[
        CitizenshipCatalogFullResponseSchema,
        CitizenshipCatalogPartialResponseSchema,
    ]:
        full_schema = await self._citizenship_catalog_repository.get_by_id(
            citizenship_id
        )
        if not full_schema:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Citizenship with ID: %(ATTR_ID)s was not found.")
                % {"ATTR_ID": citizenship_id},
            )

        if include_all_locales:
            return full_schema

        chosen_language = get_locale()
        localized_name = CitizenshipCatalogService.__get_localized_name(full_schema)

        return CitizenshipCatalogPartialResponseSchema(
            id=full_schema.id,
            lang=chosen_language,
            name=localized_name,
            country_code=full_schema.country_code,
            created_at=full_schema.created_at,
            changed_at=full_schema.changed_at,
        )

    async def get_citizenship_records(
        self,
        pagination_params: PaginationParams,
        name_filter: Optional[str] = None,
        country_code_filter: Optional[str] = None,
        include_all_locales: bool = False,
    ) -> MultipleCitizenshipSchema:
        page: int = pagination_params.page or 1  # for mypy
        limit: int = pagination_params.limit or 30  # for mypy

        items_full_schemas = (
            await self._citizenship_catalog_repository.get_citizenship_records(
                page=page,
                limit=limit,
                name_filter=name_filter,
                country_code_filter=country_code_filter,
            )
        )
        total_items = (
            await self._citizenship_catalog_repository.get_total_number_of_citizenship_records()
        )

        if include_all_locales:
            # type ignore:
            items: List[
                Union[
                    CitizenshipCatalogFullResponseSchema,
                    CitizenshipCatalogPartialResponseSchema,
                ]
            ] = items_full_schemas  # type: ignore[assignment]
        else:
            chosen_language = get_locale()

            items = [
                CitizenshipCatalogPartialResponseSchema(
                    id=citizenship.id,
                    lang=chosen_language,
                    name=CitizenshipCatalogService.__get_localized_name(citizenship),
                    country_code=citizenship.country_code,
                    created_at=citizenship.created_at,
                    changed_at=citizenship.changed_at,
                )
                for citizenship in items_full_schemas
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

        return MultipleCitizenshipSchema(
            items=items,
            pagination=pagination,
        )

    async def add_citizenship(
        self, request_dto: AddCitizenshipSchema
    ) -> CitizenshipCatalogFullResponseSchema:
        # Check that 'name' field is not taken already
        if await self._citizenship_catalog_repository.get_by_default_name(
            request_dto.name
        ):
            raise InstanceAlreadyExistsError(
                status_code=409,
                detail=_("Citizenship with name: '%(NAME)s' already exists.")
                % {"NAME": request_dto.name},
            )

        # Check that 'country_code' field is not taken already
        if await self._citizenship_catalog_repository.get_by_country_code(
            request_dto.country_code
        ):
            raise InstanceAlreadyExistsError(
                status_code=409,
                detail=_("Citizenship with country code: '%(CODE)s' already exists.")
                % {"CODE": request_dto.country_code},
            )

        # Check that value in the 'name_locales' entry is not taken already
        for code, value in request_dto.name_locales.items():
            if await self._citizenship_catalog_repository.get_by_locale(code, value):
                raise InstanceAlreadyExistsError(
                    status_code=409,
                    detail=_(
                        "Citizenship's '%(CODE)s' locale: '%(VALUE)s' already exists in some "
                        "record's locale. It's already taken."
                    )
                    % {"VALUE": value, "CODE": code},
                )

        return await self._citizenship_catalog_repository.add_citizenship(request_dto)

    async def update_citizenship(
        self,
        citizenship_id: int,
        request_dto: UpdateCitizenshipSchema,
    ) -> CitizenshipCatalogFullResponseSchema:
        # Check if context attribute exists
        existing = await self._citizenship_catalog_repository.get_by_id(citizenship_id)
        if not existing:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Citizenship with id: %(ID)s not found.")
                % {"ID": citizenship_id},
            )

        default_language = project_settings.DEFAULT_LANGUAGE

        if request_dto.lang is not None and request_dto.lang != existing.lang:
            if request_dto.lang != default_language:
                raise ValueError(
                    _("Field 'lang' must be '%(DEFAULT_LANG)s.'")
                    % {"DEFAULT_LANG": default_language}
                )

        # Check that 'name' field is not taken already
        if request_dto.name is not None and request_dto.name != existing.name:
            if await self._citizenship_catalog_repository.get_by_default_name(
                request_dto.name
            ):
                raise InstanceAlreadyExistsError(
                    status_code=409,
                    detail=_("Citizenship with name: '%(NAME)s' already exists.")
                    % {"NAME": request_dto.name},
                )

        # Check that 'country_code' field is not taken already
        if (
            request_dto.country_code is not None
            and request_dto.country_code != existing.country_code
        ):
            if await self._citizenship_catalog_repository.get_by_country_code(
                request_dto.country_code
            ):
                raise InstanceAlreadyExistsError(
                    status_code=409,
                    detail=_(
                        "Citizenship with country code: '%(CODE)s' already exists."
                    )
                    % {"CODE": request_dto.country_code},
                )

        if request_dto.name_locales is not None:
            existing_locales = existing.name_locales or {}
            for language_code, value in request_dto.name_locales.items():
                if existing_locales.get(language_code) == value:
                    continue

                if await self._citizenship_catalog_repository.get_by_locale(
                    language_code, value
                ):
                    raise InstanceAlreadyExistsError(
                        status_code=409,
                        detail=_(
                            "Citizenship's '%(CODE)s' locale: '%(VALUE)s' already exists in some "
                            "record's locale. It's already taken."
                        )
                        % {"VALUE": value, "CODE": language_code},
                    )

        updated = await self._citizenship_catalog_repository.update_citizenship(
            citizenship_id, request_dto
        )

        return updated

    async def delete_by_id(self, citizenship_id: int) -> None:
        # Check if context attribute exists
        existing = await self._citizenship_catalog_repository.get_by_id(citizenship_id)
        if not existing:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Citizenship with id: %(ID)s not found.")
                % {"ID": citizenship_id},
            )

        await self._citizenship_catalog_repository.delete_by_id(citizenship_id)
