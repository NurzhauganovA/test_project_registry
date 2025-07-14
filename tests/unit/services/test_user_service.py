import datetime
import uuid

import pytest
from unittest.mock import AsyncMock

from src.apps.users.domain.enums import ActionsOnUserEnum
from src.apps.users.domain.models.user import UserDomain
from src.apps.users.infrastructure.schemas.user_schemas import UserSchema
from src.apps.users.services.user_service import UserService
from src.shared.exceptions import InvalidActionTypeError, NoInstanceFoundError, InstanceAlreadyExistsError


@pytest.mark.asyncio
async def test_get_by_id_success(dummy_user_repo, dummy_user_id, dummy_user_domain, dummy_logger):
    dummy_user_repo.get_by_id.return_value = dummy_user_domain
    service = UserService(dummy_user_repo, dummy_logger)

    result = await service.get_by_id(dummy_user_id)

    dummy_user_repo.get_by_id.assert_awaited_once_with(dummy_user_id)
    assert result is dummy_user_domain


@pytest.mark.asyncio
async def test_get_by_id_not_found_raises(dummy_user_repo, dummy_user_id, dummy_logger):
    dummy_user_repo.get_by_id.return_value = None
    service = UserService(dummy_user_repo, dummy_logger)

    with pytest.raises(NoInstanceFoundError) as exc:
        await service.get_by_id(dummy_user_id)

    err = exc.value
    assert err.status_code == 404
    assert str(dummy_user_id) in err.detail


@pytest.mark.asyncio
async def test_create_user_success(dummy_user_repo, dummy_user_domain, dummy_logger):
    dummy_user_repo.get_by_id.return_value = None
    dummy_user_repo.get_by_iin.return_value = None
    dummy_user_repo.create.return_value = dummy_user_domain

    dto = UserSchema(
        id=dummy_user_domain.id,
        first_name=dummy_user_domain.first_name,
        last_name=dummy_user_domain.last_name,
        middle_name=dummy_user_domain.middle_name,
        iin=dummy_user_domain.iin,
        date_of_birth=dummy_user_domain.date_of_birth,
        client_roles=dummy_user_domain.client_roles,
        enabled=dummy_user_domain.enabled,
        served_patient_types=dummy_user_domain.served_patient_types,
        served_referral_types=dummy_user_domain.served_referral_types,
        served_referral_origins=dummy_user_domain.served_referral_origins,
        served_payment_types=dummy_user_domain.served_payment_types,
        specializations=dummy_user_domain.specializations,
        attachment_data=dummy_user_domain.attachment_data,
    )
    service = UserService(dummy_user_repo, dummy_logger)

    result = await service.create(dto)

    dummy_user_repo.get_by_id.assert_awaited_once_with(dto.id)
    dummy_user_repo.get_by_iin.assert_awaited_once_with(dto.iin)
    dummy_user_repo.create.assert_awaited_once_with(dummy_user_domain)
    
    assert result is dummy_user_domain


@pytest.mark.asyncio
async def test_create_user_duplicate_id_raises(dummy_user_repo, dummy_user_domain, dummy_logger):
    dummy_user_repo.get_by_id.return_value = dummy_user_domain
    dto = UserSchema(
        id=dummy_user_domain.id,
        first_name="X",
        last_name="Y",
        middle_name="Z",
        iin="000000000000",
        date_of_birth=datetime.date.today(),
        client_roles=[],
        enabled=True,
        served_patient_types=dummy_user_domain.served_patient_types,
        served_referral_types=dummy_user_domain.served_referral_types,
        served_referral_origins=dummy_user_domain.served_referral_origins,
        served_payment_types=dummy_user_domain.served_payment_types,
        specializations=dummy_user_domain.specializations,
        attachment_data=dummy_user_domain.attachment_data,
    )
    service = UserService(dummy_user_repo, dummy_logger)

    with pytest.raises(InstanceAlreadyExistsError) as exc:
        await service.create(dto)

    err = exc.value
    assert err.status_code == 409
    assert str(dummy_user_domain.id) in err.detail


@pytest.mark.asyncio
async def test_create_user_duplicate_iin_raises(dummy_user_repo, dummy_user_domain, dummy_logger):
    dummy_user_repo.get_by_id.return_value = None
    dummy_user_repo.get_by_iin.return_value = dummy_user_domain
    other_id = uuid.uuid4()
    dto = UserSchema(
        id=other_id,
        first_name="A",
        last_name="B",
        middle_name="C",
        iin=dummy_user_domain.iin,
        date_of_birth=datetime.date.today(),
        client_roles=[],
        enabled=False,
        served_patient_types=dummy_user_domain.served_patient_types,
        served_referral_types=dummy_user_domain.served_referral_types,
        served_referral_origins=dummy_user_domain.served_referral_origins,
        served_payment_types=dummy_user_domain.served_payment_types,
        specializations=dummy_user_domain.specializations,
        attachment_data=dummy_user_domain.attachment_data,
    )
    service = UserService(dummy_user_repo, dummy_logger)

    with pytest.raises(InstanceAlreadyExistsError) as exc:
        await service.create(dto)

    err = exc.value
    assert err.status_code == 409
    assert dummy_user_domain.iin in err.detail


@pytest.mark.asyncio
async def test_update_user_not_found_raises(dummy_user_repo, dummy_user_id, dummy_logger, dummy_user_domain):
    dummy_user_repo.get_by_id.return_value = None
    dto = UserSchema(
        id=dummy_user_id,
        first_name=dummy_user_domain.first_name,
        last_name=dummy_user_domain.last_name,
        middle_name=dummy_user_domain.middle_name,
        iin=dummy_user_domain.iin,
        date_of_birth=dummy_user_domain.date_of_birth,
        client_roles=dummy_user_domain.client_roles,
        enabled=dummy_user_domain.enabled,
        served_patient_types=dummy_user_domain.served_patient_types,
        served_referral_types=dummy_user_domain.served_referral_types,
        served_referral_origins=dummy_user_domain.served_referral_origins,
        served_payment_types=dummy_user_domain.served_payment_types,
        specializations=dummy_user_domain.specializations,
        attachment_data=dummy_user_domain.attachment_data,
    )
    service = UserService(dummy_user_repo, dummy_logger)

    with pytest.raises(NoInstanceFoundError):
        await service.update_user(dto)


@pytest.mark.asyncio
async def test_update_user_success(dummy_user_repo, dummy_user_domain, dummy_logger):
    dummy_user_repo.get_by_id.return_value = dummy_user_domain
    updated = UserDomain(**{**dummy_user_domain.__dict__, "first_name": "Alice"})
    dummy_user_repo.update.return_value = updated

    dto = UserSchema(
        id=dummy_user_domain.id,
        first_name="Alice",
        last_name=dummy_user_domain.last_name,
        middle_name=dummy_user_domain.middle_name,
        iin=dummy_user_domain.iin,
        date_of_birth=dummy_user_domain.date_of_birth,
        client_roles=dummy_user_domain.client_roles,
        enabled=dummy_user_domain.enabled,
        served_patient_types=dummy_user_domain.served_patient_types,
        served_referral_types=dummy_user_domain.served_referral_types,
        served_referral_origins=dummy_user_domain.served_referral_origins,
        served_payment_types=dummy_user_domain.served_payment_types,
        specializations=dummy_user_domain.specializations,
        attachment_data=dummy_user_domain.attachment_data,
    )
    service = UserService(dummy_user_repo, dummy_logger)

    result = await service.update_user(dto)

    dummy_user_repo.get_by_id.assert_awaited_once_with(dto.id)
    args, _ = dummy_user_repo.update.call_args
    sent_domain: UserDomain = args[0]
    assert sent_domain.first_name == "Alice"
    assert sent_domain.last_name == dummy_user_domain.last_name
    assert result is updated


@pytest.mark.asyncio
async def test_delete_user_not_found_raises(dummy_user_repo, dummy_user_id, dummy_logger):
    dummy_user_repo.get_by_id.return_value = None
    service = UserService(dummy_user_repo, dummy_logger)

    with pytest.raises(NoInstanceFoundError):
        await service.delete_user(dummy_user_id)


@pytest.mark.asyncio
async def test_delete_user_success(dummy_user_repo, dummy_user_domain, dummy_logger):
    dummy_user_repo.get_by_id.return_value = dummy_user_domain
    service = UserService(dummy_user_repo, dummy_logger)

    await service.delete_user(dummy_user_domain.id)

    dummy_user_repo.get_by_id.assert_awaited_once_with(dummy_user_domain.id)
    dummy_user_repo.delete.assert_awaited_once_with(dummy_user_domain.id)


