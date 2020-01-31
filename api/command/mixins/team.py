"""Encapsulate the common business logic of team commands."""
import logging
from typing import List
from app.model import User, Team
from interface.github import GithubAPIException, GithubInterface
from interface.slack import SlackAPIError, Bot
from utils.slack_parse import check_permissions
import db.utils as db_utils
from db.facade import DBFacade


class TeamCommandApis:
    """Encapsulate the various APIs for team command logic."""

    def __init__(self):
        """Declare the interfaces needed."""
        self._db_facade: DBFacade = None
        self._gh_interface: GithubInterface = None
        self._slack_client: Bot = None

    def team_list(self) -> List[Team]:
        """
        Return a list of all teams.

        :return: List of ``Team`` objects representing all teams
                 in the workspace
        """
        logging.info("Team list command API called")
        teams = self._db_facade.query(Team)
        logging.info(f"{len(teams)} teams found")
        return teams

    def team_view(self, gh_team_name: str) -> Team:
        """
        View team information from the database.

        :param gh_team_name: name of the team to view
        :raises: LookupError if a team with the specified team name
                 does not exist
        :raises: RuntimeError if more than one team has the specified
                 team name
        :return: ``Team`` object if found
        """
        logging.info("Team view command API called")
        return db_utils.get_team_by_name(self._db_facade, gh_team_name)

    def team_create(self,
                    caller_id: str,
                    gh_team_name: str,
                    display_name: str = None,
                    platform: str = None,
                    channel: str = None,
                    lead_id: str = None) -> bool:
        """
        Create a team both in the Rocket database and Github organization.

        :param caller_id: Slack ID of the user who is calling the API
        :param gh_team_name: desired team name to give the team on Github
        :param display_name: display name to give the team when displayed
                             in various places
        :param platform: main platform this team's projects are based on
        :param channel: name of the Slack channel whose channel members
                        are to be added to the team - its members will be
                        added to the team in the Rocket database and added
                        to the Github team as well
        :param lead_id: Slack ID of the user who will be made the lead of
                        this team
        :raises: LookupError if the calling user or tech lead cannot be found
                 in the database
        :raises: PermissionError if the calling user has insufficient
                 permissions to create a team, or if the specified user with
                 lead_id does not have the permission to be a lead
        :raises: SlackAPIError if a channel name is provided by an error
                 is encountered retrieving the members of that channel
        :raises: GithubAPIException if an error occurs on team creation or
                 Github team member addition
        :return: True if the team creation was successful, False otherwise
        """
        logging.info("Team create command API called")
        command_user = self._db_facade.retrieve(User, caller_id)
        logging.debug(f"Calling user: {command_user.__str__()}")

        if not check_permissions(command_user, None):
            msg = f"Calling user with Slack ID {caller_id} has permission" \
                f" level {str(command_user.permissions_level)}, " \
                "insufficient for creating a team!"
            logging.error(msg)
            raise PermissionError(msg)

        gh_team_id = str(self._gh_interface.org_create_team(gh_team_name))
        logging.debug(f"Github team {gh_team_name} created with "
                      f"Github team ID {gh_team_id}")
        team = Team(gh_team_id, gh_team_name, "")

        if display_name is not None:
            logging.debug(f"Attaching display name {display_name} "
                          f"to {gh_team_name}")
            team.display_name = display_name

        if platform is not None:
            logging.debug(f"Attaching platform {platform} to {gh_team_name}")
            team.platform = platform

        if channel is not None:
            logging.debug(f"Adding channel members of #{channel} "
                          f"to {gh_team_name}")
            try:
                channel_member_ids = \
                    self._slack_client.get_channel_users(channel)
                logging.debug(f"Member IDs of members found in #{channel}: "
                              f"{channel_member_ids}")
            except SlackAPIError as e:
                msg = f"Channel member query on channel #{channel} failed: " \
                    f"{e.error}"
                logging.error(msg)
                raise SlackAPIError(msg)
            for member_id in channel_member_ids:
                try:
                    member = self._db_facade.retrieve(User, member_id)
                    self._gh_interface.add_team_member(member.github_username,
                                                       gh_team_id)
                    team.add_member(member.github_id)
                    logging.debug(f"Member with ID {member.slack_id} added "
                                  f"to {gh_team_name}")
                except LookupError:
                    logging.warning(f"Member with ID {member_id} not found, "
                                    "ignoring...")
                    pass
        else:
            self._gh_interface.add_team_member(command_user.github_username,
                                               gh_team_id)
            team.add_member(command_user.github_id)
            logging.debug(f"Calling user with ID {command_user.slack_id} "
                          f"added to {gh_team_name}")

        if lead_id is not None:
            lead = self._db_facade.retrieve(User, lead_id)

            if check_permissions(lead, None):
                lead_in_team = self._gh_interface.has_team_member(
                    lead.github_username,
                    gh_team_id)
                if not lead_in_team:
                    self._gh_interface.add_team_member(lead.github_username,
                                                       gh_team_id)

                team.add_member(lead.github_id)
                team.add_team_lead(lead.github_id)
                logging.debug(f"User with ID {lead_id} set as tech lead of "
                              f"{gh_team_name}")
            else:
                msg = f"User specified with lead ID {lead_id} has" \
                    f" permission level {str(lead.permissions_level)}, " \
                    "insufficient to lead a team!"
                logging.error(msg)
                raise PermissionError(msg)
        else:
            team.add_team_lead(command_user.github_id)
            logging.debug(f"Calling user with ID {command_user.github_id} set"
                          f" as tech lead of {gh_team_name}")

        created = self._db_facade.store(team)
        return created

    def team_add(self,
                 caller_id: str,
                 add_user_id: str,
                 gh_team_name: str) -> bool:
        """
        Add a user to a team.

        :param caller_id: Slack ID of user who called the API
        :param add_user_id: Slack ID of user to add to a team
        :param gh_team_name: Github team name of the team to add a user to
        :raises: LookupError if the calling user, user to add,
                 or specified team cannot be found in the database
        :raises: RuntimeError if more than one team has the specified
                 team name
        :raises: PermissionError if the calling user has insufficient
                 permission to add members to the specified team
        :raises: GithubAPIException if an error occurs when adding the user to
                 the Github team
        :return: True if adding the member to the team was successful,
                 False otherwise
        """
        logging.info("Team add command API called")
        command_user = self._db_facade.retrieve(User, caller_id)
        logging.debug(f"Calling user: {command_user.__str__()}")

        team = db_utils.get_team_by_name(self._db_facade, gh_team_name)

        if not check_permissions(command_user, team):
            msg = f"User with ID {caller_id} has insufficient permissions" \
                f" to add members to team {gh_team_name}"
            logging.error(msg)
            raise PermissionError(msg)

        add_user = self._db_facade.retrieve(User, add_user_id)
        logging.debug(f"User to add: {add_user.__str__()}")

        self._gh_interface.add_team_member(add_user.github_username,
                                           team.github_team_id)
        team.add_member(add_user.github_id)

        added = self._db_facade.store(team)
        return added

    def team_remove(self,
                    caller_id: str,
                    gh_team_name: str,
                    rem_user_id: str) -> bool:
        """
        Remove the specified user from a team.

        If the user is also a team lead, removes team lead status from Team.

        :param caller_id: Slack ID of user who called command
        :param gh_team_name: Github team name of the team to remove user from
        :param rem_user_id: Slack ID of user to remove from team
        :raises: LookupError if the calling user, user to remove,
                 or specified team cannot be found in the database
        :raises: RuntimeError if more than one team has the specified
                 team name
        :raises: PermissionError if the calling user has insufficient
                 permission to remove members to the specified team
        :raises: GithubAPIException if an error occured removing the user from
                 the Github team
        :return: True if user was removed from team successfully,
                 False otherwise
        """
        logging.info("Team remove command API called")
        command_user = self._db_facade.retrieve(User, caller_id)
        logging.debug(f"Calling user: {command_user.__str__()}")

        team = db_utils.get_team_by_name(self._db_facade, gh_team_name)

        if not check_permissions(command_user, team):
            msg = f"User with ID {caller_id} has insufficient permissions" \
                f" to remove members to team {gh_team_name}"
            logging.error(msg)
            raise PermissionError(msg)

        rem_user = self._db_facade.retrieve(User, rem_user_id)
        logging.debug(f"User to remove: {rem_user.__str__()}")

        if not self._gh_interface.has_team_member(rem_user.github_username,
                                                  team.github_team_id):
            msg = f"Github user {rem_user.github_username} not a member" \
                f" of Github team with ID {team.github_team_id}"
            logging.error(msg)
            raise GithubAPIException(msg)
        self._gh_interface.remove_team_member(rem_user.github_username,
                                              team.github_team_id)
        team.discard_member(rem_user.github_id)
        if team.has_team_lead(rem_user.github_id):
            team.discard_team_lead(rem_user.github_id)

        removed = self._db_facade.store(team)
        return removed

    def team_edit(self,
                  caller_id: str,
                  gh_team_name: str,
                  display_name: str = None,
                  platform: str = None) -> bool:
        """
        Edit the properties of a specific team.

        Team leads can only edit the teams that they are a part of, but admins
        can edit any team.

        :param caller_id: Slack ID of user who called command
        :param display_name: display name to change to if not None
        :param platform: platform to change to if not None
        :raises: LookupError if the calling user or team to edit
                 could not be found
        :raises: RuntimeError if more than one team has the specified
                 team name
        :raises: PermissionError if the calling user does not have sufficient
                 permissions to edit the specified team
        :return: True if the edit was successful, False otherwise
        """
        logging.info("Team edit command API called")
        command_user = self._db_facade.retrieve(User, caller_id)
        logging.debug(f"Calling user: {command_user.__str__()}")

        team = db_utils.get_team_by_name(self._db_facade, gh_team_name)

        if not check_permissions(command_user, team):
            msg = f"User with ID {caller_id} has insufficient permissions" \
                f" to edit team {gh_team_name}"
            logging.error(msg)
            raise PermissionError(msg)

        if display_name is not None:
            logging.debug(f"Attaching display name {display_name} "
                          f"to {gh_team_name}")
            team.display_name = display_name

        if platform is not None:
            logging.debug(f"Attaching platform {platform} to {gh_team_name}")
            team.platform = platform

        edited = self._db_facade.store(team)
        return edited

    def team_lead(self,
                  caller_id: str,
                  lead_id: str,
                  gh_team_name: str,
                  remove: bool = False) -> bool:
        """
        Add a user as a team lead, and add them to team if not already added.

        :param caller_id: Slack ID of user who called command
        :param lead_id: Slack ID of user to declare as team lead
        :param gh_team_name: Github team name of team to add a lead to
        :param remove: if True, removes the user as team lead of the team
        :raises: LookupError if the calling user, the team to add a lead to
                 could not be found, the user is not on the team, or the user
                 is not a lead on the team
        :raises: RuntimeError if more than one team has the specified
                 team name
        :raises: PermissionError if the calling user does not have sufficient
                 permissions to add a lead to the specified team
        :returns: True if removal was successful, False otherwise
        """
        logging.info("Team lead command API called")
        command_user = self._db_facade.retrieve(User, caller_id)
        logging.debug(f"Calling user: {command_user.__str__()}")

        team = db_utils.get_team_by_name(self._db_facade, gh_team_name)

        if not check_permissions(command_user, team):
            msg = f"User with ID {caller_id} has insufficient permissions" \
                f" to add lead to team {gh_team_name}"
            logging.error(msg)
            raise PermissionError(msg)

        lead_user = self._db_facade.retrieve(User, lead_id)
        logging.debug(f"User to add as lead: {lead_user.__str__()}")

        if remove:
            if not team.has_member(lead_user.github_id):
                msg = f"User with Github ID {lead_user.github_id} not a " \
                    "member of specified team"
                logging.error(msg)
                raise LookupError(msg)
            if team.has_team_lead(lead_user.github_id):
                team.discard_team_lead(lead_user.github_id)
                discarded = self._db_facade.store(team)
                return discarded
            else:
                msg = f"User with Github ID {lead_user.github_id} not a " \
                    "lead of specified team"
                logging.error(msg)
                raise LookupError(msg)
        else:
            if not team.has_member(lead_user.github_id):
                team.add_member(lead_user.github_id)
                self._gh_interface.add_team_member(lead_user.github_username,
                                                   team.github_team_id)
            team.add_team_lead(lead_user.github_id)
            added = self._db_facade.store(team)
            return added

    def team_delete(self,
                    caller_id: str,
                    gh_team_name: str) -> None:
        """
        Permanently delete a team.

        :param gh_team_name: Github team name of the team to delete
        :param caller_id: Slack ID of user who called command
        :raises: LookupError if the calling user or the team to delete could
                 not be found
        :raises: RuntimeError if more than one team has the specified
                 team name
        :raises: PermissionError if the calling user does not have sufficient
                 permissions to delete the specified team
        """
        logging.info("Team delete command API called")
        command_user = self._db_facade.retrieve(User, caller_id)
        logging.debug(f"Calling user: {command_user.__str__()}")

        team = db_utils.get_team_by_name(self._db_facade, gh_team_name)

        if not check_permissions(command_user, team):
            msg = f"User with ID {caller_id} has insufficient permissions" \
                f" to delete team {gh_team_name}"
            logging.error(msg)
            raise PermissionError(msg)

        self._gh_interface.org_delete_team(int(team.github_team_id))

        self._db_facade.delete(Team, team.github_team_id)
        logging.info(f"{gh_team_name} successfully deleted")

    def team_refresh(self, caller_id: str) -> bool:
        """
        Ensure that the local team database is the same as Github's.

        In the event that our local team database is outdated compared to
        the teams on Github, this command can be called to fix things.

        :param caller_id: Slack ID of the user calling the command
        :raises: LookupError if the calling user cannot be found
        :raises: PermissionError if the calling user has insufficient
                 permissions to refresh the local database
        :raises: GithubAPIException if  there was a failure in fetching
                 Github team information
        :returns: True if synchronization was successful, False otherwise
        """
        logging.info("Team refresh command API called")
        num_changed = 0
        num_added = 0
        num_deleted = 0

        command_user = self._db_facade.retrieve(User, caller_id)
        logging.debug(f"Calling user: {command_user.__str__()}")

        if not check_permissions(command_user, None):
            msg = f"User with ID {caller_id} has insufficient permissions" \
                " to refresh the local team database"
            logging.error(msg)
            raise PermissionError(msg)

        local_teams: List[Team] = self._db_facade.query(Team)
        remote_teams: List[Team] = self._gh_interface.org_get_teams()
        local_team_dict = dict((team.github_team_id, team)
                               for team in local_teams)
        remote_team_dict = dict((team.github_team_id, team)
                                for team in remote_teams)

        # remove teams not in github anymore
        for local_id in local_team_dict:
            if local_id not in remote_team_dict:
                self._db_facade.delete(Team, local_id)
                logging.debug(f"Team with Github ID {local_id} deleted")
                num_deleted += 1

        # add teams to db that are in github but not in local database
        for remote_id in remote_team_dict:
            remote_team = remote_team_dict[remote_id]
            if remote_id not in local_team_dict:
                stored = self._db_facade.store(remote_team)
                if stored:
                    logging.debug("Created new team with "
                                  f"Github ID {remote_id}")
                    num_added += 1
                else:
                    logging.error("Failed to create new team with "
                                  f"Github ID {remote_id}")
                    return False
            else:
                # and finally, if a local team differs, update it
                local_team = local_team_dict[remote_id]
                if local_team.github_team_name != \
                    remote_team.github_team_name \
                        or local_team.members != remote_team.members:
                    # update the old team, to retain additional parameters
                    local_team.github_team_name = remote_team.github_team_name
                    local_team.members = remote_team.members
                    edited = self._db_facade.store(local_team)
                    if edited:
                        logging.debug("Successfully edited team with "
                                      f"Github ID {remote_id}")
                        num_changed += 1
                    else:
                        logging.error("Failed to edit team with"
                                      f"Github ID {remote_id}")
                        return False

        logging.info(f"{num_changed} teams changed, {num_added} added, "
                     f"{num_deleted} deleted. Wonderful.")
        return True
