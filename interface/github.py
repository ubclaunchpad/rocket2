"""Utility classes for interacting with Github API via PyGithub."""
from github import GithubObject, GithubException


class GithubInterface:
    """Utility class for interacting with Github API."""

    def __init__(self, github, org):
        """Initialize bot by creating Github object and get organization."""
        try:
            self.github = github
            self.org = self.github.get_organization(org)
        except GithubException as e:
            raise GithubAPIException(e.data)

    def org_add_member(self, username):
        """Add/update to member with given username to organization."""
        try:
            user = self.github.get_user(username)
            self.org.add_to_members(user, "member")
        except GithubException as e:
            raise GithubAPIException(e.data)

    def org_add_admin(self, username):
        """Add member with given username as admin to organization."""
        try:
            user = self.github.get_user(username)
            self.org.add_to_members(user, "admin")
        except GithubException as e:
            raise GithubAPIException(e.data)

    def org_remove_member(self, username):
        """Remove member with given username from organization."""
        try:
            user = self.github.get_user(username)
            self.org.remove_from_membership(user)
        except GithubException as e:
            raise GithubAPIException(e.data)

    def org_has_member(self, username):
        """Return true if user with username is member of organization."""
        try:
            user = self.github.get_user(username)
            return self.org.has_in_members(user)
        except GithubException as e:
            raise GithubAPIException(e.data)

    def org_get_team(self, id):
        """Given Github team ID, return team from organization."""
        try:
            team = self.org.get_team(id)
            return team
        except GithubException as e:
            raise GithubAPIException(e.data)

    def org_create_team(self, name):
        """
        Create team with given name and add to organization.

        :param name: name of team
        :return: Github team ID
        """
        try:
            team = self.org.\
                create_team(name, GithubObject.NotSet, "closed", "push")
            return team.id
        except GithubException as e:
            raise GithubAPIException(e.data)

    def org_delete_team(self, id):
        """Get team with given ID and delete it from organization."""
        try:
            team = self.org_get_team(id)
            team.delete()
        except GithubException as e:
            raise GithubAPIException(e.data)

    def org_edit_team(self, key, name, description=None):
        """
        Get team with given ID and edit name and description.

        :param key: team's Github ID
        :param name: new team name
        :param description: new team description
        :return: None
        """
        try:
            team = self.org_get_team(key)
            if description is not None:
                team.edit(name, description)
            else:
                team.edit(name)
        except GithubException as e:
            raise GithubAPIException(e.data)

    def org_get_teams(self):
        """Return array of teams associated with organization."""
        try:
            teams = self.org.get_teams()
            team_array = []
            for team in teams:
                # convert PaginatedList to List
                team_array.append(team)
            return team_array
        except GithubException as e:
            raise GithubAPIException(e.data)

# ---------------------------------------------------------------
# --------------- methods related to team members ---------------
# ---------------------------------------------------------------

    def list_team_members(self, team_id):
        """Return a list of users in the team of id team_id."""
        try:
            team = self.github.get_team(team_id)
            return map(lambda x: x, team.get_members())
        except GithubException as e:
            raise GithubAPIException(e.data)

    def get_team_member(self, member_username, team_id):
        """Return a team member with a username of member_username."""
        try:
            team = self.github.get_team(team_id)
            team_members = map(lambda x: x, team.get_members())
            return next(
                member for member in team_members
                if member.name == member_username)
        except GithubException as e:
            raise GithubAPIException(e.data)
        except StopIteration as e:
            raise GithubAPIException(
                "user \"{}\" does not exist in team \"{}\""
                .format(member_username, team_id))

    def add_team_member(self, username, team_id):
        """Add user with given username to team with id team_id."""
        try:
            team = self.github.get_team(team_id)
            new_member = self.github.get_user(username)
            team.add_membership(new_member)
        except GithubAPIException as e:
            raise GithubAPIException(e.data)

    def remove_team_member(self, username, team_id):
        """Remove user with given username from team with id team_id."""
        try:
            team = self.github.get_team(team_id)
            to_be_removed_member = self.github.get_user(username)
            team.remove_membership(to_be_removed_member)
        except GithubAPIException as e:
            raise GithubAPIException(e.data)


class GithubAPIException(Exception):
    """Exception representing an error while calling Github API."""

    def __init__(self, data):
        """
        Initialize a new GithubAPIException.

        :param data:
        """
        self.data = data
