from typing import List, Optional
from sqlalchemy import func, select

from src.apps.platform_rules.infrastructure.api.schemas.requests.platform_rules_schemas import (
    CreatePlatformRuleSchema,
    UpdatePlatformRuleSchema,
)
from src.apps.platform_rules.infrastructure.api.schemas.responses.platform_rules_schemas import (
    ResponsePlatformRuleSchema,
)
from src.apps.platform_rules.infrastructure.db_models.models import (
    SQLAlchemyPlatformRule,
)
from src.apps.platform_rules.interfaces.platform_rules_repository_interface import (
    PlatformRulesRepositoryInterface,
)
from src.apps.platform_rules.mappers import map_platform_rule_db_entity_to_schema
from src.shared.infrastructure.base import BaseRepository


class SQLAlchemyPlatformRulesRepositoryImpl(
    BaseRepository, PlatformRulesRepositoryInterface
):
    async def get_total_number_of_platform_rules(self) -> int:
        query = select(func.count(SQLAlchemyPlatformRule.id))
        result = await self._async_db_session.execute(query)

        return result.scalar_one()

    async def get_by_id(
        self, platform_rule_id: int
    ) -> Optional[ResponsePlatformRuleSchema]:
        query = select(SQLAlchemyPlatformRule).where(
            SQLAlchemyPlatformRule.id == platform_rule_id
        )
        result = await self._async_db_session.execute(query)
        platform_rule = result.scalar_one_or_none()

        if platform_rule:
            return map_platform_rule_db_entity_to_schema(platform_rule)

        return None

    async def get_by_key(
        self, platform_rule_key: str
    ) -> Optional[ResponsePlatformRuleSchema]:
        query = select(SQLAlchemyPlatformRule).where(
            SQLAlchemyPlatformRule.rule_data.has_key(platform_rule_key)
        )
        result = await self._async_db_session.execute(query)
        platform_rule = result.scalar_one_or_none()

        if platform_rule:
            return map_platform_rule_db_entity_to_schema(platform_rule)

        return None

    async def get_platform_rules(
        self,
        filters: dict,
        page: int = 1,
        limit: int = 30,
    ) -> List[ResponsePlatformRuleSchema]:
        offset = (page - 1) * limit
        query = select(SQLAlchemyPlatformRule).offset(offset)

        # Applying filters...
        if filters.get("key_filter"):
            key_filter_value = filters["key_filter"].lower()
            if filters.get("key_filter"):
                key_filter_value = filters["key_filter"]
                query = query.where(
                    SQLAlchemyPlatformRule.rule_data.has_key(key_filter_value)
                )

        result = await self._async_db_session.execute(query)
        platform_rules = result.scalars().all()

        return [
            map_platform_rule_db_entity_to_schema(platform_rule)
            for platform_rule in platform_rules
        ]

    async def create_platform_rule(
        self, request_dto: CreatePlatformRuleSchema
    ) -> ResponsePlatformRuleSchema:
        new_platform_rule = SQLAlchemyPlatformRule(
            # In schema, key - separate field. In DB - it's inside rule_data.
            rule_data={request_dto.key: request_dto.rule_data},
            description=request_dto.description,
        )
        self._async_db_session.add(new_platform_rule)

        await self._async_db_session.flush()
        await self._async_db_session.refresh(new_platform_rule)
        await self._async_db_session.commit()

        return map_platform_rule_db_entity_to_schema(new_platform_rule)

    async def update_platform_rule(
        self, platform_rule_id: int, request_dto: UpdatePlatformRuleSchema
    ) -> ResponsePlatformRuleSchema:
        query = select(SQLAlchemyPlatformRule).where(
            SQLAlchemyPlatformRule.id == platform_rule_id
        )
        result = await self._async_db_session.execute(query)
        platform_rule_to_update = result.scalar_one_or_none()

        platform_rule_to_update.rule_data = {request_dto.key: request_dto.rule_data}
        platform_rule_to_update.description = request_dto.description

        await self._async_db_session.flush()
        await self._async_db_session.refresh(platform_rule_to_update)
        await self._async_db_session.commit()

        return map_platform_rule_db_entity_to_schema(platform_rule_to_update)

    async def delete_by_id(self, platform_rule_id: int) -> None:
        query = select(SQLAlchemyPlatformRule).where(
            SQLAlchemyPlatformRule.id == platform_rule_id
        )
        result = await self._async_db_session.execute(query)
        platform_rule_to_delete = result.scalar_one_or_none()

        await self._async_db_session.delete(platform_rule_to_delete)
        await self._async_db_session.commit()
