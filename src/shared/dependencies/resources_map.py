from enum import Enum


class AvailableScopesEnum(str, Enum):
    READ = "read"
    CREATE = "create"
    DELETE = "delete"
    UPDATE = "update"


class AvailableResourcesEnum(str, Enum):
    SCHEDULES = "schedules"
    APPOINTMENTS = "appointments"
    PATIENTS_DIAGNOSES = "patients_diagnoses"

    # Catalogs (In Russian: "Справочники")
    DIAGNOSES_CATALOG = "diagnoses_catalog"
    IDENTITY_DOCUMENTS_CATALOG = "identity_documents_catalog"
