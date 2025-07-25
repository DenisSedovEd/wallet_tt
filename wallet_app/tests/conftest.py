from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
import pytest_asyncio
from api.v1.wallets.views import router as wallets_router
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
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
    :return: экземпляра FastAPI приложения
    """
    app = FastAPI()
    app.include_router(wallets_router)
    return app


@pytest.fixture
def wallet_factory():
    """
    Создание разных кошельков с уникальным uuid.
    :return: Фабрика wallet
    """

    def _factory(balance=Decimal("100.00")):
        return Wallet(uuid=uuid4(), balance=balance)

    return _factory


@pytest.fixture
def mock_crud(wallet_factory):
    """
    Создание мокового crud.
    :param wallet_factory: Фабрика wallet
    :return: moc crud
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
