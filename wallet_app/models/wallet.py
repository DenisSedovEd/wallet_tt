from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Numeric
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from models import Base


class Wallet(Base):
    __tablename__ = "wallets"
    uuid: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    balance: Mapped[Decimal] = mapped_column(
        Numeric(20, 2),
        default=Decimal("0.00"),
    )
