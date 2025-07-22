import datetime
import importlib
import uuid
from typing import List, Dict, Any, Optional
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient

import pytest
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.apps.catalogs.enums import IdentityDocumentTypeEnum
from src.apps.catalogs.infrastructure.api.schemas.requests.diagnoses_catalog_request_schemas import \
    AddDiagnosisRequestSchema, UpdateDiagnosisRequestSchema, AddDiagnosedPatientDiagnosisRecordRequestSchema, \
    UpdateDiagnosedPatientDiagnosisRecordRequestSchema
from src.apps.catalogs.infrastructure.api.schemas.requests.identity_documents_catalog_request_schemas import \
    AddIdentityDocumentRequestSchema, UpdateIdentityDocumentRequestSchema
from src.apps.catalogs.infrastructure.api.schemas.requests.insurance_info_catalog_request_schemas import \
    AddInsuranceInfoRecordSchema
from src.apps.catalogs.infrastructure.api.schemas.responses.diagnoses_catalog_response_schemas import \
    DiagnosesCatalogResponseSchema, DiagnosedPatientDiagnosisResponseSchema, DiagnosesCatalogBaseResponseSchema
from src.apps.catalogs.infrastructure.api.schemas.responses.identity_documents_catalog_response_schemas import \
    IdentityDocumentResponseSchema
from src.apps.catalogs.infrastructure.db_models.diagnoses_catalogue import SQLAlchemyDiagnosesCatalogue, \
    SQLAlchemyPatientsAndDiagnoses
from src.apps.catalogs.infrastructure.db_models.identity_documents_catalogue import SQLAlchemyIdentityDocumentsCatalogue
from src.apps.catalogs.infrastructure.repositories.citizenship_catalog_repository import \
    SQLAlchemyCitizenshipCatalogueRepositoryImpl
from src.apps.catalogs.infrastructure.repositories.diagnoses_and_patients_repository import \
    SQLAlchemyDiagnosedPatientDiagnosisRepositoryImpl
from src.apps.catalogs.infrastructure.repositories.diagnoses_catalog_repository import \
    SQLAlchemyDiagnosesCatalogRepositoryImpl
from src.apps.catalogs.infrastructure.repositories.identity_documents_catalog_repository import \
    SQLAlchemyIdentityDocumentsCatalogRepositoryImpl
from src.apps.catalogs.infrastructure.repositories.insurance_info_catalog_repository import \
    SQLAlchemyInsuranceInfoCatalogRepositoryImpl
from src.apps.catalogs.infrastructure.repositories.nationalities_catalog_repository import \
    SQLAlchemyNationalitiesCatalogRepositoryImpl
from src.apps.catalogs.services.identity_documents_catalog_service import IdentityDocumentsCatalogService
from src.apps.catalogs.services.insurance_info_catalog_service import InsuranceInfoCatalogService
from src.apps.catalogs.services.nationalities_catalog_service import NationalitiesCatalogService
from src.apps.patients.infrastructure.api.schemas.responses.patient_response_schemas import \
    PatientTruncatedResponseSchema
from src.apps.patients.infrastructure.repositories.patient_repository import SQLAlchemyPatientRepository
from src.apps.patients.services.patients_service import PatientService
from src.apps.platform_rules.infrastructure.api.schemas.responses.platform_rules_schemas import \
    ResponsePlatformRuleSchema
