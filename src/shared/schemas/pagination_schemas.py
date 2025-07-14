from typing import Optional

from fastapi import Query
from pydantic import BaseModel

from src.shared.exceptions import InvalidPaginationParamsError
from src.shared.helpers.validation_helpers import (
    validate_pagination_limit,
    validate_pagination_page,
)


class PaginationParams:
    def __init__(
        self,
        limit: Optional[int] = Query(
            default=100,
            ge=1,
            le=100,
            description="Number of records per page",
        ),
        page: Optional[int] = Query(
            default=1,
            ge=1,
            description="Page number",
        ),
    ):
        self.limit = limit
        self.page = page

        if self.limit:
            try:
                validate_pagination_limit(self.limit)
            except ValueError as e:
                raise InvalidPaginationParamsError(status_code=422, detail=str(e))

        if self.page:
            try:
                validate_pagination_page(self.page)
            except ValueError as e:
                raise InvalidPaginationParamsError(status_code=422, detail=str(e))


class PaginationMetaDataSchema(BaseModel):
    current_page: int
    per_page: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool
