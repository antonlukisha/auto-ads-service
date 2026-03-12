import asyncio
from typing import cast

from sqlalchemy import BinaryExpression, select

from app.core.config import get_config
from app.core.database import db
from app.core.logging import get_logger
from app.core.security import password_manager
from app.models.sqlalchemy_models import User

logger = get_logger(__name__)


async def seed_admin() -> None:
    """
    Seed the database with an admin user
    """

    cfg = get_config()

    try:
        await db.initialize(cfg.postgres_dsn)

        async for session in db.get_session():
            try:
                result = await session.execute(
                    select(User).where(cast(BinaryExpression, User.username == "admin"))
                )

                user = result.scalar_one_or_none()

                if not user:
                    admin = User(
                        username="admin",
                        password_hash=password_manager.get_password_hash("admin_pass"),
                    )

                    session.add(admin)
                    await session.commit()

                    logger.info("Admin user created")
            except Exception as e:
                if session:
                    await session.rollback()
                logger.error(f"Failed to seed admin user: {e}")
                raise

    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise
    finally:
        await db.close()
        logger.info("Database connection closed")


def main():
    """
    Entry point for console script
    """
    asyncio.run(seed_admin())


if __name__ == "__main__":
    main()
