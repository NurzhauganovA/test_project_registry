import math
from datetime import date
from typing import List, Optional
from uuid import UUID

from src.apps.catalogs.exceptions import InactiveDiagnosisError
from src.apps.catalogs.infrastructure.api.schemas.requests.diagnoses_catalog_request_schemas import (
    AddDiagnosedPatientDiagnosisRecordRequestSchema,
    UpdateDiagnosedPatientDiagnosisRecordRequestSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.requests.filters.diagnoses_and_patients_filters import (
    DiagnosesAndPatientsFilterParams,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.diagnoses_catalog_response_schemas import (
    DiagnosedPatientDiagnosisResponseSchema,
    MultipleDiagnosedPatientDiagnosisResponseSchema,
)
from src.apps.catalogs.interfaces.diagnoses_and_patients_repository_interface import (
    DiagnosedPatientDiagnosisRepositoryInterface,
)
from src.apps.catalogs.services.diagnoses_catalogue_service import (
    DiagnosesCatalogService,
)
from src.apps.patients.services.patients_service import PatientService
from src.apps.users.services.user_service import UserService
from src.core.i18n import _
from src.core.logger import LoggerService
from src.shared.exceptions import NoInstanceFoundError
from src.shared.schemas.pagination_schemas import (
    PaginationMetaDataSchema,
    PaginationParams,
)


class DiagnosedPatientDiagnosisService:
    def __init__(
        self,
        logger: LoggerService,
        diagnoses_catalog_service: DiagnosesCatalogService,
        patient_service: PatientService,
        user_service: UserService,
        diagnosed_patient_diagnosis_repository: DiagnosedPatientDiagnosisRepositoryInterface,
    ):
        self._logger = logger
        self._diagnoses_catalog_service = diagnoses_catalog_service
        self._patient_service = patient_service
        self._user_service = user_service
        self._diagnosed_patient_diagnosis_repository = (
            diagnosed_patient_diagnosis_repository
        )

    @staticmethod
    def _check_record_exists_by_id(
        record: Optional[DiagnosedPatientDiagnosisResponseSchema],
        original_id: UUID,
    ) -> DiagnosedPatientDiagnosisResponseSchema:
        """
        Checks if a diagnosed patient diagnosis record exists by its ID.

        Args:
            record: The diagnosis record object returned from the repository or None.
            original_id: The ID that was requested.

        Returns:
            The record object if it exists.

        Raises:
            NoInstanceFoundError: If the record was not found.
        """
        if record:
            return record

        raise NoInstanceFoundError(
            status_code=404,
            detail=_("Patient diagnosis record with ID: %(ID)s was not found.")
            % {"ID": str(original_id)},
        )

    async def _check_record_is_unique(
        self,
        patient_id: UUID,
        diagnosis_id: int,
        date_diagnosed: Optional[date] = None,
        exclude_id: Optional[UUID] = None,
    ):
        """
        Checks that no other record with the same patient, diagnosis, and date exists.

        Args:
            patient_id: UUID of the patient.
            diagnosis_id: int ID of the diagnosis.
            date_diagnosed: (Optional) Date of diagnosis.
            exclude_id: (Optional) Exclude this record (for updates).

        Raises:
            InstanceAlreadyExistsError: If a conflicting record already exists.
        """
        exists = await self._diagnosed_patient_diagnosis_repository.exists_patient_diagnosis_record(
            patient_id=patient_id,
            diagnosis_id=diagnosis_id,
            date_diagnosed=date_diagnosed,
            exclude_id=exclude_id,
        )
        if exists:
            from src.shared.exceptions import InstanceAlreadyExistsError

            raise InstanceAlreadyExistsError(
                status_code=409,
                detail=_(
                    "Diagnosis record for this patient, diagnosis and date already exists."
                ),
            )

    async def get_by_id(
        self,
        record_id: UUID,
    ) -> DiagnosedPatientDiagnosisResponseSchema:
        record = await self._diagnosed_patient_diagnosis_repository.get_by_id(record_id)
        return self._check_record_exists_by_id(record, record_id)

    async def get_patient_and_diagnoses_records(
        self,
        filters: DiagnosesAndPatientsFilterParams,
        pagination_params: PaginationParams,
    ) -> MultipleDiagnosedPatientDiagnosisResponseSchema:
        page: int = pagination_params.page or 1
        limit: int = pagination_params.limit or 30

        items: List[DiagnosedPatientDiagnosisResponseSchema] = (
            await self._diagnosed_patient_diagnosis_repository.get_patient_and_diagnoses_records(
                filters=filters.to_dict(exclude_none=True),
                page=page,
                limit=limit,
            )
        )

        total_items = (
            await self._diagnosed_patient_diagnosis_repository.get_total_number_of_patients_and_diagnoses_records()
        )

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

        return MultipleDiagnosedPatientDiagnosisResponseSchema(
            items=items,
            pagination=pagination,
        )

    async def add_patient_diagnosis_record(
        self, request_dto: AddDiagnosedPatientDiagnosisRecordRequestSchema
    ) -> DiagnosedPatientDiagnosisResponseSchema:
        # Check that diagnosis, patient and doctor (if provided) exist
        diagnoses = await self._diagnoses_catalog_service.get_by_id(
            request_dto.diagnosis_id
        )
        await self._patient_service.get_by_id(request_dto.patient_id)
        if request_dto.doctor_id:
            await self._user_service.get_by_id(request_dto.doctor_id)

        if not diagnoses.is_active:
            raise InactiveDiagnosisError(
                status_code=409, detail=_("Provided diagnosis is not active.")
            )

        # Check for uniqueness: no duplicate record for patient + diagnosis + date
        await self._check_record_is_unique(
            patient_id=request_dto.patient_id,
            diagnosis_id=request_dto.diagnosis_id,
            date_diagnosed=request_dto.date_diagnosed,
        )

        return await self._diagnosed_patient_diagnosis_repository.add_patient_diagnosis_record(
            request_dto
        )

    async def update_patient_diagnosis_record(
        self,
        record_id: UUID,
        request_dto: UpdateDiagnosedPatientDiagnosisRecordRequestSchema,
    ) -> DiagnosedPatientDiagnosisResponseSchema:
        existing = await self._diagnosed_patient_diagnosis_repository.get_by_id(
            record_id
        )
        existing = self._check_record_exists_by_id(existing, record_id)

        # Determine fields for uniqueness check (take from DTO if present, else from existing)
        patient_id = getattr(request_dto, "patient_id", None) or existing.patient.id
        diagnosis_id = (
            getattr(request_dto, "diagnosis_id", None) or existing.diagnosis.id
        )
        date_diagnosed = (
            getattr(request_dto, "date_diagnosed", None) or existing.date_diagnosed
        )

        # Check for uniqueness: no duplicate record for patient + diagnosis + date (excluding current)
        await self._check_record_is_unique(
            patient_id=patient_id,
            diagnosis_id=diagnosis_id,
            date_diagnosed=date_diagnosed,
            exclude_id=record_id,
        )

        # Check that doctor exists (if provided)
        if request_dto.doctor_id:
            await self._user_service.get_by_id(request_dto.doctor_id)

        updated = await self._diagnosed_patient_diagnosis_repository.update_patient_diagnosis_record(
            record_id, request_dto
        )

        return updated

    async def delete_by_id(self, record_id: UUID) -> None:
        # Check that record exists
        existing = await self._diagnosed_patient_diagnosis_repository.get_by_id(
            record_id
        )
        self._check_record_exists_by_id(existing, record_id)

        await self._diagnosed_patient_diagnosis_repository.delete_by_id(record_id)
