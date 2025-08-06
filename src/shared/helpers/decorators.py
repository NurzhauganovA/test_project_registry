from functools import wraps

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.core.logger import LoggerService
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


def handle_kafka_event(
        action_type: str,
        model_name: str,
):
    """
    Decorator for handling exceptions and logging in asynchronous Kafka event handlers.
    Wraps an async function, catches exceptions, and logs critical errors using the provided logger.

    Args:
        action_type (str): The type of action (e.g., "CREATE", "UPDATE", "DELETE").
        model_name (str): The name of the model (e.g., "cat_citizenship").

    Returns:
        Callable: The wrapped function with exception handling and logging.

    Note:
        The decorated function **must** accept a `logger` parameter, which is an instance of LoggerService.
        If `logger` is not passed (neither as a positional nor a keyword argument),
        and an exception occurs, an explicit RuntimeError will be raised
        indicating that the logger instance was not found.

    Example usage:
        @handle_kafka_event("DELETE", "cat_citizenship")
        async def handler(_raw_message: bytes,
                          schema_data: EventerResponseSchema,
                          service: CitizenshipCatalogService,
                          logger: LoggerService):
            # Event handling logic
            ...

    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs) -> None:
            # Trying to find among the named
            logger = kwargs.get('logger')

            if logger is None:
                # Trying to find among positional ones by type
                for arg in args:
                    if isinstance(arg, LoggerService):
                        logger = arg
                        break

            try:
                result = await func(*args, **kwargs)

                if logger is None:
                    raise RuntimeError(
                        "Logger instance not found in arguments of the decorated function."
                    )

                # Attempt to get an object with action/id for informative success log
                schema_data = None
                for arg in args:
                    if hasattr(arg, 'action') and hasattr(arg, 'id'):
                        schema_data = arg
                        break

                if schema_data:
                    logger.info(
                        f"Successfully handled '{schema_data.action}' type event for model: '{model_name}'. "
                        f"Record with ID: {getattr(schema_data, 'id', 'N/A')} processed."
                    )
                else:
                    # If schema_data is not found
                    logger.info(
                        f"Successfully handled '{action_type}' type event for model: '{model_name}'."
                    )

                return result

            except Exception as err:
                schema_data = None
                for arg in args:
                    if hasattr(arg, 'action'):
                        schema_data = arg
                        break

                action = schema_data.action if schema_data else action_type

                if logger is None:
                    raise RuntimeError(
                        "Logger instance not found in arguments of the decorated function."
                    )

                logger.critical(
                    f"Failed to handle '{action}' type event for model: '{model_name}'. {err}",
                    exc_info=True,
                )

                return

        return wrapper

    return decorator
