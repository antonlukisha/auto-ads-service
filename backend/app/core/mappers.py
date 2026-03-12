from app.models.domain import Car as DomainCar
from app.models.domain import User as DomainUser
from app.models.sqlalchemy_models import Car, User


class UserMapper:

    @classmethod
    def to_domain(cls, obj: User) -> DomainUser:
        """
        Convert SQLAlchemy object to domain object

        :param obj: User object
        :type obj: User
        :return: DomainUser object
        :rtype: DomainUser
        """
        try:
            return DomainUser.model_validate(
                {
                    "id": str(obj.id),
                    "username": obj.username,
                    "password_hash": obj.password_hash,
                    "created_at": obj.created_at,
                }
            )
        except Exception as e:
            raise e

    @classmethod
    def to_domain_list(cls, objs: list[User]) -> list[DomainUser]:
        """
        Convert SQLAlchemy object to domain object

        :param objs: List of User objects
        :type objs: list[User]
        :return: List of DomainUser objects
        :rtype: list[DomainUser]
        """
        try:
            return [cls.to_domain(obj) for obj in objs]
        except Exception as e:
            raise e


class CarMapper:

    @classmethod
    def to_domain_list(cls, objs: list[Car]) -> list[DomainCar]:
        """
        Convert SQLAlchemy object to domain object

        :param objs: List of Car objects
        :type objs: list[Car]
        :return: List of DomainCar objects
        :rtype: list[DomainCar]
        """
        try:
            return [cls.to_domain(obj) for obj in objs]
        except Exception as e:
            raise e

    @classmethod
    def to_domain(cls, obj: Car) -> DomainCar:
        """
        Convert SQLAlchemy object to domain object

        :param obj: Car object
        :type obj: Car
        :return: DomainCar object
        :rtype: DomainCar
        """
        try:
            return DomainCar.model_validate(
                {
                    "id": str(obj.id),
                    "brand": obj.brand,
                    "model": obj.model,
                    "year": obj.year,
                    "price": obj.price,
                    "color": obj.color,
                    "url": obj.url,
                    "created_at": obj.created_at,
                    "updated_at": obj.updated_at,
                }
            )
        except Exception as e:
            raise e
