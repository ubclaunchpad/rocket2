"""Command parsing for user events."""
import argparse
import logging
import shlex
from flask import jsonify
from model.permissions import Permissions
from model.user import User


class UserCommand:
    """Represent User Command Parser."""

    command_name = "user"
    help = "User Command Reference:\n\n @rocket user" \
           "\n\n Options:\n\n" \
           " edit \n --name NAME\n" \
           " --email ADDRESS\n --pos YOURPOSITION\n" \
           " --major YOURMAJOR\n --bio YOURBIO\n" \
           " 'edit properties of your Launch Pad profile\n" \
           " surround arguments with spaces with single quotes'" \
           "\n ADMIN/TEAM LEAD ONLY option: --member MEMBER_ID\n" \
           " 'edit properties of another " \
           "user's Launch Pad profile'\n\n" \
           " view MEMBER_ID\n 'view information about a user'" \
           "\n\n " \
           "help\n 'outputs options for user commands'\n\n " \
           "ADMIN ONLY\n\n delete MEMBER_ID\n" \
           " 'permanently delete member's Launch Pad profile'"
    permission_error = "You do not have the sufficient " \
                       "permission level for this command!"
    lookup_error = "User not found!"
    delete_text = "Deleted user with Slack ID: "

    def __init__(self, db_facade):
        """Initialize user command."""
        logging.info("Initializing UserCommand instance")
        self.parser = argparse.ArgumentParser(prog="user")
        self.parser.add_argument("user")
        self.init_subparsers()
        self.facade = db_facade

    def init_subparsers(self):
        """Initialize subparsers for user command."""
        subparsers = self.parser.add_subparsers(dest="which")

        """Parser for view command."""
        parser_view = subparsers.add_parser("view")
        parser_view.set_defaults(which="view")
        parser_view.add_argument("--slack_id", type=str, action='store')

        """Parser for add command."""
        # DEBUG
        parser_add = subparsers.add_parser("add")
        parser_add.set_defaults(which="add")

        """Parser for help command."""
        parser_help = subparsers.add_parser("help")
        parser_help.set_defaults(which="help")

        """Parser for delete command."""
        parser_delete = subparsers.add_parser("delete")
        parser_delete.set_defaults(which="delete")
        parser_delete.add_argument("slack_id", type=str, action='store')

        """Parser for edit command."""
        parser_edit = subparsers.add_parser("edit")
        parser_edit.set_defaults(which='edit')
        parser_edit.add_argument("--name", type=str, action='store')
        parser_edit.add_argument("--email", type=str, action='store')
        parser_edit.add_argument("--pos", type=str, action='store')
        parser_edit.add_argument("--github", type=str, action='store')
        parser_edit.add_argument("--major", type=str, action='store')
        parser_edit.add_argument("--bio", type=str, action='store')
        parser_edit.add_argument("--member", type=str, action='store')

    def get_name(self):
        """Return the command type."""
        return self.command_name

    def get_help(self):
        """Return command options for user events."""
        return self.help

    def handle(self, command, user_id):
        """Handle command by splitting into substrings and giving to parser."""
        logging.debug("Handling UserCommand")
        command_arg = shlex.split(command)
        args = None

        try:
            args = self.parser.parse_args(command_arg)
        except SystemExit:
            return self.help, 200

        if args.which is None or args.which == "help":
            return self.help, 200

        elif args.which == "view":
            return self.view_helper(user_id, args.slack_id)

        elif args.which == "add":
            # XXX: Remove in production
            return self.add_helper(user_id)

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
            }
            return self.edit_helper(user_id, param_list)

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
        edited_user = None
        if param_list["member"] is not None:
            try:
                admin_user = self.facade.retrieve_user(user_id)
                if admin_user.get_permissions_level() != Permissions.admin:
                    return self.permission_error, 200
                else:
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
            edited_user.set_github_username(param_list["github"])
        if param_list["major"]:
            edited_user.set_major(param_list["major"])
        if param_list["bio"]:
            edited_user.set_biography(param_list["bio"])

        self.facade.store_user(edited_user)
        return "User edited: " + str(edited_user), 200

    def delete_helper(self, user_id, slack_id):
        """
        Delete user from database.

        Delete user with ``slack_id`` from database if user with ``user_id``
        has admin permission level. **Note**: deleting yourself is entirely
        possible.

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

    def add_helper(self, user_id):
        """
        Add the user to the database via user id.

        :param user_id: Slack ID of user to be added
        :return: ``"User added!", 200``
        """
        self.facade.store_user(User(user_id))
        return 'User added!', 200
