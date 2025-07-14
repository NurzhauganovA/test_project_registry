from src.apps.medical_staff_journal.exceptions import NoInstanceFoundError
from src.apps.medical_staff_journal.infrastructure.api.schemas.responses.rpn_integration_response_schemas import (
    ResponseSpecialistAttachmentInfoSchema,
)
from src.apps.medical_staff_journal.interfaces.rpn_integration_service_repository_interface import (
    RpnIntegrationServiceRepositoryInterface,
)
from src.core.i18n import _
from src.core.logger import LoggerService


class MedicalStaffJournalService:
    def __init__(
        self,
        logger: LoggerService,
        rpn_integration_service_repository: RpnIntegrationServiceRepositoryInterface,
    ) -> None:
        self._logger = logger
        self._repository = rpn_integration_service_repository

    async def get_specialist_current_attachment_info(
        self,
        iin: str,
    ) -> ResponseSpecialistAttachmentInfoSchema:
        response_dto = await self._repository.get_specialist_current_attachment_info(
            iin=iin
        )
        if response_dto is None:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("No active attachments found for this specialist."),
            )

        required_fields = [
            "first_name",
            "last_name",
            "middle_name",
            "iin",
            "attachment_data",
        ]

        missing = any(not getattr(response_dto, field) for field in required_fields)

        if missing:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("No active attachments found for this specialist."),
            )

        return response_dto
