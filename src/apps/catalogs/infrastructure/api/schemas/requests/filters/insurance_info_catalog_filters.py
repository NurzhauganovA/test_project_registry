from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import Query


class InsuranceInfoCatalogFilterParams:
    def __init__(
        self,
        patient_id_filter: Optional[UUID] = Query(
            None, description="Patient's ID to filter by"
        ),
        financing_source_id_filter: Optional[int] = Query(
            None, description="Financing source ID to filter by"
        ),
        policy_number_filter: Optional[str] = Query(
            None, description="Policy number to filter by (exact match)"
        ),
        company_name_filter: Optional[str] = Query(
            None, description="Company name to filter by (exact match)"
        ),
        valid_from_filter: Optional[date] = Query(
            None, description="Valid from filter"
        ),
        valid_till_filter: Optional[date] = Query(
            None, description="Valid till filter"
        ),
    ):
        self.patient_id = patient_id_filter
        self.financing_source_id = financing_source_id_filter
        self.policy_number = policy_number_filter
        self.company = company_name_filter
        self.valid_from = valid_from_filter
        self.valid_till = valid_till_filter

    def to_dict(self, exclude_none: bool = True) -> dict:
        data = vars(self)
        return {
            key: value
            for key, value in data.items()
            if not exclude_none or value is not None
        }
