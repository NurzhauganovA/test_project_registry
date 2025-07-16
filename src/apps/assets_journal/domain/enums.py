import enum


class AssetStatusEnum(enum.Enum):
    """Статус актива"""
    REGISTERED = "registered"         # Зарегистрирован
    CONFIRMED = "confirmed"          # Подтвержден
    REFUSED = "refused"              # Отказан
    CANCELLED = "cancelled"          # Отменен


class AssetDeliveryStatusEnum(enum.Enum):
    """Статус доставки"""
    RECEIVED_AUTOMATICALLY = "received_automatically"  # Получен автоматически
    PENDING_DELIVERY = "pending_delivery"             # Ожидает доставки
    DELIVERED = "delivered"                           # Доставлен


class AssetTypeEnum(enum.Enum):
    """Тип актива"""
    STATIONARY = "stationary"         # Стационар
    EMERGENCY = "emergency"           # Скорая помощь
    POLYCLINIC = "polyclinic"        # Поликлиника
    MATERNITY = "maternity"          # Роддом
    NEWBORN = "newborn"              # Новорожденный
    DECEASED = "deceased"            # Умерший
    HOSPITAL_REFUSAL = "hospital_refusal"  # Отказ от госпитализации


class ReferralTargetEnum(enum.Enum):
    """Цель направления"""
    REHABILITATION = "600"           # Восстановительное лечение
    TREATMENT = "100"                # Лечение
    DIAGNOSIS = "200"                # Диагностика
    CONSULTATION = "300"             # Консультация


class ReferralTypeEnum(enum.Enum):
    """Тип направления"""
    REHABILITATION_TREATMENT = "800" # Направление на восстановительное лечение
    PLANNED_HOSPITALIZATION = "100" # Плановая госпитализация
    EMERGENCY_HOSPITALIZATION = "200" # Экстренная госпитализация


class RehabilitationTypeEnum(enum.Enum):
    """Тип реабилитации"""
    MEDICAL = "200"                  # Медицинская реабилитация
    SOCIAL = "100"                   # Социальная реабилитация


class EmergencyOutcomeEnum(enum.Enum):
    """Исход обращения скорой помощи"""
    HOSPITALIZED = "hospitalized"           # Госпитализирован
    TREATED_AT_HOME = "treated_at_home"     # Лечение на дому
    REFUSED_TREATMENT = "refused_treatment" # Отказ от лечения
    DEATH = "death"                         # Смерть
    TRANSFERRED = "transferred"             # Передан другой службе


class DiagnosisTypeEnum(enum.Enum):
    """Тип диагноза"""
    PRIMARY = "primary"              # Основной
    SECONDARY = "secondary"          # Сопутствующий
    COMPLICATION = "complication"    # Осложнение


class DeliveryTypeEnum(enum.Enum):
    """Вид родов"""
    NATURAL = "natural"              # Естественные роды
    CESAREAN = "cesarean"            # Кесарево сечение
    FORCEPS = "forceps"              # Наложение щипцов
    VACUUM = "vacuum"                # Вакуум-экстракция


class PregnancyWeekEnum(enum.Enum):
    """Срок беременности (в неделях)"""
    WEEK_22_27 = "22-27"             # 22-27 недель
    WEEK_28_36 = "28-36"             # 28-36 недель
    WEEK_37_42 = "37-42"             # 37-42 недели
    WEEK_43_PLUS = "43+"             # 43+ недель


class NewbornConditionEnum(enum.Enum):
    """Состояние новорожденного"""
    EXCELLENT = "excellent"          # Отличное
    GOOD = "good"                    # Хорошее
    SATISFACTORY = "satisfactory"    # Удовлетворительное
    SEVERE = "severe"                # Тяжелое
    CRITICAL = "critical"            # Критическое


class TransferDestinationEnum(enum.Enum):
    """Переведен в"""
    HOME = "home"                    # Домой
    ANOTHER_DEPARTMENT = "another_department"  # Другое отделение
    ANOTHER_HOSPITAL = "another_hospital"      # Другую больницу
    REHABILITATION = "rehabilitation"          # Реабилитацию
    SPECIALIZED_CENTER = "specialized_center"  # Специализированный центр


class MedicalServiceTypeEnum(enum.Enum):
    """Тип медицинской услуги"""
    PHARMACY = "pharmacy"            # Аптека
    BLOOD_TEST = "blood_test"        # Анализ крови