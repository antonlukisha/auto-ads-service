from app.core.logging import get_logger
from app.core.mappers import UserMapper
from app.core.security import jwt_manager, password_manager
from app.models.domain import User
from app.repositories.users import UserRepository

logger = get_logger("services.auth")


class AuthService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def login(self, username: str, password: str) -> tuple[str, User]:
        """
        Authenticate user and return token.

        :param username: Username
        :type username: str
        :param password: User's password
        :type password: str
        :return: Tuple of (access_token, refresh_token, User)
        :rtype: tuple[str, User]
        """
        try:
            user = await self.repo.get_by_username(username)
            if not user:
                raise ValueError("Invalid username or password")

            if not password_manager.verify_password(password, str(user.password_hash)):
                raise ValueError("Invalid username or password")

            access_token = jwt_manager.create_access_token(str(user.id))

            return access_token, UserMapper.to_domain(user)

        except Exception as e:
            raise e
