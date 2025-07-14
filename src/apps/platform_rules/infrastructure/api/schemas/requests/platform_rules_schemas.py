from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator

from src.apps.platform_rules.infrastructure.validation_helpers import validate_rule_data


class CreatePlatformRuleSchema(BaseModel):
    key: str = Field(..., description="Platform rule key (name)")
    rule_data: Dict[str, Any] = Field(
        ..., description="Platform rule JSON data (key and its value)"
    )
    description: Optional[str] = Field(None, description="Platform rule description")

    @field_validator("rule_data", mode="before")
    def validate_rule_data(cls, data, info):
        key = info.data.get("key")
        if key:
            validate_rule_data(key, data)

        return data


class UpdatePlatformRuleSchema(BaseModel):
    key: str = Field(..., description="Platform rule key (name)")
    rule_data: Dict[str, Any] = Field(
        ..., description="Platform rule JSON data (key and its value)"
    )
    description: Optional[str] = Field(None, description="Platform rule description")

    @field_validator("rule_data", mode="before")
    def validate_rule_data(cls, data, info):
        key = info.data.get("key")
        if key:
            validate_rule_data(key, data)

        return data
