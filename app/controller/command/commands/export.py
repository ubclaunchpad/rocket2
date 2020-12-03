"""Command parsing for user events."""
import logging
import shlex

from argparse import ArgumentParser, _SubParsersAction
from app.controller import ResponseTuple
from app.controller.command.commands.base import Command
from db.facade import DBFacade
from app.model import User
from db.utils import get_team_by_name, get_team_members
from utils.slack_parse import check_permissions


class ExportCommand(Command):
    """Represent Export Command Parser."""

    command_name = "export"
    permission_error = "You do not have the sufficient " \
                       "permission level for this command!"
    lookup_error = "Lookup error!"
    no_emails_missing_msg = "All members have emails! Nice!"
    char_limit_exceed_msg = "WARNING! Could not export all emails for " \
                            "exceeding slack character limits :("
    no_user_msg = "No members found for exporting emails!"
    desc = f"for dealing with {command_name}s"
    # Slack currently allows to send 16000 characters max
    MAX_CHAR_LIMIT = 15950

    def __init__(self, db_facade: DBFacade):
        """Initialize export command."""
        logging.info("Initializing ExportCommand instance")
        self.parser = ArgumentParser(prog="/rocket")
        self.parser.add_argument("export")
        self.subparser = self.init_subparsers()
        self.facade = db_facade

    def init_subparsers(self) -> _SubParsersAction:
        """
        Initialize subparsers for export command.

        :meta private:
        """
        subparsers = self.parser.add_subparsers(dest="which")

        # Parser for emails command
        parser_view = subparsers.add_parser(
            'emails', description='(Admin/Lead only) Export emails of all '
                                  'users')
        parser_view.add_argument("--team", metavar="TEAM",
                                 type=str, action='store',
                                 help="(Admin/Lead only) Export emails"
                                      " by team name")

        return subparsers

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
                command_user = self.facade.retrieve(User, user_id)
                if not check_permissions(command_user, None):
                    return self.permission_error, 200

                # Check if team name is provided
                if args.team is not None:
                    users = self.get_team_users(args.team)
                    return self.export_emails_helper(users)
                else:  # if team name is not provided, export all emails
                    users = self.facade.query(User)
                    return self.export_emails_helper(users)
            except LookupError:
                return self.lookup_error, 200
        else:
            return self.get_help(), 200

    def get_team_users(self, team_name):
        team = get_team_by_name(self.facade, team_name)
        return get_team_members(self.facade, team)

    def export_emails_helper(self,
                             users: list) -> ResponseTuple:
        """
         returns emails of all users
         + names of the users who do not have an email
        """

        if len(users) == 0:
            return self.no_user_msg, 200

        emails = []
        ids_missing_emails = []

        for i in range(len(users)):
            if users[i].email == '':
                ids_missing_emails.append(users[i].slack_id)
                continue

            emails.append(users[i].email)

        emails_str = ",".join(emails)

        if len(ids_missing_emails) != 0:
            ret = "```" + emails_str + "```\n\n" \
                  + "\n\nMembers who don't have an " \
                    "email: {}".format(
                        ",".join(map(lambda u: f"<@{u}>", ids_missing_emails)))
            if len(ret) >= self.MAX_CHAR_LIMIT:
                ret = self.handle_char_limit_exceeded(ret, "\n\nMembers who")
        else:
            ret = "```" + emails_str + "```" \
                  + "\n\n" + self.no_emails_missing_msg
            if len(ret) >= self.MAX_CHAR_LIMIT:
                ret = self.handle_char_limit_exceeded(
                    ret, self.no_emails_missing_msg)

        return ret, 200

    def handle_char_limit_exceeded(self, ret_str, find_str):
        """
        Find the last occurrence (index) of ``find_str``
        and chop off items before that index

        Assume that items are separated by commas.

        :return: a string of emails with char limit exceed
                 warning message that is under ``MAX_CHAR_LIMIT``
        """
        last_find_idx = ret_str.rfind(find_str)
        temp_str1 = ret_str[:last_find_idx]
        temp_str2 = ret_str[last_find_idx:]
        max_end_idx = \
            self.MAX_CHAR_LIMIT \
            - len(temp_str2) - len(self.char_limit_exceed_msg)
        temp_str3 = temp_str1[:max_end_idx]
        last_comma_idx = temp_str3.rfind(',')
        temp_str3 = temp_str3[:last_comma_idx]
        return \
            temp_str3 + "```\n\n" + temp_str2 \
            + "\n\n" + self.char_limit_exceed_msg
