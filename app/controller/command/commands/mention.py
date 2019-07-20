import argparse
import logging
import shlex
from app.controller import ResponseTuple
from app.controller.command.commands.karma import KarmaCommand
from db.facade import DBFacade


class MentionCommand:
    """Mention command parser"""

    command_name = "mention"
    help = "Mention command reference:\n\n /rocket Mention"\
        "\n\nOptions:\n\n" \
        "user"
    lookup_error = "User doesn't exist"
    desc = "for dealing with " + command_name

    def __init__(self, db_facade: DBFacade) -> None:
        """Initialize Mention command"""
        logging.info("Starting Mention command initializer")
        self.parser = argparse.ArgumentParser(prog="Mention")
        self.parser.add_argument("Mention")
        self.facade = db_facade

    def handle(self, command: str, user_id: str) -> ResponseTuple:
        """Handle command by splitting into substrings"""
        logging.debug('Handling Mention Command')
        command_arg = shlex.split(command)
        if(len(command_arg) <= 1):
            return self.help, 200
        elif(command_arg[1] == "help"):
            return self.help, 200
        elif(command_arg[1] == '++'):
            return self.karma_mention_helper(user_id, command_arg[0])

    def karma_mention_helper(self,
                             giver_id: str,
                             receiver_id: str) -> ResponseTuple:
        return KarmaCommand(self.facade).add_karma(giver_id, receiver_id)
