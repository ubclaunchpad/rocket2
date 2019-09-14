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
    def from_dict(d: Dict[str, Any]) -> 'RocketModel':
        """
        Convert dict response object to data model object.

        :param d: the dictionary representing a data model
        :return: returns converted data model object.
        """
        pass

    # TODO: Add to_dict and and is_valid abstract methods
