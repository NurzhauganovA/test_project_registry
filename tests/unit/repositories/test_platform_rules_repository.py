import pytest
from unittest.mock import AsyncMock, MagicMock

from src.apps.platform_rules.infrastructure.api.schemas.requests.platform_rules_schemas import (
    UpdatePlatformRuleSchema,
    CreatePlatformRuleSchema
)
from src.apps.platform_rules.infrastructure.repositories.platform_rules_repository import (
    SQLAlchemyPlatformRulesRepositoryImpl
)


@pytest.mark.asyncio
async def test_get_by_id_found(mock_async_db_session, dummy_db_platform_rule, dummy_logger, monkeypatch):
    result = MagicMock()
    result.scalar_one_or_none.return_value = dummy_db_platform_rule
    mock_async_db_session.execute = AsyncMock(return_value=result)

    repository = SQLAlchemyPlatformRulesRepositoryImpl(mock_async_db_session, dummy_logger)

    monkeypatch.setattr(
        "src.apps.platform_rules.mappers.map_platform_rule_db_entity_to_schema",
        lambda db_obj: MagicMock(
            id=db_obj.id,
            description=db_obj.description,
            rule_data={"value": 30},
        )
    )

    result = await repository.get_by_id(1)
    assert result.id == dummy_db_platform_rule.id
    assert result.description == dummy_db_platform_rule.description
    assert result.rule_data == {"value": 30}


@pytest.mark.asyncio
async def test_get_by_id_not_found(mock_async_db_session, dummy_logger):
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    mock_async_db_session.execute = AsyncMock(return_value=result)

    repository = SQLAlchemyPlatformRulesRepositoryImpl(mock_async_db_session, dummy_logger)
    result = await repository.get_by_id(42)
    assert result is None


@pytest.mark.asyncio
async def test_get_by_key_found(mock_async_db_session, dummy_db_platform_rule, dummy_logger, monkeypatch):
    result = MagicMock()
    result.scalar_one_or_none.return_value = dummy_db_platform_rule
    mock_async_db_session.execute = AsyncMock(return_value=result)

    repository = SQLAlchemyPlatformRulesRepositoryImpl(mock_async_db_session, dummy_logger)
    monkeypatch.setattr(
        "src.apps.platform_rules.mappers.map_platform_rule_db_entity_to_schema",
        lambda db_obj: {"id": db_obj.id, "description": db_obj.description, "rule_data": db_obj.rule_data}
    )

    result = await repository.get_by_key("MAX_SCHEDULE_PERIOD")
    assert result.id == dummy_db_platform_rule.id


@pytest.mark.asyncio
async def test_get_platform_rules(mock_async_db_session, dummy_db_platform_rule, dummy_logger, monkeypatch):
    result = MagicMock()
    result.scalars.return_value.all.return_value = [dummy_db_platform_rule]
    mock_async_db_session.execute = AsyncMock(return_value=result)

    repository = SQLAlchemyPlatformRulesRepositoryImpl(mock_async_db_session, dummy_logger)
    monkeypatch.setattr(
        "src.apps.platform_rules.mappers.map_platform_rule_db_entity_to_schema",
        lambda db_obj: {"id": db_obj.id, "description": db_obj.description, "rule_data": db_obj.rule_data}
    )

    result = await repository.get_platform_rules(filters={}, page=1, limit=10)
    assert len(result) == 1
    assert result[0].id == dummy_db_platform_rule.id


@pytest.mark.asyncio
async def test_create_platform_rule(mock_async_db_session, dummy_logger, monkeypatch):
    mock_async_db_session.add = MagicMock()
    mock_async_db_session.flush = AsyncMock()
    mock_async_db_session.refresh = AsyncMock()
    mock_async_db_session.commit = AsyncMock()

    repository = SQLAlchemyPlatformRulesRepositoryImpl(mock_async_db_session, dummy_logger)

    dummy_obj = MagicMock()
    dummy_obj.id = 1
    dummy_obj.rule_data = {"MAX_SCHEDULE_PERIOD": {"value": 30}}
    dummy_obj.description = "desc"

    mock_async_db_session.refresh.side_effect = lambda obj: obj

    monkeypatch.setattr(
        "src.apps.platform_rules.mappers.map_platform_rule_db_entity_to_schema",
        lambda db_obj: {"id": db_obj.id, "description": db_obj.description, "rule_data": db_obj.rule_data}
    )

    dto = CreatePlatformRuleSchema(
        key="MAX_SCHEDULE_PERIOD",
        rule_data={"value": 30},
        description="desc"
    )

    mock_async_db_session.add.side_effect = lambda obj: setattr(obj, "id", 1)
    mock_async_db_session.refresh.side_effect = lambda obj: setattr(obj, "id", 1)
    result = await repository.create_platform_rule(dto)

    assert result.rule_data["value"] == 30


@pytest.mark.asyncio
async def test_update_platform_rule(mock_async_db_session, dummy_db_platform_rule, dummy_logger, monkeypatch):
    result = MagicMock()
    result.scalar_one_or_none.return_value = dummy_db_platform_rule
    mock_async_db_session.execute = AsyncMock(return_value=result)
    mock_async_db_session.flush = AsyncMock()
    mock_async_db_session.refresh = AsyncMock()
    mock_async_db_session.commit = AsyncMock()

    repository = SQLAlchemyPlatformRulesRepositoryImpl(mock_async_db_session, dummy_logger)
    monkeypatch.setattr(
        "src.apps.platform_rules.mappers.map_platform_rule_db_entity_to_schema",
        lambda db_obj: {"id": db_obj.id, "description": db_obj.description, "rule_data": db_obj.rule_data}
    )
    dto = UpdatePlatformRuleSchema(key="MAX_SCHEDULE_PERIOD", rule_data={"value": 42}, description="updated")
    result = await repository.update_platform_rule(1, dto)
    assert result.rule_data["value"] == 42


@pytest.mark.asyncio
async def test_delete_by_id(mock_async_db_session, dummy_db_platform_rule, dummy_logger):
    result = MagicMock()
    result.scalar_one_or_none.return_value = dummy_db_platform_rule
    mock_async_db_session.execute = AsyncMock(return_value=result)
    mock_async_db_session.delete = AsyncMock()
    mock_async_db_session.commit = AsyncMock()

    repository = SQLAlchemyPlatformRulesRepositoryImpl(mock_async_db_session, dummy_logger)
    await repository.delete_by_id(1)
    mock_async_db_session.delete.assert_called_with(dummy_db_platform_rule)
    mock_async_db_session.commit.assert_called_once()
