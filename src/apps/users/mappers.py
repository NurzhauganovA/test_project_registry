from src.apps.users.domain.models.user import UserDomain
from src.apps.users.infrastructure.db_models.models import User
from src.apps.users.infrastructure.schemas.user_schemas import (
    AttachmentDataModel,
    DoctorTruncatedResponseSchema,
    UserSchema,
)


def map_user_domain_to_db_entity(
    user: UserDomain,
    existing_db_entity: User | None = None
) -> User:
    if existing_db_entity is None:
        return User(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            middle_name=user.middle_name,
            full_name=" ".join(
                filter(None, [user.last_name, user.first_name, user.middle_name or ""])
            )[:256],
            iin=user.iin,
            date_of_birth=user.date_of_birth,
            client_roles=user.client_roles,
            enabled=user.enabled,
            served_patient_types=user.served_patient_types,
            served_referral_types=user.served_referral_types,
            served_referral_origins=user.served_referral_origins,
            served_payment_types=user.served_payment_types,
            attachment_data=user.attachment_data,
            specializations=user.specializations,
        )

    existing_db_entity.first_name = user.first_name
    existing_db_entity.last_name = user.last_name
    existing_db_entity.middle_name = user.middle_name
    existing_db_entity.full_name = " ".join(
        filter(None, [user.last_name, user.first_name, user.middle_name or ""])
    )[:256]
    existing_db_entity.iin = user.iin
    existing_db_entity.date_of_birth = user.date_of_birth
    existing_db_entity.client_roles = user.client_roles
    existing_db_entity.enabled = user.enabled
    existing_db_entity.served_patient_types = user.served_patient_types
    existing_db_entity.served_referral_types = user.served_referral_types
    existing_db_entity.served_referral_origins = user.served_referral_origins
    existing_db_entity.served_payment_types = user.served_payment_types
    existing_db_entity.attachment_data = user.attachment_data
    existing_db_entity.specializations = user.specializations

    return existing_db_entity


def map_user_db_entity_to_domain(user_from_db: User) -> UserDomain:
    return UserDomain(
        id=user_from_db.id,
        first_name=user_from_db.first_name,
        last_name=user_from_db.last_name,
        middle_name=user_from_db.middle_name,
        iin=user_from_db.iin,
        date_of_birth=user_from_db.date_of_birth,
        client_roles=user_from_db.client_roles,
        enabled=user_from_db.enabled,
        served_patient_types=user_from_db.served_patient_types,
        served_referral_types=user_from_db.served_referral_types,
        served_referral_origins=user_from_db.served_referral_origins,
        served_payment_types=user_from_db.served_payment_types,
        attachment_data=user_from_db.attachment_data,
        specializations=user_from_db.specializations,
    )


def map_doctor_db_entity_to_truncated_response_schema(
    db_doctor: User,
) -> DoctorTruncatedResponseSchema:
    return DoctorTruncatedResponseSchema(
        id=db_doctor.id,
        iin=db_doctor.iin,
        first_name=db_doctor.first_name,
        last_name=db_doctor.last_name,
        middle_name=db_doctor.middle_name,
    )


def map_user_schema_to_domain(user_schema: UserSchema, existing: UserDomain | None = None) -> UserDomain:
    def choose(field_name):
        val = getattr(user_schema, field_name, None)
        if val is not None:
            return val

        if existing:
            return getattr(existing, field_name, None)

        return None

    attachment_data = (
        user_schema.attachment_data.model_dump()
        if user_schema.attachment_data
        else {}
    )

    specializations = (
        [
            spec.model_dump()
            for spec in user_schema.specializations
        ]
        if user_schema.specializations
        else []
    )

    return UserDomain(
        id=choose("id"),
        first_name=choose("first_name"),
        last_name=choose("last_name"),
        middle_name=choose("middle_name"),
        iin=choose("iin"),
        date_of_birth=choose("date_of_birth"),
        client_roles=choose("client_roles"),
        enabled=choose("enabled"),
        served_patient_types=choose("served_patient_types"),
        served_referral_types=choose("served_referral_types"),
        served_referral_origins=choose("served_referral_origins"),
        served_payment_types=choose("served_payment_types"),
        attachment_data=attachment_data if attachment_data is not None else {},
        specializations=specializations if specializations is not None else [],
    )


def map_user_domain_to_schema(user: UserDomain) -> UserSchema:
    raw = user.attachment_data or {}

    area_number = raw.get("area_number")
    organization_name = raw.get("organization_name")
    attachment_date = raw.get("attachment_date")
    detachment_date = raw.get("detachment_date")
    department_name = raw.get("department_name")

    if (
        area_number is None
        and organization_name is None
        and attachment_date is None
        and detachment_date is None
        and department_name is None
    ):
        attachment = None
    else:
        attachment = AttachmentDataModel(
            area_number=area_number,
            organization_name=organization_name,
            attachment_date=attachment_date,
            detachment_date=detachment_date,
            department_name=department_name,
        )

    return UserSchema(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        middle_name=user.middle_name,
        iin=user.iin,
        date_of_birth=user.date_of_birth,
        client_roles=user.client_roles,
        enabled=user.enabled,
        served_patient_types=user.served_patient_types,
        served_referral_types=user.served_referral_types,
        served_referral_origins=user.served_referral_origins,
        served_payment_types=user.served_payment_types,
        attachment_data=attachment,
        specializations=user.specializations,
    )
