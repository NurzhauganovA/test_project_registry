import json
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional
from uuid import UUID

from src.apps.assets_journal.domain.enums import AssetDeliveryStatusEnum, AssetStatusEnum
from src.apps.assets_journal.domain.models.maternity_asset import MaternityAssetDomain, MaternityAssetListItemDomain
from src.apps.assets_journal.infrastructure.api.schemas.requests.maternity_asset_schemas import (
    MaternityAssetFilterParams,
    CreateMaternityAssetSchema,
    UpdateMaternityAssetSchema,
    CreateMaternityAssetByPatientIdSchema,
)
from src.apps.assets_journal.interfaces.maternity_repository_interfaces import (
    MaternityAssetRepositoryInterface,
)
from src.apps.assets_journal.interfaces.uow_interface import (
    AssetsJournalUnitOfWorkInterface,
)
from src.apps.assets_journal.mappers.maternity_asset_mappers import (
    map_bg_response_to_maternity_domain,
    map_create_schema_to_domain,
    map_maternity_diagnosis_schema_to_domain,
)
from src.apps.catalogs.services.medical_organizations_catalog_service import MedicalOrganizationsCatalogService
from src.apps.patients.services.patients_service import PatientService
from src.core.i18n import _
from src.core.logger import LoggerService
from src.shared.exceptions import NoInstanceFoundError
from src.shared.schemas.pagination_schemas import PaginationParams


