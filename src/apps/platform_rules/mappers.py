from datetime import date, time
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator

from src.apps.platform_rules.infrastructure.api.schemas.responses.platform_rules_schemas import (
    ResponsePlatformRuleSchema,
)
from src.apps.platform_rules.infrastructure.db_models.models import (
    SQLAlchemyPlatformRule,
)


class MaxSchedulePeriodDataSchema(BaseModel):
    value: int = Field(..., gt=0, strict=True)


class ReducedDaySchema(BaseModel):
    date: date
    is_active: bool
    work_start_time: Optional[time] = None
    work_end_time: Optional[time] = None

    @model_validator(mode="after")
    def check_active_fields(self):
        if self.is_active:
            if (not self.work_start_time) or (not self.work_end_time):
                raise ValueError(
                    "If 'is_active' field is provided as True - both 'work_start_time' "
                    "and 'work_end_time' are required.'"
                )

        return self


class ReducedDaysDataSchema(BaseModel):
    days: List[ReducedDaySchema]


def map_platform_rule_db_entity_to_schema(
    platform_rule_from_db: SQLAlchemyPlatformRule,
) -> ResponsePlatformRuleSchema:
    rule_data = platform_rule_from_db.rule_data  # {'MAX_SCHEDULE_PERIOD': {...}}
    key = next(iter(rule_data.keys()))
    data = rule_data[key]

    return ResponsePlatformRuleSchema(
        id=platform_rule_from_db.id,
        key=key,
        rule_data=data,
        description=platform_rule_from_db.description,
    )


# Admin-panel Service rules mapping
RULE_DATA_SCHEMAS = {
    "MAX_SCHEDULE_PERIOD": MaxSchedulePeriodDataSchema,
    "REDUCED_DAYS": ReducedDaysDataSchema,
}
