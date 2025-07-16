import enum


class AppointmentPatientTypeEnum(enum.Enum):
    ADULT = "adult"
    CHILD = "child"


class AppointmentStatusEnum(enum.Enum):
    FREE = "free"
    BOOKED = "booked"
    CANCELLED = "cancelled"
    APPOINTMENT = "appointment"


class AppointmentReferralTypeEnum(enum.Enum):
    WITHOUT_REFERRAL = "without_referral"
    WITH_REFERRAL = "with_referral"


class AppointmentReferralOriginTypeEnum(enum.Enum):
    INTERNAL = "self_registration"
    EXTERNAL = "from_external_organization"


class AppointmentTypeEnum(enum.Enum):
    INITIAL = "initial"
    REVISIT = "revisit"
    CONSULTATION = "consultation"


class AppointmentInsuranceType(enum.Enum):
    GOBMP = "GOBMP"
    DMS = "DMS"
    OSMS = "OSMS"
    PAID = "paid"
