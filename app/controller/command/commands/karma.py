"""Command for parsing karma."""
import logging
import shlex
from app.controller.command.commands.base import Command
from argparse import ArgumentParser, _SubParsersAction
from app.model import User, Permissions
from app.controller import ResponseTuple


class KarmaCommand(Command):
    """karma command parser."""

    command_name = "karma"
    help = "karma command reference:\n\n /rocket karma"\
           "\n\nOptions:\n\n" \
           "user"
    lookup_error = "User doesn't exist"
    desc = "for dealing with " + command_name
    permission_error = "You do not have the sufficient " \
                       "permission level for this command!"
    karma_default_amount = 1

    def __init__(self, db_facade):
        """Initialize karma command."""
        logging.info("Starting karma command initializer")
        self.parser = ArgumentParser(prog="/rocket")
        self.parser.add_argument("karma")
        self.subparser = self.init_subparsers()
        self.facade = db_facade
        self.help = self.get_help()

    def init_subparsers(self) -> _SubParsersAction:
        """Initialize subparsers for karma command."""
        subparsers: _SubParsersAction = \
            self.parser.add_subparsers(dest="which")

        """Parser for set command."""
        parser_set = subparsers.add_parser("set")
        parser_set.set_defaults(which="set",
                                help="Manually sets a user's karma")
        parser_set.add_argument("username", metavar="USERNAME",
                                type=str, action='store',
                                help="slack id of kuser's karma to set")
        parser_set.add_argument("amount", metavar="amount",
                                type=int, action='store',
                                help="Amount of karma to set into user")

        """Parser for reset command."""
        parser_reset = subparsers.add_parser("reset")
        parser_reset.set_defaults(which="reset",
                                  help="resets users id")
        parser_reset.add_argument("-a", "--all", action="store_true",
                                  help="Use to reset all user's karma amount")

        """Parser for view command."""
        parser_view = subparsers.add_parser("view")
        parser_view.set_defaults(which="view",
                                 help="view a user's karma amount")
        parser_view.add_argument("username", metavar="USERNAME",
                                 type=str, action='store',
                                 help="slack id of user karma to view")
        return subparsers

    def handle(self, command, user_id):
        """Handle command by splitting into substrings."""
        logging.info('Handling karma Command')
        command_arg = shlex.split(command)
        args = None

        try:
            args = self.parser.parse_args(command_arg)
        except SystemExit:
            return self.get_help(), 200

        if args.which == "set":
            return self.set_helper(user_id, args.username, args.amount)
        elif args.which == "reset":
            return self.reset_helper(user_id, args.all)
        elif args.which == "view":
            return self.view_helper(user_id, args.username)
        else:
            return self.get_help(), 200

    def get_help(self) -> str:
        """Return command options for team events."""
        res = "\n*" + self.command_name + " commands:*```"
        for argument in self.subparser.choices:
            name = argument.capitalize()
            res += "\n*" + name + "*\n"
            res += self.subparser.choices[argument].format_help()
        return res + "```"

    def set_helper(self,
                   user_id: str,
                   slack_id: str,
                   amount: int) -> ResponseTuple:
        """Manually sets a user's karma."""
        try:
            user = self.facade.retrieve(User, user_id)
            if user.permissions_level == Permissions.admin:
                user = self.facade.retrieve(User, slack_id)
                user.karma = amount
                self.facade.store(user)
                return f"set {user.name}'s karma to {amount}", 200
            else:
                return self.permission_error, 200
        except LookupError:
            return self.lookup_error, 200

    def reset_helper(self,
                     user_id: str,
                     reset_all: bool) -> ResponseTuple:
        """Reset all users' karma."""
        try:
            user = self.facade.retrieve(User, user_id)
            if not user.permissions_level == Permissions.admin:
                return self.permission_error, 200
            if reset_all:
                user_list = self.facade.query(User, [])
                for user in user_list:
                    user.karma = self.karma_default_amount
                    self.facade.store(user)
                return (
                    "reset all users karma to"
                    f"{self.karma_default_amount}",
                    200
                )
            else:
                return self.get_help(), 200
        except LookupError:
            return self.lookup_error, 200

    def view_helper(self,
                    user_id: str,
                    slack_id: str) -> ResponseTuple:
        """Allow user to view how much karma someone has."""
        try:
            user = self.facade.retrieve(User, slack_id)
            return f"{user.name} has {user.karma} karma", 200
        except LookupError:
            return self.lookup_error, 200
