import inspect
from typing import Any, Awaitable, Dict, List, TypeVar

from dependency_injector import containers, providers

from src.apps.assets_journal.infrastructure.api.stationary_asset_routes import (
    stationary_assets_router,
)
from src.apps.catalogs.infrastructure.api.citizenship_catalog_routes import (
    citizenship_catalog_router,
)
from src.apps.catalogs.infrastructure.api.diagnoses_and_patients_routes import (
    diagnosed_patient_diagnosis_router,
)
from src.apps.catalogs.infrastructure.api.diagnoses_catalog_routes import (
    diagnoses_catalog_router,
)
from src.apps.catalogs.infrastructure.api.financing_sources_catalog_routes import (
    financing_sources_catalog_router,
)
from src.apps.catalogs.infrastructure.api.insurance_info_catalog_routes import (
    insurance_info_catalog_router,
)
from src.apps.catalogs.infrastructure.api.medical_organizations_catalog_routes import (
    medical_organizations_router,
)
from src.apps.catalogs.infrastructure.api.nationalities_catalog_routes import (
    nationalities_catalog_router,
)
from src.apps.catalogs.infrastructure.api.patient_context_attributes_catalog_routes import (
    patient_context_attributes_router,
)
from src.apps.medical_staff_journal.infrastructure.api.medical_staff_journal_routes import (
    medical_staff_journal_router,
)
from src.apps.patients.infrastructure.api.patient_routes import patients_router
from src.apps.platform_rules.infrastructure.api.platform_rules_routes import (
    platform_rules_router,
)
from src.apps.registry.infrastructure.api.appointment_routes import appointments_router
from src.apps.registry.infrastructure.api.schedule_days_routes import (
    schedule_days_router,
)
from src.apps.registry.infrastructure.api.schedule_routes import schedule_router
from src.shared.exception_handlers import (
    application_error_handler,
    auth_service_error_handler,
    dependencies_error_handler,
    rpn_integration_error_handler,
)
from src.shared.exceptions import (
    ApplicationError,
    AuthServiceError,
    DependencyError,
    RpnIntegrationServiceError,
)

T = TypeVar("T")


async def asyncify(result: T | Awaitable[T]) -> T | Awaitable[T]:
    if inspect.isawaitable(result):
        return await result
    else:
        return result


def get_routers() -> List[Dict[str, Any]]:
    routers = [
        {
            "router": schedule_router,
            "tag": ["Schedule routes"],
        },
        {
            "router": schedule_days_router,
            "tag": ["Schedule days routes"],
        },
        {
            "router": appointments_router,
            "tag": ["Appointments routes"],
        },
        {
            "router": medical_staff_journal_router,
            "tag": ["Medical staff journal routes"],
        },
        {
            "router": platform_rules_router,
            "tag": ["Platform rules routes"],
        },
        {
            "router": citizenship_catalog_router,
            "tag": ["Citizenship catalog routes"],
        },
        {
            "router": nationalities_catalog_router,
            "tag": ["Nationalities catalog routes"],
        },
        {
            "router": patient_context_attributes_router,
            "tag": ["Patient context attributes catalog routes"],
        },
        {
            "router": financing_sources_catalog_router,
            "tag": ["Financing sources catalog routes"],
        },
        {
            "router": medical_organizations_router,
            "tag": ["Medical organizations routes"],
        },
        {
            "router": insurance_info_catalog_router,
            "tag": ["Insurance info catalog routes"],
        },
        {
            "router": patients_router,
            "tag": ["Patient routes"],
        },
        {
            "router": diagnoses_catalog_router,
            "tag": (
                (diagnoses_catalog_router.tags)
                if diagnoses_catalog_router.tags
                else ["Diagnoses Catalog Routes"]
            ),
        },
        {
            "router": diagnosed_patient_diagnosis_router,
            "tag": (
                (diagnosed_patient_diagnosis_router.tags)
                if diagnosed_patient_diagnosis_router.tags
                else ["Patient's Diagnoses Routes"]
            ),
        },
        # Assets Journal routes
        {
            "router": stationary_assets_router,
            "tag": ["Stationary assets routes"],
        },
    ]

    return routers


def get_exception_handlers() -> List[Dict[str, Any]]:
    exception_handlers = [
        {"handler": application_error_handler, "error": ApplicationError},
        {"handler": auth_service_error_handler, "error": AuthServiceError},
        {"handler": dependencies_error_handler, "error": DependencyError},
        {"handler": rpn_integration_error_handler, "error": RpnIntegrationServiceError},
    ]

    return exception_handlers


def wire_subcontainers(container: containers.Container) -> None:
    for provider in container.traverse(types=[providers.Container]):
        provider.wire()


def unwire_subcontainers(container: containers.Container) -> None:
    for provider in container.traverse(types=[providers.Container]):
        provider.unwire()
