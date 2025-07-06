from typing import AsyncGenerator, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from models.db import session_factory
from .crud import WalletCRUD


async def get_session() -> AsyncGenerator[AsyncSession]:
    """
    Генератор асинхронной сессии
    :return:
    """
    async with session_factory() as session:
        yield session


async def wallet_crud(
    session: Annotated[
        AsyncSession,
        Depends(get_session),
    ],
) -> WalletCRUD:
    """
    Функция для оборачивания асинхронной сесии в CRUD.
    :param session: Async session from sqlalchemy,
    полученная путем связи с генератором сессий.
    :return: Объект класса WalletCRUD уже с имеющейся сессией.
    """
    return WalletCRUD(session)