from src.apps.platform_rules.infrastructure.db_models.models import SQLAlchemyPlatformRule
from src.apps.registry.domain.enums import AppointmentPatientTypeEnum
from src.apps.catalogs.infrastructure.api.schemas.responses.financing_sources_catalog_response_schemas import (
    FinancingSourceFullResponseSchema
)
from src.apps.catalogs.infrastructure.db_models.insurance_info_catalogue import SQLAlchemyInsuranceInfoCatalogue
from src.apps.catalogs.infrastructure.db_models.financing_sources_catalogue import SQLAlchemyFinancingSourcesCatalog
from src.apps.catalogs.infrastructure.db_models.nationalities_catalogue import SQLAlchemyNationalitiesCatalogue
from src.apps.catalogs.infrastructure.repositories.financing_sources_repository import (
    SQLAlchemyFinancingSourcesCatalogRepositoryImpl
)
from src.apps.catalogs.interfaces.financing_sources_catalog_repository_interface import (
    FinancingSourcesCatalogRepositoryInterface
)
from src.apps.catalogs.services.financing_sources_catalog_service import FinancingSourceCatalogService
from src.apps.catalogs.infrastructure.api.schemas.requests.medical_organizations_catalog_schemas import (
    UpdateMedicalOrganizationSchema,
    AddMedicalOrganizationSchema
)
from src.apps.catalogs.infrastructure.api.schemas.responses.medical_organizations_catalog_schemas import (
    MedicalOrganizationCatalogFullResponseSchema,
    MedicalOrganizationCatalogPartialResponseSchema
)
from src.apps.catalogs.services.medical_organizations_catalog_service import MedicalOrganizationsCatalogService
from src.apps.catalogs.infrastructure.api.schemas.responses.citizenship_catalog_response_schemas import (
    CitizenshipCatalogPartialResponseSchema,
    CitizenshipCatalogFullResponseSchema
)
from src.apps.catalogs.services.citizenship_catalog_service import CitizenshipCatalogService
from src.apps.catalogs.services.patient_context_attribute_service import PatientContextAttributeService
from src.apps.registry.domain.enums import (
    AppointmentStatusEnum,
    AppointmentTypeEnum,
    AppointmentInsuranceType
)
from src.apps.registry.domain.models.appointment import AppointmentDomain
from src.apps.registry.domain.models.schedule import ScheduleDomain
from src.apps.registry.infrastructure.api.schemas.requests.schedule_day_schemas import (
    CreateScheduleDaySchema,
    UpdateScheduleDaySchema
)
from src.apps.registry.infrastructure.api.schemas.responses.schedule_day_schemas import (
    ResponseScheduleDaySchema
)
from src.apps.registry.infrastructure.db_models.models import (
    Schedule,
    Appointment,
    ScheduleDay
)
from src.apps.users.infrastructure.db_models.models import User
from src.apps.users.infrastructure.schemas.user_schemas import UserSchema, AttachmentDataModel, SpecializationModel, \
    DoctorTruncatedResponseSchema
from src.apps.users.interfaces.user_repository_interface import UserRepositoryInterface
from src.core import i18n
from src.core.i18n import get_locale
from src.core.settings import project_settings
from src.apps.users.mappers import map_user_schema_to_domain
from src.shared.infrastructure.auth_service_adapter.interfaces.auth_service_repository_interface import (
    AuthServiceRepositoryInterface
)


# General fixtures
@pytest.fixture
def mock_async_db_session(mocker):
    session = mocker.MagicMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()

    return session


@pytest.fixture
def dummy_logger(mocker):
    return mocker.MagicMock()


@pytest.fixture
def mock_http_client():
    return AsyncMock(spec=AsyncClient)


@pytest.fixture(autouse=True)
def patch_i18n(monkeypatch):
    """
    We replace the translation function with identity, so that _()
     always returns the original (English) string and the tests for
     detail pass.
    """
    monkeypatch.setattr(i18n, "_", lambda s: s)


# Schedule repository fixtures
@pytest.fixture
def dummy_schedule():
    schedule = Schedule()
    schedule.id = uuid.uuid4()
    schedule.doctor_id = uuid.UUID("a5d05a81-4203-4a58-9096-40208fa4182c")
    schedule.specialization_id = 1
    schedule.schedule_name = "TestSchedule"
    schedule.appointment_interval = 20
    schedule.period_start = datetime.date.today()
    schedule.period_end = datetime.date.today() + datetime.timedelta(days=30)
    schedule.patient_type = AppointmentPatientTypeEnum.ADULT
    schedule.is_active = True
    # JSON fields
    schedule.payment_types = {"GOBMP": True, "DMS": True, "OSMS": True, "Paid": True}
    schedule.referral_types = {"with_referral": True, "without_referral": True}
    schedule.referral_origins = {"from_external_organization": True, "self_registration": False}
    schedule.days = []

    return schedule


# Appointment repository fixtures
@pytest.fixture
def dummy_db_appointment():
    appointment = Appointment()
    appointment.id = 123
    appointment.schedule_id = uuid.UUID("8edfdda7-9cee-4ade-a158-ec971f40fe5f")
    appointment.appointment_date = datetime.date(2025, 7, 3)
    appointment.appointment_time = datetime.time(8, 0, 0)
    appointment.patient_id = uuid.UUID("a5d05a81-4203-4a58-9096-40208fa4182c")
    appointment.status = AppointmentStatusEnum.BOOKED
    appointment.type = AppointmentTypeEnum.CONSULTATION
    appointment.insurance_type = AppointmentInsuranceType.DMS
    appointment.reason = "Жалоба на головную боль"
    appointment.office_number = 101
    appointment.is_patient_info_confirmation_needed = False
    appointment.paid_services = {"service1": True, "service2": False}

    return appointment


@pytest.fixture
def dummy_domain_appointment():
    appointment = AppointmentDomain(
        id=123,
        schedule_day_id=uuid.UUID("8edfdda7-9cee-4ade-a158-ec971f40fe5f"),
        time=datetime.time(8, 0, 0),
        patient_id=uuid.UUID("a5d05a81-4203-4a58-9096-40208fa4182c"),
        status=AppointmentStatusEnum.BOOKED,
        type=AppointmentTypeEnum.CONSULTATION,
        financing_sources_ids=[1],
        reason="Жалоба на головную боль",
    )

    return appointment


