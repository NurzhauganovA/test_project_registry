from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from src.apps.users.infrastructure.schemas.user_schemas import UserSchema
from src.shared.schemas.pagination_schemas import PaginationMetaDataSchema


class ResponseScheduleSchema(BaseModel):
    id: UUID
    doctor: UserSchema
    schedule_name: str
    period_start: date
    period_end: date
    is_active: bool
    appointment_interval: int
    description: Optional[str] = None

    class Config:
        from_attributes = True


class MultipleSchedulesResponseSchema(BaseModel):
    items: List[ResponseScheduleSchema]
    pagination: PaginationMetaDataSchema
