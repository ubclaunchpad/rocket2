"""Parser for all direct mentions made using rocket."""
import argparse
import logging
import shlex
from app.controller import ResponseTuple
from app.controller.command.commands.karma import KarmaCommand
from db.facade import DBFacade
from app.model import User

class MentionCommand:
    """Mention command parser."""

    command_name = "mention"
    lookup_error = "User doesn't exist"
    desc = "for dealing with " + command_name
    karma_add_amount = 1

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
            return "not supported", 200
        elif command_arg[1] == '++':
            return self.karma_mention_helper(user_id, command_arg[0])

    def karma_mention_helper(self,
                             giver_id: str,
                             receiver_id: str) -> ResponseTuple:
        """Use the karma command to help add karma to a user."""
        return self.add_karma(giver_id, receiver_id)

    def add_karma(self, giver_id, receiver_id) -> ResponseTuple:
        """Give karma from giver_id to receiver_id."""
        logging.info("giving karma to " + receiver_id)
        if giver_id == receiver_id:
            return "cannot give karma to self", 200
        try:
            user = self.facade.retrieve(User, receiver_id)
            user.karma += self.karma_add_amount
            self.facade.store(user)
            return f"gave 1 karma to {user.name}", 200
        except LookupError:
            return self.lookup_error, 200