# Schedule Day repository fixtures
@pytest.fixture
def dummy_db_schedule_day():
    schedule_day = ScheduleDay()
    schedule_day.id = uuid.UUID("c5c7ba52-60e6-464c-8d12-f52a7a812bca")
    schedule_day.schedule_id = uuid.UUID("c5c7ba52-60e6-464c-8d12-f52a7a812bca")
    schedule_day.day_of_week = 3
    schedule_day.is_active = True
    schedule_day.appointment_interval = 30
    schedule_day.work_start_time = datetime.time(9, 0)
    schedule_day.work_end_time = datetime.time(17, 0)
    schedule_day.break_start_time = datetime.time(12, 0)
    schedule_day.break_end_time = datetime.time(13, 0)
    schedule_day.date = datetime.date(2025, 7, 5)

    return schedule_day


@pytest.fixture
def dummy_response_schedule_day_schema(dummy_db_schedule_day):
    return ResponseScheduleDaySchema(
        id=dummy_db_schedule_day.id,
        schedule_id=dummy_db_schedule_day.schedule_id,
        day_of_week=dummy_db_schedule_day.day_of_week,
        is_active=dummy_db_schedule_day.is_active,
        work_start_time=dummy_db_schedule_day.work_start_time,
        work_end_time=dummy_db_schedule_day.work_end_time,
        break_start_time=dummy_db_schedule_day.break_start_time,
        break_end_time=dummy_db_schedule_day.break_end_time,
        date=dummy_db_schedule_day.date,
    )


@pytest.fixture
def dummy_create_schedule_day_schema(dummy_db_schedule_day):
    return CreateScheduleDaySchema(
        schedule_id=dummy_db_schedule_day.schedule_id,
        day_of_week=dummy_db_schedule_day.day_of_week,
        is_active=dummy_db_schedule_day.is_active,
        work_start_time=dummy_db_schedule_day.work_start_time,
        work_end_time=dummy_db_schedule_day.work_end_time,
        break_start_time=dummy_db_schedule_day.break_start_time,
        break_end_time=dummy_db_schedule_day.break_end_time,
        date=dummy_db_schedule_day.date,
    )


@pytest.fixture
def dummy_update_schedule_day_schema(dummy_db_schedule_day):
    return UpdateScheduleDaySchema(
        is_active=dummy_db_schedule_day.is_active,
        work_start_time=dummy_db_schedule_day.work_start_time,
        work_end_time=dummy_db_schedule_day.work_end_time,
        break_start_time=dummy_db_schedule_day.break_start_time,
        break_end_time=dummy_db_schedule_day.break_end_time,
    )


# Schedule repository fixtures
def make_dummy_db_schedule():
    schedule = Schedule()
    schedule.id = uuid.UUID("c5c7ba52-60e6-464c-8d12-f52a7a812bca")
    schedule.doctor_id = uuid.UUID("a5d05a81-4203-4a58-9096-40208fa4182c")
    schedule.specialization_id = 10
    schedule.schedule_name = "Test Schedule"
    schedule.period_start = datetime.date(2025, 1, 30)
    schedule.period_end = datetime.date(2025, 3, 30)
    schedule.patient_type = AppointmentPatientTypeEnum.ADULT
    schedule.is_active = True
    schedule.payment_types = {"GOBMP": False, "DMS": True, "OSMS": False, "paid": True}
    schedule.referral_types = {"with_referral": True, "without_referral": True}
    schedule.referral_origins = {"from_external_organization": True, "self_registration": False}

    return schedule


@pytest.fixture
def dummy_db_schedule():
    return make_dummy_db_schedule()


@pytest.fixture
def dummy_schedule_domain(dummy_db_schedule):
    return ScheduleDomain(
        id=dummy_db_schedule.id,
        doctor_id=dummy_db_schedule.doctor_id,
        schedule_name=dummy_db_schedule.schedule_name,
        period_start=dummy_db_schedule.period_start,
        period_end=dummy_db_schedule.period_end,
        is_active=dummy_db_schedule.is_active,
        appointment_interval=dummy_db_schedule.appointment_interval,
    )


# AuthServiceRepositoryImpl fixtures
class DummyAuthRepo(AuthServiceRepositoryInterface):
    def __init__(self, perms: List[Dict[str, Any]]):
        self.perms = perms
        self.called_with: Optional[str] = None

    async def get_permissions(self, token: str) -> List[Dict[str, Any]]:
        self.called_with = token
        return self.perms


@pytest.fixture
def dummy_auth_service_repository(dummy_permissions):
    return DummyAuthRepo(dummy_permissions)


# 'check_user_permissions' dependency fixtures
@pytest.fixture
def dummy_permissions() -> List[Dict[str, Any]]:
    permissions: List[Dict[str, Any]] = [
        {"resource_name": "dummy_resource_r"},
        {"resource_name": "dummy_resource_w"},
    ]

    return permissions


