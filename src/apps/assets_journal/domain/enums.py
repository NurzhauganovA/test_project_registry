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