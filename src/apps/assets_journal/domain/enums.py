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


class PolyclinicVisitTypeEnum(enum.Enum):
    """Тип посещения поликлиники"""
    FIRST_VISIT = "first_visit"         # Первичное обращение
    REPEAT_VISIT = "repeat_visit"       # Повторное обращение


class PolyclinicServiceTypeEnum(enum.Enum):
    """Тип услуги в поликлинике"""
    CONSULTATION = "consultation"       # Консультация
    PROCEDURE = "procedure"             # Процедура
    DIAGNOSTIC = "diagnostic"           # Диагностика
    VACCINATION = "vaccination"         # Вакцинация
    LABORATORY = "laboratory"           # Лабораторные исследования


class WeekdayEnum(enum.Enum):
    """Дни недели"""
    MONDAY = "monday"         # Понедельник
    TUESDAY = "tuesday"       # Вторник
    WEDNESDAY = "wednesday"   # Среда
    THURSDAY = "thursday"     # Четверг
    FRIDAY = "friday"         # Пятница
    SATURDAY = "saturday"     # Суббота
    SUNDAY = "sunday"         # Воскресенье


class PolyclinicOutcomeEnum(enum.Enum):
    """Исход посещения поликлиники"""
    RECOVERED = "recovered"             # Выздоровел
    IMPROVED = "improved"               # Улучшение
    WITHOUT_CHANGES = "without_changes" # Без изменений
    WORSENED = "worsened"              # Ухудшение
    REFERRED = "referred"               # Направлен к другому специалисту
    HOSPITALIZED = "hospitalized"       # Госпитализирован


class RejectionReasonByEnum(enum.Enum):
    """Кто отклонил актив"""
    PATIENT = "patient"           # Пациент
    SPECIALIST = "specialist"     # Специалист
    ADMINISTRATION = "administration"  # Администрация


class PolyclinicReasonAppeal(enum.Enum):
    """Повод обращения"""
    PATRONAGE = "patronage"         # Патронаж
    ROUTINE_CHECKUP = "routine_checkup"  # Плановый осмотр


class PolyclinicTypeActiveVisit(enum.Enum):
    """Вид активного посещения"""
    FIRST_APPEAL = "first_appeal"       # Первичное обращение
    REPEAT_APPEAL = "repeat_appeal"     # Повторное обращение
    EMERGENCY_APPEAL = "emergency_appeal"  # Экстренное обращение
    PLANNED_APPEAL = "planned_appeal"   # Плановое обращение


class MaternityOutcomeEnum(enum.Enum):
    """Исход лечения в роддоме"""
    DISCHARGED = "discharged"           # Выписан
    TRANSFERRED = "transferred"         # Переведен
    IMPROVED = "improved"               # Улучшение
    DEATH = "death"                     # Смерть


class MaternityAdmissionTypeEnum(enum.Enum):
    """Тип госпитализации в роддом"""
    PLANNED = "planned"                 # Плановая
    EMERGENCY = "emergency"             # Экстренная
    REFERRAL = "referral"               # По направлению


class MaternityDiagnosisTypeEnum(enum.Enum):
    """Тип диагноза в роддоме"""
    PRIMARY = "primary"                 # Основной
    SECONDARY = "secondary"             # Сопутствующий
    COMPLICATION = "complication"       # Осложнение


class MaternityStayTypeEnum(enum.Enum):
    """Тип пребывания в роддоме"""
    DELIVERY = "delivery"               # Роды
    GYNECOLOGY = "gynecology"           # Гинекология
    PATHOLOGY = "pathology"             # Патология беременности
    OBSERVATION = "observation"         # Наблюдение


class MaternityStatusEnum(enum.Enum):
    """Статус пациентки в роддоме"""
    PREGNANT = "pregnant"               # Беременная
    IN_LABOR = "in_labor"               # В родах
    POSTPARTUM = "postpartum"           # Послеродовая
    GYNECOLOGICAL = "gynecological"     # Гинекологическая


class SickLeaveStatusEnum(enum.Enum):
    """Статус больничного листа"""
    OPEN = "open"                    # Открыт
    CLOSED = "closed"                # Закрыт
    CANCELLED = "cancelled"          # Отменен
    EXTENSION = "extension"          # Продление


class SickLeaveTypeEnum(enum.Enum):
    """Тип больничного листа"""
    ILLNESS = "illness"               # Заболевание
    INJURY = "injury"                 # Травма
    QUARANTINE = "quarantine"         # Карантин
    CARE = "care"                     # Уход за больным
    PREGNANCY = "pregnancy"           # Беременность и роды
    REHABILITATION = "rehabilitation" # Реабилитация


class WorkCapacityEnum(enum.Enum):
    """Трудоспособность"""
    TEMPORARILY_DISABLED = "temporarily_disabled"            # Временно нетрудоспособен
    LIMITED_CAPACITY = "limited_capacity"                    # Ограниченно трудоспособен
    TRANSFERRED_TO_LIGHT_WORK = "transferred_to_light_work"  # Переведен на легкую работу


class SickLeaveReasonEnum(enum.Enum):
    """Причина выдачи больничного листа"""
    ACUTE_ILLNESS = "acute_illness"                     # Острое заболевание
    CHRONIC_ILLNESS = "chronic_illness"                 # Хроническое заболевание
    WORK_INJURY = "work_injury"                         # Производственная травма
    DOMESTIC_INJURY = "domestic_injury"                 # Бытовая травма
    PREGNANCY_COMPLICATIONS = "pregnancy_complications" # Осложнения беременности
    CHILD_CARE = "child_care"                           # Уход за ребенком
    FAMILY_MEMBER_CARE = "family_member_care"           # Уход за членом семьи