@pytest.fixture
def dummy_permissions_with_scopes() -> list:
    return [
        {"resource_name": "dummy_resource_r", "scopes": ["read"]},
        {"resource_name": "dummy_resource_w", "scopes": ["write", "read"]},
    ]


# User repository and service fixtures
@pytest.fixture
def dummy_db_user() -> User:
    user = User()
    user.id = uuid.uuid4()
    user.first_name = "John"
    user.last_name = "Doe"
    user.middle_name = "M"
    user.iin = "123456789012"
    user.date_of_birth = datetime.date(1990, 1, 1)
    user.client_roles = ["user"]
    user.enabled = True
    return user


@pytest.fixture(autouse=True)
def patch_map_entity_to_domain(monkeypatch, dummy_db_user, dummy_user_domain):
    repository_module = importlib.import_module(
        "src.apps.users.infrastructure.repositories.user_repository"
    )
    monkeypatch.setattr(
        repository_module,
        "map_user_db_entity_to_domain",
        lambda db_obj: dummy_user_domain,
    )
    monkeypatch.setattr(
        repository_module,
        "map_user_domain_to_db_entity",
        lambda domain_obj: dummy_db_user,
    )


@pytest.fixture
def dummy_user_repo():
    repository = MagicMock(spec=UserRepositoryInterface)
    repository.get_by_id = AsyncMock()
    repository.get_by_iin = AsyncMock()
    repository.create = AsyncMock()
    repository.update = AsyncMock()
    repository.delete = AsyncMock()

    return repository


@pytest.fixture
def dummy_user_id():
    return uuid.uuid4()


@pytest.fixture
def dummy_user_domain():
    schema = UserSchema(
        id=uuid.uuid4(),
        first_name="John",
        last_name="Doe",
        middle_name="M",
        iin="123456789012",
        date_of_birth=datetime.date(1990, 1, 1),
        client_roles=["User", "Doctor"],
        enabled=True,
        specializations=[
            SpecializationModel(name="Терапевт", id='137')
        ],
        attachment_data=AttachmentDataModel(
            area_number=1,
            organization_name="Central Hospital",
            attachment_date="2024-01-01",
            detachment_date="2024-12-31",
            department_name="Therapy"
        ),
        served_patient_types=["adult", "child"],
        served_referral_types=["with_referral", "without_referral"],
        served_referral_origins=["from_external_organization", "self_registration"],
        served_payment_types=["GOBMP", "DMS", "OSMS", "paid"],
    )

    return map_user_schema_to_domain(schema)


@pytest.fixture(autouse=True)
def patch_map_user_schema_to_domain(monkeypatch, dummy_user_domain):
    service_module = importlib.import_module("src.apps.users.services.user_service")
    monkeypatch.setattr(
        service_module,
        "map_user_schema_to_domain",
        lambda schema: dummy_user_domain,
    )


@pytest.fixture
def mock_citizenship_catalog_repository(mock_async_db_session, dummy_logger):
    return SQLAlchemyCitizenshipCatalogueRepositoryImpl(
        async_db_session=mock_async_db_session,
        logger=dummy_logger,
    )


# Nationalities catalog fixtures
@pytest.fixture
def mock_nationalities_catalog_repository(
        mock_async_db_session,
        dummy_logger
) -> SQLAlchemyNationalitiesCatalogRepositoryImpl:
    return SQLAlchemyNationalitiesCatalogRepositoryImpl(
        async_db_session=mock_async_db_session,
        logger=dummy_logger,
    )


@pytest.fixture
def dummy_nationality_from_db():
    db_object = MagicMock(spec=SQLAlchemyNationalitiesCatalogue)

    # Fields assigning...
    db_object.id = 1
    db_object.name_ru = "Русский"
    db_object.name_en = "Russian"
    db_object.name_kz = "Орыс"

    return db_object


# Fixtures for patient context attributes
@pytest.fixture(autouse=True)
def default_language(monkeypatch):
    monkeypatch.setattr(project_settings, "DEFAULT_LANGUAGE", "en")


@pytest.fixture(autouse=True)
def locale(monkeypatch):
    monkeypatch.setattr(
        "src.apps.catalogs.services.nationalities_catalog_service.get_locale",
        lambda: "en",
    )
    monkeypatch.setattr(
        "src.apps.catalogs.services.patient_context_attribute_service.get_locale",
        lambda: "en",
    )
    monkeypatch.setattr(
        "src.apps.catalogs.services.financing_sources_catalog_service.get_locale",
        lambda: "ru",
    )


