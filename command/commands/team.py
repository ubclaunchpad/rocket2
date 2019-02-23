"""Command parsing for team events."""
import argparse
import logging
import shlex
from interface.github import GithubAPIException
from model.team import Team


class TeamCommand:
    """Represent Team Command Parser."""

    command_name = "team"
    desc = "for dealing with " + command_name + "s"
    permission_error = "Insufficient permission level to run command!"

    def __init__(self, db_facade, gh, sc):
        """
        Initialize team command parser.

        :param db_facade: Given Dynamo_DB Facade
        :param gh: Given Github Interface
        :param sc: GIven Slack Client Interface
        """
        logging.info("Initializing TeamCommand instance")
        self.facade = db_facade
        self.gh = gh
        self.sc = sc
        self.desc = ""
        self.parser = argparse.ArgumentParser(prog="/rocket")
        self.parser.add_argument("team")
        self.subparser = self.init_subparsers()
        self.help = self.get_help()

    def init_subparsers(self):
        """Initialize subparsers for team command."""
        subparsers = self.parser.add_subparsers(dest="which")

        """Parser for list command."""
        parser_list = subparsers.add_parser("list")
        parser_list.set_defaults(which="list",
                                 help="Outputs the Github team names "
                                      "and displays names of all teams.")

        """Parser for view command."""
        parser_view = subparsers.add_parser("view")
        parser_view.set_defaults(which="view",
                                 help="View information and members of "
                                      "a team.")
        parser_view.add_argument("team_name", type=str, action='store')

        """Parser for delete command."""
        parser_delete = subparsers.add_parser("delete")
        parser_delete.set_defaults(which="delete",
                                   help="(Admin only) Permanently delete "
                                        "specified team.")
        parser_delete.add_argument("team_name", type=str, action='store')

        """Parser for create command."""
        parser_create = subparsers.add_parser("create")
        parser_create.set_defaults(which="create",
                                   help="(Admin only)"
                                        "Create a new team with the "
                                        "Github team name and provided "
                                        "optional parameters. NOTE: "
                                        "you will be added to this team.")
        parser_create.add_argument("team_name", type=str, action='store',
                                   help="Github name of your team (required).")
        parser_create.add_argument("--name", type=str, action='store',
                                   help="Display name of your team.")
        parser_create.add_argument("--platform", type=str, action='store',
                                   help="The team's main platform.")
        parser_create.add_argument('--channel', type=str, action='store',
                                   help="Add all members of this channel "
                                        "to the created team.")

        """Parser for add command."""
        parser_add = subparsers.add_parser("add")
        parser_add.set_defaults(which="add",
                                help="Add a user to a given team.")
        parser_add.add_argument("team_name", type=str, action='store',
                                help="Team to add the user to.")
        parser_add.add_argument("slack_id", type=str, action='store',
                                help="User to be added to team.")

        """Parser for remove command."""
        parser_remove = subparsers.add_parser("remove")
        parser_remove.set_defaults(which="remove",
                                   help="Remove a user from given team.")
        parser_remove.add_argument("team_name", type=str, action='store',
                                   help="Team to remove user from.")
        parser_remove.add_argument("slack_id", type=str, action='store',
                                   help="User to be removed from team.")

        """Parser for edit command."""
        parser_edit = subparsers.add_parser("edit")
        parser_edit.set_defaults(which='edit',
                                 help="(Admin only)"
                                      "Edit properties of specified team.")
        parser_edit.add_argument("team_name", type=str, action='store',
                                 help="Name of team to edit.")
        parser_edit.add_argument("--name", type=str, action='store',
                                 help="Display name the team should have.")
        parser_edit.add_argument("--platform", type=str, action='store',
                                 help="Platform the team should have.")
        return subparsers

    def get_name(self):
        """Return the command type."""
        return self.command_name

    def get_desc(self):
        """Return the description of this command."""
        return self.desc

    def get_help(self):
        """Return command options for team events."""
        res = "\n*" + self.command_name + " commands:*```"
        for argument in self.subparser.choices:
            name = argument.capitalize()
            res += "\n*" + name + "*\n"
            res += self.subparser.choices[argument].format_help()
        return res + "```"

    def handle(self, command, user_id):
        """Handle command by splitting into substrings and giving to parser."""
        logging.debug("Handling TeamCommand")
        command_arg = shlex.split(command)
        args = None

        try:
            args = self.parser.parse_args(command_arg)
        except SystemExit:
            return self.get_help(), 200

        if args.which == "list":
            # stub
            return "listing all teams", 200

        elif args.which == "view":
            # stub
            return "viewing " + args.team_name, 200

        elif args.which == "delete":
            # stub
            return args.team_name + " was deleted", 200

        elif args.which == "create":
            param_list = {
                "team_name": args.team_name,
                "name": args.name,
                "platform": args.platform,
                "channel": args.channel
            }
            return self.create_helper(param_list)

        elif args.which == "add":
            # stub
            return "added " + args.slack_id + " to " + args.team_name, 200

        elif args.which == "remove":
            # stub
            return "removed " + args.slack_id + " from " + args.team_name, 200

        elif args.which == "edit":
            # stub
            msg = "team edited: {}, ".format(args.team_name)
            if args.name is not None:
                msg += "name: {}, ".format(args.name)
            if args.platform is not None:
                msg += "platform: {}, ".format(args.platform)
            return msg, 200

        else:
            return self.get_help(), 200

    def create_helper(self, param_list):
        """
        Creates Team and calls GitHub API to create in GitHub.

        If ``param_list[name]`` is not ``None``, will
        add a display name. If ``param_list[channel] is not
        ``None``, will add all members of channel in which the
        command was called into the team.
        :param param_list: List of parameters for creating team
        :return: returns error message if team created unsuccessfully
                    otherwise returns success message
        """
        try:
            msg = "new team: {}, ".format(param_list["team_name"])
            team_id = self.gh.org_create_team()
            team = Team(team_id, param_list["team_name"], "")
            if param_list["name"] is not None:
                msg += "name: {}, ".format(param_list["name"])
                team.display_name = param_list["name"]
            if param_list["platform"] is not None:
                msg += "platform: {}, ".format(param_list["platform"])
                team.platform = param_list["platform"]
            if param_list["channel"] is not None:
                msg += "add channel"
                # stub: cannot finish until teamMember PR is pushed
            self.facade.store_team(team)
            return msg, 200
        except GithubAPIException as e:
            logging.error("team created unsuccessfully")
            return "Team created unsuccessfully with the following error" + e.data
