"""Test Github class."""
from unittest.mock import MagicMock

from interface.github import GithubInterface, GithubAPIException
from github import Github, Organization, NamedUser, GithubException, Team
from unittest import mock, TestCase


class TestGithubInterface(TestCase):
    """Test case for GithubInterface class."""

    def setUp(self):
        """Set up testing environment."""
        self.mock_github = mock.MagicMock(Github)
        self.mock_org = mock.MagicMock(Organization.Organization)
        self.mock_github.get_organization.return_value = self.mock_org
        self.test_bot = GithubInterface(self.mock_github, "Launch Pad")

        # make mock team
        self.mock_team = mock.MagicMock(Team.Team)
        self.mock_github.get_team = mock.MagicMock(return_value=self.mock_team)

    def test_org_add_member(self):
        """Test GithubInterface method org_add_member."""
        mock_user: MagicMock = mock.MagicMock(NamedUser.NamedUser)
        self.mock_github.get_user.return_value = mock_user
        self.test_bot.org_add_member("user@email.com")
        self.mock_org.add_to_members.\
            assert_called_once_with(mock_user, "member")

    def test_org_add_admin(self):
        """Test GithubInterface method org_add_admin."""
        mock_user: MagicMock = mock.MagicMock(NamedUser.NamedUser)
        self.mock_github.get_user.return_value = mock_user
        self.test_bot.org_add_admin("user@email.com")
        self.mock_org.add_to_members.\
            assert_called_once_with(mock_user, "admin")

    def test_org_remove_member(self):
        """Test Github method org_remove_member."""
        mock_user: MagicMock = mock.MagicMock(NamedUser.NamedUser)
        self.mock_github.get_user.return_value = mock_user
        self.test_bot.org_remove_member("user@email.com")
        self.mock_org.remove_from_membership.assert_called_once_with(mock_user)

    def test_org_has_member(self):
        """Test GithubInterface method org_has_member."""
        mock_user: MagicMock = mock.MagicMock(NamedUser.NamedUser)
        self.mock_github.get_user.return_value = mock_user
        self.test_bot.org_has_member("user@email.com")
        self.mock_org.has_in_members.assert_called_once_with(mock_user)

    def test_setup_exception(self):
        """Test GithubInterface setup with exception raised."""
        self.mock_github.\
            get_organization.side_effect = GithubException("status", "data")
        try:
            test_bot = GithubInterface(self.mock_github, "Launch Pad")
            assert False
        except GithubAPIException as e:
            pass

    def test_org_add_member_exception(self):
        """Test GithubInterface method org_add_member with exception raised."""
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
        """Test GithubInterface method org_add_admin with exception raised."""
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
        """Test GithubInterface org_remove_member with exception raised."""
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
        """Test GithubInterface method org_has_member with exception raised."""
        self.mock_org.has_in_members.\
            side_effect = GithubException("status", "data")
        try:
            mock_user: MagicMock = mock.MagicMock(NamedUser.NamedUser)
            self.mock_github.get_user.return_value = mock_user
            self.test_bot.org_has_member("user@email.com")
            assert False
        except GithubAPIException as e:
            pass

# -------------------------------------------------------------
# --------------- Tests related to team members ---------------
# -------------------------------------------------------------

    def test_tmem_list_team_members(self):
        """Test if list_team_members returns the right team members."""
        # Question: should we expect to receive list of username strings or PyGithub's internal user object
        test_team_members_list = [mock.MagicMock(NamedUser.NamedUser)]
        self.mock_team.list_team_members = mock.MagicMock(return_value=test_team_members_list)
        self.test_bot.list_team_members('test_team_id')
        self.mock_github.get_team.assert_called_once_with('test_team_id')


    def test_tmem_get_team_member(self):
        """Test if method gets the correct member when member exists."""
        test_user = mock.MagicMock(NamedUser.NamedUser)
        test_user.name = 'member_username'

        pass

    def test_tmem_add_team_member(self):
        """Test if a user is added to a team properly."""
        pass

    def test_tmem_remove_team_member(self):
        """Test if the user removed is no longer in the team"""
        pass
