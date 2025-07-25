from decimal import Decimal
from uuid import UUID

from exceptions import NotEnoughBalanceError, WalletNotFound
from models import Wallet
from schemas.operation import OperationTypeSchema
from schemas.wallet import WalletCreateSchema
from sqlalchemy.ext.asyncio import AsyncSession


class WalletCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, wallet: WalletCreateSchema) -> Wallet:
        """
        Асинхронный метод создания кошелька.
        :param wallet:
        :return:
        """
        wallet = Wallet(balance=wallet.balance)
        self.session.add(wallet)
        await self.session.commit()
        return wallet

    async def get_by_uuid(self, wallet_uuid: UUID) -> Wallet | None:
        """
        Асинхронный метод получения кошелька.
        :param wallet_uuid:
        :return:
        """
        return await self.session.get(Wallet, wallet_uuid)

    async def operation(
        self,
        wallet_uuid: UUID,
        op_type: OperationTypeSchema,
        amount: Decimal,
    ) -> Wallet:
        """
        Асинхронный метод выполнения определенной операции.
        :param wallet_uuid:
        :param op_type:
        :param amount:
        :return:
        """
        wallet = await self.get_by_uuid(wallet_uuid)
        if not wallet:
            raise WalletNotFound(wallet_uuid)
        if op_type == OperationTypeSchema.DEPOSIT:
            wallet.balance += amount
        elif op_type == OperationTypeSchema.WITHDRAW:
            if wallet.balance < amount:
                raise NotEnoughBalanceError(
                    f"На кошельке {wallet_uuid} недостаточно средств."
                )
            wallet.balance -= amount
        else:
            raise ValueError(f"Unknown operation type: {op_type}")
        await self.session.commit()
        return wallet
