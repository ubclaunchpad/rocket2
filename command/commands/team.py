"""Command parsing for team events."""
import argparse
import shlex


class TeamCommand:
    """Represent Team Command Parser."""

    __command_name = "team"
    __help = ""

    """Top level Team parser."""
    parser = argparse.ArgumentParser(prog="team")
    parser.add_argument("team")
    subparsers = parser.add_subparsers()

    """Parser for view command."""
    parser_view = subparsers.add_parser("view")
    parser_view.set_defaults(which="view")
    parser_view.add_argument("team_name", type=str, action='store')

    """Parser for help command."""
    parser_view = subparsers.add_parser("help")
    parser_view.set_defaults(which="help")

    """Parser for delete command."""
    parser_delete = subparsers.add_parser("delete")
    parser_delete.set_defaults(which="delete")
    parser_delete.add_argument("team_name", type=str, action='store')

    """Parser for add command."""
    parser_delete = subparsers.add_parser("add")
    parser_delete.set_defaults(which="add")
    parser_delete.add_argument("team_name", type=str, action='store')
    parser_delete.add_argument("display_name", type=str, action='store')

    def get_name(self):
        """Return the command type."""
        return self.__command_name

    def get_help(self):
        """Return command options for team events."""
        return self.__help

    def handle(self, command):
        """Handle command by splitting into substrings and giving to parser."""
        command_arg = shlex.split(command)
        args = self.parser.parse_args(command_arg)
        if args.which == "view":
            # stub
            return "viewing " + args.team_name

        elif args.which == "help":
            # stub
            return self.get_help()

        elif args.which == "delete":
            # stub
            return args.team_name + " was deleted"

        elif args.which == "add":
            # stub
            return "new team " + args.display_name + ", id " + args.team_name
