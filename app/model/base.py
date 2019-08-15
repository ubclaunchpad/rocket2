"""Define the abstract base class for a data model."""
from abc import ABC, abstractmethod
from typing import Dict, Any


class RocketModel(ABC):
    """Define the properties and methods needed for a data model."""

    @abstractmethod
    def get_attachment(self) -> Dict[str, Any]:
        """Return slack-formatted attachment (dictionary) for data model."""
        pass

    @staticmethod
    @abstractmethod
    def to_dict(model: 'Model') -> Dict[str, Any]:
        """
        Convert data model object to dict object.

        The difference with the in-built ``self.__dict__`` is that this is more
        compatible with storing into NoSQL databases like DynamoDB.

        :param model: the data model object
        :return: the dictionary representing the data model
        """
        pass

    @staticmethod
    @abstractmethod
    def from_dict(d: Dict[str, Any]) -> 'Model':
        """
        Convert dict response object to data model object.

        :param d: the dictionary representing a data model
        :return: returns converted data model object.
        """
        pass

    @staticmethod
    @abstractmethod
    def is_valid(model: 'Model') -> bool:
        """
        Return true if this data model has no missing required fields.

        :param model: data model object to check
        :return: return true if this data model has no missing required fields
        """
        pass
