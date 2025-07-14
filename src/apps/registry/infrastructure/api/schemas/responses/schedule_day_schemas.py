from datetime import date, time
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from src.shared.schemas.pagination_schemas import PaginationMetaDataSchema


class ResponseScheduleDaySchema(BaseModel):
    id: UUID
    schedule_id: UUID
    day_of_week: int
    is_active: bool
    work_start_time: time
    work_end_time: time
    break_start_time: Optional[time] = None
    break_end_time: Optional[time] = None
    date: date


class MultipleScheduleDaysResponseSchema(BaseModel):
    items: List[ResponseScheduleDaySchema]
    pagination: PaginationMetaDataSchema
