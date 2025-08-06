from abc import ABC, abstractmethod
from types import TracebackType
from typing import Optional, Type

from src.apps.registry.interfaces.repository_interfaces import (
    AppointmentRepositoryInterface,
    ScheduleDayRepositoryInterface,
    ScheduleRepositoryInterface,
)


class UnitOfWorkInterface(ABC):
    @property
    @abstractmethod
    def schedule_day_repository(self) -> ScheduleDayRepositoryInterface:
        ...

    @property
    @abstractmethod
    def schedule_repository(self) -> ScheduleRepositoryInterface:
        ...

    @property
    @abstractmethod
    def appointment_repository(self) -> AppointmentRepositoryInterface:
        ...

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWorkInterface":
        ...

    @abstractmethod
    async def __aexit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType],
    ) -> None:
        ...
