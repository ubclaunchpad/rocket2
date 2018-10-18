"""Command parsing for user events."""
import argparse
import shlex


class UserCommand:
    """Represent User Command Parser."""

    __command_name = "user"
    __help = "User Command Reference:\n\n @rocket user\n\n Options:\n\n" \
             " edit \n --name NAME\n" \
             " --email ADDRESS\n --pos YOURPOSITION\n" \
             " --major YOURMAJOR\n --bio YOURBIO\n" \
             " 'edit properties of your Launch Pad profile\n" \
             " surround arguments with spaces with single quotes'" \
             "\n ADMIN/TEAM LEAD ONLY option: --member MEMBER_ID\n" \
             " 'edit properties of another user's Launch Pad profile'\n\n" \
             " view MEMBER_ID\n 'view information about a user'\n\n " \
             "help\n 'outputs options for user commands'\n\n " \
             "ADMIN ONLY\n\n delete MEMBER_ID\n" \
             " 'permanently delete member's Launch Pad profile'"

    """Top level User parser."""
    parser = argparse.ArgumentParser(prog="user")
    parser.add_argument("user")
    subparsers = parser.add_subparsers()

    """Parser for view command."""
    parser_view = subparsers.add_parser("view")
    parser_view.set_defaults(which="view")
    parser_view.add_argument("slack_id", type=str, action='store')

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
        return self.__command_name

    def get_help(self):
        """Return command options for user events."""
        return self.__help

    def handle(self, command):
        """Handle command by splitting into substrings and giving to parser."""
        command_arg = shlex.split(command)
        args = self.parser.parse_args(command_arg)
        if args.which == "view":
            # stub
            return args.slack_id

        elif args.which == "help":
            # stub
            return self.__help

        elif args.which == "delete":
            # stub
            return "deleting " + args.slack_id

        elif args.which == "edit":
            # stub
            msg = "user edited: "
            if args.member is not None:
                msg += "member: {}, ".format(args.member)
            if args.name is not None:
                msg += "name: {}, ".format(args.name)
            if args.email is not None:
                msg += "email: {}, ".format(args.email)
            if args.pos is not None:
                msg += "position: {}, ".format(args.pos)
            if args.github is not None:
                msg += "github: {}, ".format(args.github)
            if args.major is not None:
                msg += "major: {}, ".format(args.major)
            if args.bio is not None:
                msg += "bio: {}".format(args.bio)
            return msg
