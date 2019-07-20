"""Pack the modules contained in the commands directory."""
from typing import Union
from app.controller.command.commands.team import TeamCommand
from app.controller.command.commands.user import UserCommand
from app.controller.command.commands.token import TokenCommand
from app.controller.command.commands.karma import KarmaCommand
from app.controller.command.commands.mention import MentionCommand

UnionCommands = Union[TeamCommand, UserCommand,
                      TokenCommand, KarmaCommand, MentionCommand]
