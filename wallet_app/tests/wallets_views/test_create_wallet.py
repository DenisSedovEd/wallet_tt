import pytest
from uuid import uuid4
from decimal import Decimal

from fastapi import status
from schemas.wallet import WalletCreateSchema
from models.wallet import Wallet


# @pytest.mark.asyncio
# async def test_index(client):
#     """
#     Тестирование базовой точки входа в API.
#     :param client:
#     :return:
#     """
#     resp = await client.get("/wallets/")
#     assert resp.status_code == 200
#     assert resp.json() == {"message": "Wallet API"}


@pytest.mark.asyncio
async def test_create_wallet_success(client, mock_crud):
    """
    Успешное создание кошелька через get запрос.
    :param client:
    :param mock_crud:
    :return:
    """
    req = {"balance": "200.00"}
    wallet = Wallet(uuid=uuid4(), balance=Decimal(req["balance"]))
    mock_crud.create.return_value = wallet

    resp = await client.post("/wallets/", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert data["uuid"] == str(wallet.uuid)
    assert data["balance"] == req["balance"]
    mock_crud.create.assert_awaited_once()
    args, _ = mock_crud.create.await_args
    assert isinstance(args[0], WalletCreateSchema)
    assert args[0].balance == Decimal(req["balance"])


@pytest.mark.asyncio
async def test_create_wallet_invalid_body(client):
    """
    Невалидный ответ баланса кошелька.
    В случае задания баланса при создании кошелька.
    :param client:
    :return:
    """
    req = {"balance": "not_a_decimal"}
    resp = await client.post("/wallets/", json=req)
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
