import math
from datetime import date
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status, Query

from src.apps.assets_journal.container import AssetsJournalContainer
from src.apps.assets_journal.infrastructure.api.schemas.requests.staff_assignment_schemas import (
    StaffAssignmentFilterParams,
    CreateStaffAssignmentSchema,
    UpdateStaffAssignmentSchema,
    CompleteStaffAssignmentSchema,
    ExtendStaffAssignmentSchema,
)
from src.apps.assets_journal.infrastructure.api.schemas.responses.staff_assignment_schemas import (
    MultipleStaffAssignmentsResponseSchema,
    StaffAssignmentResponseSchema,
    StaffAssignmentListItemSchema,
    StaffAssignmentStatisticsSchema,
    SpecialistAssignmentsResponseSchema,
    AreaAssignmentsResponseSchema,
    DepartmentAssignmentsResponseSchema,
)
from src.apps.assets_journal.mappers.staff_assignment_mappers import (
    map_staff_assignment_domain_to_full_response,
    map_staff_assignment_domain_to_list_item,
)
from src.apps.assets_journal.services.staff_assignment_service import StaffAssignmentService
from src.shared.dependencies.check_user_permissions import check_user_permissions
from src.shared.schemas.pagination_schemas import (
    PaginationMetaDataSchema,
    PaginationParams,
)
from src.apps.assets_journal.domain.enums import (
    StaffAssignmentStatusEnum,
    MedicalSpecializationEnum,
    MedicalDepartmentEnum,
    AreaTypeEnum,
)

staff_assignments_router = APIRouter()