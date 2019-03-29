"""Command parsing for team events."""
import logging
import shlex
from argparse import ArgumentParser, _SubParsersAction
from command import ResponseTuple
from db.facade import DBFacade
from interface.github import GithubAPIException, GithubInterface
from model import Team, User
from flask import jsonify
from command.util import check_credentials
from typing import Any, Dict, Optional


class TeamCommand:
    """Represent Team Command Parser."""

    command_name = "team"
    desc = "for dealing with " + command_name + "s"
    permission_error = "You do not have the sufficient " \
                       "permission level for this command!"
    lookup_error = "Lookup error: User not found!"

    def __init__(self,
                 db_facade: DBFacade,
                 gh: GithubInterface,
                 sc: Any) -> None:
        """
        Initialize team command parser.

        :param db_facade: Given Dynamo_DB Facade
        :param gh: Given Github Interface
        :param sc: Given Slack Client Interface
        """
        logging.info("Initializing TeamCommand instance")
        self.facade = db_facade
        self.gh = gh
        self.sc = sc
        self.desc = ""
        self.parser = ArgumentParser(prog="/rocket")
        self.parser.add_argument("team")
        self.subparser = self.init_subparsers()
        self.help = self.get_help()

    def init_subparsers(self) -> _SubParsersAction:
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
        parser_create.add_argument("--channel", type=str, action='store',
                                   help="Add all members of this channel "
                                        "to the created team.")
        parser_create.add_argument("--lead", type=str, action='store',
                                   help="Add given user as team lead"
                                        "to created team.")

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

        """Parser for lead command."""
        parser_lead = subparsers.add_parser("lead")
        parser_lead.set_defaults(which='lead',
                                 help="Edit leads of specified team.")
        parser_lead.add_argument("team_name", type=str, action='store',
                                 help="Name of team to edit.")
        parser_lead.add_argument("slack_id", type=str, action='store',
                                 help="User to be added/removed as lead.")
        parser_lead.add_argument("--remove", action='store_true',
                                 help="Remove the user as team lead.")
        return subparsers

    def get_name(self) -> str:
        """Return the command type."""
        return self.command_name

    def get_desc(self) -> str:
        """Return the description of this command."""
        return self.desc

    def get_help(self) -> str:
        """Return command options for team events."""
        res = "\n*" + self.command_name + " commands:*```"
        for argument in self.subparser.choices:
            name = argument.capitalize()
            res += "\n*" + name + "*\n"
            res += self.subparser.choices[argument].format_help()
        return res + "```"

    def handle(self,
               command: str,
               user_id: str) -> ResponseTuple:
        """Handle command by splitting into substrings and giving to parser."""
        logging.debug("Handling TeamCommand")
        command_arg = shlex.split(command)
        args = None

        try:
            args = self.parser.parse_args(command_arg)
        except SystemExit:
            return self.get_help(), 200

        if args.which == "list":
            return self.list_helper()

        elif args.which == "view":
            return self.view_helper(args.team_name)

        elif args.which == "delete":
            return self.delete_helper(args.team_name, user_id)

        elif args.which == "create":
            param_list = {
                "team_name": args.team_name,
                "name": args.name,
                "platform": args.platform,
                "channel": args.channel,
                "lead": args.lead
            }
            return self.create_helper(param_list, user_id)

        elif args.which == "add":
            param_list = {
                "team_name": args.team_name,
                "slack_id": args.slack_id
            }
            return self.add_helper(param_list, user_id)

        elif args.which == "remove":
            param_list = {
                "team_name": args.team_name,
                "slack_id": args.slack_id
            }
            return self.remove_helper(param_list, user_id)

        elif args.which == "edit":
            param_list = {
                "team_name": args.team_name,
                "name": args.name,
                "platform": args.platform
            }
            return self.edit_helper(param_list, user_id)

        elif args.which == "lead":
            param_list = {
                "team_name": args.team_name,
                "slack_id": args.slack_id,
                "remove": args.remove
            }
            return self.lead_helper(param_list, user_id)

        else:
            return self.get_help(), 200

    def list_helper(self):
        """
        Return display information of all teams.

        :return: return error message if lookup error,
                 otherwise return teams' information
        """
        try:
            return jsonify({'attachments': [team.get_basic_attachment() for
                                            team in self.facade.query(Team)]})
        except LookupError:
            return self.lookup_error, 200

    def view_helper(self, team_name):
        """
        Return display information and members of specified team.

        :param team_name: name of team being viewed
        :return: return error message if team not found,
                otherwise return team information
        """
        try:
            team = self.facade.retrieve(Team, team_name)
            return jsonify({'attachments': [team.get_attachment()]}), 200
        except LookupError:
            return self.lookup_error, 200
        
    def create_helper(self, param_list, user_id):
        """
        Create Team and calls GitHub API to create in GitHub.

        If ``param_list[name]`` is not ``None``, will
        add a display name. If ``param_list[channel] is not
        ``None``, will add all members of channel in which the
        command was called into the team.
        :param param_list: List of parameters for creating team
        :param user_id: Slack ID of user who called command
        :return: return error message if team created unsuccessfully
                 otherwise returns success message
        """
        try:
            command_user = self.facade.retrieve(User, user_id)
            if not check_credentials(command_user, None):
                return self.permission_error, 200
            msg = f"New team created: {param_list['team_name']}, "
            team_id = self.gh.org_create_team()
            team = Team(team_id, param_list['team_name'], "")
            if param_list["name"] is not None:
                msg += f"name: {param_list['name']}, "
                team.display_name = param_list['name']
            if param_list["platform"] is not None:
                msg += f"platform: {param_list['platform']}, "
                team.platform = param_list['platform']
            if param_list["channel"] is not None:
                msg += "added channel, "
                for member_id in self.sc.get_channel_users(
                        param_list["channel"]):
                    member = self.facade.retrieve(User, member_id)
                    self.gh.add_team_member(member.github_username, team_id)
                    team.add_member(member.github_id)
            else:
                self.gh.add_team_member(command_user.github_username, team_id)
                team.add_member(command_user.github_id)
            if param_list["lead"] is not None:
                msg += "added lead"
                lead_user = self.facade.retrieve(User, param_list["lead"])
                team.add_team_lead(lead_user.github_id)
                if not self.gh.has_team_member(lead_user.github_username,
                                               team_id):
                    self.gh.add_team_member(lead_user.github_username, team_id)
            else:
                team.add_team_lead(command_user.github_id)

            self.facade.store(team)
            return msg, 200
        except GithubAPIException as e:
            logging.error("team creation unsuccessful")
            return f"Team creation unsuccessful with the" \
                   f" following error: {e.data}", 200
        except LookupError:
            return self.lookup_error, 200

    def add_helper(self, param_list, user_id):
        """
        Add User to Team.

        If User with user_id is not admin or team lead of specified Team,
        User will not be added and return error message.
        :param param_list: List of parameters for adding user
        :param user_id: Slack ID of user who called command
        :return: return error message if user added unsuccessfully
                 or if user has insufficient permission level,
                 otherwise returns success message
        """
        try:
            command_user = self.facade.retrieve(User, user_id)
            team = self.facade.retrieve(Team, param_list['team_name'])
            if not check_credentials(command_user, team):
                return self.permission_error, 200

            user = self.facade.retrieve(User, param_list['slack_id'])
            team.add_member(user.github_id)
            self.gh.add_team_member(user.github_username, team.github_team_id)
            self.facade.store(team)
            msg = "Added User to " + param_list['team_name']
            ret = {'attachments': [team.get_attachment()], 'text': msg}
            return jsonify(ret), 200

        except LookupError:
            return self.lookup_error, 200
        except GithubAPIException as e:
            logging.error("user added unsuccessfully to team")
            return f"User added unsuccessfully with the " \
                   f"following error: {e.data}", 200

    def remove_helper(self, param_list, user_id):
        """
        Remove Specified User from Team.

        If User is also a team lead, removes team lead status from Team.
        If User with user_id is not admin or team lead of specified Team,
        User will not be removed and return error message.
        :param param_list: List of parameters for removing user
        :param user_id: Slack ID of user who called command
        :return: return error message if user removed unsuccessfully,
                 if user is not in team, or if user has
                 insufficient permission level, otherwise returns
                 success message
        """
        try:
            command_user = self.facade.retrieve(User, user_id)
            team = self.facade.retrieve(Team, param_list['team_name'])
            if not check_credentials(command_user, team):
                return self.permission_error, 200

            user = self.facade.retrieve(User, param_list['slack_id'])
            if not self.gh.has_team_member(user.github_username,
                                           team.github_team_id):
                return "User not in team!", 200
            team.discard_member(user.github_id)
            if team.has_team_lead(user.github_id):
                team.discard_team_lead(user.github_id)
            self.gh.remove_team_member(user.github_username,
                                       team.github_team_id)
            self.facade.store(team)
            msg = "Removed User from " + param_list['team_name']
            ret = {'attachments': [team.get_attachment()], 'text': msg}
            return jsonify(ret), 200

        except LookupError:
            return self.lookup_error, 200
        except GithubAPIException as e:
            logging.error("user removed unsuccessfully from team")
            return f"User removed unsuccessfully with " \
                   f"the following error: {e.data}", 200

    def edit_helper(self, param_list, user_id):
        """
        Edit the properties of a specific team.

        Team Leads can only edit the
        teams that they are a part of, but admins can edit any teams.
        :param param_list: List of parameters for editing team
        :param user_id: Slack ID of user who called command
        :return: return error message if user has insufficient permission level
                 or team edited unsuccessfully,
                 otherwise return success message
        """
        try:
            command_user = self.facade.retrieve(User, user_id)
            team = self.facade.retrieve(Team, param_list['team_name'])
            if not check_credentials(command_user, team):
                return self.permission_error, 200
            msg = f"Team edited: {param_list['team_name']}, "
            if param_list['name'] is not None:
                msg += f"name: {param_list['name']}, "
                team.display_name = param_list['name']
            if param_list['platform'] is not None:
                msg += f"platform: {param_list['platform']}"
                team.platform = param_list['platform']
            self.facade.store(team)
            ret = {'attachments': [team.get_attachment()], 'text': msg}
            return jsonify(ret), 200
        except LookupError:
            return self.lookup_error, 200

    def lead_helper(self, param_list, user_id):
        """
        Add a user as Team Lead, and adds them to team if not already added.

        If `--remove` flag is used, will remove user as Team Lead,
        but not from the team.
        :param param_list: List of parameters for editing leads
        :param user_id: Slack ID of user who called command
        :return: return error message if user has insufficient permission level
                 or lead demoted unsuccessfully, otherwise return
                 success message
        """
        try:
            command_user = self.facade.retrieve(User, user_id)
            team = self.facade.retrieve(Team, param_list['team_name'])
            if not check_credentials(command_user, team):
                return self.permission_error, 200
            user = self.facade.retrieve(User, param_list["slack_id"])
            msg = ""
            if param_list["remove"]:
                if not team.has_member(user.github_id):
                    return "User not in team!", 200
                if team.has_team_lead(user.github_id):
                    team.discard_team_lead(user.github_id)
                self.facade.store(team)
                msg = f"User removed as team lead from" \
                      f" {param_list['team_name']}"
            else:
                if not team.has_member(user.github_id):
                    team.add_member(user.github_id)
                    self.gh.add_team_member(user.github_username,
                                            team.github_team_id)
                team.add_team_lead(user.github_id)
                self.facade.store(team)
                msg = f"User added as team lead to" \
                      f" {param_list['team_name']}"
            ret = {'attachments': [team.get_attachment()], 'text': msg}
            return jsonify(ret), 200
        except LookupError:
                return self.lookup_error, 200
        except GithubAPIException as e:
            logging.error("team lead edit unsuccessful")
            return f"Edit team lead was unsuccessful " \
                   f"with the following error: {e.data}", 200

    def delete_helper(self, team_name, user_id):
        """
        Permanently delete a team.

        :param team_name: Name of team to be deleted
        :param user_id: Slack ID of user who called command
        :return: return error message if user has insufficient permission level
                 or team deleted unsuccessfully, otherwise return
                 success message
        """
        try:
            command_user = self.facade.retrieve(User, user_id)
            team = self.facade.retrieve(Team, team_name)
            if not check_credentials(command_user, team):
                return self.permission_error, 200
            self.facade.delete(Team, team)
            self.gh.org_delete_team(team.github_team_id)
            return f"Team {team_name} deleted", 200
        except LookupError:
                return self.lookup_error, 200
        except GithubAPIException as e:
            logging.error("team delete unsuccessful")
            return f"Team delete was unsuccessful with " \
                   f"the following error: {e.data}", 200
