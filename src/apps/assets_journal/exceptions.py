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


class InvalidAssetStatusTransitionError(AssetsJournalAppError):
    """Недопустимый переход статуса актива"""
    pass


class BGDataLoadError(AssetsJournalAppError):
    """Ошибка загрузки данных из BG"""
    pass


class InvalidBGDataFormatError(AssetsJournalAppError):
    """Неверный формат данных BG"""
    pass