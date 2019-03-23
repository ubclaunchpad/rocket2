import argparse
import logging
import shlex
import re


class KarmaCommand:
    """karma command parser"""

    command_name = "karma"
    help = "karma command reference:\n\n /rocket karma"\
        "\n\nOptions:\n\n" \
        "user"
    lookup_error = "User doesn't exist"
    desc = "for dealing with " + command_name

    def __init__(self, db_facade):
        """Initialize karma command"""
        logging.info("Starting karma command initializer")
        self.parser = argparse.ArgumentParser(prog="karma")
        self.parser.add_argument("karma")
        self.facade = db_facade

    def handle(self, command, user_id):
        """Handle command by splitting into substrings"""
        logging.debug('Handling karma Command')
        command_arg = shlex.split(command)

        if(self.is_user(command_arg[0])):
            return self.short_karma_helper(user_id, command_arg[0], command_arg[1])
        elif(command_arg[0] == "karma" and self.is_user(command_arg[1])):
            reciever = self.parse_reciever(command_arg)
            return self.karma_helper(user_id, reciever, 1)