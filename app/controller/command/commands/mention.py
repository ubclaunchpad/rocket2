"""Parser for all direct mentions made using rocket."""
import argparse
import logging
import shlex
from app.controller.command.commands.base import Command
from app.controller import ResponseTuple
from db.facade import DBFacade
from app.model import User


class MentionCommand(Command):
    """Mention command parser."""

    command_name = "mention"
    lookup_error = "User doesn't exist"
    desc = "for dealing with " + command_name
    karma_add_amount = 1
    unsupported_error = "unsupported usage"

    def __init__(self, db_facade: DBFacade) -> None:
        """Initialize Mention command."""
        logging.info("Starting Mention command initializer")
        self.parser = argparse.ArgumentParser(prog="Mention")
        self.parser.add_argument("Mention")
        self.facade = db_facade

    def handle(self, command: str, user_id: str) -> ResponseTuple:
        """Handle command by splitting into substrings."""
        logging.debug('Handling Mention Command')
        command_arg = shlex.split(command)
        if len(command_arg) <= 1:
            return "invalid command", 200
        elif command_arg[1] == '++':
            return self.add_karma(user_id, command_arg[0])
        else:
            return "unsupported usage", 200

    def add_karma(self, giver_id: str, receiver_id: str) -> ResponseTuple:
        """Give karma from giver_id to receiver_id."""
        logging.info("giving karma to " + receiver_id)
        if giver_id == receiver_id:
            return "cannot give karma to self", 200
        try:
            user = self.facade.retrieve(User, receiver_id)
            user.karma += self.karma_add_amount
            self.facade.store(user)
            return f"gave {self.karma_add_amount} karma to {user.name}", 200
        except LookupError:
            return self.lookup_error, 200
