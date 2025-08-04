from typing import Type, TypeVar

from mis_eventer_lib.schemas.event_schema import EventerResponseSchema
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class MapperError(Exception):
    pass


def map_event_payload_to_schema(event_data: EventerResponseSchema, model: Type[T]) -> T:
    """
    Generic mapper payload.data from event to the required Pydantic schema.

    Args:
        event_data (EventerResponseSchema): Incoming event with payload.
        model (Type[T]): Pydantic schema class to map to.

    Returns:
        T: Model schema instance with valid data.

    Raises:
        MapperError: In case of no payload or validation error.
    """
    if not event_data.payload or not isinstance(event_data.payload, dict):
        raise MapperError("Payload data is missing or invalid.")

    raw_data = event_data.payload.get("data")
    if raw_data is None:
        raise MapperError("Payload 'data' field is missing.")

    if hasattr(model, "id"):
        raw_data["id"] = event_data.event_id

    try:
        return model(**raw_data)
    except ValidationError as err:
        raise MapperError(f"Data validation error for {model.__name__}: {err}") from err
