from model.user import User
from typing import Dict, cast
import argparse
import logging
import shlex
import re
import pdb

class MentionCommand:
    """Mention command parser"""

    command_name = "Mention"
    help = "Mention command reference:\n\n /rocket Mention"\
        "\n\nOptions:\n\n" \
        "user"
    lookup_error = "User doesn't exist"
    desc = "for dealing with " + command_name
    karma_add_amount = 1

    def __init__(self, db_facade):
        """Initialize Mention command"""
        logging.info("Starting Mention command initializer")
        self.parser = argparse.ArgumentParser(prog="Mention")
        self.parser.add_argument("Mention")
        self.facade = db_facade

    def handle(self, command, user_id):
        """Handle command by splitting into substrings"""
        logging.debug('Handling Mention Command')
        command_arg = shlex.split(command)
        if(len(command_arg) <= 1):
            return self.help, 200
        elif(command_arg[1] == "help"):
            return self.help, 200
        elif(command_arg[1] == '++'):
            return self.karma_mention_helper(user_id, command_arg[0], self.karma_add_amount)

    def karma_mention_helper(self, giver, reciever, amount):
        logging.info("giving karma to " + reciever)
        if(giver == reciever):
            return "cannot give karma to self", 200
        try:
            user = cast(User, self.facade.retrieve(User, reciever))
            user.karma += amount
            self.facade.store(user)
            return f"gave 1 karma to {user.name}", 200
        except:
            return self.lookup_error, 200
