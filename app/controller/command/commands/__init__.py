"""Pack the modules contained in the commands directory."""
from typing import Union
from app.controller.command.commands.team import TeamCommand
from app.controller.command.commands.user import UserCommand
from app.controller.command.commands.token import TokenCommand

UnionCommands = Union[TeamCommand, UserCommand, TokenCommand]
