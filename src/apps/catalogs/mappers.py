from src.apps.catalogs.infrastructure.api.schemas.requests.diagnoses_catalog_request_schemas import (
    AddDiagnosedPatientDiagnosisRecordRequestSchema,
    AddDiagnosisRequestSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.requests.identity_documents_catalog_request_schemas import (
    AddIdentityDocumentRequestSchema,
    UpdateIdentityDocumentRequestSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.requests.insurance_info_catalog_request_schemas import (
    AddInsuranceInfoRecordSchema,
    UpdateInsuranceInfoRecordSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.diagnoses_catalog_response_schemas import (
    DiagnosedPatientDiagnosisResponseSchema,
    DiagnosesCatalogResponseSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.identity_documents_catalog_response_schemas import (
    IdentityDocumentResponseSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.insurance_info_catalog_response_schemas import (
    ResponseInsuranceInfoRecordSchema,
)
from src.apps.catalogs.infrastructure.db_models.diagnoses_catalogue import (
    SQLAlchemyDiagnosesCatalogue,
    SQLAlchemyPatientsAndDiagnoses,
)
from src.apps.catalogs.infrastructure.db_models.identity_documents_catalogue import (
    SQLAlchemyIdentityDocumentsCatalogue,
)
from src.apps.catalogs.infrastructure.db_models.insurance_info_catalogue import (
    SQLAlchemyInsuranceInfoCatalogue,
)
from src.apps.patients.mappers import map_patient_db_entity_to_truncated_response_schema
from src.apps.users.mappers import map_doctor_db_entity_to_truncated_response_schema


def map_diagnosis_catalog_db_entity_to_response_schema(
    db_entity: SQLAlchemyDiagnosesCatalogue,
) -> DiagnosesCatalogResponseSchema:
    return DiagnosesCatalogResponseSchema(
        id=db_entity.id,
        diagnosis_code=db_entity.diagnosis_code,
        description=db_entity.description,
        is_active=db_entity.is_active,
    )


def map_diagnosis_catalog_create_schema_to_db_entity(
    create_schema: AddDiagnosisRequestSchema,
) -> SQLAlchemyDiagnosesCatalogue:
    return SQLAlchemyDiagnosesCatalogue(
        diagnosis_code=create_schema.diagnosis_code,
        description=create_schema.description,
        is_active=create_schema.is_active if create_schema.is_active else True,
    )


def map_diagnosed_patient_diagnosis_db_entity_to_response_schema(
    db_entity: SQLAlchemyPatientsAndDiagnoses,
) -> DiagnosedPatientDiagnosisResponseSchema:
    return DiagnosedPatientDiagnosisResponseSchema(
        id=db_entity.id,
        date_diagnosed=db_entity.date_diagnosed,
        comment=db_entity.comment,
        diagnosis=map_diagnosis_catalog_db_entity_to_response_schema(
            db_entity.diagnosis
        ),
        patient=map_patient_db_entity_to_truncated_response_schema(db_entity.patient),
        doctor=(
            map_doctor_db_entity_to_truncated_response_schema(db_entity.doctor)
            if db_entity.doctor
            else None
        ),
    )


def map_diagnosed_patient_diagnosis_create_schema_to_db_entity(
    create_schema: AddDiagnosedPatientDiagnosisRecordRequestSchema,
) -> SQLAlchemyPatientsAndDiagnoses:
    return SQLAlchemyPatientsAndDiagnoses(
        date_diagnosed=create_schema.date_diagnosed,
        comment=create_schema.comment,
        diagnosis_id=create_schema.diagnosis_id,
        patient_id=create_schema.patient_id,
        doctor_id=create_schema.doctor_id,
    )


def map_insurance_info_create_schema_to_db_entity(
    create_schema: AddInsuranceInfoRecordSchema,
) -> SQLAlchemyInsuranceInfoCatalogue:
    return SQLAlchemyInsuranceInfoCatalogue(
        financing_source_id=create_schema.financing_source_id,
        policy_number=create_schema.policy_number,
        company=create_schema.company,
        valid_from=create_schema.valid_from,
        valid_till=create_schema.valid_till,
        comment=create_schema.comment,
        patient_id=create_schema.patient_id,
    )


def map_insurance_info_update_schema_to_db_entity(
    db_entity: SQLAlchemyInsuranceInfoCatalogue,
    update_schema: UpdateInsuranceInfoRecordSchema,
) -> SQLAlchemyInsuranceInfoCatalogue:
    """
    Update the database entity fields with values from the update schema.

    Only fields explicitly provided in the update schema (`model_fields_set`) are updated.
    This allows distinguishing between fields that should remain unchanged and those
    that should be explicitly set to None (i.e., cleared).

    Args:
        db_entity (SQLAlchemyInsuranceInfoCatalogue): The existing database entity to update.
        update_schema (UpdateInsuranceInfoRecordSchema): The Pydantic update schema containing new values.

    Returns:
        SQLAlchemyInsuranceInfoCatalogue: The updated database entity with applied changes.
    """
    for field in update_schema.model_fields_set:
        value = getattr(update_schema, field)
        setattr(db_entity, field, value)

    return db_entity


def map_insurance_info_db_entity_to_response_schema(
    db_entity: SQLAlchemyInsuranceInfoCatalogue,
) -> ResponseInsuranceInfoRecordSchema:
    return ResponseInsuranceInfoRecordSchema(
        id=db_entity.id,
        financing_source_id=db_entity.financing_source_id,
        policy_number=db_entity.policy_number,
        company=db_entity.company,
        valid_from=db_entity.valid_from,
        valid_till=db_entity.valid_till,
        comment=db_entity.comment,
        patient_id=db_entity.patient_id,
    )


def map_identity_document_create_schema_to_db_entity(
    create_schema: AddIdentityDocumentRequestSchema,
) -> SQLAlchemyIdentityDocumentsCatalogue:
    return SQLAlchemyIdentityDocumentsCatalogue(
        patient_id=create_schema.patient_id,
        type=create_schema.type,
        series=create_schema.series,
        number=create_schema.number,
        issued_by=create_schema.issued_by,
        issue_date=create_schema.issue_date,
        expiration_date=create_schema.expiration_date,
    )


def map_identity_document_update_schema_to_db_entity(
    db_entity: SQLAlchemyIdentityDocumentsCatalogue,
    update_schema: UpdateIdentityDocumentRequestSchema,
) -> SQLAlchemyIdentityDocumentsCatalogue:
    update_data = update_schema.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_entity, field, value)

    return db_entity


def map_identity_document_db_entity_to_response_schema(
    db_entity: SQLAlchemyIdentityDocumentsCatalogue,
) -> IdentityDocumentResponseSchema:
    return IdentityDocumentResponseSchema(
        id=db_entity.id,
        patient_id=db_entity.patient_id,
        type=db_entity.type,
        series=db_entity.series,
        number=db_entity.number,
        issued_by=db_entity.issued_by,
        issue_date=db_entity.issue_date,
        expiration_date=db_entity.expiration_date,
    )
