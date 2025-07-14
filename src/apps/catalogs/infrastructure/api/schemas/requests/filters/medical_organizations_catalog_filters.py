from typing import Optional

from fastapi import Query


class MedicalOrganizationsCatalogFilterParams:
    def __init__(
        self,
        name_filter: Optional[str] = Query(
            None, description="Organization name to filter by"
        ),
        organization_code_filter: Optional[str] = Query(
            None, description="Organization code to filter by"
        ),
        address_filter: Optional[str] = Query(
            None, description="Organization's address to filter by"
        ),
    ):
        self.name_filter = name_filter
        self.organization_code_filter = organization_code_filter
        self.address_filter = address_filter

    def to_dict(self, exclude_none: bool = True) -> dict:
        data = vars(self)
        return {
            key: value
            for key, value in data.items()
            if not exclude_none or value is not None
        }
