from typing import cast

from sqlalchemy import BinaryExpression, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.sqlalchemy_models import User
from app.repositories.base import BaseRepository

logger = get_logger("repositories.users")


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_username(self, username: str) -> User | None:
        """
        Get user by username.
        [SELECT * FROM users WHERE username = :username]

        :param username: Username
        :type username: str
        :return: User object if found, None otherwise
        :rtype: User | None
        """
        try:
            condition = cast(BinaryExpression, self.model.username == username)
            result = await self.session.execute(select(self.model).where(condition))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            raise e