@pytest.fixture
def nationalities_catalog_repository():
    repository = MagicMock(spec=SQLAlchemyNationalitiesCatalogRepositoryImpl)

    repository.get_by_id = AsyncMock()
    repository.get_nationalities = AsyncMock()
    repository.get_total_number_of_nationalities = AsyncMock()
    repository.get_by_default_name = AsyncMock()
    repository.get_by_locale = AsyncMock()
    repository.add_nationality = AsyncMock()
    repository.update_nationality = AsyncMock()

    return repository


@pytest.fixture
def patient_context_attributes_repository():
    repository = MagicMock()

    repository.get_by_id = AsyncMock()
    repository.get_patient_context_attributes = AsyncMock()
    repository.get_total_number_of_patient_context_attributes = AsyncMock()
    repository.get_by_default_name = AsyncMock()
    repository.get_by_locale = AsyncMock()
    repository.add_patient_context_attribute = AsyncMock()
    repository.update_patient_context_attribute = AsyncMock()
    repository.delete_by_id = AsyncMock()

    return repository


@pytest.fixture
def nationalities_catalog_service(dummy_logger, nationalities_catalog_repository):
    return NationalitiesCatalogService(dummy_logger, nationalities_catalog_repository)


@pytest.fixture
def patient_context_attribute_service(dummy_logger, patient_context_attributes_repository):
    return PatientContextAttributeService(dummy_logger, patient_context_attributes_repository)


@pytest.fixture
def financing_sources_catalog_repository(mock_async_db_session, dummy_logger):
    return SQLAlchemyFinancingSourcesCatalogRepositoryImpl(
        async_db_session=mock_async_db_session,
        logger=dummy_logger,
    )


@pytest.fixture
def dummy_financing_source_from_db():
    return SQLAlchemyFinancingSourcesCatalog(
        id=7,
        name="DummyName",
        code="DummyCode",
        lang=get_locale(),
        name_locales={
            "en": "DummyName_EN",
            "kk": "DummyName_KK",
        },
        created_at=datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc),
        changed_at=datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc),
    )


@pytest.fixture
def mock_financing_sources_catalog_repository(mock_async_db_session, dummy_logger):
    repository = MagicMock(spec=FinancingSourcesCatalogRepositoryInterface)

    repository.get_by_id = AsyncMock()
    repository.get_financing_sources = AsyncMock()
    repository.get_total_number_of_financing_sources = AsyncMock()
    repository.get_by_default_name = AsyncMock()
    repository.get_by_name_locale = AsyncMock()
    repository.get_by_financing_source_code = AsyncMock()
    repository.add_financing_source = AsyncMock()
    repository.update_financing_source = AsyncMock()

    return repository


@pytest.fixture
def medical_organizations_repository():
    repository = MagicMock()

    repository.get_by_id = AsyncMock()
    repository.get_medical_organizations = AsyncMock()
    repository.get_total_number_of_medical_organizations = AsyncMock()
    repository.get_by_default_name = AsyncMock()
    repository.get_by_organization_code = AsyncMock()
    repository.get_by_name_locale = AsyncMock()
    repository.get_by_address_locale = AsyncMock()
    repository.add_medical_organization = AsyncMock()
    repository.update_medical_organization = AsyncMock()
    repository.delete_by_id = AsyncMock()

    return repository


@pytest.fixture
def dummy_citizenship_full():
    now = datetime.datetime.now(datetime.UTC)
    return CitizenshipCatalogFullResponseSchema(
        id=1,
        name="TestCountryCitizenship",
        lang=project_settings.DEFAULT_LANGUAGE,
        name_locales={"ru": "ТестоваяСтрана"},
        country_code="TC",
        created_at=now,
        changed_at=now,
    )


@pytest.fixture
def dummy_citizenship_partial(dummy_citizenship_full):
    return CitizenshipCatalogPartialResponseSchema(
        id=dummy_citizenship_full.id,
        name=dummy_citizenship_full.name,
        lang=project_settings.DEFAULT_LANGUAGE,
        country_code=dummy_citizenship_full.country_code,
        created_at=dummy_citizenship_full.created_at,
        changed_at=dummy_citizenship_full.changed_at,
    )


@pytest.fixture
def mock_citizenship_repository(mocker, dummy_citizenship_full):
    repository = MagicMock()

    repository.get_by_id = AsyncMock(return_value=dummy_citizenship_full)
    repository.get_citizenship_records = AsyncMock(return_value=[dummy_citizenship_full])
    repository.get_total_number_of_citizenship_records = AsyncMock(return_value=1)
    repository.get_by_default_name = AsyncMock(return_value=False)
    repository.get_by_country_code = AsyncMock(return_value=None)
    repository.get_by_locale = AsyncMock(return_value=False)
    repository.add_citizenship = AsyncMock(return_value=dummy_citizenship_full)
    repository.update_citizenship = AsyncMock(return_value=dummy_citizenship_full)
    repository.delete_by_id = AsyncMock()

    return repository


