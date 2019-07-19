"""Pack the modules contained in the commands directory."""
from typing import Union
from command.commands.team import TeamCommand
from command.commands.user import UserCommand
from command.commands.token import TokenCommand
from command.commands.karma import KarmaCommand

UnionCommands = Union[TeamCommand, UserCommand, TokenCommand, KarmaCommand]
