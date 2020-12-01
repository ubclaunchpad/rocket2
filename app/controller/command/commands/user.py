"""Command parsing for user events."""
import logging
import shlex

from argparse import ArgumentParser, _SubParsersAction, Namespace
from app.controller import ResponseTuple
from app.controller.command.commands.base import Command
from db.facade import DBFacade
from interface.github import GithubAPIException, GithubInterface
from interface.gcp import GCPInterface
from interface.gcp_utils import sync_user_email_perms
from app.model import User, Team, Permissions
from typing import Optional
from utils.slack_parse import escape_email


class UserCommand(Command):
    """Represent User Command Parser."""

    command_name = "user"
    permission_error = "You do not have the sufficient " \
                       "permission level for this command!"
    lookup_error = "Lookup error! User not found!"
    viewinspect_noghid = 'Specified user does not have a Github account'\
        'registered with Rocket.'
    delete_text = "Deleted user with Slack ID: "
    desc = f"for dealing with {command_name}s"

    def __init__(self,
                 db_facade: DBFacade,
                 github_interface: GithubInterface,
                 gcp: Optional[GCPInterface]):
        """Initialize user command."""
        super().__init__()
        logging.info("Initializing UserCommand instance")
        self.parser = ArgumentParser(prog="/rocket")
        self.parser.add_argument("user")
        self.subparser = self.init_subparsers()
        self.help = self.get_help()
        self.facade = db_facade
        self.github = github_interface
        self.gcp = gcp

    def init_subparsers(self) -> _SubParsersAction:
        """
        Initialize subparsers for user command.

        :meta private:
        """
        subparsers = self.parser.add_subparsers(dest="which")

        # Parser for view command
        parser_view = subparsers.add_parser(
            "view", description="View information about a given user")
        parser_view.add_argument("--username", metavar="USERNAME",
                                 type=str, action='store',
                                 help="Query user by Slack ID")
        parser_view.add_argument("--github", metavar="GITHUB",
                                 type=str, action='store',
                                 help="Query user by GitHub username")
        parser_view.add_argument("--email", metavar="EMAIL",
                                 type=str, action='store',
                                 help="Query user by email address")
        parser_view.add_argument('--inspect', action='store_true',
                                 help='See team memberships of user')

        """Parser for add command."""
        parser_add = subparsers.add_parser(
            "add", description="Add a user to rocket2's database.")
        parser_add.add_argument("-f", "--force", action="store_true",
                                help="Set to store user even if already "
                                     "added to database.")

        """Parser for delete command."""
        parser_delete = subparsers.add_parser(
            "delete", description="(Admin only) permanently delete"
                                  " member's profile.")
        parser_delete.add_argument("username", metavar="USERNAME",
                                   type=str, action='store',
                                   help="Slack id of member to delete.")

        """Parser for edit command."""
        parser_edit = subparsers.add_parser(
            "edit", description="Edit properties of your Launch Pad "
                                "profile (surround arguments containing "
                                "spaces with quotes)")
        parser_edit.add_argument("--name", type=str, action='store',
                                 help="Add to change your name.")
        parser_edit.add_argument("--email", type=str, action='store',
                                 help="Add to change your email.")
        parser_edit.add_argument("--pos", type=str, action='store',
                                 help="Add to change your position.")
        parser_edit.add_argument("--github", type=str, action='store',
                                 help="Add to change your github username.")
        parser_edit.add_argument("--major", type=str, action='store',
                                 help="Add to change your major.")
        parser_edit.add_argument("--bio", type=str, action='store',
                                 help="Add to change your biography.")
        parser_edit.add_argument("--username", type=str, action='store',
                                 help="(Admin only) Add to edit properties "
                                      "of another user.")
        parser_edit.add_argument("--permission",
                                 type=lambda x: Permissions.__getitem__(x),
                                 help="(Admin only) Add to edit permission "
                                      "level of a user.",
                                 action='store', choices=list(Permissions))
        return subparsers

    def handle(self,
               command: str,
               user_id: str) -> ResponseTuple:
        """Handle command by splitting into substrings and giving to parser."""
        logging.debug("Handling UserCommand")
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

        if args.which == "view":
            return self.view_helper(user_id, args)

        elif args.which == "add":
            return self.add_helper(user_id, args.force)

        elif args.which == "delete":
            return self.delete_helper(user_id, args.username)

        elif args.which == "edit":
            return self.edit_helper(user_id, args)

        else:
            return self.get_help(), 200

    def viewinspect_helper(self, user: User):
        """
        Return an attachment that is the membership info.

        If the user does not have a Github ID to look up, just display user
        info and say that the user doesn't have a good Github ID.

        :param someid: Slack ID/Github username of user to look up
        :return: user info and membership info if user is found, or error
                    message if we cannot find the user in question
        """
        if user.github_username:
            membership = self.facade.query_or(
                Team, [('members', user.github_id),
                       ('team_leads', user.github_id)])
            member_of = ['- ' + t.github_team_name for t in membership]
            lead_of = ['- ' + t.github_team_name for t in membership
                       if t.is_team_lead(user.github_id)]
            member_of_str = '\n'.join(sorted(member_of))
            lead_of_str = '\n'.join(sorted(lead_of))
            ret = f'''
*Membership in:*
{member_of_str}

*Leading teams:*
{lead_of_str}
'''
        else:
            ret = f'''
{self.viewinspect_noghid}
'''

        return {
            'mrkdwn_in': ['text'],
            'text': ret
        }

    def edit_helper(self,
                    user_id: str,
                    args: Namespace) -> ResponseTuple:
        """
        Edit user from database.

        If ``args.username is not None``, this function edits using
        the ID from ``args.username`` (must be an admin to do so).
        Otherwise, edits the user that called the function.

        :param user_id: Slack ID of user who is calling the command
        :param args: List of user parameters that are to be edited
        :return: error message if not admin and command edits another user,
            or the edit message if user is edited
        """
        is_admin = False
        edited_user = None
        msg = ""
        if args.username is not None:
            try:
                admin_user = self.facade.retrieve(User, user_id)
                if admin_user.permissions_level != Permissions.admin:
                    return self.permission_error, 200
                else:
                    is_admin = True
                    edited_id = args.username
                    edited_user = self.facade.retrieve(User, edited_id)
            except LookupError:
                return self.lookup_error, 200
        else:
            try:
                edited_user = self.facade.retrieve(User, user_id)
            except LookupError:
                return self.lookup_error, 200

        if args.name:
            edited_user.name = args.name
        if args.email:
            edited_user.email = escape_email(args.email)
        if args.pos:
            edited_user.position = args.pos
        if args.github:
            try:
                github_id = self.github.org_add_member(args.github)
                edited_user.github_username = args.github
                edited_user.github_id = github_id
            except GithubAPIException:
                msg = f"\nError adding user {args.github} to " \
                      f"GitHub organization"
                logging.error(msg)
        if args.major:
            edited_user.major = args.major
        if args.bio:
            edited_user.biography = args.bio
        if args.permission and is_admin:
            edited_user.permissions_level = args.permission
        elif args.permission and not is_admin:
            msg += "\nCannot change own permission: user isn't admin."
            logging.warning(f"User {user_id} tried to elevate permissions"
                            " level.")

        self.facade.store(edited_user)

        # Sync permissions only if email was updated
        if args.email:
            sync_user_email_perms(self.gcp, self.facade, edited_user)

        ret = {'attachments': [edited_user.get_attachment()]}
        if msg != "":
            # mypy doesn't like the fact that there could be different types
            # for the values of the dict ret, so we have to ignore this line
            # for now
            ret['text'] = msg  # type: ignore
        return ret, 200

    def delete_helper(self,
                      user_id: str,
                      slack_id: str) -> ResponseTuple:
        """
        Delete user from database.

        Delete user with ``slack_id`` from database if user with ``user_id``
        has admin permission level.

        **Note**: user can delete themselves.

        :param user_id: Slack ID of user who is calling the command
        :param slack_id: Slack ID of user who is being deleted
        :return: permission error message if not admin, or a successful
                 deletion message if user is deleted.
        """
        try:
            user_command = self.facade.retrieve(User, user_id)
            if user_command.permissions_level == Permissions.admin:
                self.facade.delete(User, slack_id)
                return self.delete_text + slack_id, 200
            else:
                return self.permission_error, 200
        except LookupError:
            return self.lookup_error, 200

    def view_helper(self,
                    user_id: str,
                    args: Namespace) -> ResponseTuple:
        """
        View user info from database.

        If no parameters are provided, returns information of ``user_id``. If
        ``args.username`` is provided, returns the specific user
        matching the Slack ID provided, otherwise returns all users that match
        all traits of other provided parameters (e.g. ``github`` and ``email``)

        :param user_id: Slack ID of user who is calling command
        :param args: List of user parameters defining the query
        :return: error message if user not found in database, else information
                 about the user, or users.
        """
        try:
            if args.username:
                user = self.facade.retrieve(User, args.username)
            # If no query parameters are provided, get the sender
            elif not args.github and not args.email:
                user = self.facade.retrieve(User, user_id)
            else:
                query = []
                if args.github:
                    query.append(('github', args.github))
                if args.email:
                    query.append(('email', escape_email(args.email)))

                users = self.facade.query(User, query)
                if len(users) == 0:
                    raise LookupError
                elif len(users) > 1:
                    return {
                        'text': 'Warning - multiple users found!',
                        'attachments': [u.get_attachment() for u in users]
                    }, 200
                else:
                    user = users[0]

            if args.inspect:
                return {'attachments': [
                    user.get_attachment(),
                    self.viewinspect_helper(user)
                ]}, 200
            else:
                return {'attachments': [user.get_attachment()]}, 200
        except LookupError:
            return self.lookup_error, 200

    def add_helper(self,
                   user_id: str,
                   use_force: bool) -> ResponseTuple:
        """
        Add the user to the database via user id.

        :param user_id: Slack ID of user to be added
        :param use_force: If this is set, we store the user even if they are
                          already added in the database
        :return: ``"User added!", 200`` or error message if user exists in db
        """
        # Try to look up and avoid overwriting if we are not using force
        if not use_force:
            try:
                self.facade.retrieve(User, user_id)
                return 'User already exists; to overwrite user, add `-f`', 200
            except LookupError:
                pass

        self.facade.store(User(user_id))
        return 'User added!', 200
