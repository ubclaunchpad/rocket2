"""Command parsing for team events."""
import argparse
import shlex


class TeamCommand:
    """Represent Team Command Parser."""

    command_name = "team"
    help = """# Team Command Reference
    `@rocket team`
    All parameters with whitespace must be enclosed by quotation marks.
    ## Options to specify input
    * `list`
        * outputs the Github team names and display names of all teams
    * `view` GITHUB_TEAM_NAME
        * view information and members of a team
    * `help`
        * outputs options for team commands
    ## TEAM LEAD or ADMIN only
    * `create` GITHUB_TEAM_NAME [`--name` DISPLAY_NAME] [`--platform` PLATFORM]
        * create a new team with a Github team name and optional parameters
        * the user will be automatically added to the new team
    The following can only be used by a team lead in the team or an admin:
    * `edit` GITHUB_TEAM_NAME
        * [`--name` DISPLAY_NAME]
        * [`--platform` PLATFORM]
            * edit properties of specified team
    * `add` GITHUB_TEAM_NAME @Slack User
        * add the specified user to the team
    * `remove` GITHUB_TEAM_NAME @Slack User
        * remove the specified user from the team
    * `delete` GITHUB_TEAM_NAME
        * permanently delete the specified team"""

    def __init__(self):
        """Initialize team command parser."""
        self.parser = argparse.ArgumentParser(prog="team")
        self.parser.add_argument("team")
        self.init_subparsers()

    def init_subparsers(self):
        """Initialize subparsers for team command."""
        subparsers = self.parser.add_subparsers(dest="which")

        """Parser for list command."""
        parser_list = subparsers.add_parser("list")
        parser_list.set_defaults(which="list")

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

        """Parser for create command."""
        parser_create = subparsers.add_parser("create")
        parser_create.set_defaults(which="create")
        parser_create.add_argument("team_name", type=str, action='store')
        parser_create.add_argument("--name", type=str, action='store')
        parser_create.add_argument("--platform", type=str, action='store')

        """Parser for add command."""
        parser_add = subparsers.add_parser("add")
        parser_add.set_defaults(which="add")
        parser_add.add_argument("team_name", type=str, action='store')
        parser_add.add_argument("slack_id", type=str, action='store')

        """Parser for remove command."""
        parser_remove = subparsers.add_parser("remove")
        parser_remove.set_defaults(which="remove")
        parser_remove.add_argument("team_name", type=str, action='store')
        parser_remove.add_argument("slack_id", type=str, action='store')

        """Parser for edit command."""
        parser_edit = subparsers.add_parser("edit")
        parser_edit.set_defaults(which='edit')
        parser_edit.add_argument("team_name", type=str, action='store')
        parser_edit.add_argument("--name", type=str, action='store')
        parser_edit.add_argument("--platform", type=str, action='store')

    def get_name(self):
        """Return the command type."""
        return self.command_name

    def get_help(self):
        """Return command options for team events."""
        return self.help

    def handle(self, command):
        """Handle command by splitting into substrings and giving to parser."""
        command_arg = shlex.split(command)
        args = self.parser.parse_args(command_arg)
        if args.which == "list":
            # stub
            return "listing all teams"

        elif args.which == "view":
            # stub
            return "viewing " + args.team_name

        elif args.which == "help":
            # stub
            return self.get_help()

        elif args.which == "delete":
            # stub
            return args.team_name + " was deleted"

        elif args.which == "create":
            # stub
            msg = "new team: {}, ".format(args.team_name)
            if args.name is not None:
                msg += "name: {}, ".format(args.name)
            if args.platform is not None:
                msg += "platform: {}, ".format(args.platform)
            return msg

        elif args.which == "add":
            # stub
            return "added " + args.slack_id + " to " + args.team_name

        elif args.which == "remove":
            # stub
            return "removed " + args.slack_id + " from " + args.team_name

        elif args.which == "edit":
            # stub
            msg = "team edited: {}, ".format(args.team_name)
            if args.name is not None:
                msg += "name: {}, ".format(args.name)
            if args.platform is not None:
                msg += "platform: {}, ".format(args.platform)
            return msg