class HomeCallStatusEnum(enum.Enum):
    """Статус вызова на дом"""
    REGISTERED = "registered"           # Зарегистрирован
    IN_PROGRESS = "in_progress"         # В работе
    COMPLETED = "completed"             # Выполнен
    CANCELLED = "cancelled"             # Отменен


class HomeCallCategoryEnum(enum.Enum):
    """Категория вызова"""
    EMERGENCY = "emergency"             # Экстренный
    URGENT = "urgent"                   # Срочный
    PLANNED = "planned"                 # Плановый


class HomeCallSourceEnum(enum.Enum):
    """Источник вызова"""
    EGOV = "egov"                     # Egov
    CALL_PATIENT = "call_patient"       # Звонок пациента
    APPLICATION = "application"         # Приложение


class HomeCallReasonEnum(enum.Enum):
    """Повод вызова"""
    ILLNESS = "illness"                 # Заболевание
    INJURY = "injury"                   # Травма
    CONSULTATION = "consultation"       # Консультация
    VACCINATION = "vaccination"         # Вакцинация
    MEDICAL_CERTIFICATE = "medical_certificate"  # Справка
    CHRONIC_DISEASE = "chronic_disease" # Хроническое заболевание
    ACUTE_CONDITION = "acute_condition" # Острое состояние
    PREVENTIVE_CARE = "preventive_care" # Профилактический осмотр
    OTHER = "other"                     # Другое


class HomeCallTypeEnum(enum.Enum):
    """Тип вызова"""
    THERAPEUTIC = "therapeutic"         # Терапевтический
    PEDIATRIC = "pediatric"             # Педиатрический
    SPECIALIST = "specialist"           # Специализированный
    NURSING = "nursing"                 # Сестринский
    DIAGNOSTIC = "diagnostic"           # Диагностический


class HomeCallVisitTypeEnum(enum.Enum):
    """Вид посещения"""
    PRIMARY = "primary"                 # Первичный
    REPEAT = "repeat"                   # Повторный


class HomeCallUrgencyEnum(enum.Enum):
    """Срочность вызова"""
    IMMEDIATE = "immediate"             # Немедленно
    WITHIN_1_HOUR = "within_1_hour"     # В течение 1 часа
    WITHIN_4_HOURS = "within_4_hours"   # В течение 4 часов
    WITHIN_24_HOURS = "within_24_hours" # В течение 24 часов
    PLANNED = "planned"                 # Плановый


class HomeCallOutcomeEnum(enum.Enum):
    """Исход вызова"""
    TREATED_AT_HOME = "treated_at_home"         # Лечение на дому
    HOSPITALIZED = "hospitalized"               # Госпитализирован
    REFERRED_TO_CLINIC = "referred_to_clinic"   # Направлен в поликлинику
    REFUSED_TREATMENT = "refused_treatment"     # Отказ от лечения
    PATIENT_NOT_FOUND = "patient_not_found"     # Пациент не найден
    FALSE_CALL = "false_call"                   # Ложный вызов


class StaffAssignmentStatusEnum(enum.Enum):
    """Статус назначения медперсонала"""
    ACTIVE = "active"                   # Активен
    INACTIVE = "inactive"               # Неактивен
    SUSPENDED = "suspended"             # Приостановлен
    COMPLETED = "completed"             # Завершен


class MedicalSpecializationEnum(enum.Enum):
    """Медицинские специализации"""
    THERAPIST = "therapist"             # Терапевт
    PEDIATRICIAN = "pediatrician"       # Педиатр
    CARDIOLOGIST = "cardiologist"       # Кардиолог
    NEUROLOGIST = "neurologist"         # Невролог
    SURGEON = "surgeon"                 # Хирург
    GYNECOLOGIST = "gynecologist"       # Гинеколог
    UROLOGIST = "urologist"             # Уролог
    DERMATOLOGIST = "dermatologist"     # Дерматолог
    OPHTHALMOLOGIST = "ophthalmologist" # Офтальмолог
    OTOLARYNGOLOGIST = "otolaryngologist" # ЛОР
    PSYCHIATRIST = "psychiatrist"       # Психиатр
    PSYCHOLOGIST = "psychologist"       # Психолог
    PSYCHOTHERAPIST = "psychotherapist" # Психотерапевт
    GENERAL_PRACTITIONER = "general_practitioner" # Врач общей практики
    NURSE = "nurse"                     # Медсестра
    PARAMEDIC = "paramedic"             # Фельдшер


class MedicalDepartmentEnum(enum.Enum):
    """Медицинские отделения"""
    THERAPEUTIC = "therapeutic"         # Терапевтическое
    PEDIATRIC = "pediatric"             # Педиатрическое
    SURGICAL = "surgical"               # Хирургическое
    GYNECOLOGICAL = "gynecological"     # Гинекологическое
    NEUROLOGICAL = "neurological"       # Неврологическое
    CARDIOLOGICAL = "cardiological"     # Кардиологическое
    PSYCHIATRIC = "psychiatric"         # Психиатрическое
    DERMATOLOGICAL = "dermatological"   # Дерматологическое
    OPHTHALMOLOGICAL = "ophthalmological" # Офтальмологическое
    OTOLARYNGOLOGICAL = "otolaryngological" # ЛОР
    EMERGENCY = "emergency"             # Скорая помощь
    OUTPATIENT = "outpatient"           # Поликлиническое
    GENERAL_PRACTICE = "general_practice" # Общая практика


class AreaTypeEnum(enum.Enum):
    """Типы участков"""
    THERAPEUTIC = "therapeutic"         # Терапевтический
    PEDIATRIC = "pediatric"             # Педиатрический
    GENERAL_PRACTICE = "general_practice" # Общей практики
    SPECIALIZED = "specialized"         # Специализированный