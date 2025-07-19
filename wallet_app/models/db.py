from config import settings
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

engine = create_async_engine(
    url=settings.db.url,
    echo=settings.db.echo,
)

session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autocommit=False,
)
