"""Define the abstract base class for a command parser."""
from abc import ABC, abstractmethod
from app.controller import ResponseTuple
from typing import Optional


class Command(ABC):
    """Define the properties and methods needed for a command parser."""

    command_name = ""
    desc = ""

    def __init__(self):
        self.subparser = None

    @abstractmethod
    def handle(self,
               _command: str,
               user_id: str) -> ResponseTuple:
        """Handle a command."""
        pass

    def get_help(self, subcommand: Optional[str] = None) -> str:
        """
        Return command options with Slack formatting.

        If ``self.subparser`` isn't used, return the command's description
        instead.

        If ``subcommand`` is specified, return options for that specific
        subcommand (if that subcommand is one of the subparser's choices).
        Otherwise return a list of subcommands along with a short description.

        :param subcommand: name of specific subcommand to get help
        :return: nicely formatted string of options and help text
        """
        if self.subparser is None:
            return self.desc

        def get_subcommand_help(sc: str) -> str:
            """Return the help message of a specific subcommand."""
            cmd = self.subparser.choices[sc]
            return f'\n*{cmd.prog}*: {cmd.description}\n'

        if subcommand is None or subcommand not in self.subparser.choices:
            res = f"\n*{self.command_name} commands:*"
            for argument in self.subparser.choices:
                cmd = self.subparser.choices[argument]
                res += f'\n*{cmd.prog}*: {cmd.description}'
            return res
        else:
            res = "\n```"
            cmd = self.subparser.choices[subcommand]
            res += cmd.format_help()
            return res + "```"
