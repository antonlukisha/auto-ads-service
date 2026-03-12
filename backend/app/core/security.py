from datetime import UTC, datetime, timedelta
from typing import cast

import bcrypt
from jose import JWTError, jwt

from app.core.config import get_config


class PasswordManager:

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify plain password against hashed password.

        :param plain_password: Plain password
        :type plain_password: str
        :param hashed_password: Hashed password
        :type hashed_password: str
        :return: True if passwords match, False otherwise
        :rtype: bool
        """
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        Hash a password.

        :param password: Password to hash
        :type password: str
        :return: Hashed password
        :rtype: str
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


class JWTManager:
    def __init__(self) -> None:
        self.config = get_config().jwt
        self.secret_key = self.config.secret_key
        self.algorithm = self.config.algorithm

    def create_access_token(self, user_id: str) -> str:
        """
        Create JWT access token.

        :param user_id: User ID
        :type user_id: str
        :return: JWT access token
        :rtype: str
        """
        expire = datetime.now(UTC) + timedelta(minutes=self.config.access_token_expire_minutes)
        payload = {"sub": str(user_id), "exp": expire, "type": "access"}
        return cast(str, jwt.encode(payload, self.secret_key, algorithm=self.algorithm))

    def verify_token(self, token: str, expected_type: str = "access") -> str | None:
        """
        Verify token and return user_id if valid.

        :param token: JWT token
        :type token: str
        :param expected_type: Expected token type (default: "access", options: "access", "refresh", "verification")
        :type expected_type: str
        :return: User ID if valid, None otherwise
        :rtype: str | None
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != expected_type:
                return None
            return cast(str, payload.get("sub"))
        except (JWTError, ValueError, TypeError):
            return None


jwt_manager = JWTManager()
password_manager = PasswordManager()
