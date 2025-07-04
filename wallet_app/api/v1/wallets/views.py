from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from api.v1.wallets.crud import WalletCRUD
from models import Wallet
from schemas.wallet import WalletCreateSchema, WalletReadSchema, WalletReadBalanceSchema
from schemas.operation import OperationTypeSchema
from api.v1.wallets.dependecies import wallet_crud

router = APIRouter(prefix="/wallets", tags=["wallets"])


@router.get("/")
async def index():
    return {"message": "Wallet API"}


@router.get("/{wallet_uuid}", response_model=WalletReadBalanceSchema)
async def get_balance(
    wallet_uuid: UUID, crud: Annotated[WalletCRUD, Depends(wallet_crud)]
) -> Wallet:
    return await crud.get_by_uuid(wallet_uuid)


@router.post("/", response_model=WalletReadSchema)
async def create_wallet(
    wallet: WalletCreateSchema, crud: Annotated[WalletCRUD, Depends(wallet_crud)]
) -> Wallet:
    return await crud.create(wallet)


@router.post("{wallet_uuid}/operation", response_model=WalletReadBalanceSchema)
async def wallet_operation(
    wallet_uuid: UUID,
    operation_type: OperationTypeSchema,
    amount: Decimal,
    crud: Annotated[WalletCRUD, Depends(wallet_crud)],
) -> Wallet:
    return await crud.operation(wallet_uuid, operation_type, amount)
