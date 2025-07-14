from abc import ABC, abstractmethod
from typing import List, Optional

from src.apps.platform_rules.infrastructure.api.schemas.requests.platform_rules_schemas import (
    CreatePlatformRuleSchema,
    UpdatePlatformRuleSchema,
)
from src.apps.platform_rules.infrastructure.api.schemas.responses.platform_rules_schemas import (
    ResponsePlatformRuleSchema,
)


class PlatformRulesRepositoryInterface(ABC):
    @abstractmethod
    async def get_total_number_of_platform_rules(self) -> int:
        """
        Retrieve a number of ALL platform rules from the Registry Service DB.

        :return: Number of ALL platform rules from the Registry Service DB as INT
        """
        pass

    @abstractmethod
    async def get_by_id(
        self, platform_rule_id: int
    ) -> Optional[ResponsePlatformRuleSchema]:
        """
        Retrieves a platform rule from the DB by its ID.

        :param platform_rule_id: Unique platform rule ID (int)
        :return: ResponsePlatformRuleSchema representing the platform rule or None if not found
        """
        pass

    @abstractmethod
    async def get_by_key(
        self, platform_rule_key: str
    ) -> Optional[ResponsePlatformRuleSchema]:
        """
        Retrieves a platform rule from the DB by its key (name).

        :param platform_rule_key: Unique platform rule key (name)
        :return: ResponsePlatformRuleSchema representing the platform rule or None if not found
        """
        pass

    @abstractmethod
    async def get_platform_rules(
        self,
        filters: dict,
        page: int = 1,
        limit: int = 30,
    ) -> List[ResponsePlatformRuleSchema]:
        """
        Retrieves a platform rules from the DB based on the given filters and pagination parameters.

        :param page: Pagination parameter representing the number of items per page.
        :param limit: Number of elements per page.
        :param filters: Filter parameters dict containing fields to filter by.

        :return: List if ResponsePlatformRuleSchema corresponding the provided filters
        """
        pass

    @abstractmethod
    async def create_platform_rule(
        self, request_dto: CreatePlatformRuleSchema
    ) -> ResponsePlatformRuleSchema:
        """
        Creates a platform rule in the DB by a given parameters.

        :param request_dto: CreatePlatformRuleSchema containing all data needed for creation
        :return: ResponsePlatformRuleSchema representing just created platform rule
        """
        pass

    @abstractmethod
    async def update_platform_rule(
        self, platform_rule_id: int, request_dto: UpdatePlatformRuleSchema
    ) -> ResponsePlatformRuleSchema:
        """
        Updates a platform rule in the DB by a given optional parameters.

        :param platform_rule_id: Unique platform rule ID (int)
        :param request_dto: UpdatePlatformRuleSchema containing fields to update

        :return: ResponsePlatformRuleSchema representing just updated platform rule
        """
        pass

    @abstractmethod
    async def delete_by_id(self, platform_rule_id: int) -> None:
        """
        Deletes a platform rule from the DB by its ID.

        :param platform_rule_id: Unique platform rule ID (int)

        :return: None
        """
        pass
