"""Utility classes for interacting with Github API via PyGithub."""
from github import Github, GithubObject, GithubException
from github.NamedUser import NamedUser
from github.Team import Team
from interface.exceptions.github import GithubAPIException
from interface.github_app import GithubAppInterface, \
    DefaultGithubAppAuthFactory
from app.model.team import Team as ModelTeam
from typing import cast, List
from functools import wraps


def handle_github_error(func):
    """Github error handler that updates Github App API token if necessary."""
    @wraps(func)
    def wrapper(self, *arg, **kwargs):
        try:
            return func(self, *arg, **kwargs)
        except GithubException as e:
            if e.status == 401:
                self.github = self.github_factory.create()
                try:
                    return func(self, *arg, **kwargs)
                except GithubException as e:
                    raise GithubAPIException(e.data)
            else:
                raise GithubAPIException(e.data)

    return wrapper


class DefaultGithubFactory:
    """Default factory for creating interface to Github API."""

    def __init__(self, app_id: str, private_key: str):
        """
        Init factory.

        :param app_id: Github Apps ID
        :param private_key: Private key provided by Github Apps registration
        """
        self.auth = GithubAppInterface(
            DefaultGithubAppAuthFactory(app_id, private_key))
        self.github = Github

    def create(self) -> Github:
        """Create instance of pygithub interface with Github Apps API token."""
        return self.github(self.auth.create_api_token())


class GithubInterface:
    """Utility class for interacting with Github API."""

    def __init__(self,
                 github_factory: DefaultGithubFactory,
                 org: str) -> None:
        """Initialize bot by creating Github object and get organization."""
        self.github_factory = github_factory
        self.github = github_factory.create()
        try:
            self.org = self.github.get_organization(org)
        except GithubException as e:
            raise GithubAPIException(e.data)

    @handle_github_error
    def org_add_member(self, username: str) -> str:
        """Add/update to member with given username to organization."""
        user = self.github.get_user(username)
        self.org.add_to_members(user, "member")
        return str(user.id)

    @handle_github_error
    def org_add_admin(self, username: str) -> None:
        """Add member with given username as admin to organization."""
        user = self.github.get_user(username)
        self.org.add_to_members(user, "admin")

    @handle_github_error
    def org_remove_member(self, username: str) -> None:
        """Remove member with given username from organization."""
        user = self.github.get_user(username)
        self.org.remove_from_membership(user)

    @handle_github_error
    def org_has_member(self, username: str) -> bool:
        """Return true if user with username is member of organization."""
        user = self.github.get_user(username)
        return cast(bool, self.org.has_in_members(user))

    @handle_github_error
    def org_get_team(self, id: int) -> Team:
        """Given Github team ID, return team from organization."""
        return self.org.get_team(id)

    @handle_github_error
    def org_create_team(self, name: str) -> int:
        """
        Create team with given name and add to organization.

        :param name: name of team
        :return: Github team ID
        """
        team = self.org.create_team(name,
                                    GithubObject.NotSet,
                                    "closed",
                                    "push")
        return cast(int, team.id)

    @handle_github_error
    def org_delete_team(self, id: int) -> None:
        """Get team with given ID and delete it from organization."""
        team = self.org_get_team(id)
        team.delete()

    @handle_github_error
    def org_edit_team(self,
                      key: int,
                      name: str,
                      description: str = None) -> None:
        """
        Get team with given ID and edit name and description.

        :param key: team's Github ID
        :param name: new team name
        :param description: new team description
        """
        team = self.org_get_team(key)
        if description is not None:
            team.edit(name, description)
        else:
            team.edit(name)

    @handle_github_error
    def org_get_teams(self) -> List[Team]:
        """Return array of teams associated with organization."""
        teams = self.org.get_teams()
        team_array = []
        for team in teams:
            # convert PaginatedList to List
            team_model = ModelTeam(str(team.id), team.name, "")
            team_model.members = set(str(user.id)
                                     for user in
                                     self.list_team_members(team.id))
            team_array.append(team_model)
        return team_array

    # ---------------------------------------------------------------
    # --------------- methods related to team members ---------------
    # ---------------------------------------------------------------

    @handle_github_error
    def list_team_members(self, team_id: str) -> List[NamedUser]:
        """Return a list of users in the team of id team_id."""
        team = self.github.get_team(team_id)
        return cast(List[NamedUser], list(team.get_members()))

    @handle_github_error
    def get_team_member(self, username: str, team_id: str) -> NamedUser:
        """Return a team member with a username of username."""
        try:
            team = self.github.get_team(team_id)
            team_members = team.get_members()
            return next(
                member for member in team_members
                if member.name == username)
        except StopIteration:
            raise GithubAPIException(
                f"User \"{username}\" does not exist in team \"{team_id}\"!")

    @handle_github_error
    def add_team_member(self, username: str, team_id: str) -> None:
        """Add user with given username to team with id team_id."""
        team = self.github.get_team(team_id)
        new_member = self.github.get_user(username)
        team.add_membership(new_member)

    @handle_github_error
    def has_team_member(self, username: str, team_id: str) -> bool:
        """Check if team with team_id contains user with username."""
        team = self.github.get_team(team_id)
        member = self.github.get_user(username)
        return cast(bool, team.has_in_members(member))

    @handle_github_error
    def remove_team_member(self, username: str, team_id: str) -> None:
        """Remove user with given username from team with id team_id."""
        team = self.github.get_team(team_id)
        to_be_removed_member = self.github.get_user(username)
        team.remove_membership(to_be_removed_member)
