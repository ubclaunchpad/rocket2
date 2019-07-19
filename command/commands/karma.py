import argparse
import logging
import pdb
import re
import shlex
from argparse import ArgumentParser, _SubParsersAction
from model import User, Permissions
from command import ResponseTuple
from model.user import User


class KarmaCommand:
    """karma command parser"""

    command_name = "karma"
    help = "karma command reference:\n\n /rocket karma"\
           "\n\nOptions:\n\n" \
           "user"
    lookup_error = "User doesn't exist"
    desc = "for dealing with " + command_name
    permission_error = "You do not have the sufficient " \
                       "permission level for this command!"
    karma_add_amount = 1
    karma_default_amount = 1

    def __init__(self, db_facade):
        """Initialize karma command"""
        logging.info("Starting karma command initializer")
        self.parser = argparse.ArgumentParser(prog="/rocket")
        self.parser.add_argument("karma")
        self.subparser = self.init_subparsers()
        self.facade = db_facade
        self.help = self.get_help()

    def handle(self, command, user_id):
        """Handle command by splitting into substrings"""
        logging.info('Handling karma Command')
        command_arg = shlex.split(command)
        args = None

        try:
            args = self.parser.parse_args(command_arg)
        except SystemExit:
            return self.get_help(), 200
        
        if args.which == "set":
            return self.set_helper(user_id, args.slack_id, args.amount)
        elif args.which == "reset":
            return self.reset_helper(user_id, args.all)
        elif args.which == "view":
            return self.view_helper(user_id, args.slack_id)
        else:
            return self.get_help(), 200

    def add_karma(self, giver_id, receiver_id) -> ResponseTuple:
        """Gives karma from giver_id to receiver_id"""
        logging.info("giving karma to " + receiver_id)
        if(giver_id == receiver_id):
            return "cannot give karma to self", 200
        try:
            user = self.facade.retrieve(User, receiver_id)
            user.karma += self.karma_add_amount
            self.facade.store(user)
            return f"gave 1 karma to {user.name}", 200
        except:
            return self.lookup_error, 200
    
    def is_user(self, id) -> bool:
        return re.match("^[UW][A-Z0-9]{8}$", id)

    def get_help(self) -> str:
        """Return command options for team events."""
        res = "\n*" + self.command_name + " commands:*```"
        for argument in self.subparser.choices:
            name = argument.capitalize()
            res += "\n*" + name + "*\n"
            res += self.subparser.choices[argument].format_help()
        return res + "```"


    def init_subparsers(self) -> _SubParsersAction:
        """Initialize subparsers for team command."""
        subparsers = self.parser.add_subparsers(dest="which")

        """Parser for set command."""
        parser_set = subparsers.add_parser("set")
        parser_set.set_defaults(which="set",
                                help="Manually sets a user's karma")
        parser_set.add_argument("slack_id", metavar="SLACK-ID",
                                type=str, action='store',
                                help="Use if using slack id instead of username.")
        parser_set.add_argument("amount", metavar="amount",
                                 type=int, action='store',
                                help="Amount of karma to set into user")
        
        parser_set = subparsers.add_parser("reset")
        parser_set.set_defaults(which="reset",
                                help="resets users id")
        parser_set.add_argument("-a", "--all", action="store_true",
                                help="Use to reset all user's karma amount")

        parser_set = subparsers.add_parser("view")
        parser_set.set_defaults(which="view",
                                help="view a user's karma amount")
        parser_set.add_argument("slack_id", metavar="SLACK-ID",
                                type=str, action='store',
                                help="Use if using slack id instead of username")
        return subparsers

    def set_helper(self,
                   user_id: str,
                   slack_id: str,
                   amount: int) -> ResponseTuple:
        """
        Manually sets a user's karma
        """
        try:
            user_command = self.facade.retrieve(User, user_id)
            if user_command.permissions_level == Permissions.admin:
                user = self.facade.retrieve(User, slack_id)
                user.karma = amount
                self.facade.store(user)
                return f"set user's karma to {amount}", 200
            else:
                return self.permission_error, 200
        except LookupError:
            return self.lookup_error, 200

    def reset_helper(self,
                     user_id: str,
                     reset_all: bool) -> ResponseTuple:
        """
        Resets all user's karma
        """
        try:
            user_command = self.facade.retrieve(User, user_id)
            if user_command.permissions_level == Permissions.admin:
                if reset_all:
                    user_list = self.facade.query(User, [])
                    for user in user_list:
                        user.karma = self.karma_default_amount
                        self.facade.store(user)
                    return f"reset all user's karma to {self.karma_default_amount}", 200
            else:
                return self.permission_error, 200
        except LookupError:
            return self.lookup_error, 200

    def view_helper(self,
                    user_id: str,
                    slack_id: str) -> ResponseTuple:
        """
        Allows user to view how much karma someone has
        """
        try:
            user = self.facade.retrieve(User, slack_id)
            return f"{user.name} has {user.karma} amount of karma"
        except LookupError:
            return self.lookup_error, 200
