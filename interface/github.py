"""Utility classes for interacting with Github API via PyGithub."""
from github import Github, GithubException


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

# ---------------------------------------------------------------
# --------------- methods related to team members ---------------
# ---------------------------------------------------------------

    def list_team_members(self, team_id):
        """Return a list of users in the team of id team_id."""
        try:
            team = self.github.get_team(team_id)
            # Question: Should we return github.PaginatedList.PaginatedList or just regular python's list
            return team.get_members()
        except GithubException as e:
            raise GithubAPIException(e.data)
        
    def get_team_member(self, member_username, team_id):
        """Return a team member with a username of member_username"""
        try:
            team = self.github.get_team(team_id)
            team_members = team.get_members()
            return next(member for member in team_members if member.name == member_username)
        except GithubException as e:
            raise GithubAPIException(e.data)
        except StopIteration as e:
            raise GithubAPIException("user {} does not exist in team {}".format(member_username, team_id))

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
