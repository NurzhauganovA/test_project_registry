import copy
import datetime
import uuid
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

from src.apps.catalogs.infrastructure.api.schemas.responses.diagnoses_catalog_response_schemas import \
    DiagnosedPatientDiagnosisResponseSchema
from src.apps.patients.infrastructure.api.schemas.responses.patient_response_schemas import \
    PatientTruncatedResponseSchema
from src.apps.users.infrastructure.schemas.user_schemas import DoctorTruncatedResponseSchema


@pytest.mark.asyncio
async def test_get_total_number_of_diagnoses(
        diagnoses_and_patients_repository_impl
):
    mock_response_from_db = MagicMock()
    mock_response_from_db.scalar_one.return_value = 34
    diagnoses_and_patients_repository_impl._async_db_session.execute = AsyncMock(return_value=mock_response_from_db)

    result = await diagnoses_and_patients_repository_impl.get_total_number_of_patients_and_diagnoses_records()

    assert isinstance(result, int)
    assert result == 34


@pytest.mark.asyncio
async def test_get_by_id_found(
        diagnoses_and_patients_repository_impl,
        mock_diagnoses_and_patients_response_from_db,
        mock_diagnoses_and_patients_response_schema
):
    mock_response_from_db = MagicMock()
    mock_response_from_db.scalar_one_or_none.return_value = mock_diagnoses_and_patients_response_from_db
    diagnoses_and_patients_repository_impl._async_db_session.execute = AsyncMock(return_value=mock_response_from_db)

    # Patch the mapper
    with patch(
            "src.apps.catalogs.infrastructure.repositories.diagnoses_and_patients_"
            "repository.map_diagnosed_patient_diagnosis_db_entity_to_response_schema",
            return_value=mock_diagnoses_and_patients_response_schema
    ):
        result = await diagnoses_and_patients_repository_impl.get_by_id(uuid.uuid4())

    assert isinstance(result, type(mock_diagnoses_and_patients_response_schema))
    assert result.id == mock_diagnoses_and_patients_response_schema.id
    assert result.date_diagnosed == mock_diagnoses_and_patients_response_from_db.date_diagnosed


