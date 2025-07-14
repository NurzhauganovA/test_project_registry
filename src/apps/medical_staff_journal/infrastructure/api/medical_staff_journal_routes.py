from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.apps.medical_staff_journal.container import MedicalStaffJournalContainer
from src.apps.medical_staff_journal.infrastructure.api.schemas.responses.rpn_integration_response_schemas import (
    ResponseSpecialistAttachmentInfoSchema,
)
from src.apps.medical_staff_journal.services.medical_staff_jornal_service import (
    MedicalStaffJournalService,
)

medical_staff_journal_router = APIRouter()


@medical_staff_journal_router.get(
    path="/medical_staff_journal/specialists/{iin}/active_attachment",
    response_model=ResponseSpecialistAttachmentInfoSchema,
)
@inject
async def get_specialist_current_active_attachment(
    iin: str,
    medical_staff_journal_service: MedicalStaffJournalService = Depends(
        Provide[MedicalStaffJournalContainer.medical_staff_journal_service]
    ),
) -> ResponseSpecialistAttachmentInfoSchema:
    return await medical_staff_journal_service.get_specialist_current_attachment_info(
        iin=iin,
    )
