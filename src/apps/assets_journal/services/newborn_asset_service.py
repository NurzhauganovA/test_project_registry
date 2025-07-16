import json
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional
from uuid import UUID

from src.apps.assets_journal.domain.enums import AssetDeliveryStatusEnum, AssetStatusEnum
from src.apps.assets_journal.domain.models.newborn_asset import NewbornAssetDomain, NewbornAssetListItemDomain, \
    MotherData, NewbornData
from src.apps.assets_journal.infrastructure.api.schemas.requests.newborn_asset_schemas import (
    NewbornAssetFilterParams,
    CreateNewbornAssetSchema,
    UpdateNewbornAssetSchema,
    CreateNewbornAssetByPatientIdSchema,
)
from src.apps.assets_journal.infrastructure.api.schemas.responses.newborn_asset_schemas import (
    NewbornAssetStatisticsSchema,
)
from src.apps.assets_journal.interfaces.newborn_repository_interfaces import (
    NewbornAssetRepositoryInterface,
)
from src.apps.assets_journal.interfaces.uow_interface import (
    AssetsJournalUnitOfWorkInterface,
)
from src.apps.assets_journal.mappers.newborn_asset_mappers import (
    map_bg_response_to_newborn_domain,
    map_create_schema_to_domain,
    map_newborn_diagnosis_schema_to_domain,
    map_mother_data_schema_to_domain,
    map_newborn_data_schema_to_domain,
)
from src.apps.catalogs.services.medical_organizations_catalog_service import MedicalOrganizationsCatalogService
from src.apps.patients.services.patients_service import PatientService
from src.core.i18n import _
from src.core.logger import LoggerService
from src.shared.exceptions import NoInstanceFoundError
from src.shared.schemas.pagination_schemas import PaginationParams