@pytest.mark.asyncio
async def test_get_by_id_not_found(
        diagnoses_and_patients_repository_impl,
):
    mock_response_from_db = MagicMock()
    mock_response_from_db.scalar_one_or_none.return_value = None
    diagnoses_and_patients_repository_impl._async_db_session.execute = AsyncMock(return_value=mock_response_from_db)

    result = await diagnoses_and_patients_repository_impl.get_by_id(uuid.uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_get_patient_and_diagnoses_records_WITHOUT_filters(
        diagnoses_and_patients_repository_impl,
        mock_diagnoses_and_patients_response_from_db,
        mock_diagnoses_and_patients_response_schema
):
    # Dummy responses
    dummy_diagnosis_and_patients_response_1 = mock_diagnoses_and_patients_response_from_db
    dummy_diagnosis_and_patients_response_2 = copy.deepcopy(mock_diagnoses_and_patients_response_from_db)

    # Make them different
    dummy_diagnosis_and_patients_response_2.id = uuid.uuid4()
    dummy_diagnosis_and_patients_response_2.date_diagnosed = datetime.date(2025, 5, 5)

    mock_response_from_db = MagicMock()
    mock_response_from_db.scalars.return_value.all.return_value = [
        dummy_diagnosis_and_patients_response_1,
        dummy_diagnosis_and_patients_response_2
    ]
    diagnoses_and_patients_repository_impl._async_db_session.execute = AsyncMock(return_value=mock_response_from_db)

    with patch(
            "src.apps.catalogs.infrastructure.repositories.diagnoses_and_patients_"
            "repository.map_diagnosed_patient_diagnosis_db_entity_to_response_schema",
            return_value=mock_diagnoses_and_patients_response_schema
    ):
        result = await diagnoses_and_patients_repository_impl.get_patient_and_diagnoses_records(filters=None)


    assert isinstance(result, list)
    assert len(result) == 2


@pytest.mark.asyncio
async def test_get_patient_and_diagnoses_records_WITH_filters_and_pagination(
        diagnoses_and_patients_repository_impl,
        mock_diagnoses_and_patients_response_from_db,
        mock_diagnoses_and_patients_response_schema
):
    mock_response_from_db = MagicMock()
    mock_response_from_db.scalars.return_value.all.return_value = [
        mock_diagnoses_and_patients_response_from_db
    ]
    diagnoses_and_patients_repository_impl._async_db_session.execute = AsyncMock(return_value=mock_response_from_db)

    # Prepare filters
    filters_to_return_existing = {
        'patient_id': mock_diagnoses_and_patients_response_from_db.patient_id,
        'doctor_id': mock_diagnoses_and_patients_response_from_db.doctor_id,
        'diagnosis_code': 'AJ-09',
        'date_diagnosed_from': mock_diagnoses_and_patients_response_from_db.date_diagnosed,
        'date_diagnosed_to': mock_diagnoses_and_patients_response_from_db.date_diagnosed,
    }

    filters_to_return_none = {
        'date_diagnosed_from': datetime.date(1960, 5, 5),
        'date_diagnosed_to': datetime.date(1960, 5, 6),
    }

    # Scenario when found something
    with patch(
            "src.apps.catalogs.infrastructure.repositories.diagnoses_and_patients_"
            "repository.map_diagnosed_patient_diagnosis_db_entity_to_response_schema",
            return_value=mock_diagnoses_and_patients_response_schema
    ):
        result = await diagnoses_and_patients_repository_impl.get_patient_and_diagnoses_records(
            filters=filters_to_return_existing
        )

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0] == mock_diagnoses_and_patients_response_schema

    # Scenario when nothing found
    mock_response_from_db = MagicMock()
    mock_response_from_db.scalars.return_value.all.return_value = []
    diagnoses_and_patients_repository_impl._async_db_session.execute = AsyncMock(return_value=mock_response_from_db)


    result = await diagnoses_and_patients_repository_impl.get_patient_and_diagnoses_records(
        filters=filters_to_return_none
    )

    assert isinstance(result, list)
    assert len(result) == 0
    
    
