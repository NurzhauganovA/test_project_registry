import enum


class PatientSocialStatusEnum(str, enum.Enum):
    EMPLOYED = "employed"
    UNEMPLOYED = "unemployed"
    SELF_EMPLOYED = "self_employed"
    STUDENT = "student"
    RETIRED = "retired"
    CHILD = "child"
    DISABLED = "disabled"
    NOT_SPECIFIED = "not_specified"


class PatientMaritalStatusEnum(str, enum.Enum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"
    NOT_SPECIFIED = "not_specified"


class PatientGenderEnum(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    NOT_SPECIFIED = "not_specified"


class PatientRelativesKinshipEnum(str, enum.Enum):
    MOTHER = "mother"
    FATHER = "father"
    GRANDMOTHER = "grandmother"
    GRANDFATHER = "grandfather"
    BROTHER = "brother"
    SISTER = "sister"
    COUSIN = "cousin"
    GUARDIAN = "guardian"
    SON = "son"
    DAUGHTER = "daughter"

    NOT_SPECIFIED = "not_specified"


class PatientAddressesEnum(str, enum.Enum):
    ACTUAL = "actual"
    REGISTRATION = "registration"

    NOT_SPECIFIED = "not_specified"


class PatientContactTypeEnum(str, enum.Enum):
    PHONE_NUMBER = "phone_number"
    EMAIL = "email"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"

    NOT_SPECIFIED = "not_specified"


class PatientProfileStatusEnum(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    INACTIVE = "inactive"
