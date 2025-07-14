from typing import Optional

from fastapi import Query


class PlatformRulesFilterParams:
    def __init__(
        self,
        key_filter: Optional[str] = Query(
            None, description="Key to filter platform rules by"
        ),
    ):
        self.key_filter = key_filter

    def to_dict(self, exclude_none: bool = True) -> dict:
        data = vars(self)
        return {
            key: value
            for key, value in data.items()
            if not exclude_none or value is not None
        }
