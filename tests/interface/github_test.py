"""Test GitBot class."""
from unittest.mock import MagicMock

from interface.github import GitBot, GithubAPIException
from github import Github, Organization, NamedUser, GithubException
from unittest import mock, TestCase


class TestGitBot(TestCase):
    """Test case for GitBot class."""

    def setUp(self):
        """Set up testing environment."""
        self.mock_github = mock.MagicMock(Github)
        self.mock_org = mock.MagicMock(Organization.Organization)
        self.mock_github.get_organization.return_value = self.mock_org
        self.test_bot = GitBot(self.mock_github, "Launchpad")

    def test_org_add_member(self):
        """Test the GitBot method org_add_member."""
        mock_user: MagicMock = mock.MagicMock(NamedUser.NamedUser)
        self.mock_github.get_user.return_value = mock_user
        self.test_bot.org_add_member("user@email.com")
        self.mock_org.add_to_members.\
            assert_called_once_with(mock_user, "member")

    def test_org_add_admin(self):
        """Test the GitBot method org_add_admin."""
        mock_user: MagicMock = mock.MagicMock(NamedUser.NamedUser)
        self.mock_github.get_user.return_value = mock_user
        self.test_bot.org_add_admin("user@email.com")
        self.mock_org.add_to_members.\
            assert_called_once_with(mock_user, "admin")

    def test_org_remove_member(self):
        """Test the GitBot method org_remove_member."""
        mock_user: MagicMock = mock.MagicMock(NamedUser.NamedUser)
        self.mock_github.get_user.return_value = mock_user
        self.test_bot.org_remove_member("user@email.com")
        self.mock_org.remove_from_membership.assert_called_once_with(mock_user)

    def test_org_has_member(self):
        """Test the GitBot method org_has_member."""
        mock_user: MagicMock = mock.MagicMock(NamedUser.NamedUser)
        self.mock_github.get_user.return_value = mock_user
        self.test_bot.org_has_member("user@email.com")
        self.mock_org.has_in_members.assert_called_once_with(mock_user)

    def test_setup_exception(self):
        """Test the GitBot setup with exception raised."""
        self.mock_github.\
            get_organization.side_effect = GithubException("status", "data")
        try:
            test_bot = GitBot(self.mock_github, "Launchpad")
            assert False
        except GithubAPIException as e:
            pass

    def test_org_add_member_exception(self):
        """Test the GitBot method org_add_member with exception raised."""
        self.mock_org.add_to_members.\
            side_effect = GithubException("status", "data")
        try:
            mock_user: MagicMock = mock.MagicMock(NamedUser.NamedUser)
            self.mock_github.get_user.return_value = mock_user
            self.test_bot.org_add_member("user@email.com")
            assert False
        except GithubAPIException as e:
            pass

    def test_org_add_admin_exception(self):
        """Test the GitBot method org_add_admin with exception raised."""
        self.mock_org.add_to_members.\
            side_effect = GithubException("status", "data")
        try:
            mock_user: MagicMock = mock.MagicMock(NamedUser.NamedUser)
            self.mock_github.get_user.return_value = mock_user
            self.test_bot.org_add_admin("user@email.com")
            assert False
        except GithubAPIException as e:
            pass

    def test_org_remove_member_exception(self):
        """Test the GitBot method org_remove_member with exception raised."""
        self.mock_org.remove_from_membership.\
            side_effect = GithubException("status", "data")
        try:
            mock_user: MagicMock = mock.MagicMock(NamedUser.NamedUser)
            self.mock_github.get_user.return_value = mock_user
            self.test_bot.org_remove_member("user@email.com")
            assert False
        except GithubAPIException as e:
            pass

    def test_org_has_member_exception(self):
        """Test the GitBot method org_has_member with exception raised."""
        self.mock_org.has_in_members.\
            side_effect = GithubException("status", "data")
        try:
            mock_user: MagicMock = mock.MagicMock(NamedUser.NamedUser)
            self.mock_github.get_user.return_value = mock_user
            self.test_bot.org_has_member("user@email.com")
            assert False
        except GithubAPIException as e:
            pass
