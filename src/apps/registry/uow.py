from src.apps.registry.infrastructure.repositories.appointment_repository import (
    AppointmentRepositoryImpl,
)
from src.apps.registry.infrastructure.repositories.schedule_day_repostiory import (
    ScheduleDayRepositoryImpl,
)
from src.apps.registry.infrastructure.repositories.schedule_repository import (
    ScheduleRepositoryImpl,
)
from src.shared.base_uow import BaseUnitOfWork


class UnitOfWorkImpl(BaseUnitOfWork):
    @property
    def schedule_day_repository(self) -> ScheduleDayRepositoryImpl:
        return ScheduleDayRepositoryImpl(
            async_db_session=self._session, logger=self._logger
        )

    @property
    def schedule_repository(self) -> ScheduleRepositoryImpl:
        return ScheduleRepositoryImpl(
            async_db_session=self._session, logger=self._logger
        )

    @property
    def appointment_repository(self) -> AppointmentRepositoryImpl:
        return AppointmentRepositoryImpl(
            async_db_session=self._session, logger=self._logger
        )
