from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Dict, List, Optional
from uuid import UUID

from src.apps.catalogs.infrastructure.api.schemas.requests.diagnoses_catalog_request_schemas import (
    AddDiagnosedPatientDiagnosisRecordRequestSchema,
    UpdateDiagnosedPatientDiagnosisRecordRequestSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.diagnoses_catalog_response_schemas import (
    DiagnosedPatientDiagnosisResponseSchema,
)


class DiagnosedPatientDiagnosisRepositoryInterface(ABC):
    @abstractmethod
    async def get_total_number_of_patients_and_diagnoses_records(self) -> int:
        """
        Retrieve a number of ALL patient and diagnoses records from the Registry Service DB.

        :return: Number of ALL patients and diagnoses from the Registry Service DB as INT
        """
        pass

    @abstractmethod
    async def exists_patient_diagnosis_record(
        self,
        patient_id: UUID,
        diagnosis_id: int,
        date_diagnosed: Optional[date] = None,
        exclude_id: Optional[UUID] = None,
    ) -> bool:
        """
        Checks if a patient diagnosis record already exists for the given patient, diagnosis, and date.

        This method is used to ensure the uniqueness of patient diagnosis records based on
        the combination of `patient_id`, `diagnosis_id`, and `date_diagnosed`.
        Optionally, an existing record can be excluded from the check (useful for update operations).

        Args:
            patient_id: Unique identifier of the patient.
            diagnosis_id: Unique identifier of the diagnosis.
            date_diagnosed: Date of diagnosis (Optional).
            exclude_id: Unique identifier of a record to exclude from the check (for updates). Optional.

        Returns:
            True if a conflicting record exists, False otherwise.
        """
        pass

    @abstractmethod
    async def get_by_id(
        self, record_id: UUID
    ) -> Optional[DiagnosedPatientDiagnosisResponseSchema]:
        """
        Retrieve a patient's diagnosis record by its unique identifier.

        :param record_id: Unique identifier of the patient's diagnosis record.
        :type record_id: UUID
        :return: Patient's diagnosis instance or None if not found.

        :rtype: Optional[DiagnosedPatientDiagnosisResponseSchema]
        """
        pass

    @abstractmethod
    async def get_patient_and_diagnoses_records(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        limit: int = 30,
    ) -> List[DiagnosedPatientDiagnosisResponseSchema]:
        """
        Retrieve a list of patient and diagnoses records, filtered by params if needed.

        :param filters: Parameters to filter records by.
        :param page: Pagination page parameter.
        :type page: int
        :param limit: Pagination limit (per page) parameter.
        :type limit: int

        :return: List of matching patient and diagnoses records.
        :rtype: List[DiagnosedPatientDiagnosisResponseSchema]
        """
        pass

    @abstractmethod
    async def add_patient_diagnosis_record(
        self, request_dto: AddDiagnosedPatientDiagnosisRecordRequestSchema
    ) -> DiagnosedPatientDiagnosisResponseSchema:
        """
        Add a new patient's diagnosis record to the DB.

        :param request_dto: Data for creating a new patient's diagnosis record.
        :type request_dto: AddDiagnosedPatientDiagnosisRecordRequestSchema

        :return: The created patient's diagnosis record.
        :rtype: DiagnosedPatientDiagnosisResponseSchema
        """
        pass

    @abstractmethod
    async def update_patient_diagnosis_record(
        self,
        record_id: UUID,
        request_dto: UpdateDiagnosedPatientDiagnosisRecordRequestSchema,
    ) -> DiagnosedPatientDiagnosisResponseSchema:
        """
        Update an existing patient's diagnosis record.

        :param record_id: Patient's diagnosis record ID to update.
        :param request_dto: Data for updating a patient's diagnosis record.
        :type request_dto: UpdateDiagnosedPatientDiagnosisRecordRequestSchema

        :return: The updated diagnosis record.
        :rtype: DiagnosedPatientDiagnosisResponseSchema
        """
        pass

    @abstractmethod
    async def delete_by_id(self, record_id: UUID) -> None:
        """
        Delete a patient's diagnosis record by its unique identifier.

        :param record_id: Unique identifier of the patient's diagnoses record to delete.
        :type record_id: UUID
        :return: None
        """
        pass