class MaternityAssetService:
    """Сервис для работы с активами роддома"""

    def __init__(
            self,
            uow: AssetsJournalUnitOfWorkInterface,
            maternity_asset_repository: MaternityAssetRepositoryInterface,
            patients_service: PatientService,
            medical_organizations_catalog_service: MedicalOrganizationsCatalogService,
            logger: LoggerService,
    ):
        self._uow = uow
        self._maternity_asset_repository = maternity_asset_repository
        self._patients_service = patients_service
        self._medical_organizations_catalog_service = medical_organizations_catalog_service
        self._logger = logger

    async def get_by_id(self, asset_id: UUID) -> MaternityAssetDomain:
        """
        Получить актив по ID с загрузкой данных организации

        :param asset_id: ID актива
        :return: Доменная модель актива
        :raises NoInstanceFoundError: Если актив не найден
        """
        asset = await self._maternity_asset_repository.get_by_id(asset_id)
        if not asset:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Актив роддома с ID: %(ID)s не найден.") % {"ID": asset_id}
            )

        # Загружаем данные организации если есть organization_id
        await self._load_organization_data(asset)

        return asset

    async def get_assets(
            self,
            pagination_params: PaginationParams,
            filter_params: MaternityAssetFilterParams,
    ) -> Tuple[List[MaternityAssetListItemDomain], int]:
        """
        Получить список активов с фильтрацией и пагинацией

        :param pagination_params: Параметры пагинации
        :param filter_params: Параметры фильтрации
        :return: Кортеж из списка активов и общего количества
        """
        filters = filter_params.to_dict(exclude_none=True)

        assets = await self._maternity_asset_repository.get_assets(
            filters=filters,
            page=pagination_params.page,
            limit=pagination_params.limit,
        )

        # Загружаем данные организаций для каждого актива
        await self._load_organization_data_for_assets(assets)

        total_count = await self._maternity_asset_repository.get_total_count(filters)

        return assets, total_count

    async def get_assets_by_organization(
            self,
            organization_id: int,
            pagination_params: PaginationParams,
            filter_params: MaternityAssetFilterParams,
    ) -> tuple[list[MaternityAssetListItemDomain], int]:
        """
        Получить список активов по организации

        :param organization_id: ID организации
        :param pagination_params: Параметры пагинации
        :param filter_params: Параметры фильтрации по организации
        :return: Кортеж из списка активов и общего количества
        """
        filters = filter_params.to_dict(exclude_none=True)
        filters['organization_id'] = organization_id  # Добавляем фильтр по организации

        assets = await self._maternity_asset_repository.get_assets(
            filters=filters,
            page=pagination_params.page,
            limit=pagination_params.limit,
        )

        # Загружаем данные организаций для каждого актива
        await self._load_organization_data_for_assets(assets)

        total_count = await self._maternity_asset_repository.get_total_count(filters)

        return assets, total_count

    async def get_assets_by_patient(
            self,
            patient_id: UUID,
            pagination_params: PaginationParams,
    ) -> Tuple[List[MaternityAssetDomain], int]:
        """
        Получить список активов пациента

        :param patient_id: ID пациента
        :param pagination_params: Параметры пагинации
        :return: Кортеж из списка активов и общего количества
        """
        filters = {'patient_id': patient_id}

        assets = await self._maternity_asset_repository.get_assets(
            filters=filters,
            page=pagination_params.page,
            limit=pagination_params.limit,
        )

        # Загружаем данные организаций для каждого актива
        await self._load_organization_data_for_assets(assets)

        total_count = await self._maternity_asset_repository.get_total_count(filters)

        return assets, total_count

    async def create_asset(self, create_schema: CreateMaternityAssetSchema) -> MaternityAssetDomain:
        """
        Создать новый актив

        :param create_schema: Схема создания актива
        :return: Созданная доменная модель актива
        """
        # Находим пациента по ИИН
        patient = await self._patients_service.get_by_iin(create_schema.patient_iin)
        if not patient:
            raise NoInstanceFoundError(
                status_code=404,
                detail=_("Пациент с ИИН %(IIN)s не найден.") % {"IIN": create_schema.patient_iin}
            )

        # Проверяем, что актив с таким BG ID еще не существует
        if create_schema.bg_asset_id:
            existing_asset = await self._maternity_asset_repository.get_by_bg_asset_id(
                create_schema.bg_asset_id
            )
            if existing_asset:
                raise ValueError(
                    _("Актив с BG ID %(ID)s уже существует.") % {"ID": create_schema.bg_asset_id}
                )

        # Mapping
        asset_domain = map_create_schema_to_domain(create_schema, patient.id)

        async with self._uow:
            created_asset = await self._uow.maternity_asset_repository.create(asset_domain)

        # Загружаем данные организации
        await self._load_organization_data(created_asset)

        self._logger.info(f"Создан новый актив роддома {created_asset.id} для пациента {patient.iin}")

        return created_asset

    async def create_asset_by_patient_id(
            self,
            create_schema: CreateMaternityAssetByPatientIdSchema,
            patient_id: UUID
    ) -> MaternityAssetDomain:
        """
        Создать новый актив по ID пациента

        :param create_schema: Схема создания актива с ID пациента
        :param patient_id: ID пациента
        :return: Созданная доменная модель актива
        """
        # Проверяем, что актив с таким BG ID еще не существует
        if create_schema.bg_asset_id:
            existing_asset = await self._maternity_asset_repository.get_by_bg_asset_id(
                create_schema.bg_asset_id
            )
            if existing_asset:
                raise ValueError(
                    _("Актив с BG ID %(ID)s уже существует.") % {"ID": create_schema.bg_asset_id}
                )

        # Преобразуем диагнозы
        diagnoses = [map_maternity_diagnosis_schema_to_domain(d) for d in create_schema.diagnoses]

        # Преобразуем схему в доменную модель
        from src.apps.assets_journal.domain.models.maternity_asset import MaternityAssetDomain

        asset_domain = MaternityAssetDomain(
            bg_asset_id=create_schema.bg_asset_id,
            patient_id=patient_id,
            receive_date=create_schema.receive_date,
            receive_time=create_schema.receive_time,
            actual_datetime=create_schema.actual_datetime or create_schema.receive_date,
            received_from=create_schema.received_from,
            is_repeat=create_schema.is_repeat,
            stay_period_start=create_schema.stay_period_start,
            stay_period_end=create_schema.stay_period_end,
            stay_outcome=create_schema.stay_outcome,
            admission_type=create_schema.admission_type,
            stay_type=create_schema.stay_type,
            patient_status=create_schema.patient_status,
            diagnoses=diagnoses,
            area=create_schema.area,
            specialization=create_schema.specialization,
            specialist=create_schema.specialist,
            note=create_schema.note,
        )

        async with self._uow:
            created_asset = await self._uow.maternity_asset_repository.create(asset_domain)

        # Загружаем данные организации
        await self._load_organization_data(created_asset)

        self._logger.info(f"Создан новый актив роддома {created_asset.id} по ID пациента {patient_id}")

        return created_asset

    async def update_asset(
            self,
            asset_id: UUID,
            update_schema: UpdateMaternityAssetSchema
    ) -> MaternityAssetDomain:
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
                    from src.apps.assets_journal.infrastructure.api.schemas.requests.maternity_asset_schemas import \
                        MaternityDiagnosisSchema

                    diagnoses = []
                    for diagnosis_data in value:
                        # Если это уже объект схемы
                        if isinstance(diagnosis_data, MaternityDiagnosisSchema):
                            diagnoses.append(map_maternity_diagnosis_schema_to_domain(diagnosis_data))
                        # Если это словарь, создаем объект схемы
                        elif isinstance(diagnosis_data, dict):
                            diagnosis_schema = MaternityDiagnosisSchema(**diagnosis_data)
                            diagnoses.append(map_maternity_diagnosis_schema_to_domain(diagnosis_schema))

                    setattr(asset, field, diagnoses)
                elif field in ["status", "delivery_status"]:
                    # Специальная обработка статусов - не устанавливаем напрямую
                    continue
                else:
                    setattr(asset, field, value)

        # Специальная логика для статусов
        if update_schema.status and update_schema.status != asset.status:
            asset.update_status(update_schema.status)

        if update_schema.delivery_status and update_schema.delivery_status != asset.delivery_status:
            asset.update_delivery_status(update_schema.delivery_status)

        # Обновление исхода пребывания
        if update_schema.stay_outcome and update_schema.stay_outcome != asset.stay_outcome:
            asset.update_stay_outcome(update_schema.stay_outcome)

        # Обновление статуса пациентки
        if update_schema.patient_status and update_schema.patient_status != asset.patient_status:
            asset.update_patient_status(update_schema.patient_status)

        # Добавление примечания (не заменяем, а добавляем)
        if update_schema.note and update_schema.note != asset.note:
            asset.add_note(update_schema.note)

        # Обновляем время последнего изменения
        asset.updated_at = datetime.utcnow()

        async with self._uow:
            updated_asset = await self._uow.maternity_asset_repository.update(asset)

        # Загружаем данные организации
        await self._load_organization_data(updated_asset)

        self._logger.info(f"Обновлен актив роддома {asset_id}")

        return updated_asset

    async def delete_asset(self, asset_id: UUID) -> None:
        """
        Удалить актив

        :param asset_id: ID актива
        :raises NoInstanceFoundError: Если актив не найден
        """
        # Проверяем существование актива
        asset = await self.get_by_id(asset_id)

        # Проверяем, можно ли удалить актив
        if asset.is_confirmed:
            raise ValueError(_("Нельзя удалить подтвержденный актив."))

        self._logger.info(f"Удаление актива роддома {asset_id}")

        async with self._uow:
            await self._uow.maternity_asset_repository.delete(asset_id)

    async def confirm_asset(self, asset_id: UUID) -> MaternityAssetDomain:
        """
        Подтвердить актив

        :param asset_id: ID актива
        :return: Обновленная доменная модель актива
        """
        asset = await self.get_by_id(asset_id)

        # Проверяем, что актив еще не подтвержден
        if asset.is_confirmed:
            raise ValueError(_("Актив уже подтвержден."))

        # Проверяем, что актив не отклонен
        if asset.is_refused:
            raise ValueError(_("Нельзя подтвердить отклоненный актив."))

        asset.confirm_asset()

        async with self._uow:
            updated_asset = await self._uow.maternity_asset_repository.update(asset)

        # Загружаем данные организации
        await self._load_organization_data(updated_asset)

        self._logger.info(f"Актив роддома {asset_id} подтвержден")

        return updated_asset

    async def load_assets_from_bg_file(self, file_path: str = None) -> List[MaternityAssetDomain]:
        """
        Загрузить активы из файла BG

        :param file_path: Путь к JSON файлу с данными BG
        :return: Список созданных активов
        """
        if not file_path:
            # Используем файл по умолчанию
            project_root = Path(__file__).parent.parent.parent.parent
            file_path = project_root / "data" / "bg_responses" / "maternity_assets_response.json"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                bg_data = json.load(f)

            self._logger.info(f"Начинаем загрузку активов роддома из файла: {file_path}")

            # Преобразуем данные BG в доменные модели
            assets_to_create = []
            skipped_count = 0
            error_count = 0

            for item in bg_data:
                try:
                    # Проверяем, что актив еще не существует
                    bg_asset_id = item.get("id", "")
                    if bg_asset_id and await self._maternity_asset_repository.exists_by_bg_asset_id(bg_asset_id):
                        skipped_count += 1
                        continue

                    # Находим пациента по данным из BG
                    patient_data = item.get("patient", {})
                    patient_iin = patient_data.get("personin", "")

                    if patient_iin:
                        try:
                            patient = await self._patients_service.get_by_iin(patient_iin)
                            asset_domain = map_bg_response_to_maternity_domain(item, patient.id)
                            assets_to_create.append(asset_domain)
                        except NoInstanceFoundError:
                            self._logger.warning(
                                f"Пациент с ИИН {patient_iin} не найден, пропускаем актив {bg_asset_id}")
                            skipped_count += 1
                    else:
                        self._logger.warning(f"Отсутствует ИИН пациента в данных BG для актива {bg_asset_id}")
                        skipped_count += 1

                except Exception as e:
                    self._logger.error(f"Ошибка при обработке актива {item.get('id', 'unknown')}: {str(e)}")
                    error_count += 1

            if not assets_to_create:
                self._logger.info(f"Нет новых активов для создания. Пропущено: {skipped_count}, ошибок: {error_count}")
                return []

            # Массовое создание активов
            async with self._uow:
                created_assets = await self._uow.maternity_asset_repository.bulk_create(assets_to_create)

            # Загружаем данные организаций для созданных активов
            await self._load_organization_data_for_assets(created_assets)

            self._logger.info(
                f"Успешно загружено {len(created_assets)} активов роддома из файла BG. "
                f"Пропущено: {skipped_count}, ошибок: {error_count}"
            )
            return created_assets

        except FileNotFoundError:
            self._logger.error(f"Файл BG данных не найден: {file_path}")
            raise ValueError(_("Файл с данными BG не найден"))
        except json.JSONDecodeError as e:
            self._logger.error(f"Ошибка парсинга JSON файла: {file_path}, ошибка: {str(e)}")
            raise ValueError(_("Ошибка в формате файла данных BG"))
        except Exception as e:
            self._logger.error(f"Ошибка при загрузке данных из файла BG: {str(e)}")
            raise ValueError(_("Ошибка при загрузке данных из файла BG: %(error)s") % {"error": str(e)})

    async def _load_organization_data(self, asset: MaternityAssetDomain) -> None:
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

    async def _load_organization_data_for_assets(self, assets: List[MaternityAssetDomain]) -> None:
        """
        Загрузить данные организаций для списка активов

        :param assets: Список доменных моделей активов
        """
        if not assets:
            return

        # Собираем уникальные ID организаций
        organization_ids = set()
        for asset in assets:
            if asset.organization_id:
                organization_ids.add(asset.organization_id)

        if not organization_ids:
            return

        # Загружаем все организации
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