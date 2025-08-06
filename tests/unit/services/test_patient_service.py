import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

from src.apps.patients.domain.patient import PatientDomain
from src.apps.patients.infrastructure.api.schemas.requests.patient_request_schemas import UpdatePatientSchema
from src.shared.exceptions import NoInstanceFoundError, InstanceAlreadyExistsError


@pytest.mark.asyncio
async def test_get_by_id_found(patient_service, mock_patient_repository, dummy_domain_patient):
    mock_patient_repository.get_by_id.return_value = dummy_domain_patient

    result = await patient_service.get_by_id(dummy_domain_patient.id)

    assert result is dummy_domain_patient
    mock_patient_repository.get_by_id.assert_awaited_once_with(dummy_domain_patient.id)


@pytest.mark.asyncio
async def test_get_by_id_not_found(patient_service, mock_patient_repository):
    mock_patient_repository.get_by_id.return_value = None

    with pytest.raises(NoInstanceFoundError) as ei:
        await patient_service.get_by_id(uuid4())
    assert ei.value.status_code == 404
    assert "Patient with ID" in ei.value.detail


@pytest.mark.asyncio
async def test_get_by_iin_found(patient_service, mock_patient_repository, dummy_domain_patient):
    mock_patient_repository.get_by_iin.return_value = dummy_domain_patient

    result = await patient_service.get_by_iin(dummy_domain_patient.iin)

    assert result is dummy_domain_patient
    mock_patient_repository.get_by_iin.assert_awaited_once_with(dummy_domain_patient.iin)


@pytest.mark.asyncio
async def test_get_by_iin_not_found(patient_service, mock_patient_repository):
    mock_patient_repository.get_by_iin.return_value = None

    with pytest.raises(NoInstanceFoundError):
        await patient_service.get_by_iin("000000000000")


@pytest.mark.asyncio
async def test_get_patients_calls_repository(patient_service, mock_patient_repository):
    filters = MagicMock(to_dict=lambda **kw: {"iin": "111"})
    pagination = MagicMock(page=5, limit=50)

    expected_patients = [dummy := object()]
    expected_total = 123

    mock_patient_repository.get_patients = AsyncMock(return_value=expected_patients)
    mock_patient_repository.get_total_number_of_patients = AsyncMock(return_value=expected_total)

    patients, total = await patient_service.get_patients(filters, pagination)

    assert patients == expected_patients
    assert total == expected_total

    mock_patient_repository.get_total_number_of_patients.assert_awaited_once_with()
    mock_patient_repository.get_patients.assert_awaited_once_with(
        filters={"iin": "111"},
        page=5,
        limit=50,
    )


@pytest.mark.asyncio
async def test_get_patients_returns_patients_and_total(patient_service, mock_patient_repository):
    filters = MagicMock(to_dict=lambda **kw: {"iin": "123"})
    pagination = MagicMock(page=2, limit=10)
    fake_patients = [object(), object()]
    mock_patient_repository.get_patients.return_value = fake_patients
    mock_patient_repository.get_total_number_of_patients.return_value = 22

    result_patients, total = await patient_service.get_patients(filters, pagination)

    assert result_patients == fake_patients
    assert total == 22
    mock_patient_repository.get_patients.assert_awaited_once_with(
        filters={"iin": "123"}, page=2, limit=10
    )
    mock_patient_repository.get_total_number_of_patients.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_get_patients_none_filters(patient_service, mock_patient_repository):
    filters = MagicMock(to_dict=lambda **kw: {})
    pagination = MagicMock(page=1, limit=10)
    mock_patient_repository.get_patients.return_value = []
    mock_patient_repository.get_total_number_of_patients.return_value = 0

    result_patients, total = await patient_service.get_patients(filters, pagination)

    assert result_patients == []
    assert total == 0

    mock_patient_repository.get_patients.assert_not_awaited()
    mock_patient_repository.get_total_number_of_patients.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_get_patients_returns_empty_and_total(patient_service, mock_patient_repository):
    filters = MagicMock(to_dict=lambda **kw: {'iin': '123'})
    pagination = MagicMock(page=1, limit=10)
    mock_patient_repository.get_patients.return_value = []
    mock_patient_repository.get_total_number_of_patients.return_value = 0

    result_patients, total = await patient_service.get_patients(filters, pagination)

    assert result_patients == []
    assert total == 0
    mock_patient_repository.get_patients.assert_awaited_once_with(
        filters={'iin': '123'}, page=1, limit=10
    )
    mock_patient_repository.get_total_number_of_patients.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_create_patient_success(patient_service, mock_patient_repository, mock_uow, dummy_domain_patient):
    mock_patient_repository.get_by_iin.return_value = None
    for svc in patient_service._citizenship_service, patient_service._nationalities_service, patient_service._medical_org_service:
        svc.get_by_id.return_value = object()
    for svc in patient_service._financing_source_service, patient_service._patient_context_attributes_service:
        svc.get_by_id.return_value = object()

    created = object()
    mock_uow.patients_repository.create_patient.return_value = created

    result = await patient_service.create_patient(dummy_domain_patient)

    mock_patient_repository.get_by_iin.assert_awaited_once_with(dummy_domain_patient.iin)
    patient_service._citizenship_service.get_by_id.assert_awaited_once_with(dummy_domain_patient.citizenship_id)

    mock_uow.patients_repository.create_patient.assert_awaited_once_with(dummy_domain_patient)
    assert result is created


