from datetime import date
from enum import Enum

from src.apps.patients.domain.patient import PatientDomain
from src.apps.patients.infrastructure.api.schemas.jsonb_fields_schemas import (
    PatientAddressItemSchema,
    PatientAttachmentDataItemSchema,
    PatientContactInfoItemSchema,
    PatientRelativeItemSchema,
)
from src.apps.patients.infrastructure.api.schemas.requests.patient_request_schemas import (
    CreatePatientSchema,
    UpdatePatientSchema,
)
from src.apps.patients.infrastructure.api.schemas.responses.patient_response_schemas import (
    PatientTruncatedResponseSchema,
    ResponsePatientSchema,
)
from src.apps.patients.infrastructure.db_models.patients import SQLAlchemyPatient


def is_empty_structure(value):
    if value is None:
        return True

    if isinstance(value, dict):
        return all(is_empty_structure(v) for v in value.values())

    if isinstance(value, list):
        return all(is_empty_structure(v) for v in value)

    return False


def serialize_value(value):
    if value is None:
        return None

    if isinstance(value, date):
        return value.isoformat()

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, list):
        return [serialize_value(value) for value in value]

    if isinstance(value, dict):
        return {key: serialize_value(value) for key, value in value.items()}

    return value


def safe_serialize(value):
    if is_empty_structure(value):
        return None

    return serialize_value(value)


def map_patient_db_entity_to_domain(db_patient: SQLAlchemyPatient) -> PatientDomain:
    """
    Maps SQLAlchemy patient entity to a domain model.
    """
    return PatientDomain(
        id=db_patient.id,
        iin=db_patient.iin,
        first_name=db_patient.first_name,
        last_name=db_patient.last_name,
        middle_name=db_patient.middle_name,
        maiden_name=db_patient.maiden_name,
        date_of_birth=db_patient.date_of_birth,
        gender=db_patient.gender,
        citizenship_id=db_patient.citizenship_id,
        nationality_id=db_patient.nationality_id,
        financing_sources_ids=(
            [source.id for source in db_patient.financing_sources]
            if db_patient.financing_sources
            else None
        ),
        context_attributes_ids=(
            [attribute.id for attribute in db_patient.additional_attributes]
            if db_patient.additional_attributes
            else None
        ),
        social_status=db_patient.social_status,
        marital_status=db_patient.marital_status,
        attachment_data=db_patient.attachment_data,
        relatives=db_patient.relatives,
        addresses=db_patient.addresses,
        contact_info=db_patient.contact_info,
        profile_status=db_patient.profile_status,
    )


def map_patient_db_entity_to_truncated_response_schema(
    db_patient: SQLAlchemyPatient,
) -> PatientTruncatedResponseSchema:
    return PatientTruncatedResponseSchema(
        id=db_patient.id,
        iin=db_patient.iin,
        first_name=db_patient.first_name,
        last_name=db_patient.last_name,
        middle_name=db_patient.middle_name,
    )


def map_patient_domain_to_db_entity(patient: PatientDomain) -> SQLAlchemyPatient:
    relatives_json = safe_serialize(patient.relatives or [])
    addresses_json = safe_serialize(patient.addresses or [])
    contact_info_json = safe_serialize(patient.contact_info or [])
    attachment_data_json = safe_serialize(patient.attachment_data or {})

    return SQLAlchemyPatient(
        iin=patient.iin,
        first_name=patient.first_name,
        last_name=patient.last_name,
        middle_name=patient.middle_name,
        maiden_name=patient.maiden_name,
        date_of_birth=patient.date_of_birth,
        gender=patient.gender.value if patient.gender else None,
        social_status=patient.social_status.value if patient.social_status else None,
        marital_status=patient.marital_status.value if patient.marital_status else None,
        profile_status=patient.profile_status.value if patient.profile_status else None,
        citizenship_id=patient.citizenship_id,
        nationality_id=patient.nationality_id,
        attachment_data=attachment_data_json,
        relatives=relatives_json,
        addresses=addresses_json,
        contact_info=contact_info_json,
    )


