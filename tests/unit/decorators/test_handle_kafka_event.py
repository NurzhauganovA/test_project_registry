from uuid import UUID
import pytest

from src.shared.helpers.decorators import handle_kafka_event


class DummySchema:
    def __init__(
            self,
            action: str,
            id: int | UUID | str
    ) -> None:
        self.action = action
        self.id = id


@pytest.mark.asyncio
async def test_handle_kafka_event_success(dummy_logger):
    dummy_schema = DummySchema(action='create', id=42)

    @handle_kafka_event('create', 'dummy_model')
    async def handler(_raw, schema_data, logger):
        assert schema_data == dummy_schema
        return 'result'

    result = await handler(None, dummy_schema, logger=dummy_logger)
    assert result == 'result'
    dummy_logger.info.assert_called_with(
        "Successfully handled 'create' type event for model: 'dummy_model'. Record with ID: 42 processed."
    )


@pytest.mark.asyncio
async def test_handle_kafka_event_success_without_schema(dummy_logger):
    @handle_kafka_event("update", "dummy_model")
    async def handler(_raw, some_arg, logger):
        return "ok"

    result = await handler(None, "no_schema_obj", logger=dummy_logger)

    assert result == "ok"
    dummy_logger.info.assert_called_with(
        "Successfully handled 'update' type event for model: 'dummy_model'."
    )
    

@pytest.mark.asyncio
async def test_handle_kafka_event_exception_logged(dummy_logger):
    dummy_schema = DummySchema(action="delete", id=99)

    @handle_kafka_event("delete", "dummy_model")
    async def handler(_raw, schema_data, logger):
        raise ValueError("fail")

    result = await handler(None, dummy_schema, logger=dummy_logger)

    dummy_logger.critical.assert_called()
    args, kwargs = dummy_logger.critical.call_args
    assert "Failed to handle 'delete' type event for model: 'dummy_model'." in args[0]
    assert "fail" in args[0]
    assert kwargs.get("exc_info") is True
    assert result is None


@pytest.mark.asyncio
async def test_handle_kafka_event_no_logger_raises():
    dummy_schema = DummySchema(action="create", id=1)

    @handle_kafka_event("create", "dummy_model")
    async def handler(_raw, schema_data):
        return "something"

    with pytest.raises(RuntimeError, match="Logger instance not found"):
        await handler(None, dummy_schema)
