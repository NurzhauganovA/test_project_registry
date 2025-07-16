from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class AdditionalServiceSchema(BaseModel):
    name: str = Field(..., description="Additional service name")
    financing_source_id: int = Field(..., description="Financing source ID")
    price: Optional[Decimal] = Field(
        default=Decimal(0), description="Price of the service"
    )