@pytest.fixture
def financing_sources_catalog_service(dummy_logger, mock_financing_sources_catalog_repository):
    return FinancingSourceCatalogService(dummy_logger, mock_financing_sources_catalog_repository)


@pytest.fixture
def dummy_full_financing_source_schema():
    return FinancingSourceFullResponseSchema.model_construct(
        id=7,
        name="NameEN",
        financing_source_code="CODE1",
        lang="en",
        name_locales={"ru": "ИмяRU"},
        created_at=datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc),
        changed_at=datetime.datetime(2020, 1, 2, tzinfo=datetime.timezone.utc),
    )


@pytest.fixture
def full_medorg():
    return MedicalOrganizationCatalogFullResponseSchema(
        id=7,
        name="NewOrg",
        code="MO-2",
        address="New Address",
        lang="en",
        name_locales={"ru": "Новая"},
        address_locales={"ru": "Новый адрес"},
        created_at=datetime.datetime(2025, 1, 1, tzinfo=datetime.UTC),
        changed_at=datetime.datetime(2025, 1, 2, tzinfo=datetime.UTC),
    )


@pytest.fixture
def medorg_partial(full_medorg):
    return MedicalOrganizationCatalogPartialResponseSchema(
        id=full_medorg.id,
        name=full_medorg.name,
        organization_code=full_medorg.organization_code,
        address=full_medorg.address,
        lang="en",
        created_at=full_medorg.created_at,
        changed_at=full_medorg.changed_at,
    )


@pytest.fixture
def add_medorg_schema():
    return AddMedicalOrganizationSchema.model_construct(
        name="NewOrg",
        organization_code="MO-2",
        address="New Address",
        lang="en",
        name_locales={"ru": "Новая"},
        address_locales={"ru": "Новый адрес"},
    )


@pytest.fixture
def update_medorg_schema():
    return UpdateMedicalOrganizationSchema.model_construct(
        name="UpdatedOrg",
        organization_code="MO-3",
        address="Updated Address",
        lang="en",
        name_locales={"ru": "Обновлённая"},
        address_locales={"ru": "Обновлённый адрес"},
    )


@pytest.fixture
def medical_organizations_service(dummy_logger, medical_organizations_repository):
    return MedicalOrganizationsCatalogService(dummy_logger, medical_organizations_repository)


@pytest.fixture
def citizenship_service(mock_citizenship_repository, dummy_logger):
    return CitizenshipCatalogService(dummy_logger, mock_citizenship_repository)


# Platform rules fixtures
@pytest.fixture
def dummy_db_platform_rule():
    db_object = MagicMock(spec=SQLAlchemyPlatformRule)
    db_object.id = 1
    db_object.rule_data = {"MAX_SCHEDULE_PERIOD": {"value": 30}}
    db_object.description = "Test description"

    return db_object


@pytest.fixture
def dummy_response_platform_rule(dummy_db_platform_rule):
    return ResponsePlatformRuleSchema(
        id=1,
        key="MAX_SCHEDULE_PERIOD",
        rule_data={"value": 30},
        description="desc",
    )


# Patients repository fixtures
@pytest.fixture
def mock_patient_repository_impl(mock_async_db_session, dummy_logger) -> SQLAlchemyPatientRepository:
    return SQLAlchemyPatientRepository(mock_async_db_session, dummy_logger)


@pytest.fixture
def dummy_db_patient():
    db_object = MagicMock()
    db_object.id = uuid.uuid4()
    db_object.iin = "040806501543"

    return db_object


@pytest.fixture
def dummy_domain_patient():
    domain_object = MagicMock()
    return domain_object


@pytest.fixture(autouse=True)
def patch_mapper(monkeypatch, dummy_domain_patient):
    monkeypatch.setattr(
        "src.apps.patients.infrastructure.repositories.patient_repository.map_patient_db_entity_to_domain",
        lambda db_obj: dummy_domain_patient
    )


@pytest.fixture
def mock_patient_repository():
    repository = MagicMock()

    repository.get_by_id = AsyncMock()
    repository.get_by_iin = AsyncMock()
    repository.get_patients = AsyncMock()
    repository.get_total_number_of_patients = AsyncMock()

    return repository


@pytest.fixture
def mock_catalog_services():
    return (
        AsyncMock(),  # citizenship_service
        AsyncMock(),  # nationalities_service
        AsyncMock(),  # medical_org_service
        AsyncMock(),  # financing_source_service
        AsyncMock(),  # patient_context_attributes_service
    )


@pytest.fixture
def mock_uow():
    uow = MagicMock()

    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)

    uow.patients_repository = MagicMock(
        create_patient=AsyncMock(),
        update_patient=AsyncMock(),
        delete_by_id=AsyncMock()
    )

    return uow


