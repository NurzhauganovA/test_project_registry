from typing import List, Tuple
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from src.apps.catalogs.services.citizenship_catalog_service import (
    CitizenshipCatalogService,
)
from src.apps.catalogs.services.financing_sources_catalog_service import (
    FinancingSourceCatalogService,
)
from src.apps.catalogs.services.medical_organizations_catalog_service import (
    MedicalOrganizationsCatalogService,
)
from src.apps.catalogs.services.nationalities_catalog_service import (
    NationalitiesCatalogService,
)
from src.apps.catalogs.services.patient_context_attribute_service import (
    PatientContextAttributeService,
)
from src.apps.patients.domain.patient import PatientDomain
from src.apps.patients.infrastructure.api.schemas.requests.patient_request_schemas import (
    UpdatePatientSchema,
)
from src.apps.patients.infrastructure.api.schemas.requests.patients_filter_params import (
    PatientsFilterParams,
)
from src.apps.patients.infrastructure.repositories.patient_repository import (
    SQLAlchemyPatientRepository,
)
from src.apps.patients.interfaces.uow_interface import UnitOfWorkInterface
from src.apps.patients.mappers import map_update_schema_to_domain
from src.core.i18n import _
from src.shared.exceptions import (
    ApplicationError,
    DeleteRestrictedError,
    InstanceAlreadyExistsError,
    NoInstanceFoundError,
)
from src.shared.schemas.pagination_schemas import PaginationParams


class PatientService:
    def __init__(
        self,
        uow: UnitOfWorkInterface,
        patients_repository: SQLAlchemyPatientRepository,
        citizenship_service: CitizenshipCatalogService,
        nationalities_service: NationalitiesCatalogService,
        medical_org_service: MedicalOrganizationsCatalogService,
        financing_source_service: FinancingSourceCatalogService,
        patient_context_attributes_service: PatientContextAttributeService,
    ):
        self._uow = uow
        self._patients_repository = patients_repository
        self._citizenship_service = citizenship_service
        self._nationalities_service = nationalities_service
        self._medical_org_service = medical_org_service
        self._financing_source_service = financing_source_service
        self._patient_context_attributes_service = patient_context_attributes_service

    async def _validate_related_entities(self, patient: PatientDomain) -> None:
        """Checks that all FK and M2M connections for a patient exist by calling catalog services."""
        # ONE-to-ONE relations
        await self._citizenship_service.get_by_id(patient.citizenship_id)
        await self._nationalities_service.get_by_id(patient.nationality_id)

        attachment_data = patient.attachment_data
        if attachment_data:
            attached_clinic_id = attachment_data.get("attached_clinic_id")
            if attached_clinic_id:
                await self._medical_org_service.get_by_id(attached_clinic_id)

        # MANY-to-MANY relations
        for source_id in patient.financing_sources_ids:
            await self._financing_source_service.get_by_id(source_id)

        if patient.context_attributes_ids:
            for attribute_id in patient.context_attributes_ids:
                await self._patient_context_attributes_service.get_by_id(attribute_id)

    async def get_by_id(self, patient_id: UUID) -> PatientDomain:
        patient = await self._patients_repository.get_by_id(patient_id)
        if not patient:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Patient with ID: '%(ID)s' not found.") % {"ID": patient_id},
            )

        return patient

    async def get_by_iin(self, patient_iin: str) -> PatientDomain:
        patient = await self._patients_repository.get_by_iin(patient_iin)
        if not patient:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Patient with IIN: '%(IIN)s' not found.")
                % {"IIN": patient_iin},
            )

        return patient

    async def get_patients(
        self,
        filter_params: PatientsFilterParams,
        pagination_params: PaginationParams,
    ) -> Tuple[List[PatientDomain], int]:
        total_amount_of_patients: int = (
            await self._patients_repository.get_total_number_of_patients()
        )

        patients = await self._patients_repository.get_patients(
            filters=filter_params.to_dict(exclude_none=True),
            page=pagination_params.page,
            limit=pagination_params.limit,
        )

        return patients, total_amount_of_patients

    async def create_patient(self, patient: PatientDomain) -> PatientDomain:
        # Check if this IIN is not taken already
        existing_patient_by_iin = await self._patients_repository.get_by_iin(
            patient.iin
        )
        if existing_patient_by_iin:
            raise InstanceAlreadyExistsError(
                status_code=409,
                detail=_("Patient with IIN: '%(IIN)s' already exists.")
                % {"IIN": patient.iin},
            )

        # Check that all ONE-to-ONE and MANY-to-MANY relations for patient exist
        await self._validate_related_entities(patient)

        async with self._uow:
            created = await self._uow.patients_repository.create_patient(patient)

        return created

    async def update_patient(
        self, patient_id: UUID, dto: UpdatePatientSchema
    ) -> PatientDomain:
        # Check that patient with this ID exists
        existing_patient = await self.get_by_id(patient_id)
        patient_to_update: PatientDomain = map_update_schema_to_domain(
            dto, existing_patient
        )

        # Check if this IIN is not taken already
        if dto.iin is not None:
            existing_patient_by_iin = await self._patients_repository.get_by_iin(
                dto.iin
            )
            if existing_patient_by_iin and existing_patient_by_iin.id != patient_id:
                raise InstanceAlreadyExistsError(
                    status_code=409,
                    detail=_("Patient with IIN: '%(IIN)s' already exists.")
                    % {"IIN": dto.iin},
                )

        # Check that all ONE-to-ONE and MANY-to-MANY relations for patient exist
        await self._validate_related_entities(patient_to_update)

        async with self._uow:
            await self._uow.patients_repository.update_patient(patient_to_update)

        # Get fresh patients since 'update_patient' repository method doesn't reload a query
        fresh_patient: PatientDomain | None = await self._patients_repository.get_by_id(
            patient_id
        )
        if fresh_patient is None:
            raise ApplicationError(
                status_code=500,
                detail=_("Something went wrong. Please, try again later."),
            )

        return fresh_patient

    async def update_patient_attachment_data(
        self, patient_id: UUID, attachment_data: dict
    ) -> PatientDomain:
        """
        Обновить attachment_data пациента

        :param patient_id: ID пациента
        :param attachment_data: Новые данные прикрепления
        :return: Обновленная доменная модель пациента
        """
        # Получаем существующего пациента
        patient = await self.get_by_id(patient_id)

        # Обновляем attachment_data
        patient.attachment_data = attachment_data

        async with self._uow:
            updated_patient = await self._uow.patients_repository.update_patient(
                patient
            )

        return updated_patient

    async def delete_patient(self, patient_id: UUID) -> None:
        # Check that patient with this ID exists
        await self.get_by_id(patient_id)

        try:
            async with self._uow:
                await self._uow.patients_repository.delete_by_id(patient_id)
        except IntegrityError as err:
            raise DeleteRestrictedError(
                status_code=409,
                detail=_(
                    "Impossible to delete patient with ID: '%(ID)s'. Related entities exist."
                ),
            ) from err
