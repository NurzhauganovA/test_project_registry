from types import TracebackType
from typing import Optional, Type

from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.registry.interfaces.uow_interface import UnitOfWorkInterface
from src.core.logger import LoggerService


class BaseUnitOfWork(UnitOfWorkInterface):
    def __init__(self, session: AsyncSession, logger: LoggerService):
        self._session = session
        self._logger = logger
        self._is_active = False

    async def __aenter__(self) -> "BaseUnitOfWork":
        self._is_active = True
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()

        await self._session.close()
        self._is_active = False

    async def commit(self) -> None:
        """Commit the current transaction."""
        if self._is_active and self._session.in_transaction():
            await self._session.commit()

    async def rollback(self) -> None:
        """Rollback the current transaction."""
        if self._is_active and self._session.in_transaction():
            await self._session.rollback()
