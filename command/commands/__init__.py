"""Pack the modules contained in the commands directory."""
from typing import Union
from command.commands.team import TeamCommand
from command.commands.user import UserCommand
from command.commands.token import TokenCommand
from command.commands.karma import KarmaCommand
from command.commands.mention import MentionCommand

UnionCommands = Union[TeamCommand, UserCommand, TokenCommand, KarmaCommand, MentionCommand]
