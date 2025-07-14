from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict

from src.shared.schemas.pagination_schemas import PaginationMetaDataSchema


class ResponsePlatformRuleSchema(BaseModel):
    id: int = Field(..., description="Platform rule ID")
    key: str = Field(..., description="Platform rule key (name)")
    rule_data: Dict[str, Any] = Field(
        ..., description="Platform rule JSON data (key and its value)"
    )
    description: Optional[str] = Field(None, description="Platform rule description")

    model_config = SettingsConfigDict(
        from_attributes=True,
    )


class MultiplePlatformRulesResponseSchema(BaseModel):
    items: List[ResponsePlatformRuleSchema]
    pagination: PaginationMetaDataSchema
