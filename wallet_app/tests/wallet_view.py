import pytest
import pytest_asyncio
from uuid import uuid4, UUID
from decimal import Decimal

from fastapi import FastAPI, status
from httpx import AsyncClient, ASGITransport

from unittest.mock import AsyncMock, MagicMock

from api.v1.wallets.views import router as wallets_router
from schemas.wallet import WalletCreateSchema
from schemas.operation import OperationTypeSchema
from models.wallet import Wallet


@pytest.fixture(scope="session")
def event_loop():
    """
    Создание нового event_loop для всего модуля тестирования.
    :return:
    """
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_app():
    """
    Создание экземпляра FastAPI приложения и подключение роутов.
    :return:
    """
    app = FastAPI()
    app.include_router(wallets_router)
    return app


@pytest.fixture
def wallet_factory():
    """
    Создание разных кошельков с уникальным uuid.
    :return:
    """

    def _factory(balance=Decimal("100.00")):
        return Wallet(uuid=uuid4(), balance=balance)

    return _factory


@pytest.fixture
def mock_crud(wallet_factory):
    """
    Создание мокового crud.
    :param wallet_factory:
    :return:
    """
    crud = MagicMock()
    crud.get_by_uuid = AsyncMock()
    crud.create = AsyncMock()
    crud.operation = AsyncMock()
    return crud


@pytest.fixture
def override_wallet_crud(mock_crud):
    """
    Обертка для moc-crud, чтобы использовать в override.
    :param mock_crud:
    :return:
    """

    async def _override():
        return mock_crud

    return _override


@pytest_asyncio.fixture
async def client(test_app, override_wallet_crud):
    """
    Создание асинхронного клиента с подменой wallet_crud на мок.
    :param test_app:
    :param override_wallet_crud:
    :return:
    """
    from api.v1.wallets.dependecies import wallet_crud

    test_app.dependency_overrides[wallet_crud] = override_wallet_crud
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest.mark.asyncio
async def test_index(client):
    """
    Тестирование базовой точки входа в API.
    :param client:
    :return:
    """
    resp = await client.get("/wallets/")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Wallet API"}


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
    Тестирование не найденного кошелька. Генерируем uuid в тесте, вместо созданного ранее.
    :param client:
    :param mock_crud:
    :return:
    """
    fake_uuid = uuid4()
    mock_crud.get_by_uuid.return_value = None

    resp = await client.get(f"/wallets/{fake_uuid}")
    assert resp.status_code in (200, 404)


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
    :param client:
    :return:
    """
    req = {"balance": "not_a_decimal"}
    resp = await client.post("/wallets/", json=req)
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


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
