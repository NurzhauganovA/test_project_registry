from src.shared.exceptions import ApplicationError


class AssetsJournalAppError(ApplicationError):
    """Базовое исключение для модуля журналов активов"""
    origin = "assets_journal"


class StationaryAssetNotFoundError(AssetsJournalAppError):
    """Актив стационара не найден"""
    pass


class StationaryAssetAlreadyExistsError(AssetsJournalAppError):
    """Актив стационара уже существует"""
    pass


class StationaryAssetAlreadyConfirmedError(AssetsJournalAppError):
    """Актив стационара уже подтвержден"""
    pass


class StationaryAssetAlreadyRefusedError(AssetsJournalAppError):
    """Актив стационара уже отказан"""
    pass


class EmergencyAssetNotFoundError(AssetsJournalAppError):
    """Актив скорой помощи не найден"""
    pass


class EmergencyAssetAlreadyExistsError(AssetsJournalAppError):
    """Актив скорой помощи уже существует"""
    pass


class EmergencyAssetAlreadyConfirmedError(AssetsJournalAppError):
    """Актив скорой помощи уже подтвержден"""
    pass


class EmergencyAssetAlreadyRefusedError(AssetsJournalAppError):
    """Актив скорой помощи уже отказан"""
    pass


class InvalidDiagnosisDataError(AssetsJournalAppError):
    """Неверные данные диагноза"""
    pass


class InvalidAssetStatusTransitionError(AssetsJournalAppError):
    """Недопустимый переход статуса актива"""
    pass


class BGDataLoadError(AssetsJournalAppError):
    """Ошибка загрузки данных из BG"""
    pass


class InvalidBGDataFormatError(AssetsJournalAppError):
    """Неверный формат данных BG"""
    pass