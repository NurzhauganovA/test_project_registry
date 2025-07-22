from enum import Enum


class VisitCatalogueTypeEnum(str, Enum):
    """
    Enum representing the visit catalogue type.

    Note:
        * AMBULATORY (In Russian: "Амбулаторный приём")
        * INPATIENT (In Russian: "Стационарный приём")
        * EMERGENCY (In Russian: "Экстренное обращение")
        * HOME (In Russian: "Вызов врача на дом")
        * CONSULTATION (In Russian: "Консультация")
        * SCREENING (In Russian: "Скрининговый осмотр")
        * PREVENTIVE (In Russian: "Профилактический осмотр")
        * LABORATORY (In Russian: "Лабораторное обследование")
        * DIAGNOSTIC (In Russian: "Диагностическое обследование")
        * INDUSTRIAL (In Russian: "Промышленная медицина")
        * VACCINATION (In Russian: "Вакцинация")
        * OTHER (In Russian: "Другое")

    IMPORTANT:
        Any changes to this enum (adding, renaming, or removing values)
        must be reflected accordingly in the localization mapping
        (e.g., `VISIT_TYPE_TRANSLATIONS` dictionary) to keep translations
        consistent and up to date.
    """

    AMBULATORY = "ambulatory"
    INPATIENT = "inpatient"
    EMERGENCY = "emergency"
    HOME = "home"
    CONSULTATION = "consultation"
    SCREENING = "screening"
    PREVENTIVE = "preventive"
    LABORATORY = "laboratory"
    DIAGNOSTIC = "diagnostic"
    INDUSTRIAL = "industrial"
    VACCINATION = "vaccination"
    OTHER = "other"


class IdentityDocumentTypeEnum(str, Enum):
    ID_CARD = "id_card"
    PASSPORT = "passport"
    BIRTH_CERTIFICATE = "birth_certificate"
    RESIDENCE_PERMIT = "residence_permit"
    OTHER = "other"
