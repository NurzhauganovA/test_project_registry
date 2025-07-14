from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID

from src.apps.patients.domain.patient import PatientDomain


class PatientRepositoryInterface(ABC):
    @abstractmethod
    async def get_total_number_of_patients(self) -> int:
        """
        Retrieve a number of ALL patients from the Registry Service DB.

        :return: Amount of ALL patients from the Registry Service DB as INT
        """
        pass

    @abstractmethod
    async def get_by_id(self, patient_id: UUID) -> Optional[PatientDomain]:
        """
        Retrieves a patient by its id from the DB or None if nothing was found.

        :param patient_id: Patient's unique identifier
        :return: Patient domain object or None if nothing was found.
        """
        pass

    @abstractmethod
    async def get_by_iin(self, patient_iin: str) -> Optional[PatientDomain]:
        """
        Retrieves a patient by its IIN from the DB or None if nothing was found.

        :param patient_iin: Patient's IIN
        :return: Patient domain object or None if nothing was found.
        """
        pass

    @abstractmethod
    async def get_patients(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        limit: int = 30,
    ) -> List[PatientDomain]:
        """
        Retrieves a patients from the DB based on the given filters (if provided).

        :param filters: Parameters to filter patients by
        :param page: Pagination parameter (page number)
        :param limit: Pagination parameter (items per page)

        :return: Patient domain object or None if nothing was found.
        """
        pass

    @abstractmethod
    async def create_patient(self, patient_domain: PatientDomain) -> PatientDomain:
        """
        Creates a new patient.

        :param patient_domain: Patient domain object
        :return: Patient domain object
        """
        pass

    @abstractmethod
    async def update_patient(self, patient_domain: PatientDomain) -> PatientDomain:
        """
        Updates the patient.

        :param patient_domain: Patient domain object
        :return: Patient domain object
        """
        pass

    @abstractmethod
    async def delete_by_id(self, patient_id: UUID) -> None:
        """
        Deletes a patient by its id from the DB.

        :param patient_id: Patient's unique identifier
        """
        pass
