from abc import ABC, abstractmethod

from src.apps.registry.interfaces.repository_interfaces import (
    AppointmentRepositoryInterface,
    ScheduleDayRepositoryInterface,
    ScheduleRepositoryInterface,
)


class UnitOfWorkInterface(ABC):
    schedule_day_repository: ScheduleDayRepositoryInterface
    schedule_repository: ScheduleRepositoryInterface
    appointment_repository: AppointmentRepositoryInterface

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass
