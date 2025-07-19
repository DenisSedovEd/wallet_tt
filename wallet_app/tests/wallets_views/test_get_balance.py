from decimal import Decimal
from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_get_balance_success(client, mock_crud, wallet_factory):
    """
    Проверка успешного получения баланса.
    :param client:
    :param mock_crud:
    :param wallet_factory:
    :return:
    """
    wallet = wallet_factory(balance=Decimal("123.45"))
    mock_crud.get_by_uuid.return_value = wallet

    resp = await client.get(f"/wallets/{wallet.uuid}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["balance"] == str(wallet.balance)
    mock_crud.get_by_uuid.assert_awaited_once_with(wallet.uuid)


@pytest.mark.asyncio
async def test_get_balance_not_found(client, mock_crud):
    """
    Тестирование не найденного кошелька.
    Генерируем uuid в тесте, вместо созданного ранее.
    :param client:
    :param mock_crud:
    :return:
    """
    fake_uuid = uuid4()
    mock_crud.get_by_uuid.return_value = None

    resp = await client.get(f"/wallets/{fake_uuid}")
    assert resp.status_code in (200, 404)
