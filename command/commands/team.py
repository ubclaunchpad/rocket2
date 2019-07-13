"""Command parsing for team events."""
import logging
import shlex
from argparse import ArgumentParser, _SubParsersAction
from command import ResponseTuple
from command.commands.base import Command
from db.facade import DBFacade
from interface.github import GithubAPIException, GithubInterface
from model import Team, User
from command.util import check_permissions
from typing import Any, List
from flask import jsonify


class TeamCommand(Command):
    """Represent Team Command Parser."""

    command_name = "team"
    desc = "for dealing with " + command_name + "s"
    permission_error = "You do not have the sufficient " \
                       "permission level for this command!"
    lookup_error = "Lookup error: Object not found!"

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
        self.desc = "for dealing with teams"
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
        parser_view.add_argument("team_name", metavar='team-name',
                                 type=str, action='store')

        """Parser for delete command."""
        parser_delete = subparsers.add_parser("delete")
        parser_delete.set_defaults(which="delete",
                                   help="(Admin only) Permanently delete "
                                        "specified team.")
        parser_delete.add_argument("team_name", metavar='team-name',
                                   type=str, action='store')

        """Parser for create command."""
        parser_create = subparsers.add_parser("create")
        parser_create.set_defaults(which="create",
                                   help="(Admin only)"
                                        "Create a new team with the "
                                        "Github team name and provided "
                                        "optional parameters. NOTE: "
                                        "you will be added to this team.")
        parser_create.add_argument("team_name", metavar='team-name',
                                   type=str, action='store',
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
        parser_add.add_argument("team_name", metavar='team-name',
                                type=str, action='store',
                                help="Team to add the user to.")
        parser_add.add_argument("slack_id", metavar='slack-id',
                                type=str, action='store',
                                help="User to be added to team.")

        """Parser for remove command."""
        parser_remove = subparsers.add_parser("remove")
        parser_remove.set_defaults(which="remove",
                                   help="Remove a user from given team.")
        parser_remove.add_argument("team_name", metavar='team-name',
                                   type=str, action='store',
                                   help="Team to remove user from.")
        parser_remove.add_argument("slack_id", metavar='slack-id',
                                   type=str, action='store',
                                   help="User to be removed from team.")

        """Parser for edit command."""
        parser_edit = subparsers.add_parser("edit")
        parser_edit.set_defaults(which='edit',
                                 help="(Admin only)"
                                      "Edit properties of specified team.")
        parser_edit.add_argument("team_name", metavar='team-name',
                                 type=str, action='store',
                                 help="Name of team to edit.")
        parser_edit.add_argument("--name", type=str, action='store',
                                 help="Display name the team should have.")
        parser_edit.add_argument("--platform", type=str, action='store',
                                 help="Platform the team should have.")

        """Parser for lead command."""
        parser_lead = subparsers.add_parser("lead")
        parser_lead.set_defaults(which='lead',
                                 help="Edit leads of specified team.")
        parser_lead.add_argument("team_name", metavar='team-name',
                                 type=str, action='store',
                                 help="Name of team to edit.")
        parser_lead.add_argument("slack_id", metavar='slack-id',
                                 type=str, action='store',
                                 help="User to be added/removed as lead.")
        parser_lead.add_argument("--remove", action='store_true',
                                 help="Remove the user as team lead.")

        """Parser for refresh command."""
        parser_refresh = subparsers.add_parser("refresh")
        parser_refresh.set_defaults(which='refresh',
                                    help="(Admin only)"
                                         "Refresh local team database.")
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

        elif args.which == "refresh":
            return self.refresh_helper(user_id)

        else:
            return self.get_help(), 200

    def list_helper(self) -> ResponseTuple:
        """
        Return display information of all teams.

        :return: error message if lookup error or no teams,
                 otherwise return teams' information
        """
        try:
            teams = self.facade.query(Team)
            if not teams:
                return "No Teams Exist!", 200
            attachment = [team.get_basic_attachment() for
                          team in teams]
            return jsonify({'attachments': attachment}), 200
        except LookupError:
            return self.lookup_error, 200

    def view_helper(self, team_name) -> ResponseTuple:
        """
        Return display information and members of specified team.

        :param team_name: name of team being viewed
        :return: error message if team not found,
                 otherwise return team information
        """
        try:
            team = self.facade.retrieve(Team, team_name)
            return jsonify({'attachments': [team.get_attachment()]}), 200
        except LookupError:
            return self.lookup_error, 200

    def create_helper(self, param_list, user_id) -> ResponseTuple:
        """
        Create team and calls GitHub API to create the team in GitHub.

        If ``param_list[name] is not None``, will add a display name. If
        ``param_list[channel] is not None``, will add all members of channel in
        which the command was called into the team.

        :param param_list: List of parameters for creating team
        :param user_id: Slack ID of user who called command
        :return: error message if team created unsuccessfully otherwise returns
                 success message
        """
        try:
            command_user = self.facade.retrieve(User, user_id)
            if not check_permissions(command_user, None):
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

    def add_helper(self, param_list, user_id) -> ResponseTuple:
        """
        Add user to team.

        If user is not admin or team lead of specified team, the user will not
        be added and an error message is returned.

        :param param_list: List of parameters for adding user
        :param user_id: Slack ID of user who called command
        :return: error message if user added unsuccessfully or if user has
                 insufficient permission level, otherwise returns success
                 message
        """
        try:
            command_user = self.facade.retrieve(User, user_id)
            team = self.facade.retrieve(Team, param_list['team_name'])
            if not check_permissions(command_user, team):
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

    def remove_helper(self, param_list, user_id) -> ResponseTuple:
        """
        Remove specified user from a team.

        If the user is also a team lead, removes team lead status from Team. If
        user is not admin or team lead of specified team, user will not be
        removed and an error message is returned.

        :param param_list: List of parameters for removing user
        :param user_id: Slack ID of user who called command
        :return: error message if user removed unsuccessfully, if user is not
                 in team, or if user has insufficient permission level,
                 otherwise returns success message
        """
        try:
            command_user = self.facade.retrieve(User, user_id)
            team = self.facade.retrieve(Team, param_list['team_name'])
            if not check_permissions(command_user, team):
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

    def edit_helper(self, param_list, user_id) -> ResponseTuple:
        """
        Edit the properties of a specific team.

        Team leads can only edit the teams that they are a part of, but admins
        can edit any teams.

        :param param_list: List of parameters for editing team
        :param user_id: Slack ID of user who called command
        :return: error message if user has insufficient permission level or
                 team edited unsuccessfully, otherwise return success message
        """
        try:
            command_user = self.facade.retrieve(User, user_id)
            team = self.facade.retrieve(Team, param_list['team_name'])
            if not check_permissions(command_user, team):
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

    def lead_helper(self, param_list, user_id) -> ResponseTuple:
        """
        Add a user as team lead, and add them to team if not already added.

        If ``--remove`` flag is used, user is instead demoted from being a team
        lead, but not from the team.

        :param param_list: List of parameters for editing leads
        :param user_id: Slack ID of user who called command
        :return: error message if user has insufficient permission level or
                 lead demoted unsuccessfully, otherwise return success message
        """
        try:
            command_user = self.facade.retrieve(User, user_id)
            team = self.facade.retrieve(Team, param_list['team_name'])
            if not check_permissions(command_user, team):
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

    def delete_helper(self, team_name, user_id) -> ResponseTuple:
        """
        Permanently delete a team.

        :param team_name: Name of team to be deleted
        :param user_id: Slack ID of user who called command
        :return: error message if user has insufficient permission level or
                 team deleted unsuccessfully, otherwise return success message
        """
        try:
            command_user = self.facade.retrieve(User, user_id)
            team = self.facade.retrieve(Team, team_name)
            if not check_permissions(command_user, team):
                return self.permission_error, 200
            self.facade.delete(Team, team_name)
            self.gh.org_delete_team(team.github_team_id)
            return f"Team {team_name} deleted", 200
        except LookupError:
            return self.lookup_error, 200
        except GithubAPIException as e:
            logging.error("team delete unsuccessful")
            return f"Team delete was unsuccessful with " \
                   f"the following error: {e.data}", 200

    def refresh_helper(self, user_id) -> ResponseTuple:
        """
        Ensure that the local team database is the same as GitHub's.

        In the event that our local team database is outdated compared to
        the teams on GitHub, this command can be called to fix things.

        :return: error message if user has insufficient permission level
                 otherwise returns success messages with # of teams changed
        """
        num_changed = 0
        num_added = 0
        num_deleted = 0
        modified = []
        try:
            command_user = self.facade.retrieve(User, user_id)
            if not check_permissions(command_user, None):
                return self.permission_error, 200
            local_teams: List[Team] = self.facade.query(Team)
            remote_teams: List[Team] = self.gh.org_get_teams()
            local_team_dict = dict((team.github_team_id, team)
                                   for team in local_teams)
            remote_team_dict = dict((team.github_team_id, team)
                                    for team in remote_teams)

            # remove teams not in github anymore
            for local_id in local_team_dict:
                if local_id not in remote_team_dict:
                    self.gh.org_delete_team(local_id)
                    num_deleted += 1
                    modified.append(local_team_dict[local_id].get_attachment())

            # add teams to db that are in github but not in local database
            for remote_id in remote_team_dict:
                if remote_id not in local_team_dict:
                    self.facade.store(remote_team_dict[remote_id])
                    num_added += 1
                    modified.append(remote_team_dict[remote_id]
                                    .get_attachment())
                else:
                    # and finally, if a local team differs, update it
                    old_team = local_team_dict[remote_id]
                    new_team = remote_team_dict[remote_id]
                    if old_team.github_team_name != new_team.github_team_name\
                            or old_team.members != new_team.members:

                        # update the old team, to retain additional parameters
                        old_team.github_team_name = new_team.github_team_name
                        old_team.members = new_team.members
                        self.facade.store(old_team)
                        num_changed += 1
                        modified.append(old_team.get_attachment())
        except GithubAPIException as e:
            logging.error("team refresh unsuccessful due to github error")
            return "Refresh teams was unsuccessful with " \
                   f"the following error: {e.data}", 200
        except LookupError:
            logging.error("team refresh unsuccessful due to lookup error")
            return self.lookup_error, 200
        status = f"{num_changed} teams changed, " \
            f"{num_added} added, " \
            f"{num_deleted} deleted. Wonderful."
        ret = {'attachments': modified, 'text': status}
        return jsonify(ret), 200
