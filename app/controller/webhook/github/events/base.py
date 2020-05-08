"""Define the abstract base class for a GitHub event handler."""
from abc import ABC, abstractmethod
from db.facade import DBFacade
from interface.github import GithubInterface
from app.controller import ResponseTuple
from config import Config
from typing import Dict, Any, List


class GitHubEventHandler(ABC):
    """Define the properties and methods needed for a GitHub event handler."""

    def __init__(self, db_facade: DBFacade, gh_face: GithubInterface,
                 conf: Config):
        """Give handler access to the database facade."""
        self._facade = db_facade
        self._gh = gh_face
        self._conf = conf
        super().__init__()

    @property
    @abstractmethod
    def supported_action_list(self) -> List[str]:
        """Provide a list of all actions this handler can handle."""
        pass

    @abstractmethod
    def handle(self, payload: Dict[str, Any]) -> ResponseTuple:
        """Handle a GitHub event."""
        pass
