from typing import Optional
from uuid import UUID

from fastapi import Query

from src.apps.catalogs.enums import IdentityDocumentTypeEnum


class IdentityDocumentsCatalogFilterParams:
    def __init__(
        self,
        by_patient_id: Optional[UUID] = Query(
            None, description="Patient's ID to filter by"
        ),
        by_type: Optional[IdentityDocumentTypeEnum] = Query(
            None, description="Document type to filter by"
        ),
        by_series: Optional[str] = Query(
            None, description="Document series to filter by (exact match)"
        ),
        by_number: Optional[str] = Query(
            None, description="Document number to filter by (exact match)"
        ),
        only_active: Optional[bool] = Query(
            None,
            description="Document validity to filter by. Returns only active documents.",
        ),
    ):
        self.patient_id = by_patient_id
        self.type = by_type
        self.series = by_series
        self.number = by_number
        self.only_active = only_active

    def to_dict(self, exclude_none: bool = True) -> dict:
        data = vars(self)
        return {
            key: value
            for key, value in data.items()
            if not exclude_none or value is not None
        }
