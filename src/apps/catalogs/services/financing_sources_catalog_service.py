import math
from typing import Dict, List, Optional, Union

from src.apps.catalogs.infrastructure.api.schemas.requests.financing_sources_catalog_request_schemas import (
    AddFinancingSourceSchema,
    UpdateFinancingSourceSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.financing_sources_catalog_response_schemas import (
    FinancingSourceFullResponseSchema,
    FinancingSourcePartialResponseSchema,
    MultipleFinancingSourcesSchema,
)
from src.apps.catalogs.interfaces.financing_sources_catalog_repository_interface import (
    FinancingSourcesCatalogRepositoryInterface,
)
from src.core.i18n import _, get_locale
from src.core.logger import LoggerService
from src.core.settings import project_settings
from src.shared.exceptions import InstanceAlreadyExistsError, NoInstanceFoundError
from src.shared.schemas.pagination_schemas import (
    PaginationMetaDataSchema,
    PaginationParams,
)


class FinancingSourceCatalogService:
    def __init__(
        self,
        logger: LoggerService,
        financing_sources_catalog_repository: FinancingSourcesCatalogRepositoryInterface,
    ):
        self._logger = logger
        self._financing_sources_catalog_repository = (
            financing_sources_catalog_repository
        )

    @staticmethod
    def __get_localized_name(
        financing_source: FinancingSourceFullResponseSchema,
    ) -> str:
        chosen_language = get_locale()
        default_language = project_settings.DEFAULT_LANGUAGE

        locales: Dict[str, str] = financing_source.name_locales or {}

        if financing_source.lang == chosen_language:
            return financing_source.name
        if translated := locales.get(chosen_language):
            return translated

        if default_language != chosen_language:
            if financing_source.lang == default_language:
                return financing_source.name
            if translated := locales.get(default_language):
                return translated

        return financing_source.name

    async def get_by_id(
        self,
        financing_source_id: int,
        include_all_locales: bool = False,
    ) -> Union[
        FinancingSourceFullResponseSchema,
        FinancingSourcePartialResponseSchema,
    ]:
        full_schema = await self._financing_sources_catalog_repository.get_by_id(
            financing_source_id
        )
        if not full_schema:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Financing source with ID: %(SRC_ID)s was not found.")
                % {"SRC_ID": financing_source_id},
            )

        if include_all_locales:
            return full_schema

        chosen_language = get_locale()
        localized_name = FinancingSourceCatalogService.__get_localized_name(full_schema)

        return FinancingSourcePartialResponseSchema(
            id=full_schema.id,
            lang=chosen_language,
            name=localized_name,
            code=full_schema.financing_source_code,
            created_at=full_schema.created_at,
            changed_at=full_schema.changed_at,
        )

    async def get_financing_sources(
        self,
        pagination_params: PaginationParams,
        name_filter: Optional[str] = None,
        code_filter: Optional[str] = None,
        include_all_locales: bool = False,
    ) -> MultipleFinancingSourcesSchema:
        page: int = pagination_params.page or 1  # for mypy
        limit: int = pagination_params.limit or 30  # for mypy

        items_full_schemas = (
            await self._financing_sources_catalog_repository.get_financing_sources(
                page=page,
                limit=limit,
                name_filter=name_filter,
                code_filter=code_filter,
            )
        )
        total_items = (
            await self._financing_sources_catalog_repository.get_total_number_of_financing_sources()
        )

        if include_all_locales:
            # type ignore:
            items: List[
                Union[
                    FinancingSourceFullResponseSchema,
                    FinancingSourcePartialResponseSchema,
                ]
            ] = items_full_schemas  # type: ignore[assignment]
        else:
            chosen_language = get_locale()

            items = [
                FinancingSourcePartialResponseSchema(
                    id=financing_source.id,
                    lang=chosen_language,
                    name=FinancingSourceCatalogService.__get_localized_name(
                        financing_source
                    ),
                    code=financing_source.financing_source_code,
                    created_at=financing_source.created_at,
                    changed_at=financing_source.changed_at,
                )
                for financing_source in items_full_schemas
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

        return MultipleFinancingSourcesSchema(
            items=items,
            pagination=pagination,
        )

    async def add_financing_source(
        self, request_dto: AddFinancingSourceSchema
    ) -> FinancingSourceFullResponseSchema:
        # Check that 'name' field is not taken already
        if await self._financing_sources_catalog_repository.get_by_default_name(
            request_dto.name
        ):
            raise InstanceAlreadyExistsError(
                status_code=409,
                detail=_("Financing source with name: '%(NAME)s' already exists.")
                % {"NAME": request_dto.name},
            )

        # Check that 'financing_source_code' is not taken already
        if await self._financing_sources_catalog_repository.get_by_financing_source_code(
            request_dto.financing_source_code
        ):
            raise InstanceAlreadyExistsError(
                status_code=409,
                detail=_("Financing source with code: '%(SRC_CODE)s' already exists.")
                % {"SRC_CODE": request_dto.financing_source_code},
            )

        # Check that value in the 'name_locales' entry is not taken already
        for code, value in request_dto.name_locales.items():
            if await self._financing_sources_catalog_repository.get_by_name_locale(
                code, value
            ):
                raise InstanceAlreadyExistsError(
                    status_code=409,
                    detail=_(
                        "Financing source's '%(CODE)s' locale: '%(VALUE)s' already exists in some "
                        "record's locale. It's already taken."
                    )
                    % {"VALUE": value, "CODE": code},
                )

        return await self._financing_sources_catalog_repository.add_financing_source(
            request_dto
        )

    async def update_financing_source(
        self,
        financing_source_id: int,
        request_dto: UpdateFinancingSourceSchema,
    ) -> FinancingSourceFullResponseSchema:
        # Check if context attribute exists
        existing = await self._financing_sources_catalog_repository.get_by_id(
            financing_source_id
        )
        if not existing:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Financing source with id: %(ID)s not found.")
                % {"ID": financing_source_id},
            )

        default_language = project_settings.DEFAULT_LANGUAGE

        if request_dto.lang is not None and request_dto.lang != existing.lang:
            if request_dto.lang != default_language:
                raise ValueError(
                    _("Field 'lang' must be '%(DEFAULT_LANG)s.'")
                    % {"DEFAULT_LANG": default_language}
                )

        # Check that 'name' is not taken already
        if request_dto.name is not None and request_dto.name != existing.name:
            if await self._financing_sources_catalog_repository.get_by_default_name(
                request_dto.name
            ):
                raise InstanceAlreadyExistsError(
                    status_code=409,
                    detail=_("Financing source with name: '%(NAME)s' already exists.")
                    % {"NAME": request_dto.name},
                )

        # Check that 'financing_source_code' is not taken already
        if (
            request_dto.financing_source_code is not None
            and request_dto.financing_source_code != existing.financing_source_code
        ):
            if await self._financing_sources_catalog_repository.get_by_financing_source_code(
                request_dto.financing_source_code
            ):
                raise InstanceAlreadyExistsError(
                    status_code=409,
                    detail=_(
                        "Financing source with code: '%(SRC_CODE)s' already exists."
                    )
                    % {"SRC_CODE": request_dto.financing_source_code},
                )

        if request_dto.name_locales is not None:
            existing_locales = existing.name_locales or {}
            for language_code, value in request_dto.name_locales.items():
                if existing_locales.get(language_code) == value:
                    continue

                if await self._financing_sources_catalog_repository.get_by_name_locale(
                    language_code, value
                ):
                    raise InstanceAlreadyExistsError(
                        status_code=409,
                        detail=_(
                            "Financing source's '%(CODE)s' locale: '%(VALUE)s' already exists in some "
                            "record's locale. It's already taken."
                        )
                        % {"VALUE": value, "CODE": language_code},
                    )

        updated = (
            await self._financing_sources_catalog_repository.update_financing_source(
                financing_source_id, request_dto
            )
        )

        return updated

    async def delete_by_id(self, financing_source_id: int) -> None:
        # Check if context attribute exists
        existing = await self._financing_sources_catalog_repository.get_by_id(
            financing_source_id
        )
        if not existing:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Financing source with id: %(ID)s not found.")
                % {"ID": financing_source_id},
            )

        await self._financing_sources_catalog_repository.delete_by_id(
            financing_source_id
        )
