"""Command parsing for user events."""
import argparse
import logging
import shlex
from flask import jsonify
from model.permissions import Permissions
from model.user import User
from interface.github import GithubAPIException


class UserCommand:
    """Represent User Command Parser."""

    command_name = "user"
    permission_error = "You do not have the sufficient " \
                       "permission level for this command!"
    lookup_error = "User not found!"
    delete_text = "Deleted user with Slack ID: "
    desc = "for dealing with " + command_name + "s"

    def __init__(self, db_facade, github_interface):
        """Initialize user command."""
        logging.info("Initializing UserCommand instance")
        self.parser = argparse.ArgumentParser(prog="/rocket")
        self.parser.add_argument("user")
        self.subparser = self.init_subparsers()
        self.help = self.get_help()
        self.facade = db_facade
        self.github = github_interface

    def init_subparsers(self):
        """Initialize subparsers for user command."""
        subparsers = self.parser.add_subparsers(dest="which")

        """Parser for view command."""
        parser_view = subparsers. \
            add_parser("view")
        parser_view.set_defaults(which="view",
                                 help="View information about a given user.")
        parser_view. \
            add_argument("--slack_id", type=str, action='store',
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
        parser_delete.add_argument("slack_id", type=str, action='store',
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
        parser_edit.add_argument("--permission", type=lambda x: Permissions[x],
                                 help="(Admin only) Add to edit permission "
                                      "level of a user.",
                                 action='store', choices=list(Permissions))
        return subparsers

    def get_name(self):
        """Return the command type."""
        return self.command_name

    def get_help(self):
        """Return command options for user events."""
        res = "\n*" + self.command_name + " commands:*```"
        for argument in self.subparser.choices:
            name = argument.capitalize()
            res += "\n*" + name + "*\n"
            res += self.subparser.choices[argument].format_help()
        return res + "```"

    def get_desc(self):
        """Return the description of this command."""
        return self.desc

    def handle(self, command, user_id):
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

    def edit_helper(self, user_id, param_list):
        """
        Edit user from database.

        If ``param_list['member']`` is not ``None``, this function edits using
        the ID from ``param_list['member']`` (must be an admin to do so).
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
                admin_user = self.facade.retrieve_user(user_id)
                if admin_user.get_permissions_level() != Permissions.admin:
                    return self.permission_error, 200
                else:
                    is_admin = True
                    edited_id = param_list["member"]
                    edited_user = self.facade.retrieve_user(edited_id)
            except LookupError:
                return self.lookup_error, 200
        else:
            try:
                edited_user = self.facade.retrieve_user(user_id)
            except LookupError:
                return self.lookup_error, 200

        if param_list["name"]:
            edited_user.set_name(param_list["name"])
        if param_list["email"]:
            edited_user.set_email(param_list["email"])
        if param_list["pos"]:
            edited_user.set_position(param_list["pos"])
        if param_list["github"]:
            try:
                self.github.org_add_member(param_list["github"])
                edited_user.set_github_username(param_list["github"])
            except GithubAPIException as e:
                msg = "\nError adding user {} to GitHub organization".format(
                    param_list['github'])
                logging.error(msg)
        if param_list["major"]:
            edited_user.set_major(param_list["major"])
        if param_list["bio"]:
            edited_user.set_biography(param_list["bio"])
        if param_list["permission"] and is_admin:
            edited_user.set_permissions_level(param_list["permission"])
        elif param_list["permission"] and not is_admin:
            msg += "\nCannot change own permission: user isn't admin."
            logging.warn("User {} tried to elevate permissions level."
                         .format(user_id))

        self.facade.store_user(edited_user)
        return "User edited: " + str(edited_user) + msg, 200

    def delete_helper(self, user_id, slack_id):
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
            user_command = self.facade.retrieve_user(user_id)
            if user_command.get_permissions_level() == Permissions.admin:
                self.facade.delete_user(slack_id)
                return self.delete_text + slack_id, 200
            else:
                return self.permission_error, 200
        except LookupError:
            return self.lookup_error, 200

    def view_helper(self, user_id, slack_id):
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
                user = self.facade.retrieve_user(user_id)
            else:
                user = self.facade.retrieve_user(slack_id)

            return jsonify({'attachments': [user.get_attachment()]}), 200
        except LookupError:
            return self.lookup_error, 200

    def add_helper(self, user_id, use_force):
        """
        Add the user to the database via user id.

        :param user_id: Slack ID of user to be added
        :param use_force: If this is set, we store the user even if they are
                          already added in the database
        :return: ``"User added!", 200``
        """
        # Try to look up and avoid overwriting if we are not using force
        if not use_force:
            try:
                self.facade.retrieve_user(user_id)
                return 'User already exists; to overwrite user, add `-f`', 200
            except LookupError:
                pass

        self.facade.store_user(User(user_id))
        return 'User added!', 200