@pytest.fixture
def patient_service(mock_uow, mock_patient_repository, mock_catalog_services):
    (
        citizenship_service,
        nationalities_service,
        medical_org_service,
        financing_source_service,
        patient_context_attributes_service
    ) = mock_catalog_services

    return PatientService(
        uow=mock_uow,
        patients_repository=mock_patient_repository,
        citizenship_service=citizenship_service,
        nationalities_service=nationalities_service,
        medical_org_service=medical_org_service,
        financing_source_service=financing_source_service,
        patient_context_attributes_service=patient_context_attributes_service,
    )


@pytest.fixture
def mock_insurance_info_catalog_repository():
    repository = MagicMock(spec=SQLAlchemyInsuranceInfoCatalogRepositoryImpl)

    repository.get_total_number_of_insurance_info_records = AsyncMock()
    repository.get_by_id = AsyncMock()
    repository.get_insurance_info_records = AsyncMock()
    repository.add_insurance_info_record = AsyncMock()
    repository.update_insurance_info_record = AsyncMock()
    repository.delete_by_id = AsyncMock()

    return repository


@pytest.fixture
def mock_patients_service():
    service = MagicMock(spec=PatientService)
    service.get_by_id = AsyncMock()

    return service


@pytest.fixture
def mock_financing_sources_catalog_service():
    service = MagicMock(spec=FinancingSourceCatalogService)
    service.get_by_id = AsyncMock()

    return service


@pytest.fixture
def insurance_info_service(
        dummy_logger,
        mock_insurance_info_catalog_repository,
        mock_patients_service,
        mock_financing_sources_catalog_service,
):
    return InsuranceInfoCatalogService(
        logger=dummy_logger,
        insurance_info_catalog_repository=mock_insurance_info_catalog_repository,
        patients_service=mock_patients_service,
        financing_sources_catalog_service=mock_financing_sources_catalog_service
    )


@pytest.fixture
def insurance_info_catalog_repository_impl(dummy_logger, mock_async_db_session):
    return SQLAlchemyInsuranceInfoCatalogRepositoryImpl(
        logger=dummy_logger,
        async_db_session=mock_async_db_session
    )


@pytest.fixture
def mock_add_insurance_info_catalog_schema():
    return AddInsuranceInfoRecordSchema(
        policy_number="DUMMY_POLICY_NUMBER_001",
        company="Dummy Company Limited",
        valid_from=datetime.date(2025, 6, 5),
        valid_till=datetime.date(2026, 6, 5),
        comment="One-year insurance plan",
        patient_id=uuid.uuid4(),
        financing_source_id=1
    )


@pytest.fixture
def mock_update_insurance_info_catalog_schema():
    return AddInsuranceInfoRecordSchema(
        policy_number="UPDATED_DUMMY_POLICY_NUMBER_001",
        company="Updated Dummy Company Limited",
        valid_from=datetime.date(2025, 6, 5),
        valid_till=None,
        comment=None,
        patient_id=uuid.uuid4(),
        financing_source_id=1
    )


@pytest.fixture
def mock_insurance_info_db_entity():
    return SQLAlchemyInsuranceInfoCatalogue(
        id=1,
        policy_number="DUMMY_POLICY_NUMBER_001",
        company="Dummy Company Limited",
        valid_from=datetime.date(2025, 6, 5),
        valid_till=datetime.date(2026, 6, 5),
        comment="One-year insurance plan",
        patient_id=uuid.uuid4(),
        financing_source_id=1
    )


# Diagnoses catalog fixtures
@pytest.fixture
def diagnoses_catalog_repository_impl(
        mock_async_db_session,
        dummy_logger
):
    return SQLAlchemyDiagnosesCatalogRepositoryImpl(
        async_db_session=mock_async_db_session,
        logger=dummy_logger
    )


@pytest.fixture
def mock_diagnoses_catalog_response_from_db():
    return SQLAlchemyDiagnosesCatalogue(
        id=12,
        diagnosis_code='AJ-09',
        description='Dummy description',
        is_active=True,
    )


@pytest.fixture
def mock_diagnoses_catalog_response_schema():
    return DiagnosesCatalogResponseSchema(
        id=12,
        diagnosis_code='AJ-09',
        description='Dummy description',
        is_active=True,
    )


@pytest.fixture
def mock_diagnoses_catalog_add_schema():
    return AddDiagnosisRequestSchema(
        diagnosis_code='AJ-09',
        description='Dummy description',
        is_active=True,
    )


@pytest.fixture
def mock_diagnoses_catalog_update_schema():
    return UpdateDiagnosisRequestSchema(
        diagnosis_code='МКБ-24',
        description='Dummy updated description',
        is_active=False,
    )


# Diagnoses and patients repository fixtures
@pytest.fixture
def diagnoses_and_patients_repository_impl(
        mock_async_db_session,
        dummy_logger
):
    return SQLAlchemyDiagnosedPatientDiagnosisRepositoryImpl(
        async_db_session=mock_async_db_session,
        logger=dummy_logger
    )


