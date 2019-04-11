"""Command parsing for user events."""
import logging
import shlex

from argparse import ArgumentParser, _SubParsersAction
from command import ResponseTuple
from db.facade import DBFacade
from flask import jsonify
from interface.github import GithubAPIException, GithubInterface
from model import User, Permissions
from typing import Dict, cast


class UserCommand:
    """Represent User Command Parser."""

    command_name = "user"
    permission_error = "You do not have the sufficient " \
                       "permission level for this command!"
    lookup_error = "Lookup error! User not found!"
    delete_text = "Deleted user with Slack ID: "
    desc = f"for dealing with {command_name}s"

    def __init__(self,
                 db_facade: DBFacade,
                 github_interface: GithubInterface) -> None:
        """Initialize user command."""
        logging.info("Initializing UserCommand instance")
        self.parser = ArgumentParser(prog="/rocket")
        self.parser.add_argument("user")
        self.subparser = self.init_subparsers()
        self.help = self.get_help()
        self.facade = db_facade
        self.github = github_interface

    def init_subparsers(self) -> _SubParsersAction:
        """Initialize subparsers for user command."""
        subparsers = self.parser.add_subparsers(dest="which")

        """Parser for view command."""
        parser_view = subparsers. \
            add_parser("view")
        parser_view.set_defaults(which="view",
                                 help="View information about a given user.")
        parser_view. \
            add_argument("--slack-id", metavar="SLACK-ID",
                         type=str, action='store',
                         help="Use if using slack id instead of username.")

        """Parser for add command."""
        parser_add = subparsers.add_parser("add")
        parser_add.set_defaults(which="add",
                                help="Add a user to rocket2's database.")
        parser_add.add_argument("-f", "--force", action="store_true",
                                help="Set to store user even if already "
                                     "added to database.")

        """Parser for delete command."""
        parser_delete = subparsers.add_parser("delete")
        parser_delete.set_defaults(which="delete",
                                   help="(Admin only) permanently delete "
                                        "member's profile.")
        parser_delete.add_argument("slack_id", metavar="slack-id",
                                   type=str, action='store',
                                   help="Slack id of member to delete.")

        """Parser for edit command."""
        parser_edit = subparsers. \
            add_parser("edit",
                       help="Edit properties of your Launch Pad "
                            "profile (surround arguments containing "
                            "spaces with quotes)")
        parser_edit.set_defaults(which='edit')
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
        parser_edit.add_argument("--member", type=str, action='store',
                                 help="(Admin only) Add to edit properties "
                                      "of another user.")
        parser_edit.add_argument("--permission",
                                 type=lambda x: Permissions.__getitem__(x),
                                 help="(Admin only) Add to edit permission "
                                      "level of a user.",
                                 action='store', choices=list(Permissions))
        return subparsers

    def get_name(self) -> str:
        """Return the command type."""
        return self.command_name

    def get_help(self) -> str:
        """Return command options for user events."""
        res = f"\n*{self.command_name} commands:*```"
        for argument in self.subparser.choices:
            name = argument.capitalize()
            res += f"\n*{name}*\n"
            res += self.subparser.choices[argument].format_help()
        return res + "```"

    def get_desc(self) -> str:
        """Return the description of this command."""
        return self.desc

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
            return self.get_help(), 200

        if args.which == "view":
            return self.view_helper(user_id, args.slack_id)

        elif args.which == "add":
            # XXX: Remove in production
            return self.add_helper(user_id, args.force)

        elif args.which == "delete":
            return self.delete_helper(user_id, args.slack_id)

        elif args.which == "edit":
            param_list = {
                "member": args.member,
                "name": args.name,
                "email": args.email,
                "pos": args.pos,
                "github": args.github,
                "major": args.major,
                "bio": args.bio,
                "permission": args.permission,
            }
            return self.edit_helper(user_id, param_list)

        else:
            return self.get_help(), 200

    def edit_helper(self,
                    user_id: str,
                    param_list: Dict[str, str]) -> ResponseTuple:
        """
        Edit user from database.

        If ``param_list['member'] is not None``, this function edits using the
        ID from ``param_list['member']`` (must be an admin to do so).
        Otherwise, edits the user that called the function.

        :param user_id: Slack ID of user who is calling the command
        :param param_list: List of user parameters that are to be edited
        :return: returns error message if not admin and command
                   edits another user, returns edit message if user is edited
        """
        is_admin = False
        edited_user = None
        msg = ""
        if param_list["member"] is not None:
            try:
                admin_user = self.facade.retrieve(User, user_id)
                if admin_user.permissions_level != Permissions.admin:
                    return self.permission_error, 200
                else:
                    is_admin = True
                    edited_id = param_list["member"]
                    edited_user = self.facade.retrieve(User, edited_id)
            except LookupError:
                return self.lookup_error, 200
        else:
            try:
                edited_user = self.facade.retrieve(User, user_id)
            except LookupError:
                return self.lookup_error, 200

        if param_list["name"]:
            edited_user.name = param_list["name"]
        if param_list["email"]:
            edited_user.email = param_list["email"]
        if param_list["pos"]:
            edited_user.position = param_list["pos"]
        if param_list["github"]:
            try:
                self.github.org_add_member(param_list["github"])
                edited_user.github_username = param_list["github"]
            except GithubAPIException:
                msg = f"\nError adding user {param_list['github']} to " \
                      "GitHub organization"
                logging.error(msg)
        if param_list["major"]:
            edited_user.major = param_list["major"]
        if param_list["bio"]:
            edited_user.biography = param_list["bio"]
        if param_list["permission"] and is_admin:
            edited_user.permissions_level = cast(Permissions,
                                                 param_list["permission"])
        elif param_list["permission"] and not is_admin:
            msg += "\nCannot change own permission: user isn't admin."
            logging.warning(f"User {user_id} tried to elevate permissions"
                            " level.")

        self.facade.store(edited_user)
        ret = {'attachments': [edited_user.get_attachment()]}
        if msg != "":
            # mypy doesn't like the fact that there could be different types
            # for the values of the dict ret, so we have to ignore this line
            # for now
            ret['text'] = msg  # type: ignore
        return jsonify(ret), 200

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
                    slack_id: str) -> ResponseTuple:
        """
        View user info from database.

        If slack_id is None, return information of ``user_id``, else return
        information of ``slack_id``.

        :param user_id: Slack ID of user who is calling command
        :param slack_id: Slack ID of user whose info is being retrieved
        :return: error message if user not found in database, else information
                 about the user
        """
        try:
            if slack_id is None:
                user = self.facade.retrieve(User, user_id)
            else:
                user = self.facade.retrieve(User, slack_id)

            return jsonify({'attachments': [user.get_attachment()]}), 200
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
