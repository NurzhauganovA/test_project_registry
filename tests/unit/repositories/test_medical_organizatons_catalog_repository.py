import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.apps.catalogs.infrastructure.db_models.medical_organizations_catalogue import \
    SQLAlchemyMedicalOrganizationsCatalogue
from src.apps.catalogs.infrastructure.repositories.medical_organizations_catalog_repository import (
    SQLAlchemyMedicalOrganizationsCatalogCatalogueRepositoryImpl
)
from src.apps.catalogs.infrastructure.api.schemas.responses.medical_organizations_catalog_schemas import (
    MedicalOrganizationCatalogFullResponseSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.requests.medical_organizations_catalog_schemas import (
    AddMedicalOrganizationSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.requests.citizenship_catalog_request_schemas import (
    UpdateCitizenshipSchema,
)
from src.core.settings import project_settings


@pytest.fixture
def mock_async_db_session():
    return MagicMock()


@pytest.fixture
def dummy_logger():
    return MagicMock()


@pytest.mark.asyncio
async def test_get_by_default_name_returns_schema(mock_async_db_session, dummy_logger):
    # подготовим ORM-объект
    orm_obj = MagicMock(spec=SQLAlchemyMedicalOrganizationsCatalogue)
    mock_async_db_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=orm_obj))
    )
    repo = SQLAlchemyMedicalOrganizationsCatalogCatalogueRepositoryImpl(
        mock_async_db_session, dummy_logger
    )

    # патчим Pydantic-валидацию, чтобы вернуть "SCHEMA"
    with patch.object(
        MedicalOrganizationCatalogFullResponseSchema,
        "model_validate",
        return_value="SCHEMA"
    ) as mv:
        result = await repo.get_by_default_name("MedOrg")
        mv.assert_called_once_with(orm_obj)
        assert result == "SCHEMA"

    mock_async_db_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_default_name_not_found(mock_async_db_session, dummy_logger):
    mock_async_db_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    )
    repo = SQLAlchemyMedicalOrganizationsCatalogCatalogueRepositoryImpl(
        mock_async_db_session, dummy_logger
    )

    result = await repo.get_by_default_name("Missing")
    assert result is None
    mock_async_db_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_organization_code_returns_schema(mock_async_db_session, dummy_logger):
    orm_obj = MagicMock(spec=SQLAlchemyMedicalOrganizationsCatalogue)
    mock_async_db_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=orm_obj))
    )
    repo = SQLAlchemyMedicalOrganizationsCatalogCatalogueRepositoryImpl(
        mock_async_db_session, dummy_logger
    )

    with patch.object(
        MedicalOrganizationCatalogFullResponseSchema,
        "model_validate",
        return_value="SCHEMA2"
    ) as mv:
        result = await repo.get_by_organization_code("CODE123")
        mv.assert_called_once_with(orm_obj)
        assert result == "SCHEMA2"

    mock_async_db_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_organization_code_not_found(mock_async_db_session, dummy_logger):
    mock_async_db_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    )
    repo = SQLAlchemyMedicalOrganizationsCatalogCatalogueRepositoryImpl(
        mock_async_db_session, dummy_logger
    )

    result = await repo.get_by_organization_code("NO_CODE")
    assert result is None
    mock_async_db_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_name_locale_returns_schema(mock_async_db_session, dummy_logger):
    orm_obj = MagicMock(spec=SQLAlchemyMedicalOrganizationsCatalogue)
    mock_async_db_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=orm_obj))
    )
    repo = SQLAlchemyMedicalOrganizationsCatalogCatalogueRepositoryImpl(
        mock_async_db_session, dummy_logger
    )

    with patch.object(
        MedicalOrganizationCatalogFullResponseSchema,
        "model_validate",
        return_value="SCHEMA3"
    ) as mv:
        result = await repo.get_by_name_locale("ru", "NameRu")
        mv.assert_called_once_with(orm_obj)
        assert result == "SCHEMA3"

    mock_async_db_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_name_locale_not_found(mock_async_db_session, dummy_logger):
    mock_async_db_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    )
    repo = SQLAlchemyMedicalOrganizationsCatalogCatalogueRepositoryImpl(
        mock_async_db_session, dummy_logger
    )

    result = await repo.get_by_name_locale("ru", "NoName")
    assert result is None
    mock_async_db_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_address_locale_returns_schema(mock_async_db_session, dummy_logger):
    orm_obj = MagicMock(spec=SQLAlchemyMedicalOrganizationsCatalogue)
    mock_async_db_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=orm_obj))
    )
    repo = SQLAlchemyMedicalOrganizationsCatalogCatalogueRepositoryImpl(
        mock_async_db_session, dummy_logger
    )

    with patch.object(
        MedicalOrganizationCatalogFullResponseSchema,
        "model_validate",
        return_value="SCHEMA4"
    ) as mv:
        result = await repo.get_by_address_locale("ru", "AddrRu")
        mv.assert_called_once_with(orm_obj)
        assert result == "SCHEMA4"

    mock_async_db_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_address_locale_not_found(mock_async_db_session, dummy_logger):
    mock_async_db_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    )
    repo = SQLAlchemyMedicalOrganizationsCatalogCatalogueRepositoryImpl(
        mock_async_db_session, dummy_logger
    )

    result = await repo.get_by_address_locale("ru", "NoAddr")
    assert result is None
    mock_async_db_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_total_number_of_medical_organizations(mock_async_db_session, dummy_logger):
    mock_async_db_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one=MagicMock(return_value=8))
    )
    repo = SQLAlchemyMedicalOrganizationsCatalogCatalogueRepositoryImpl(
        mock_async_db_session, dummy_logger
    )

    result = await repo.get_total_number_of_medical_organizations()
    assert result == 8
    mock_async_db_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id_found(mock_async_db_session, dummy_logger):
    orm_obj = MagicMock(spec=SQLAlchemyMedicalOrganizationsCatalogue)
    mock_async_db_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=orm_obj))
    )
    repo = SQLAlchemyMedicalOrganizationsCatalogCatalogueRepositoryImpl(
        mock_async_db_session, dummy_logger
    )

    with patch.object(
        MedicalOrganizationCatalogFullResponseSchema,
        "model_validate",
        return_value="FOUND"
    ) as mv:
        result = await repo.get_by_id(123)
        mv.assert_called_once_with(orm_obj)
        assert result == "FOUND"

    mock_async_db_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id_not_found(mock_async_db_session, dummy_logger):
    mock_async_db_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    )
    repo = SQLAlchemyMedicalOrganizationsCatalogCatalogueRepositoryImpl(
        mock_async_db_session, dummy_logger
    )

    result = await repo.get_by_id(999)
    assert result is None
    mock_async_db_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_medical_organizations_filters(mock_async_db_session, dummy_logger):
    rec1 = MagicMock(spec=SQLAlchemyMedicalOrganizationsCatalogue)
    rec2 = MagicMock(spec=SQLAlchemyMedicalOrganizationsCatalogue)
    scalars = MagicMock(all=MagicMock(return_value=[rec1, rec2]))
    mock_async_db_session.execute = AsyncMock(
        return_value=MagicMock(scalars=MagicMock(return_value=scalars))
    )
    repo = SQLAlchemyMedicalOrganizationsCatalogCatalogueRepositoryImpl(
        mock_async_db_session, dummy_logger
    )

    # Подменяем модель, чтобы вернуть сами ORM-объекты
    with patch.object(
        MedicalOrganizationCatalogFullResponseSchema,
        "model_validate",
        side_effect=lambda x: x
    ):
        project_settings.LANGUAGES = ["en", "ru"]
        result = await repo.get_medical_organizations(
            name_filter="a", organization_code_filter=None, address_filter="b", page=1, limit=5
        )
        assert result == [rec1, rec2]

    mock_async_db_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_medical_organization(mock_async_db_session, dummy_logger):
    schema = AddMedicalOrganizationSchema.model_construct(
        name="MedOrg", organization_code="CODEX", address="Addr", lang="en",
        name_locales={"ru": "МедОрг"}, address_locales={"ru": "Адр"}
    )

    mock_async_db_session.add = MagicMock()
    mock_async_db_session.flush = AsyncMock()
    mock_async_db_session.refresh = AsyncMock()
    mock_async_db_session.commit = AsyncMock()

    repo = SQLAlchemyMedicalOrganizationsCatalogCatalogueRepositoryImpl(
        mock_async_db_session, dummy_logger
    )

    with patch.object(
        MedicalOrganizationCatalogFullResponseSchema,
        "model_validate",
        return_value="NEW"
    ) as mv:
        out = await repo.add_medical_organization(schema)
        mv.assert_called_once()

        assert mock_async_db_session.add.call_count == 1
        added = mock_async_db_session.add.call_args[0][0]
        assert isinstance(added, SQLAlchemyMedicalOrganizationsCatalogue)

        assert added.name == schema.name
        assert added.code == schema.organization_code
        assert added.address == schema.address
        assert added.lang == schema.lang
        assert added.name_locales == schema.name_locales
        assert added.address_locales == schema.address_locales

        assert out == "NEW"
        mock_async_db_session.flush.assert_awaited_once()
        mock_async_db_session.refresh.assert_awaited_once()
        mock_async_db_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_medical_organization(mock_async_db_session, dummy_logger):
    orm_obj = MagicMock(spec=SQLAlchemyMedicalOrganizationsCatalogue)
    mock_async_db_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=orm_obj))
    )
    mock_async_db_session.flush = AsyncMock()
    mock_async_db_session.refresh = AsyncMock()
    mock_async_db_session.commit = AsyncMock()
    repo = SQLAlchemyMedicalOrganizationsCatalogCatalogueRepositoryImpl(
        mock_async_db_session, dummy_logger
    )

    schema = UpdateCitizenshipSchema.model_construct(
        name="X", name_locales={"en": "Y"}, address_locales={}
    )

    with patch.object(
        MedicalOrganizationCatalogFullResponseSchema,
        "model_validate",
        return_value="UPD"
    ) as mv:
        out = await repo.update_medical_organization(1, schema)
        mv.assert_called_once_with(orm_obj)
        assert out == "UPD"
        mock_async_db_session.flush.assert_awaited_once()
        mock_async_db_session.refresh.assert_awaited_once()
        mock_async_db_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_by_id(mock_async_db_session, dummy_logger):
    mock_async_db_session.execute = AsyncMock()
    mock_async_db_session.commit = AsyncMock()
    repo = SQLAlchemyMedicalOrganizationsCatalogCatalogueRepositoryImpl(
        mock_async_db_session, dummy_logger
    )

    await repo.delete_by_id(44)
    mock_async_db_session.execute.assert_awaited_once()
    mock_async_db_session.commit.assert_awaited_once()
