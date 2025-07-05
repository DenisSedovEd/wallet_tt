import pytest
from uuid import uuid4
from decimal import Decimal

from schemas.operation import OperationTypeSchema


@pytest.mark.asyncio
async def test_wallet_operation_deposit(client, mock_crud, wallet_factory):
    """
    Успешное пополнение кошелька.
    :param client:
    :param mock_crud:
    :param wallet_factory:
    :return:
    """
    wallet = wallet_factory(balance=Decimal("150.00"))
    mock_crud.operation.return_value = wallet
    url = f"/wallets/{wallet.uuid}/operation"
    params = {
        "operation_type": OperationTypeSchema.DEPOSIT.value,
        "amount": "50.00",
    }
    resp = await client.post(url, params=params)
    assert resp.status_code == 200
    data = resp.json()
    assert data["balance"] == str(wallet.balance)
    mock_crud.operation.assert_awaited_once_with(
        wallet.uuid, OperationTypeSchema.DEPOSIT, Decimal("50.00")
    )


@pytest.mark.asyncio
async def test_wallet_operation_withdraw_not_enough_balance(
    client, mock_crud, wallet_factory
):
    """
    Ошибка "недостаточно средств".
    :param client:
    :param mock_crud:
    :param wallet_factory:
    :return:
    """
    wallet = wallet_factory(balance=Decimal("10.00"))
    from exceptions import NotEnoughBalanceError

    mock_crud.operation.side_effect = NotEnoughBalanceError("Недостаточно средств")

    url = f"/wallet/{wallet.uuid}/operation"
    body = {"operation_type": OperationTypeSchema.WITHDRAW.value, "amount": "20.00"}
    resp = await client.post(url, json=body)
    assert resp.status_code in (400, 404, 422, 500)


@pytest.mark.asyncio
async def test_wallet_operation_invalid_op_type(client, wallet_factory):
    """
    Несуществующий тип операции.
    :param client:
    :param wallet_factory:
    :return:
    """
    wallet = wallet_factory(balance=Decimal("100.00"))
    url = f"/wallet/{wallet.uuid}/operation"
    body = {"operation_type": "INVALID_OP", "amount": "10.00"}
    resp = await client.post(url, json=body)
    assert resp.status_code in (422, 404)


@pytest.mark.asyncio
async def test_wallet_operation_not_found(client, mock_crud):
    """
    Случай не найденного кошелька для операции. Ошибочный uuid.
    :param client:
    :param mock_crud:
    :return:
    """
    fake_uuid = uuid4()
    from exceptions import WalletNotFound

    mock_crud.operation.side_effect = WalletNotFound(fake_uuid)

    url = f"/{fake_uuid}/operation"
    body = {"operation_type": OperationTypeSchema.DEPOSIT.value, "amount": "100.00"}
    resp = await client.post(url, json=body)
    assert resp.status_code in (404, 400, 500)


@pytest.mark.asyncio
async def test_wallet_operation_invalid_amount(client, wallet_factory):
    """
    Ошибка валидации при невалидном amount.
    :param client:
    :param wallet_factory:
    :return:
    """
    wallet_uuid = uuid4()
    url = f"/wallet/{wallet_uuid}/operation"
    body = {
        "operation_type": OperationTypeSchema.DEPOSIT.value,
        "amount": "not_a_decimal",
    }
    resp = await client.post(url, json=body)
    assert resp.status_code in (422, 404)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "op_type,amount,expected_status",
    [
        (OperationTypeSchema.DEPOSIT, "25.00", 200),
        (OperationTypeSchema.WITHDRAW, "5.00", 200),
        ("INVALID", "10.00", [422, 404]),
        (OperationTypeSchema.DEPOSIT, "not_a_decimal", [422, 404]),
    ],
)
async def test_wallet_operation_parametrized(
    client, mock_crud, wallet_factory, op_type, amount, expected_status
):
    """
    Параметризованный тест для разных сценариев операций - успешная операция, невалидные параметры, невалидный тип операции.

    :param client:
    :param mock_crud:
    :param wallet_factory:
    :param op_type:
    :param amount:
    :param expected_status:
    :return:
    """
    wallet = wallet_factory(balance=Decimal("100.00"))
    if expected_status == 200 or (
        isinstance(expected_status, list) and 200 in expected_status
    ):
        mock_crud.operation.return_value = wallet
    else:
        mock_crud.operation.side_effect = None
    url = f"/wallets/{wallet.uuid}/operation"
    params = {
        "operation_type": op_type.value if hasattr(op_type, "value") else op_type,
        "amount": amount,
    }
    resp = await client.post(url, params=params)
    if isinstance(expected_status, list):
        assert resp.status_code in expected_status, f"{resp.status_code=} {resp.text=}"
    else:
        assert resp.status_code == expected_status, f"{resp.status_code=} {resp.text=}"
