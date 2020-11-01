"""Define the abstract base class for a data model."""
from abc import ABC, abstractmethod
from typing import Dict, Any, TypeVar, Type

T = TypeVar('T', bound='RocketModel')


class RocketModel(ABC):
    """Define the properties and methods needed for a data model."""

    @abstractmethod
    def get_attachment(self) -> Dict[str, Any]:
        """Return slack-formatted attachment (dictionary) for data model."""
        pass

    @classmethod
    @abstractmethod
    def to_dict(cls: Type[T], model: T) -> Dict[str, Any]:
        """
        Convert data model object to dict object.

        The difference with the in-built ``self.__dict__`` is that this is more
        compatible with storing into NoSQL databases like DynamoDB.
        :param model: the data model object
        :return: the dictionary representing the data model
        """
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls: Type[T], d: Dict[str, Any]) -> T:
        """
        Convert dict response object to data model object.

        :param d: the dictionary representing a data model
        :return: the converted data model object.
        """
        pass

    @classmethod
    @abstractmethod
    def is_valid(cls: Type[T], model: T) -> bool:
        """
        Return true if this data model has no missing required fields.

        :param model: data model object to check
        :return: true if this data model has no missing required fields
        """
        pass
