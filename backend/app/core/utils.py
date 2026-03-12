import re
from uuid import UUID


def normalized_uuid(origin_uuid: UUID | str) -> UUID:
    """
    Normalize UUID to UUID object.

    :param origin_uuid: UUID string or UUID object
    :type origin_uuid: UUID | str
    :return: UUID object
    :rtype: UUID
    """
    if isinstance(origin_uuid, UUID):
        return origin_uuid
    else:
        uuid_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
        )
        if not uuid_pattern.match(origin_uuid):
            raise ValueError(f"Invalid UUID: {origin_uuid}")
        return UUID(origin_uuid)
