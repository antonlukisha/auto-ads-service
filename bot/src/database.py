from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from src.logging import get_logger

logger = get_logger("database")

Base = declarative_base()


class Database:
    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None
        self.dsn = ""

    async def initialize(self, dsn: str) -> None:
        """
        Initialize database connection.

        :param dsn: Database connection string
        :type dsn: str
        :return: nothing
        :rtype: None
        """
        self.dsn = dsn.replace("postgresql://", "postgresql+asyncpg://")
        self._engine = create_async_engine(
            self.dsn,
            echo=False,
            pool_size=40,
            max_overflow=10,
        )
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info("Database initialized")

    async def close(self) -> None:
        """
        Close database connection.
        """
        if self._engine:
            await self._engine.dispose()
            logger.info("Database connection closed")

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get database session.
        """
        if not self._session_factory:
            raise RuntimeError("Database not initialized")

        async with self._session_factory() as session:
            try:
                yield session
            finally:
                await session.close()


db = Database()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session.
    """
    async for session in db.get_session():
        yield session
