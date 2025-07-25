from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WalletCreateSchema(BaseModel):
    """
    Схема создания кошелька.
    """

    balance: Decimal
    model_config = ConfigDict(arbitrary_types_allowed=True)


class WalletReadSchema(BaseModel):
    """
    Схема возврата кошелька по запросу.
    """

    uuid: UUID
    balance: Decimal
    model_config = ConfigDict(arbitrary_types_allowed=True)


class WalletReadBalanceSchema(BaseModel):
    """
    Схема чтения баланса кошелька по uuid.
    """

    balance: Decimal
    model_config = ConfigDict(arbitrary_types_allowed=True)
