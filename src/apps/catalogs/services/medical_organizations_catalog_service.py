import math
from typing import Dict, List, Union

from src.apps.catalogs.infrastructure.api.schemas.requests.filters.medical_organizations_catalog_filters import (
    MedicalOrganizationsCatalogFilterParams,
)
from src.apps.catalogs.infrastructure.api.schemas.requests.medical_organizations_catalog_schemas import (
    AddMedicalOrganizationSchema,
    UpdateMedicalOrganizationSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.medical_organizations_catalog_schemas import (
    MedicalOrganizationCatalogFullResponseSchema,
    MedicalOrganizationCatalogPartialResponseSchema,
    MultipleMedicalOrganizationsSchema,
)
from src.apps.catalogs.interfaces.medical_organizations_catalog_repository_interface import (
    MedicalOrganizationsCatalogRepositoryInterface,
)
from src.core.i18n import _, get_locale
from src.core.logger import LoggerService
from src.core.settings import project_settings
from src.shared.exceptions import InstanceAlreadyExistsError, NoInstanceFoundError
from src.shared.schemas.pagination_schemas import (
    PaginationMetaDataSchema,
    PaginationParams,
)


class MedicalOrganizationsCatalogService:
    def __init__(
        self,
        logger: LoggerService,
        medical_organizations_catalog_repository: MedicalOrganizationsCatalogRepositoryInterface,
    ):
        self._logger = logger
        self._medical_organizations_catalog_repository = (
            medical_organizations_catalog_repository
        )

    @staticmethod
    def __get_localized_field(
        base_value: str,
        field_locales: Dict[str, str],
        obj_lang: str,
        chosen_language: str,
        default_language: str,
    ) -> str:
        """
        A generic method for getting the localized value of a field.
        """
        if obj_lang == chosen_language:
            return base_value
        if translated := field_locales.get(chosen_language):
            return translated

        if default_language != chosen_language:
            if obj_lang == default_language:
                return base_value

            if translated := field_locales.get(default_language):
                return translated

        return base_value

    @staticmethod
    def __get_localized_name(
        medical_organization: MedicalOrganizationCatalogFullResponseSchema,
    ) -> str:
        chosen_language = get_locale()
        default_language = project_settings.DEFAULT_LANGUAGE
        locales: Dict[str, str] = medical_organization.name_locales or {}
        return MedicalOrganizationsCatalogService.__get_localized_field(
            base_value=medical_organization.name,
            field_locales=locales,
            obj_lang=medical_organization.lang,
            chosen_language=chosen_language,
            default_language=default_language,
        )

    @staticmethod
    def __get_localized_address(
        medical_organization: MedicalOrganizationCatalogFullResponseSchema,
    ) -> str:
        chosen_language = get_locale()
        default_language = project_settings.DEFAULT_LANGUAGE
        locales: Dict[str, str] = medical_organization.address_locales or {}
        return MedicalOrganizationsCatalogService.__get_localized_field(
            base_value=medical_organization.address,
            field_locales=locales,
            obj_lang=medical_organization.lang,
            chosen_language=chosen_language,
            default_language=default_language,
        )

    async def get_by_id(
        self,
        medical_organization_id: int,
        include_all_locales: bool = False,
    ) -> MedicalOrganizationCatalogFullResponseSchema |  MedicalOrganizationCatalogPartialResponseSchema:
        full_schema = await self._medical_organizations_catalog_repository.get_by_id(
            medical_organization_id
        )
        if not full_schema:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Medical organization with ID: %(ORG_ID)s was not found.")
                % {"ORG_ID": medical_organization_id},
            )

        if include_all_locales:
            return full_schema

        chosen_language = get_locale()
        localized_name = MedicalOrganizationsCatalogService.__get_localized_name(
            full_schema
        )
        localized_address = MedicalOrganizationsCatalogService.__get_localized_address(
            full_schema,
        )

        return MedicalOrganizationCatalogPartialResponseSchema(
            id=full_schema.id,
            name=localized_name,
            organization_code=full_schema.organization_code,
            address=localized_address,
            lang=chosen_language,
            created_at=full_schema.created_at,
            changed_at=full_schema.changed_at,
        )

    async def get_medical_organizations(
        self,
        pagination_params: PaginationParams,
        filter_params: MedicalOrganizationsCatalogFilterParams,
        include_all_locales: bool = False,
    ) -> MultipleMedicalOrganizationsSchema:
        page: int = pagination_params.page or 1  # for mypy
        limit: int = pagination_params.limit or 30  # for mypy

        items_full_schemas = await self._medical_organizations_catalog_repository.get_medical_organizations(
            page=page,
            limit=limit,
            name_filter=filter_params.name_filter,
            organization_code_filter=filter_params.organization_code_filter,
            address_filter=filter_params.address_filter,
        )
        total_items = (
            await self._medical_organizations_catalog_repository.get_total_number_of_medical_organizations()
        )

        if include_all_locales:
            # type ignore:
            items: List[
                Union[
                    MedicalOrganizationCatalogFullResponseSchema,
                    MedicalOrganizationCatalogPartialResponseSchema,
                ]
            ] = items_full_schemas  # type: ignore[assignment]
        else:
            chosen_language = get_locale()

            items = [
                MedicalOrganizationCatalogPartialResponseSchema(
                    id=medical_organization.id,
                    lang=chosen_language,
                    organization_code=medical_organization.organization_code,
                    address=MedicalOrganizationsCatalogService.__get_localized_address(
                        medical_organization
                    ),
                    name=MedicalOrganizationsCatalogService.__get_localized_name(
                        medical_organization
                    ),
                    created_at=medical_organization.created_at,
                    changed_at=medical_organization.changed_at,
                )
                for medical_organization in items_full_schemas
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

        return MultipleMedicalOrganizationsSchema(
            items=items,
            pagination=pagination,
        )

    async def add_medical_organization(
        self, request_dto: AddMedicalOrganizationSchema
    ) -> MedicalOrganizationCatalogFullResponseSchema:
        # Check that 'name' field is not taken already
        if await self._medical_organizations_catalog_repository.get_by_default_name(
            request_dto.name
        ):
            raise InstanceAlreadyExistsError(
                status_code=409,
                detail=_("Medical organization with name: '%(NAME)s' already exists.")
                % {"NAME": request_dto.name},
            )

        # Check that 'code' (organization internal code) is not taken already
        if await self._medical_organizations_catalog_repository.get_by_organization_code(
            request_dto.organization_code
        ):
            raise InstanceAlreadyExistsError(
                status_code=409,
                detail=_(
                    "Medical organization with internal code: '%(ORG_CODE)s' already exists."
                )
                % {"ORG_CODE": request_dto.organization_code},
            )

        # Check that value in the 'name_locales' entry is not taken already
        for code, value in request_dto.name_locales.items():
            if await self._medical_organizations_catalog_repository.get_by_name_locale(
                code, value
            ):
                raise InstanceAlreadyExistsError(
                    status_code=409,
                    detail=_(
                        "Medical organization's '%(CODE)s' name locale: '%(VALUE)s' already exists in some "
                        "record's name locale. It's already taken."
                    )
                    % {"VALUE": value, "CODE": code},
                )

        return await self._medical_organizations_catalog_repository.add_medical_organization(
            request_dto
        )

    async def update_medical_organization(
        self,
        context_attribute_id: int,
        request_dto: UpdateMedicalOrganizationSchema,
    ) -> MedicalOrganizationCatalogFullResponseSchema:
        # Check if context attribute exists
        existing = await self._medical_organizations_catalog_repository.get_by_id(
            context_attribute_id
        )
        if not existing:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Medical organization with id: %(ID)s not found.")
                % {"ID": context_attribute_id},
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
            if await self._medical_organizations_catalog_repository.get_by_default_name(
                request_dto.name
            ):
                raise InstanceAlreadyExistsError(
                    status_code=409,
                    detail=_(
                        "Medical organization with name: '%(NAME)s' already exists."
                    )
                    % {"NAME": request_dto.name},
                )

        # Check that 'code' (organization internal code) is not taken already
        if (
            request_dto.organization_code is not None
            and request_dto.organization_code != existing.organization_code
        ):
            if (
                request_dto.organization_code is not None
                and request_dto.organization_code != existing.organization_code
            ):
                if await self._medical_organizations_catalog_repository.get_by_organization_code(
                    request_dto.organization_code
                ):
                    raise InstanceAlreadyExistsError(
                        status_code=409,
                        detail=_(
                            "Medical organization with internal code: '%(ORG_CODE)s' already exists."
                        )
                        % {"ORG_CODE": request_dto.organization_code},
                    )

        if request_dto.name_locales is not None:
            existing_locales = existing.name_locales or {}
            for language_code, value in request_dto.name_locales.items():
                if existing_locales.get(language_code) == value:
                    continue

                if await self._medical_organizations_catalog_repository.get_by_name_locale(
                    language_code, value
                ):
                    raise InstanceAlreadyExistsError(
                        status_code=409,
                        detail=_(
                            "Medical organization's '%(CODE)s' locale: '%(VALUE)s' already exists in some "
                            "record's locale. It's already taken."
                        )
                        % {"VALUE": value, "CODE": language_code},
                    )

        updated = await self._medical_organizations_catalog_repository.update_medical_organization(
            context_attribute_id, request_dto
        )

        return updated

    async def delete_by_id(self, context_attribute_id: int) -> None:
        # Check if context attribute exists
        existing = await self._medical_organizations_catalog_repository.get_by_id(
            context_attribute_id
        )
        if not existing:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Medical organization with id: %(ID)s not found.")
                % {"ID": context_attribute_id},
            )

        await self._medical_organizations_catalog_repository.delete_by_id(
            context_attribute_id
        )