@pytest.mark.asyncio
async def test_handle_event_create_calls_create(dummy_user_repo, dummy_user_domain, dummy_logger):
    service = UserService(dummy_user_repo, dummy_logger)
    dto = UserSchema(
        id=dummy_user_domain.id,
        first_name=dummy_user_domain.first_name,
        last_name=dummy_user_domain.last_name,
        middle_name=dummy_user_domain.middle_name,
        iin=dummy_user_domain.iin,
        date_of_birth=dummy_user_domain.date_of_birth,
        client_roles=dummy_user_domain.client_roles,
        enabled=dummy_user_domain.enabled,
        served_patient_types=dummy_user_domain.served_patient_types,
        served_referral_types=dummy_user_domain.served_referral_types,
        served_referral_origins=dummy_user_domain.served_referral_origins,
        served_payment_types=dummy_user_domain.served_payment_types,
        specializations=dummy_user_domain.specializations,
        attachment_data=dummy_user_domain.attachment_data,
    )

    create_mock = AsyncMock(return_value=dummy_user_domain)
    service.create = create_mock

    result = await service.handle_event(ActionsOnUserEnum.CREATE, dto)
    create_mock.assert_awaited_once_with(dto)
    assert result is None


@pytest.mark.asyncio
async def test_handle_event_update_calls_update(dummy_user_repo, dummy_user_domain, dummy_logger):
    service = UserService(dummy_user_repo, dummy_logger)
    dto = UserSchema(
        id=dummy_user_domain.id,
        first_name=dummy_user_domain.first_name,
        last_name=dummy_user_domain.last_name,
        middle_name=dummy_user_domain.middle_name,
        iin=dummy_user_domain.iin,
        date_of_birth=dummy_user_domain.date_of_birth,
        client_roles=dummy_user_domain.client_roles,
        enabled=dummy_user_domain.enabled,
        served_patient_types=dummy_user_domain.served_patient_types,
        served_referral_types=dummy_user_domain.served_referral_types,
        served_referral_origins=dummy_user_domain.served_referral_origins,
        served_payment_types=dummy_user_domain.served_payment_types,
        specializations=dummy_user_domain.specializations,
        attachment_data=dummy_user_domain.attachment_data,
    )

    update_mock = AsyncMock(return_value=dummy_user_domain)
    service.update_user = update_mock

    result = await service.handle_event(ActionsOnUserEnum.UPDATE, dto)
    update_mock.assert_awaited_once_with(dto)
    assert result is None


@pytest.mark.asyncio
async def test_handle_event_delete_calls_delete(dummy_user_repo, dummy_user_domain, dummy_logger):
    service = UserService(dummy_user_repo, dummy_logger)
    dto = UserSchema(
        id=dummy_user_domain.id,
        first_name=dummy_user_domain.first_name,
        last_name=dummy_user_domain.last_name,
        middle_name=dummy_user_domain.middle_name,
        iin=dummy_user_domain.iin,
        date_of_birth=dummy_user_domain.date_of_birth,
        client_roles=dummy_user_domain.client_roles,
        enabled=dummy_user_domain.enabled,
        served_patient_types=dummy_user_domain.served_patient_types,
        served_referral_types=dummy_user_domain.served_referral_types,
        served_referral_origins=dummy_user_domain.served_referral_origins,
        served_payment_types=dummy_user_domain.served_payment_types,
        specializations=dummy_user_domain.specializations,
        attachment_data=dummy_user_domain.attachment_data,
    )

    delete_mock = AsyncMock(return_value=None)
    service.delete_user = delete_mock

    result = await service.handle_event(ActionsOnUserEnum.DELETE, dto)
    delete_mock.assert_awaited_once_with(dto.id)
    assert result is None


@pytest.mark.asyncio
async def test_handle_event_invalid_action_raises(dummy_user_repo, dummy_user_domain, dummy_logger):
    service = UserService(dummy_user_repo, dummy_logger)
    dto = UserSchema(
        id=dummy_user_domain.id,
        first_name=dummy_user_domain.first_name,
        last_name=dummy_user_domain.last_name,
        middle_name=dummy_user_domain.middle_name,
        iin=dummy_user_domain.iin,
        date_of_birth=dummy_user_domain.date_of_birth,
        client_roles=dummy_user_domain.client_roles,
        enabled=dummy_user_domain.enabled,
        served_patient_types=dummy_user_domain.served_patient_types,
        served_referral_types=dummy_user_domain.served_referral_types,
        served_referral_origins=dummy_user_domain.served_referral_origins,
        served_payment_types=dummy_user_domain.served_payment_types,
        specializations=dummy_user_domain.specializations,
        attachment_data=dummy_user_domain.attachment_data,
    )

    with pytest.raises(InvalidActionTypeError) as exc:
        await service.handle_event("unknown", dto)

    err = exc.value
    assert err.status_code == 500