from functools import wraps

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.shared.exceptions import UniqueViolationError


def transactional(method):
    """
    Async decorator to wrap repository methods with automatic rollback on exceptions.

    This decorator ensures that if an exception occurs during the execution of
    the decorated async method, the associated SQLAlchemy AsyncSession will
    perform a rollback to clean up the transaction state.

    It helps prevent `PendingRollbackError` exceptions caused by unhandled
    transaction failures where a session remains in a failed state without rollback.

    Typical use case: wrapping async CRUD methods that perform database operations
    via `self._async_db_session`. When an exception occurs (e.g., integrity error),
    this decorator triggers rollback to keep the session usable for subsequent calls.

    Args:
        method (Callable): The async method to decorate, usually a repository method.

    Returns:
        Callable: Wrapped async method with automatic rollback on error.

    Raises:
        Exception: Reraises any exception caught during the method execution
        after rolling back the transaction.

    Example:
        @transactional
        async def add_entity(self, entity_dto):
            self._async_db_session.add(entity)
            await self._async_db_session.commit()

    Notes:
        - This decorator assumes the decorated method is an async instance method
          with access to `self._async_db_session` of type `AsyncSession`.
        - It does NOT perform commit; the decorated method should manage commit explicitly.
        - Using this decorator on CRUD methods will not interfere with normal operation,
          but protects against session state corruption on exceptions.
    """

    @wraps(method)
    async def wrapper(self, *args, **kwargs):
        try:
            result = await method(self, *args, **kwargs)
            return result

        except Exception:
            if hasattr(self, "_async_db_session") and isinstance(
                self._async_db_session, AsyncSession
            ):
                await self._async_db_session.rollback()

            raise

    return wrapper


def handle_unique_violation(method):
    """
    Decorator to catch PostgreSQL unique constraint violations during DB operations
    and raise a custom UniqueViolationError instead of raw DB exception.

    Helps isolate infrastructure errors in the repository layer.

    Raises:
        UniqueViolationError: If `IntegrityError` with sqlstate code: `23505` (PK Violation) occurs.
    """

    @wraps(method)
    async def wrapper(self, *args, **kwargs):
        try:
            return await method(self, *args, **kwargs)

        except IntegrityError as exc:
            if (
                exc.orig
                and hasattr(exc.orig, "sqlstate")
                and exc.orig.sqlstate == "23505"
            ):
                detail = getattr(exc.orig, "detail", "")
                constraint = (
                    getattr(exc.orig.diag, "constraint_name", "")
                    if hasattr(exc.orig, "diag")
                    else ""
                )

                if not detail:
                    detail = str(exc.orig)

                msg = "Duplicate key violation detected"
                if constraint:
                    msg += f" on constraint '{constraint}'"
                if detail:
                    msg += f": {detail}"

                raise UniqueViolationError(msg) from exc

            raise

    return wrapper