def map_patient_domain_to_response_schema(
    domain: PatientDomain,
) -> ResponsePatientSchema:
    attachment_data = domain.attachment_data or {}
    is_attachment_data_empty = all(
        attachment_data.get(key) is None for key in attachment_data.keys()
    )
    attachment_data_result = (
        None
        if is_attachment_data_empty
        else PatientAttachmentDataItemSchema(
            area_number=attachment_data.get("area_number"),
            attached_clinic_id=attachment_data.get("attached_clinic_id"),
        )
    )

    return ResponsePatientSchema(
        id=domain.id,
        iin=domain.iin,
        first_name=domain.first_name,
        last_name=domain.last_name,
        middle_name=domain.middle_name,
        maiden_name=domain.maiden_name,
        date_of_birth=domain.date_of_birth,
        gender=domain.gender,
        citizenship_id=domain.citizenship_id,
        nationality_id=domain.nationality_id,
        financing_sources_ids=(
            domain.financing_sources_ids
            if domain.financing_sources_ids is not None
            else None
        ),
        context_attributes_ids=(
            domain.context_attributes_ids
            if domain.context_attributes_ids is not None
            else None
        ),
        social_status=domain.social_status,
        marital_status=domain.marital_status,
        attachment_data=attachment_data_result,
        relatives=[
            PatientRelativeItemSchema(
                type=relative.get("type"),
                full_name=relative.get("full_name"),
                iin=relative.get("iin"),
                birth_date=relative.get("birth_date"),
                phone=relative.get("phone"),
                relation_comment=relative.get("relation_comment"),
            )
            for relative in (domain.relatives or [])
        ],
        addresses=[
            PatientAddressItemSchema(
                type=address.get("type"),
                value=address.get("value"),
                is_primary=address.get("is_primary"),
            )
            for address in (domain.addresses or [])
        ],
        contact_info=[
            PatientContactInfoItemSchema(
                type=contact_info_record.get("type"),
                value=contact_info_record.get("value"),
                is_primary=contact_info_record.get("is_primary"),
            )
            for contact_info_record in (domain.contact_info or [])
        ],
        profile_status=domain.profile_status,
    )


def map_create_schema_to_domain(schema: CreatePatientSchema) -> PatientDomain:
    return PatientDomain(
        id=None,
        iin=schema.iin,
        first_name=schema.first_name,
        last_name=schema.last_name,
        middle_name=schema.middle_name,
        maiden_name=schema.maiden_name,
        date_of_birth=schema.date_of_birth,
        gender=schema.gender,
        citizenship_id=schema.citizenship_id,
        nationality_id=schema.nationality_id,
        financing_sources_ids=schema.financing_sources_ids or None,
        context_attributes_ids=schema.context_attributes_ids or None,
        social_status=schema.social_status,
        marital_status=schema.marital_status,
        attachment_data=(
            schema.attachment_data.model_dump() if schema.attachment_data else None
        ),
        relatives=(
            [relative.model_dump() for relative in schema.relatives]
            if schema.relatives
            else None
        ),
        addresses=(
            [address.model_dump() for address in schema.addresses]
            if schema.addresses
            else None
        ),
        contact_info=(
            [
                contact_info_record.model_dump()
                for contact_info_record in schema.contact_info
            ]
            if schema.contact_info
            else None
        ),
        profile_status=schema.profile_status,
    )


def map_update_schema_to_domain(
    schema: UpdatePatientSchema, existing_patient: PatientDomain
) -> PatientDomain:
    """
    Maps a schema to an existing patient domain model.
    Updates only those fields that are explicitly defined in the schema.
    """

    def use(schema, field_name, old_value):
        # Check if the field was passed explicitly in the schema
        if field_name in schema.model_fields_set:
            val = getattr(schema, field_name)

            if val is None:
                return None

            if isinstance(val, list):
                return [item.model_dump() for item in val]

            if hasattr(val, "model_dump"):
                return val.model_dump()

            return val

        # If the field is not passed, we leave the old one
        return old_value

    return PatientDomain(
        id=existing_patient.id,
        iin=use(schema, "iin", existing_patient.iin),
        first_name=use(schema, "first_name", existing_patient.first_name),
        last_name=use(schema, "last_name", existing_patient.last_name),
        middle_name=use(schema, "middle_name", existing_patient.middle_name),
        maiden_name=use(schema, "maiden_name", existing_patient.maiden_name),
        date_of_birth=use(schema, "date_of_birth", existing_patient.date_of_birth),
        gender=use(schema, "gender", existing_patient.gender),
        citizenship_id=use(schema, "citizenship_id", existing_patient.citizenship_id),
        nationality_id=use(schema, "nationality_id", existing_patient.nationality_id),
        financing_sources_ids=use(
            schema, "financing_sources_ids", existing_patient.financing_sources_ids
        ),
        context_attributes_ids=use(
            schema, "context_attributes_ids", existing_patient.context_attributes_ids
        ),
        social_status=use(schema, "social_status", existing_patient.social_status),
        marital_status=use(schema, "marital_status", existing_patient.marital_status),
        attachment_data=use(
            schema, "attachment_data", existing_patient.attachment_data
        ),
        relatives=use(schema, "relatives", existing_patient.relatives),
        addresses=use(schema, "addresses", existing_patient.addresses),
        contact_info=use(schema, "contact_info", existing_patient.contact_info),
        profile_status=use(schema, "profile_status", existing_patient.profile_status),
    )
