"""Test GitBot class."""
from unittest.mock import MagicMock

from interface.github import GitBot, GithubException
from github import Github, Organization, NamedUser
from unittest import mock, TestCase


class TestGitBot(TestCase):
    """Test case for GitBot class."""

    def setUp(self):
        """Set up testing environment."""
        self.mock_github = mock.MagicMock(Github)
        self.mock_org = mock.MagicMock(Organization)
        self.mock_github.get_organization.return_value = self.mock_org
        self.test_bot = GitBot(self.mock_github, "Launchpad")

    def test_org_add_member(self):
        mock_user: MagicMock = mock.MagicMock(NamedUser)
        self.mock_github.get_user = mock_user
        self.test_bot.org_add_member("user@email.com")
        self.mock_org.add_to_members.assert_called_once_with(mock_user, "member")
