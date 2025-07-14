import json
from datetime import datetime

from httpx import AsyncClient, ConnectError, HTTPStatusError

from src.apps.medical_staff_journal.infrastructure.api.schemas.responses.rpn_integration_response_schemas import (
    ResponseSpecialistAttachmentInfoSchema,
    SpecialistAttachmentInfoSchema,
)
from src.apps.medical_staff_journal.interfaces.rpn_integration_service_repository_interface import (
    RpnIntegrationServiceRepositoryInterface,
)
from src.core.i18n import _
from src.core.logger import LoggerService
from src.shared.exceptions import (
    RpnIntegrationServiceConnectionError,
    RpnIntegrationServiceError,
)


class RpnIntegrationServiceRepositoryImpl(RpnIntegrationServiceRepositoryInterface):
    def __init__(self, http_client: AsyncClient, base_url: str, logger: LoggerService):
        self._http_client = http_client
        self._logger = logger
        self.base_url = base_url

    async def get_specialist_current_attachment_info(
        self,
        iin: str,
    ) -> ResponseSpecialistAttachmentInfoSchema | None:
        if not self.base_url:
            self._logger.critical("- RPN_INTEGRATION_SERVICE_BASE_URL is not set!")
            raise RpnIntegrationServiceConnectionError(
                status_code=503,
                detail=_("Something went wrong. Please, try again later."),
            )

        base_url = self.base_url

        url = f"{base_url}/specialists/current_attachment"
        try:
            response = await self._http_client.post(
                url=url,
                content=json.dumps(
                    {
                        "iin": iin,
                    }
                ),
            )
            response.raise_for_status()

        except HTTPStatusError as exc:
            raise RpnIntegrationServiceError(
                status_code=exc.response.status_code, detail=exc.response.text
            ) from exc

        except ConnectError as exc:
            error_message = "RPN Integration Service is not available."
            self._logger.critical(f"HTTP 503 - {error_message}")
            raise RpnIntegrationServiceConnectionError(
                status_code=503,
                detail=_("Something went wrong. Please, try again later."),
            ) from exc

        parsed_response = response.json()

        payload = parsed_response.get("data", None)
        if not payload:
            return None

        record = payload.get("record")
        if not isinstance(record, dict):
            self._logger.critical(
                "The data received from the RPN Integration Service is not as expected "
                "(Dict). From: auth_service_repository.get_specialist_current_attachment_info()."
            )
            raise RpnIntegrationServiceError(
                status_code=500,
                detail=_("Something went wrong. Please, try again later."),
            )

        attachment_data = record.get("attachment_data")
        if not isinstance(attachment_data, dict):
            return None

        raw = attachment_data.get("territory_number")
        if isinstance(raw, (str, int)):
            territory_number = int(raw)
        else:
            territory_number = None

        specialist_attachment_schema = SpecialistAttachmentInfoSchema(
            specialization_name=attachment_data.get("specialization_name", ""),
            territory_number=territory_number,
            organization_name=attachment_data.get("organization_name", ""),
            attachment_date=(
                (datetime.fromisoformat(attachment_data["attached_at"]).date())
                if attachment_data.get("attached_at")
                else None
            ),
            detachment_date=(
                (datetime.fromisoformat(attachment_data["detached_at"].split("T")[0]))
                if attachment_data.get("detached_at")
                else None
            ),
            department_name=attachment_data.get("department_name", ""),
        )

        record_dto = ResponseSpecialistAttachmentInfoSchema(
            first_name=record.get("first_name", ""),
            last_name=record.get("last_name", ""),
            middle_name=record.get("middle_name", ""),
            iin=record.get("iin", ""),
            attachment_data=specialist_attachment_schema,
        )

        return record_dto
