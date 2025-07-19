"""create wallet table

Revision ID: 9146422e930d
Revises:
Create Date: 2025-07-04 09:51:20.161487

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9146422e930d"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "wallets",
        sa.Column("uuid", sa.UUID(), nullable=False),
        sa.Column("balance", sa.Numeric(precision=20, scale=2), nullable=False),
        sa.PrimaryKeyConstraint("uuid", name=op.f("pk_wallets")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("wallets")