@pytest.mark.asyncio
async def test_create_patient_duplicate_iin(patient_service, mock_patient_repository, dummy_domain_patient):
    mock_patient_repository.get_by_iin.return_value = dummy_domain_patient

    with pytest.raises(InstanceAlreadyExistsError) as ei:
        await patient_service.create_patient(dummy_domain_patient)
    assert ei.value.status_code == 409
    assert "already exists" in ei.value.detail


@pytest.mark.asyncio
async def test_update_patient_success(patient_service, mock_uow, dummy_domain_patient, monkeypatch):
    patient_service.get_by_id = AsyncMock(return_value=dummy_domain_patient)
    patient_service._patients_repository.get_by_iin = AsyncMock(return_value=None)

    updated = MagicMock(name="updated_domain_patient", spec=PatientDomain)
    updated.citizenship_id = dummy_domain_patient.citizenship_id
    updated.nationality_id = dummy_domain_patient.nationality_id
    updated.attached_clinic_id = dummy_domain_patient.attached_clinic_id
    updated.financing_sources_ids = dummy_domain_patient.financing_sources_ids
    updated.context_attributes_ids = dummy_domain_patient.context_attributes_ids
    updated.attachment_data = dummy_domain_patient.attachment_data

    patient_service._patients_repository.get_by_id = AsyncMock(return_value=updated)

    monkeypatch.setattr(
        "src.apps.patients.services.patients_service.map_update_schema_to_domain",
        lambda dto, existing: updated
    )

    for svc in (
            patient_service._citizenship_service,
            patient_service._nationalities_service,
            patient_service._medical_org_service,
    ):
        svc.get_by_id.return_value = object()
    for svc in (
            patient_service._financing_source_service,
            patient_service._patient_context_attributes_service,
    ):
        svc.get_by_id.return_value = object()

    mock_uow.patients_repository.update_patient.return_value = updated

    dto = UpdatePatientSchema(iin="999999999999")
    result = await patient_service.update_patient(uuid4(), dto)

    mock_uow.patients_repository.update_patient.assert_awaited_once_with(updated)
    assert result is updated


@pytest.mark.asyncio
async def test_update_patient_not_found(patient_service):
    patient_service.get_by_id = AsyncMock(side_effect=NoInstanceFoundError(status_code=404, detail="not found"))

    with pytest.raises(NoInstanceFoundError):
        await patient_service.update_patient(uuid4(), UpdatePatientSchema())


@pytest.mark.asyncio
async def test_delete_patient_success(patient_service, mock_uow, dummy_domain_patient):
    patient_service.get_by_id = AsyncMock(return_value=dummy_domain_patient)

    await patient_service.delete_patient(dummy_domain_patient.id)

    mock_uow.patients_repository.delete_by_id.assert_awaited_once_with(dummy_domain_patient.id)


@pytest.mark.asyncio
async def test_delete_patient_not_found(patient_service):
    patient_service.get_by_id = AsyncMock(side_effect=NoInstanceFoundError(status_code=404, detail="no"))

    with pytest.raises(NoInstanceFoundError):
        await patient_service.delete_patient(uuid4())
