"""Define the abstract base class for a command parser."""
from abc import ABC, abstractmethod
from app.controller import ResponseTuple


class Command(ABC):
    """Define the properties and methods needed for a command parser."""

    @abstractmethod
    def handle(self,
               _command: str,
               user_id: str) -> ResponseTuple:
        """Handle a command."""
        pass
