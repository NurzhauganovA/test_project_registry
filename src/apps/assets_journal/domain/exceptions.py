class AssetsDomainError(Exception):
    """Базовое доменное исключение для активов"""
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(self.detail)


class StationaryAssetDomainError(AssetsDomainError):
    """Доменное исключение для активов стационара"""
    pass


class InvalidAssetStatusError(StationaryAssetDomainError):
    """Недопустимый статус актива"""
    pass


class InvalidAssetDataError(StationaryAssetDomainError):
    """Недопустимые данные актива"""
    pass


class AssetValidationError(StationaryAssetDomainError):
    """Ошибка валидации актива"""
    pass