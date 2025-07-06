from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from api.v1.wallets.crud import WalletCRUD
from exceptions import WalletNotFound, NotEnoughBalanceError
from models import Wallet
from schemas.wallet import (
    WalletCreateSchema,
    WalletReadSchema,
    WalletReadBalanceSchema,
)
from schemas.operation import OperationTypeSchema
from api.v1.wallets.dependecies import wallet_crud

router = APIRouter(prefix="/wallets", tags=["wallets"])


@router.get("/{wallet_uuid}", response_model=WalletReadBalanceSchema)
async def get_balance(
    wallet_uuid: UUID,
    crud: Annotated[
        WalletCRUD,
        Depends(wallet_crud),
    ],
) -> Wallet:
    wallet = await crud.get_by_uuid(wallet_uuid)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet


@router.post("/", response_model=WalletReadSchema)
async def create_wallet(
    wallet: WalletCreateSchema,
    crud: Annotated[
        WalletCRUD,
        Depends(wallet_crud),
    ],
) -> Wallet:
    return await crud.create(wallet)


@router.post(
    "/{wallet_uuid}/operation",
    response_model=WalletReadBalanceSchema,
)
async def wallet_operation(
    wallet_uuid: UUID,
    operation_type: OperationTypeSchema,
    amount: Decimal,
    crud: Annotated[
        WalletCRUD,
        Depends(wallet_crud),
    ],
) -> Wallet:
    try:
        return await crud.operation(wallet_uuid, operation_type, amount)
    except WalletNotFound:
        raise HTTPException(status_code=404, detail="Wallet not found")
    except NotEnoughBalanceError:
        raise HTTPException(status_code=404, detail="Not enough balance")
