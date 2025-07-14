from abc import ABC, abstractmethod

from src.apps.medical_staff_journal.infrastructure.api.schemas.responses.rpn_integration_response_schemas import (
    ResponseSpecialistAttachmentInfoSchema,
)


class RpnIntegrationServiceRepositoryInterface(ABC):
    @abstractmethod
    async def get_specialist_current_attachment_info(
        self,
        iin: str,
    ) -> ResponseSpecialistAttachmentInfoSchema | None:
        """
        Retrieves the current attachment information of a specialist based on their
        individual identification number (IIN). This method provides paginated results
        with an optional limit for the number of records per page.

        :param iin: Individual Identification Number (IIN) of the specialist to fetch
            information for.

        :return: Relevant current attachment information for the specified specialist
            in a paginated format or None if there are no records.

        :raises NotImplementedError: If the method is not implemented.
        """
        pass
