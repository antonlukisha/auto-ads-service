from typing import Generic, Type, TypeVar, cast
from uuid import UUID

from sqlalchemy import BinaryExpression, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base
from app.core.logging import get_logger
from app.core.utils import normalized_uuid

ModelType = TypeVar("ModelType", bound=Base)

logger = get_logger("repositories.base")


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, record_id: UUID | str) -> ModelType | None:
        """
        Get a single record by ID.
        [SELECT * FROM table_name WHERE id = 'record_id' LIMIT 1]

        :param record_id: The ID of the record to retrieve.
        :type record_id: str
        :return: The record if found, None otherwise.
        :rtype: ModelType | None
        """
        try:
            record_id = normalized_uuid(record_id)
            condition = cast(BinaryExpression, self.model.id == record_id)
            result = await self.session.execute(select(self.model).where(condition))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(e)
            raise e
