"""Command parsing for user events."""
import logging
import shlex

from argparse import ArgumentParser, _SubParsersAction
from app.controller import ResponseTuple
from app.controller.command.commands.base import Command
from db.facade import DBFacade
from interface.gcp import GCPInterface
from app.model import User, Permissions
from typing import Optional
from interface.slack import Bot


class ExportCommand(Command):
    """Represent Export Command Parser."""

    command_name = "export"
    permission_error = "You do not have the sufficient " \
                       "permission level for this command!"
    lookup_error = "Lookup error!"
    desc = f"for dealing with {command_name}s"

    def __init__(self,
                 db_facade: DBFacade,
                 bot: Bot,
                 gcp: Optional[GCPInterface]):
        """Initialize export command."""
        logging.info("Initializing ExportCommand instance")
        self.parser = ArgumentParser(prog="/rocket")
        self.parser.add_argument("export")
        self.subparser = self.init_subparsers()
        self.help = self.get_help()
        self.facade = db_facade
        self.gcp = gcp
        self.bot = bot

    def init_subparsers(self) -> _SubParsersAction:
        """
        Initialize subparsers for export command.

        :meta private:
        """
        subparsers = self.parser.add_subparsers(dest="which")

        # Parser for emails command
        parser_view = subparsers.add_parser("emails")
        parser_view.set_defaults(which="emails",
                                 help="(Admin only) Export emails of all users.")

        return subparsers

    def get_help(self, subcommand: str = None) -> str:
        """Return command options for user events with Slack formatting."""

        def get_subcommand_help(sc: str) -> str:
            """Return the help message of a specific subcommand."""
            message = f"\n*{sc.capitalize()}*\n"
            message += self.subparser.choices[sc].format_help()
            return message

        if subcommand is None or subcommand not in self.subparser.choices:
            res = f"\n*{self.command_name} commands:*```"
            for argument in self.subparser.choices:
                res += get_subcommand_help(argument)
            return res + "```"
        else:
            res = "\n```"
            res += get_subcommand_help(subcommand)
            return res + "```"

    def handle(self,
               command: str,
               user_id: str) -> ResponseTuple:
        """Handle command by splitting into substrings and giving to parser."""
        logging.debug("Handling ExportCommand")
        command_arg = shlex.split(command)
        args = None

        try:
            args = self.parser.parse_args(command_arg)
        except SystemExit:
            all_subcommands = list(self.subparser.choices.keys())
            present_subcommands = [subcommand for subcommand in
                                   all_subcommands
                                   if subcommand in command_arg]
            present_subcommand = None
            if len(present_subcommands) == 1:
                present_subcommand = present_subcommands[0]
            return self.get_help(subcommand=present_subcommand), 200

        if args.which == "emails":
            try:
                user_command = self.facade.retrieve(User, user_id)
                if user_command.permissions_level == Permissions.admin:
                    return self.export_helper()
                else:
                    return self.permission_error, 200
            except LookupError:
                return self.lookup_error, 200

        else:
            return self.get_help(), 200

    def export_helper(self) -> ResponseTuple:
        """
        Export emails of all users as a string + names of the users who do not have an email

        """

        params = [('permission_level', lvl) for lvl in ['admin', 'member']]
        users = self.facade.query_or(User, params)

        emails = ""
        ids_missing_emails = []

        for i in range(len(users)):
            if users[i].email == '':
                ids_missing_emails.append(users[i].slack_id)
                continue

            if i != len(users) - 1:
                emails += str(users[i].email) + ", "
            else:  # don't add , for the last member
                emails += str(users[i].email)

        if len(ids_missing_emails) != 0:
            ret = "```" + emails + "\n\nMembers who don't have an email: {}".format(
                    ", ".join(map(lambda u: f"<@{u}>", ids_missing_emails))) + "```"
        else:
            ret = "```" + emails + "```"

        return ret, 200
