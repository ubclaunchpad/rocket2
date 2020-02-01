"""Encapsulate the common business logic of all command types."""
from db.facade import DBFacade
from interface.github import GithubInterface
from interface.slack import Bot

from api.command.mixins import UserCommandApis, TeamCommandApis


class CommandApis(UserCommandApis, TeamCommandApis):
    """Encapsulate the various APIs of each command type."""

    def __init__(self,
                 db_facade: DBFacade,
                 gh_interface: GithubInterface,
                 slack_client: Bot) -> None:
        """Initialize the dependencies of command APIs."""
        self._db_facade = db_facade
        self._gh_interface = gh_interface
        self._slack_client = slack_client
