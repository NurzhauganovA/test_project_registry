from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Dict, List, Optional
from uuid import UUID

from src.apps.registry.domain.models.appointment import AppointmentDomain
from src.apps.registry.domain.models.schedule import ScheduleDomain
from src.apps.registry.infrastructure.api.schemas.requests.schedule_day_schemas import (
    CreateScheduleDaySchema,
    UpdateScheduleDaySchema,
)
from src.apps.registry.infrastructure.api.schemas.responses.schedule_day_schemas import (
    ResponseScheduleDaySchema,
)


class AppointmentRepositoryInterface(ABC):
    @abstractmethod
    async def get_total_number_of_appointments(self) -> int:
        """
        Retrieve a number of ALL appointments from the Registry Service DB.

        :return: Number of ALL appointments from the Registry Service DB as INT
        """
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[AppointmentDomain]:
        pass

    @abstractmethod
    async def get_appointments_by_day_id(
        self, schedule_day_id: UUID
    ) -> List[AppointmentDomain]:
        pass

    @abstractmethod
    async def get_by_schedule_id(
        self, schedule_id: UUID, page: int = 1, limit: int = 30
    ) -> List[AppointmentDomain]:
        """Gets a list of appointment records for the specified schedule, with pagination."""
        pass

    @abstractmethod
    async def get_appointments(
        self,
        filters: Dict[str, Any],
        limit: int = 30,
        page: int = 1,
    ) -> List[AppointmentDomain]:
        """
        Returns a list of scheduled appointment records filtered by the provided params.

        :param filters: Dictionary of filter parameters.
        :param limit: Pagination limit per page.
        :param page: Pagination page.

        :return: List of 'AppointmentDomain' objects.
        """
        pass

    @abstractmethod
    async def add(self, appointment: AppointmentDomain) -> AppointmentDomain:
        pass

    @abstractmethod
    async def update(self, appointment: AppointmentDomain) -> AppointmentDomain:
        pass

    @abstractmethod
    async def delete_by_id(self, id: int) -> None:
        pass


class ScheduleDayRepositoryInterface(ABC):
    @abstractmethod
    async def get_total_number_of_schedule_days(self) -> int:
        """
        Retrieve a number of ALL schedule days from the Registry Service DB.

        :return: Number of ALL schedule days from the Registry Service DB as INT
        """
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[ResponseScheduleDaySchema]:
        pass

    @abstractmethod
    async def get_by_schedule_and_day_of_week(
        self, schedule_id: UUID, day_of_week: int
    ) -> Optional[ResponseScheduleDaySchema]:
        pass

    @abstractmethod
    async def get_by_schedule_and_date(
        self, schedule_id: UUID, day_date: date
    ) -> Optional[ResponseScheduleDaySchema]:
        pass

    @abstractmethod
    async def get_all_by_schedule_id(
        self, schedule_id: UUID, limit: int = 30, page: int = 1
    ) -> List[ResponseScheduleDaySchema]:
        pass

    @abstractmethod
    async def add(
        self, day_schema: CreateScheduleDaySchema
    ) -> ResponseScheduleDaySchema:
        pass

    @abstractmethod
    async def update(
        self, day_id: UUID, schema: UpdateScheduleDaySchema
    ) -> ResponseScheduleDaySchema:
        pass

    @abstractmethod
    async def delete_by_id(self, id: UUID) -> None:
        pass


class ScheduleRepositoryInterface(ABC):
    @abstractmethod
    async def get_total_number_of_schedules(self) -> int:
        """
        Retrieve a number of ALL schedules from the Registry Service DB.

        :return: Amount of ALL schedules from the Registry Service DB as INT
        """
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[ScheduleDomain]:
        pass

    @abstractmethod
    async def get_schedule_by_day_id(self, day_id: UUID) -> Optional[ScheduleDomain]:
        pass

    @abstractmethod
    async def get_schedules(
        self,
        filters: dict,
        page: int = 1,
        limit: int = 30,
    ) -> List[ScheduleDomain]:
        """
        Retrieves a list of graphs from the database, taking into account the passed filters and pagination.

        :param filters: Dictionary with search filters
        (e.g., name_filter, doctor_id_filter, doctor_full_name_filter, etc.)
        :param page: Page number (for pagination), starts with 1
        :param limit: Number of elements per page (default: 30)

        :return: List of graph domain models corresponding to filters and pagination
        """
        pass

    @abstractmethod
    async def add(self, schedule: ScheduleDomain) -> ScheduleDomain:
        pass

    @abstractmethod
    async def update(self, schedule: ScheduleDomain) -> ScheduleDomain:
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        pass