class NewbornAssetService:
    """Сервис для работы с активами новорожденных"""

    def __init__(
            self,
            uow: AssetsJournalUnitOfWorkInterface,
            newborn_asset_repository: NewbornAssetRepositoryInterface,
            patients_service: PatientService,
            medical_organizations_catalog_service: MedicalOrganizationsCatalogService,
            logger: LoggerService,
    ):
        self._uow = uow
        self._newborn_asset_repository = newborn_asset_repository
        self._patients_service = patients_service
        self._medical_organizations_catalog_service = medical_organizations_catalog_service
        self._logger = logger

    async def get_by_id(self, asset_id: UUID) -> NewbornAssetDomain:
        """
        Получить актив по ID с загрузкой данных организации

        :param asset_id: ID актива
        :return: Доменная модель актива
        :raises NoInstanceFoundError: Если актив не найден
        """
        asset = await self._newborn_asset_repository.get_by_id(asset_id)
        if not asset:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Актив новорожденного с ID: %(ID)s не найден.") % {"ID": asset_id}
            )

        # Загружаем данные организации если есть organization_id
        await self._load_organization_data(asset)

        return asset

    async def get_assets(
            self,
            pagination_params: PaginationParams,
            filter_params: NewbornAssetFilterParams,
    ) -> Tuple[List[NewbornAssetListItemDomain], int]:
        """
        Получить список активов с фильтрацией и пагинацией

        :param pagination_params: Параметры пагинации
        :param filter_params: Параметры фильтрации
        :return: Кортеж из списка активов и общего количества
        """
        filters = filter_params.to_dict(exclude_none=True)

        assets = await self._newborn_asset_repository.get_assets(
            filters=filters,
            page=pagination_params.page,
            limit=pagination_params.limit,
        )

        # Загружаем данные организаций для каждого актива
        await self._load_organization_data_for_assets(assets)

        total_count = await self._newborn_asset_repository.get_total_count(filters)

        return assets, total_count

    async def get_assets_by_organization(
            self,
            organization_id: int,
            pagination_params: PaginationParams,
            filter_params: NewbornAssetFilterParams,
    ) -> tuple[list[NewbornAssetListItemDomain], int]:
        """
        Получить список активов по организации

        :param organization_id: ID организации
        :param pagination_params: Параметры пагинации
        :param filter_params: Параметры фильтрации по организации
        :return: Кортеж из списка активов и общего количества
        """
        filters = filter_params.to_dict(exclude_none=True)
        filters['organization_id'] = organization_id  # Добавляем фильтр по организации

        assets = await self._newborn_asset_repository.get_assets(
            filters=filters,
            page=pagination_params.page,
            limit=pagination_params.limit,
        )

        # Загружаем данные организаций для каждого актива
        await self._load_organization_data_for_assets(assets)

        total_count = await self._newborn_asset_repository.get_total_count(filters)

        return assets, total_count

    async def get_assets_by_patient(
            self,
            patient_id: UUID,
            pagination_params: PaginationParams,
    ) -> Tuple[List[NewbornAssetDomain], int]:
        """
        Получить список активов пациента

        :param patient_id: ID пациента
        :param pagination_params: Параметры пагинации
        :return: Кортеж из списка активов и общего количества
        """
        filters = {'patient_id': patient_id}

        assets = await self._newborn_asset_repository.get_assets(
            filters=filters,
            page=pagination_params.page,
            limit=pagination_params.limit,
        )

        # Загружаем данные организаций для каждого актива
        await self._load_organization_data_for_assets(assets)

        total_count = await self._newborn_asset_repository.get_total_count(filters)

        return assets, total_count

    async def create_asset(self, create_schema: CreateNewbornAssetSchema) -> NewbornAssetDomain:
        """
        Создать новый актив

        :param create_schema: Схема создания актива
        :return: Созданная доменная модель актива
        """
        patient_id = None

        # Если есть ИИН пациента, пытаемся найти его
        if create_schema.patient_iin:
            try:
                patient = await self._patients_service.get_by_iin(create_schema.patient_iin)
                patient_id = patient.id
            except NoInstanceFoundError:
                # Пациент не найден, создадим актив без привязки к пациенту
                # Это допустимо для новорожденных
                pass

        # Если пациент не найден и не указано ФИО, создаем временного пациента
        if not patient_id and not create_schema.patient_full_name_if_not_registered:
            raise ValueError(_("Необходимо указать ИИН существующего пациента или ФИО для незарегистрированного."))

        # Проверяем, что актив с таким BG ID еще не существует
        if create_schema.bg_asset_id:
            existing_asset = await self._newborn_asset_repository.get_by_bg_asset_id(
                create_schema.bg_asset_id
            )
            if existing_asset:
                raise ValueError(
                    _("Актив с BG ID %(ID)s уже существует.") % {"ID": create_schema.bg_asset_id}
                )

        # Mapping
        asset_domain = map_create_schema_to_domain(create_schema, patient_id)

        async with self._uow:
            created_asset = await self._uow.newborn_asset_repository.create(asset_domain)

        # Загружаем данные организации
        await self._load_organization_data(created_asset)

        return created_asset

    async def create_asset_by_patient_id(
            self,
            create_schema: CreateNewbornAssetByPatientIdSchema,
            patient_id: UUID
    ) -> NewbornAssetDomain:
        """
        Создать новый актив по ID пациента

        :param create_schema: Схема создания актива с ID пациента
        :param patient_id: ID пациента
        :return: Созданная доменная модель актива
        """
        # Проверяем, что актив с таким BG ID еще не существует
        if create_schema.bg_asset_id:
            existing_asset = await self._newborn_asset_repository.get_by_bg_asset_id(
                create_schema.bg_asset_id
            )
            if existing_asset:
                raise ValueError(
                    _("Актив с BG ID %(ID)s уже существует.") % {"ID": create_schema.bg_asset_id}
                )

        # Преобразуем данные
        diagnoses = [map_newborn_diagnosis_schema_to_domain(d) for d in create_schema.diagnoses]
        mother_data = map_mother_data_schema_to_domain(create_schema.mother_data) if create_schema.mother_data else None
        newborn_data = map_newborn_data_schema_to_domain(
            create_schema.newborn_data) if create_schema.newborn_data else None

        # Преобразуем схему в доменную модель
        asset_domain = NewbornAssetDomain(
            bg_asset_id=create_schema.bg_asset_id,
            patient_id=patient_id,
            patient_full_name_if_not_registered=create_schema.patient_full_name_if_not_registered,
            receive_date=create_schema.receive_date,
            receive_time=create_schema.receive_time,
            actual_datetime=create_schema.actual_datetime or create_schema.receive_date,
            received_from=create_schema.received_from,
            is_repeat=create_schema.is_repeat,
            mother_data=mother_data,
            newborn_data=newborn_data,
            diagnoses=diagnoses,
            diagnosis_note=create_schema.diagnosis_note,
        )

        async with self._uow:
            created_asset = await self._uow.newborn_asset_repository.create(asset_domain)

        # Загружаем данные организации
        await self._load_organization_data(created_asset)

        return created_asset

    async def update_asset(
            self,
            asset_id: UUID,
            update_schema: UpdateNewbornAssetSchema
    ) -> NewbornAssetDomain:
        """
        Обновить актив

        :param asset_id: ID актива
        :param update_schema: Схема обновления актива
        :return: Обновленная доменная модель актива
        """
        # Получаем существующий актив
        asset = await self.get_by_id(asset_id)

        # Обновляем поля
        update_data = update_schema.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(asset, field) and value is not None:
                if field == "diagnoses" and value:
                    # Специальная обработка диагнозов
                    diagnoses = [map_newborn_diagnosis_schema_to_domain(d) for d in value]
                    setattr(asset, field, diagnoses)
                elif field == "mother_data" and value:
                    # Специальная обработка данных матери
                    mother_data = map_mother_data_schema_to_domain(value)
                    setattr(asset, field, mother_data)
                elif field == "newborn_data" and value:
                    # Специальная обработка данных новорожденного
                    newborn_data = map_newborn_data_schema_to_domain(value)
                    setattr(asset, field, newborn_data)
                else:
                    setattr(asset, field, value)

        # Специальная логика для статуса
        if update_schema.status:
            asset.update_status(update_schema.status)

        if update_schema.delivery_status:
            asset.update_delivery_status(update_schema.delivery_status)

        # Добавление примечания
        if update_schema.diagnosis_note:
            asset.add_diagnosis_note(update_schema.diagnosis_note)

        async with self._uow:
            updated_asset = await self._uow.newborn_asset_repository.update(asset)

        # Загружаем данные организации
        await self._load_organization_data(updated_asset)

        return updated_asset

    async def transfer_to_organization(
            self,
            asset_id: UUID,
            new_organization_id: int,
            transfer_reason: Optional[str] = None,
            update_patient_attachment: bool = True
    ) -> NewbornAssetDomain:
        """
        Передать актив новорожденного другой организации

        :param asset_id: ID актива
        :param new_organization_id: ID новой организации
        :param transfer_reason: Причина передачи
        :param update_patient_attachment: Обновить attachment_data пациента
        :return: Обновленная доменная модель актива
        """
        # Получаем существующий актив
        asset = await self.get_by_id(asset_id)

        # Проверяем, что это не та же организация
        if asset.organization_id == new_organization_id:
            raise ValueError(_("Актив уже принадлежит указанной организации."))

        # Проверяем существование новой организации
        try:
            new_organization = await self._medical_organizations_catalog_service.get_by_id(new_organization_id)
        except NoInstanceFoundError:
            raise ValueError(_("Организация с ID %(ID)s не найдена.") % {"ID": new_organization_id})

        # Логируем передачу
        old_org_name = asset.organization_data.get('name', 'Неизвестно') if asset.organization_data else 'Неизвестно'
        self._logger.info(
            f"Передача актива новорожденного {asset_id} из организации '{old_org_name}' "
            f"в организацию '{new_organization.name}'. Причина: {transfer_reason or 'Не указана'}"
        )

        # Обновляем attachment_data пациента если требуется
        if update_patient_attachment:
            try:
                patient = await self._patients_service.get_by_id(asset.patient_id)

                # Обновляем attachment_data пациента
                attachment_data = patient.attachment_data or {}
                attachment_data['attached_clinic_id'] = new_organization_id

                # Обновляем пациента
                await self._patients_service.update_patient_attachment_data(
                    patient_id=patient.id,
                    attachment_data=attachment_data
                )
            except NoInstanceFoundError:
                # Пациент может быть не зарегистрирован для новорожденных
                self._logger.warning(f"Пациент с ID {asset.patient_id} не найден при передаче актива")

        # Выполняем передачу актива
        asset.delivery_status = AssetDeliveryStatusEnum.PENDING_DELIVERY
        asset.status = AssetStatusEnum.REGISTERED  # Сбрасываем статус на зарегистрированный
        asset.actual_datetime = datetime.utcnow()  # Обновляем фактическую дату и время

        # Добавляем примечание о передаче
        transfer_note = f"Актив передан организации '{new_organization.name}'"
        if transfer_reason:
            transfer_note += f". Причина: {transfer_reason}"

        current_note = asset.diagnosis_note or ""
        asset.diagnosis_note = f"{transfer_note}\n{current_note}" if current_note else transfer_note

        async with self._uow:
            updated_asset = await self._uow.newborn_asset_repository.update(asset)

        # Загружаем обновленные данные организации
        await self._load_organization_data(updated_asset)

        return updated_asset

    async def delete_asset(self, asset_id: UUID) -> None:
        """
        Удалить актив

        :param asset_id: ID актива
        """
        # Проверяем существование актива
        await self.get_by_id(asset_id)

        async with self._uow:
            await self._uow.newborn_asset_repository.delete(asset_id)

    async def get_statistics(
            self,
            filter_params: NewbornAssetFilterParams
    ) -> NewbornAssetStatisticsSchema:
        """
        Получить статистику активов

        :param filter_params: Параметры фильтрации
        :return: Статистика активов
        """
        filters = filter_params.to_dict(exclude_none=True)
        return await self._newborn_asset_repository.get_statistics(filters)

    async def confirm_asset(self, asset_id: UUID) -> NewbornAssetDomain:
        """
        Подтвердить актив

        :param asset_id: ID актива
        :return: Обновленная доменная модель актива
        """
        asset = await self.get_by_id(asset_id)
        asset.confirm_asset()

        async with self._uow:
            updated_asset = await self._uow.newborn_asset_repository.update(asset)

        # Загружаем данные организации
        await self._load_organization_data(updated_asset)

        return updated_asset

    async def load_assets_from_bg_file(self, file_path: str = None) -> List[NewbornAssetDomain]:
        """
        Загрузить активы из файла BG

        :param file_path: Путь к JSON файлу с данными BG
        :return: Список созданных активов
        """
        if not file_path:
            # Используем файл по умолчанию
            project_root = Path(__file__).parent.parent.parent.parent
            file_path = project_root / "data" / "bg_responses" / "newborn_assets_response.json"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                bg_data = json.load(f)

            # Преобразуем данные BG в доменные модели
            assets_to_create = []
            for item in bg_data:
                # Проверяем, что актив еще не существует
                if not await self._newborn_asset_repository.exists_by_bg_asset_id(item.get("id", "")):
                    # Находим или создаем пациента по данным из BG
                    patient_data = item.get("patient", {})
                    patient_iin = patient_data.get("personin", "")

                    patient_id = None
                    if patient_iin:
                        # Пытаемся найти существующего пациента
                        try:
                            patient = await self._patients_service.get_by_iin(patient_iin)
                            patient_id = patient.id
                        except NoInstanceFoundError:
                            self._logger.warning(
                                f"Пациент с ИИН {patient_iin} не найден, создаем актив без привязки к пациенту")

                    # Если нет пациента, создаем временный ID
                    if not patient_id:
                        from uuid import uuid4
                        patient_id = uuid4()

                    asset_domain = map_bg_response_to_newborn_domain(item, patient_id)
                    assets_to_create.append(asset_domain)

            if not assets_to_create:
                self._logger.info("Все активы из файла уже существуют в базе данных")
                return []

            # Массовое создание активов
            async with self._uow:
                created_assets = await self._uow.newborn_asset_repository.bulk_create(
                    assets_to_create
                )

            # Загружаем данные организаций для созданных активов
            await self._load_organization_data_for_assets(created_assets)

            self._logger.info(f"Успешно загружено {len(created_assets)} активов новорожденных из файла BG")
            return created_assets

        except FileNotFoundError:
            self._logger.error(f"Файл BG данных не найден: {file_path}")
            raise ValueError(_("Файл с данными BG не найден"))
        except json.JSONDecodeError:
            self._logger.error(f"Ошибка парсинга JSON файла: {file_path}")
            raise ValueError(_("Ошибка в формате файла данных BG"))
        except Exception as e:
            self._logger.error(f"Ошибка при загрузке данных из файла BG: {str(e)}")
            raise ValueError(_("Ошибка при загрузке данных из файла BG"))

    async def _load_organization_data(self, asset: NewbornAssetDomain) -> None:
        """
        Загрузить данные организации для актива

        :param asset: Доменная модель актива
        """
        if asset.organization_id:
            try:
                organization = await self._medical_organizations_catalog_service.get_by_id(asset.organization_id)
                asset.organization_data = {
                    'id': organization.id,
                    'name': organization.name,
                    'code': organization.organization_code,
                    'address': organization.address,
                }
            except NoInstanceFoundError:
                self._logger.warning(f"Организация с ID {asset.organization_id} не найдена")
                asset.organization_data = None

    async def _load_organization_data_for_assets(self, assets: List[NewbornAssetDomain]) -> None:
        """
        Загрузить данные организаций для списка активов

        :param assets: Список доменных моделей активов
        """
        # Собираем уникальные ID организаций
        organization_ids = set()
        for asset in assets:
            if asset.organization_id:
                organization_ids.add(asset.organization_id)

        # Загружаем все организации одним запросом
        organizations_data = {}
        for org_id in organization_ids:
            try:
                organization = await self._medical_organizations_catalog_service.get_by_id(org_id)
                organizations_data[org_id] = {
                    'id': organization.id,
                    'name': organization.name,
                    'code': organization.organization_code,
                    'address': organization.address,
                }
            except NoInstanceFoundError:
                self._logger.warning(f"Организация с ID {org_id} не найдена")

        # Устанавливаем данные организаций для активов
        for asset in assets:
            if asset.organization_id and asset.organization_id in organizations_data:
                asset.organization_data = organizations_data[asset.organization_id]