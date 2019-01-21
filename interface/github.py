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


class GithubAPIException(Exception):
    """Exception representing an error while calling Github API."""

    def __init__(self, data):
        """
        Initialize a new GithubAPIException.

        :param data:
        """
        self.data = data
