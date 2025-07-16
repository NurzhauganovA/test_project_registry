from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.session import sessionmaker


async def provide_async_session(
    session_factory: sessionmaker,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Asynchronous session provider for SQLAlchemy.

    This helper yields a new AsyncSession using a session factory,
    and ensures the session is correctly closed after use.

    Args:
        session_factory (sessionmaker): SQLAlchemy async session factory.

    Yields:
        AsyncSession: An instance of SQLAlchemy AsyncSession.

    Example:
        async_db_session = providers.Resource(provide_async_session, session_factory)
        # In your DI container, pass session_factory as argument.

    Note:
        Use this helper with Dependency Injector's `providers.Resource` to ensure
        per-request session lifecycle management.
    """
    async with session_factory() as session:
        yield session