@pytest.fixture
def mock_diagnoses_and_patients_response_from_db():
    return SQLAlchemyPatientsAndDiagnoses(
        id=uuid.uuid4(),
        date_diagnosed=datetime.date(2020, 6, 5),
        comment="Dummy comment",
        diagnosis_id=1,
        patient_id=uuid.uuid4(),
        doctor_id=uuid.uuid4(),
    )


@pytest.fixture
def mock_diagnoses_and_patients_response_schema(mock_diagnoses_catalog_response_schema):
    truncated_patient = PatientTruncatedResponseSchema(
        id=uuid.uuid4(),
        iin='040806501543',
        first_name='Alex',
        last_name='Turlov',
        middle_name='Alexandrovich',
    )

    truncated_doctor = DoctorTruncatedResponseSchema(
        id=uuid.uuid4(),
        iin='140866501542',
        first_name='Pupka',
        last_name='Zalupka',
        middle_name=None,
    )

    return DiagnosedPatientDiagnosisResponseSchema(
        id=uuid.uuid4(),
        date_diagnosed=datetime.date(2020, 6, 5),
        comment="Dummy comment",
        diagnosis=mock_diagnoses_catalog_response_schema,
        patient=truncated_patient,
        doctor=truncated_doctor,
    )


@pytest.fixture
def mock_diagnoses_and_patients_add_schema():
    return AddDiagnosedPatientDiagnosisRecordRequestSchema(
        date_diagnosed=datetime.date(2020, 6, 5),
        comment="Dummy comment",
        diagnosis_id=1,
        doctor_id=uuid.uuid4(),
        patient_id=uuid.uuid4(),
    )


@pytest.fixture
def mock_diagnoses_and_patients_update_schema():
    return UpdateDiagnosedPatientDiagnosisRecordRequestSchema(
        date_diagnosed=datetime.date(2020, 6, 4),
        comment=None,
        doctor_id=uuid.uuid4(),
    )


# Identity documents catalog fixtures
@pytest.fixture
def identity_documents_repository_impl(mock_async_db_session, dummy_logger):
    return SQLAlchemyIdentityDocumentsCatalogRepositoryImpl(
        async_db_session=mock_async_db_session,
        logger=dummy_logger
    )


@pytest.fixture
def mock_identity_document_db_entity():
    return SQLAlchemyIdentityDocumentsCatalogue(
        id=1,
        type=IdentityDocumentTypeEnum.ID_CARD,
        series="AB",
        number="1234567",
        issued_by="Gov",
        issue_date=datetime.date(2020, 1, 1),
        expiration_date=datetime.date(2030, 1, 1),
        patient_id=uuid.uuid4(),
        changed_at=datetime.datetime.now(),
        created_at=datetime.datetime.now(),
    )


@pytest.fixture
def mock_identity_document_response_schema(mock_identity_document_db_entity):
    return IdentityDocumentResponseSchema(
        id=mock_identity_document_db_entity.id,
        type=mock_identity_document_db_entity.type,
        series=mock_identity_document_db_entity.series,
        number=mock_identity_document_db_entity.number,
        issued_by=mock_identity_document_db_entity.issued_by,
        issue_date=mock_identity_document_db_entity.issue_date,
        expiration_date=mock_identity_document_db_entity.expiration_date,
        patient_id=mock_identity_document_db_entity.patient_id,
    )


@pytest.fixture
def mock_add_identity_document_schema():
    return AddIdentityDocumentRequestSchema(
        patient_id=uuid.uuid4(),
        type=IdentityDocumentTypeEnum.ID_CARD,
        series="AB",
        number="1234567",
        issued_by="Gov",
        issue_date=datetime.date(2020, 1, 1),
        expiration_date=datetime.date(2030, 1, 1)
    )


@pytest.fixture
def mock_update_identity_document_schema():
    return UpdateIdentityDocumentRequestSchema(
        series="CD",
        number="7654321",
        expiration_date=datetime.date(2035, 1, 1),
        patient_id=None,
        type=None,
        issued_by=None,
        issue_date=None,
    )


@pytest.fixture
def mock_identity_documents_repository(mocker):
    repo = mocker.AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_identity_documents = AsyncMock()
    repo.get_total_number_of_identity_documents = AsyncMock()
    repo.add_identity_document = AsyncMock()
    repo.update_identity_document = AsyncMock()
    repo.delete_by_id = AsyncMock()
    return repo


@pytest.fixture
def mock_patient_service(mocker):
    svc = mocker.AsyncMock()
    svc.get_by_id = AsyncMock()
    return svc


@pytest.fixture
def identity_documents_service(dummy_logger, mock_identity_documents_repository, mock_patient_service):
    return IdentityDocumentsCatalogService(
        logger=dummy_logger,
        identity_documents_repository=mock_identity_documents_repository,
        patients_service=mock_patient_service
    )
