from decimal import Decimal
from typing import Annotated
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.v1.wallets.crud import WalletCRUD
from api.v1.wallets.dependencies import wallet_crud
from api.v1.wallets.views import router
from models import Wallet
from schemas.wallet import WalletCreateSchema, WalletReadSchema, WalletReadBalanceSchema
from schemas.operation import OperationTypeSchema
from tests.conftest import get_db, override_get_db

# Создаем тестового клиента
client = TestClient(router)


# Переопределяем зависимость для тестов
def get_test_wallet_crud(db: Annotated[Session, Depends(get_db)]):
    return WalletCRUD(db)


# Применяем переопределенную зависимость
router.dependency_overrides[wallet_crud] = get_test_wallet_crud


@pytest.mark.asyncio
async def test_index(client):
    response = client.get("/wallets/")
    assert response.status_code == 200
    assert response.json() == {"message": "Wallet API"}


@pytest.mark.asyncio
async def test_create_wallet(client, db: Session):
    wallet_data = WalletCreateSchema(name="Test Wallet", balance=Decimal("100.00"))

    response = client.post("/wallets/", json=wallet_data.dict())
    assert response.status_code == 201

    data = response.json()
    assert "uuid" in data
    assert data["name"] == wallet_data.name
    assert data["balance"] == str(wallet_data.balance)


@pytest.mark.asyncio
async def test_get_balance(client, db: Session):
    # Создаем тестовый кошелек
    wallet = Wallet(uuid=uuid4(), name="Test Wallet", balance=Decimal("100.00"))
    db.add(wallet)
    db.commit()

    response = client.get(f"/wallets/{wallet.uuid}")
    assert response.status_code == 200

    data = response.json()
    assert data["uuid"] == str(wallet.uuid)
    assert data["balance"] == str(wallet.balance)


@pytest.mark.asyncio
async def test_wallet_operation(client, db: Session):
    # Создаем тестовый кошелек
    wallet = Wallet(uuid=uuid4(), name="Test Wallet", balance=Decimal("100.00"))
    db.add(wallet)
    db.commit()

    # Тестируем операцию пополнения
    response = client.post(
        f"/wallets/{wallet.uuid}/operation",
        json={"operation_type": OperationTypeSchema.deposit.value, "amount": "50.00"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["balance"] == str(Decimal("150.00"))

    # Тестируем операцию снятия
    response = client.post(
        f"/wallets/{wallet.uuid}/operation",
        json={"operation_type": OperationTypeSchema.withdraw.value, "amount": "20.00"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["balance"] == str(Decimal("130.00"))


@pytest.mark.asyncio
async def test_invalid_operation(client, db: Session):
    # Создаем тестовый кошелек
    wallet = Wallet(uuid=uuid4(), name="Test Wallet", balance=Decimal("100.00"))
    db.add(wallet)
    db.commit()

    # Попытка снять больше, чем есть на балансе
    response = client.post(
        f"/wallets/{wallet.uuid}/operation",
        json={"operation_type": OperationTypeSchema.withdraw.value},
    )