@pytest.mark.asyncio
async def test_add_patient_diagnosis_record(
        diagnoses_and_patients_repository_impl,
        mock_diagnoses_and_patients_response_from_db,
        mock_diagnoses_and_patients_response_schema,
        mock_diagnoses_and_patients_add_schema,
):
    mock_orm_obj = MagicMock()
    mock_response_from_db = MagicMock()
    mock_response_from_db.scalar_one_or_none.return_value = mock_diagnoses_and_patients_response_schema,
    diagnoses_and_patients_repository_impl._async_db_session.execute = AsyncMock(return_value=mock_response_from_db)

    # Mock the session's methods
    diagnoses_and_patients_repository_impl._async_db_session.add = MagicMock()
    diagnoses_and_patients_repository_impl._async_db_session.flush = AsyncMock()
    diagnoses_and_patients_repository_impl._async_db_session.refresh = AsyncMock()
    diagnoses_and_patients_repository_impl._async_db_session.commit = AsyncMock()

    # Patch the mappers
    with patch(
        "src.apps.catalogs.infrastructure.repositories.diagnoses_and_patients_repository"
        ".map_diagnosed_patient_diagnosis_create_schema_to_db_entity",
        return_value=mock_orm_obj
    ), patch(
        "src.apps.catalogs.infrastructure.repositories.diagnoses_and_patients_repository"
        ".map_diagnosed_patient_diagnosis_db_entity_to_response_schema",
        return_value=mock_diagnoses_and_patients_response_schema
    ):
        result = await diagnoses_and_patients_repository_impl.add_patient_diagnosis_record(
            mock_diagnoses_and_patients_add_schema
        )

    assert isinstance(result, type(mock_diagnoses_and_patients_response_schema))
    assert result.diagnosis is not None
    assert result.patient is not None
    assert result.doctor is not None
    assert result.date_diagnosed == mock_diagnoses_and_patients_response_schema.date_diagnosed

    diagnoses_and_patients_repository_impl._async_db_session.add.assert_called_once_with(mock_orm_obj)
    diagnoses_and_patients_repository_impl._async_db_session.flush.assert_awaited_once()
    diagnoses_and_patients_repository_impl._async_db_session.refresh.assert_awaited_once_with(mock_orm_obj)
    diagnoses_and_patients_repository_impl._async_db_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_diagnosis(
        diagnoses_and_patients_repository_impl,
        mock_diagnoses_and_patients_update_schema,
        mock_diagnoses_and_patients_response_schema,
        mock_diagnoses_and_patients_response_from_db,
        mock_diagnoses_catalog_response_schema,
):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_diagnoses_and_patients_response_from_db
    diagnoses_and_patients_repository_impl._async_db_session.execute = AsyncMock(return_value=mock_result)

    # Mock the session's methods
    diagnoses_and_patients_repository_impl._async_db_session.flush = AsyncMock()
    diagnoses_and_patients_repository_impl._async_db_session.refresh = AsyncMock()
    diagnoses_and_patients_repository_impl._async_db_session.commit = AsyncMock()

    # Patch the mappers
    def mapper_side_effect(db_entity):
        truncated_patient = PatientTruncatedResponseSchema(
            id=uuid.uuid4(),
            iin='040806501543',
            first_name='Alex',
            last_name='Turlov',
            middle_name='Alexandrovich',
        )

        truncated_doctor = DoctorTruncatedResponseSchema(
            id=mock_diagnoses_and_patients_update_schema.doctor_id,
            iin='140866501542',
            first_name='Pupka',
            last_name='Zalupka',
            middle_name=None,
        )

        return DiagnosedPatientDiagnosisResponseSchema(
            id=uuid.uuid4(),
            date_diagnosed=mock_diagnoses_and_patients_update_schema.date_diagnosed,
            comment="Dummy comment",
            diagnosis=mock_diagnoses_catalog_response_schema,
            patient=truncated_patient,
            doctor=truncated_doctor,
        )

    with patch(
        "src.apps.catalogs.infrastructure.repositories.diagnoses_and_patients_repository."
        "map_diagnosed_patient_diagnosis_db_entity_to_response_schema",
        side_effect=mapper_side_effect
    ):
        result = await diagnoses_and_patients_repository_impl.update_patient_diagnosis_record(
            record_id=mock_diagnoses_and_patients_response_from_db.id,
            request_dto=mock_diagnoses_and_patients_update_schema
        )

    # Check that the ORM object fields have been updated according to request_dto (exclude_unset=True)
    update_data = mock_diagnoses_and_patients_update_schema.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        assert getattr(mock_diagnoses_and_patients_response_from_db, key) == value

    assert isinstance(result, type(mock_diagnoses_and_patients_response_schema))
    assert result.date_diagnosed == mock_diagnoses_and_patients_update_schema.date_diagnosed
    assert result.doctor.id == mock_diagnoses_and_patients_update_schema.doctor_id

    diagnoses_and_patients_repository_impl._async_db_session.flush.assert_awaited_once()
    diagnoses_and_patients_repository_impl._async_db_session.refresh.assert_awaited_once_with(
        mock_diagnoses_and_patients_response_from_db
    )
    diagnoses_and_patients_repository_impl._async_db_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_by_id(
        diagnoses_and_patients_repository_impl,
):
    diagnoses_and_patients_repository_impl._async_db_session.execute = AsyncMock(return_value=None)

    # Mock the session method
    diagnoses_and_patients_repository_impl._async_db_session.commit = AsyncMock()

    await diagnoses_and_patients_repository_impl.delete_by_id(12)

    diagnoses_and_patients_repository_impl._async_db_session.commit.assert_awaited_once()
