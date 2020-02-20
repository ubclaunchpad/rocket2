"""Test Github class."""
from unittest import TestCase
from unittest.mock import MagicMock, Mock
from github import Github, Organization, NamedUser, \
    GithubException, Team
from interface.github import GithubInterface, GithubAPIException


class TestGithubInterface(TestCase):
    """Test case for GithubInterface class."""

    def setUp(self):
        """Set up testing environment."""
        self.mock_github = MagicMock(Github)
        self.mock_factory = MagicMock()
        self.mock_factory.create.return_value = self.mock_github
        self.mock_org = MagicMock(Organization.Organization)
        self.mock_github.get_organization.return_value = self.mock_org
        self.test_interface = GithubInterface(self.mock_factory,
                                              "ubclaunchpad")

        # make mock team
        self.mock_team = MagicMock(Team.Team)

        self.mock_github.get_team = MagicMock(side_effect={
            12345: self.mock_team,
        }.get)

        self.test_user = MagicMock(NamedUser.NamedUser)
        self.test_user.name = 'member_username'
        self.mock_team.get_members = MagicMock(
            return_value=[self.test_user])

    def test_try_twice_add_admin(self):
        """Test org_add_admin() where the first try gives 401."""
        mock_user = MagicMock(NamedUser.NamedUser)
        self.mock_github.get_user.side_effect = [
            GithubException(401, ''), mock_user
        ]
        self.test_interface.org_add_admin('user@email.com')
        self.mock_org.add_to_members.\
            assert_called_once_with(mock_user, 'admin')

    def test_try_thrice_add_admin(self):
        """Test org_add_admin() where all tries give 401."""
        self.mock_github.get_user.side_effect = GithubException(401, '')
        with self.assertRaises(GithubAPIException):
            self.test_interface.org_add_admin('user@email.com')

    def test_org_add_member(self):
        """Test GithubInterface method org_add_member."""
        mock_user: MagicMock = MagicMock(NamedUser.NamedUser)
        mock_user.id = 1
        self.mock_github.get_user.return_value = mock_user
        self.mock_org.has_in_members.return_value = False
        github_id = self.test_interface.org_add_member("user@email.com")
        self.mock_org.add_to_members. \
            assert_called_once_with(mock_user, "member")
        self.assertEqual(github_id, str(mock_user.id))
        # Or maybe it has already been added before....
        # stupid coverage
        self.mock_org.has_in_members.return_value = True
        github_id = self.test_interface.org_add_member("user@email.com")

    def test_org_add_admin(self):
        """Test GithubInterface method org_add_admin."""
        mock_user: MagicMock = MagicMock(NamedUser.NamedUser)
        self.mock_github.get_user.return_value = mock_user
        self.test_interface.org_add_admin("user@email.com")
        self.mock_org.add_to_members. \
            assert_called_once_with(mock_user, "admin")

    def test_org_remove_member(self):
        """Test Github method org_remove_member."""
        mock_user: MagicMock = MagicMock(NamedUser.NamedUser)
        self.mock_github.get_user.return_value = mock_user
        self.test_interface.org_remove_member("user@email.com")
        self.mock_org.remove_from_membership.assert_called_once_with(mock_user)

    def test_org_has_member(self):
        """Test GithubInterface method org_has_member."""
        mock_user: MagicMock = MagicMock(NamedUser.NamedUser)
        self.mock_github.get_user.return_value = mock_user
        self.test_interface.org_has_member("user@email.com")
        self.mock_org.has_in_members.assert_called_once_with(mock_user)

    def test_org_get_team(self):
        """Test GithubInterface method org_get_team."""
        mock_team: MagicMock = MagicMock(Team.Team)
        self.mock_org.get_team.return_value = mock_team
        self.assertEqual(self.test_interface.org_get_team(2321313), mock_team)
        self.mock_org.get_team.assert_called_once_with(2321313)

    def test_org_create_team(self):
        """Test GithubInterface method org_create_team."""
        mock_team = Mock(id=234111)
        self.mock_org.create_team.return_value = mock_team
        self.assertEqual(
            self.test_interface.org_create_team("brussel sprouts"),
            234111)
        self.mock_org.create_team. \
            assert_called_once_with("brussel sprouts", privacy='closed')

    def test_org_delete_team(self):
        """Test GithubInterface method org_delete_team."""
        mock_team = Mock(id=234111)
        self.mock_org.get_team.return_value = mock_team
        self.test_interface.org_delete_team(234111)
        self.mock_org.get_team.assert_called_once_with(234111)
        mock_team.delete.assert_called()

    def test_org_edit_team(self):
        """Test GithubInterface method org_edit_team."""
        mock_team: MagicMock = MagicMock(Team.Team)
        self.mock_org.get_team.return_value = mock_team
        self.test_interface.org_edit_team(234111, "brussels", "web team")
        self.mock_org.get_team.assert_called_once_with(234111)
        mock_team.edit.assert_called_once_with("brussels", "web team")

    def test_org_edit_team_name_only(self):
        """Test GithubInterface method org_edit_team with name only."""
        mock_team: MagicMock = MagicMock(Team.Team)
        self.mock_org.get_team.return_value = mock_team
        self.test_interface.org_edit_team(234111, "brussels")
        self.mock_org.get_team.assert_called_once_with(234111)
        mock_team.edit.assert_called_once_with("brussels")

    def test_org_get_teams(self):
        """Test GithubInterface method org_get_teams."""
        teamo = MagicMock(Team.Team)
        teamo.id = 12
        userperson = MagicMock(NamedUser)
        userperson.id = 34
        teamo.get_members.return_value = [userperson]
        self.mock_org.get_teams.return_value = [teamo]
        self.mock_org.get_team.return_value = teamo
        teams = self.test_interface.org_get_teams()
        self.mock_org.get_teams.assert_called_once()
        self.assertEqual(len(teams), 1)

    def test_setup_exception(self):
        """Test GithubInterface setup with exception raised."""
        self.mock_github. \
            get_organization.side_effect = GithubException("status", "data")
        try:
            GithubInterface(self.mock_factory, "ubclaunchpad")
            assert False
        except GithubAPIException:
            pass

    def test_org_add_member_exception(self):
        """Test GithubInterface method org_add_member with exception raised."""
        self.mock_org.add_to_members. \
            side_effect = GithubException("status", "data")
        try:
            mock_user: MagicMock = MagicMock(NamedUser.NamedUser)
            self.mock_github.get_user.return_value = mock_user
            self.mock_org.has_in_members.return_value = False
            self.test_interface.org_add_member("user@email.com")
            assert False
        except GithubAPIException:
            pass

    def test_org_add_admin_exception(self):
        """Test GithubInterface method org_add_admin with exception raised."""
        self.mock_org.add_to_members. \
            side_effect = GithubException("status", "data")
        try:
            mock_user: MagicMock = MagicMock(NamedUser.NamedUser)
            self.mock_github.get_user.return_value = mock_user
            self.test_interface.org_add_admin("user@email.com")
            assert False
        except GithubAPIException:
            pass

    def test_org_remove_member_exception(self):
        """Test GithubInterface org_remove_member with exception raised."""
        self.mock_org.remove_from_membership. \
            side_effect = GithubException("status", "data")
        try:
            mock_user: MagicMock = MagicMock(NamedUser.NamedUser)
            self.mock_github.get_user.return_value = mock_user
            self.test_interface.org_remove_member("user@email.com")
            assert False
        except GithubAPIException:
            pass

    def test_org_has_member_exception(self):
        """Test GithubInterface method org_has_member with exception raised."""
        self.mock_org.has_in_members. \
            side_effect = GithubException("status", "data")
        try:
            mock_user: MagicMock = MagicMock(NamedUser.NamedUser)
            self.mock_github.get_user.return_value = mock_user
            self.test_interface.org_has_member("user@email.com")
            assert False
        except GithubAPIException:
            pass

    def test_org_get_team_exception(self):
        """Test GithubInterface method org_get_team with exception raised."""
        self.mock_org.get_team.side_effect = GithubException("status", "data")
        try:
            self.test_interface.org_get_team(2321313)
            assert False
        except GithubAPIException:
            pass

    def test_org_create_team_exception(self):
        """Test GithubInterface method org_create_team w/ exception raised."""
        self.mock_org.create_team. \
            side_effect = GithubException("status", "data")
        try:
            self.test_interface.org_create_team("brussel sprouts")
            assert False
        except GithubAPIException:
            pass

    def test_org_delete_team_exception(self):
        """Test GithubInterface method org_delete_team w/ exception raised."""
        try:
            mock_team = Mock(id=234111)
            self.mock_org.get_team.return_value = mock_team
            mock_team.delete. \
                side_effect = GithubException("status", "data")
            self.test_interface.org_delete_team(234111)
            assert False
        except GithubAPIException:
            pass

    def test_org_edit_team_exception(self):
        """Test GithubInterface method org_edit_team with exception raised."""
        try:
            mock_team: MagicMock = MagicMock(Team.Team)
            mock_team.edit.side_effect = GithubException("status", "data")
            self.mock_org.get_team.return_value = mock_team
            self.test_interface.org_edit_team(234111, "brussels", "web team")
            assert False
        except GithubAPIException:
            pass

    def test_org_get_teams_exception(self):
        """Test GithubInterface method org_get_teams with exception raised."""
        self.mock_org.get_teams.side_effect = GithubException("status", "data")
        try:
            self.test_interface.org_get_teams()
            assert False
        except GithubAPIException:
            pass

    # -------------------------------------------------------------
    # --------------- Tests related to team members ---------------
    # -------------------------------------------------------------

    def test_tmem_list_team_members(self):
        """Test if list_team_members returns the right team members."""
        test_team_members_list = [MagicMock(NamedUser.NamedUser)]
        self.mock_team.list_team_members = MagicMock(
            return_value=test_team_members_list
        )
        self.mock_org.get_team.return_value = self.mock_team
        self.test_interface.list_team_members('12345')
        self.mock_team.get_members.assert_called_once()

    def test_tmem_get_team_member(self):
        """Test if method gets the correct member when member exists."""
        self.mock_org.get_team.return_value = self.mock_team
        assert self.test_interface.get_team_member(
            self.test_user.name,
            '12345') is self.test_user

    def test_tmem_get_nonexistent_team_member(self):
        """Test if raises GithubException when member does not exist."""
        with self.assertRaises(GithubAPIException):
            self.test_interface.get_team_member('nonexistent_username',
                                                '12345')

    def test_tmem_add_team_member(self):
        """Test if a user is added to a team properly."""
        self.mock_github.get_user = MagicMock(return_value=self.test_user)
        self.mock_team.add_membership = MagicMock()
        self.mock_org.get_team.return_value = self.mock_team
        self.test_interface.add_team_member('member_username',
                                            '12345')
        self.mock_team.add_membership.assert_called_once_with(self.test_user)

    def test_tmem_remove_team_member(self):
        """Test if the user removed is no longer in the team."""
        self.mock_github.get_user = MagicMock(return_value=self.test_user)
        self.mock_org.get_team.return_value = self.mock_team
        self.test_interface.remove_team_member(self.test_user.name,
                                               '12345')
        self.mock_team.remove_membership. \
            assert_called_once_with(self.test_user)

    def test_tmem_has_team_member(self):
        """Test if has_team_member method."""
        self.mock_github.get_user = MagicMock(return_value=self.test_user)
        self.mock_org.get_team.return_value = self.mock_team
        self.test_interface.has_team_member('member_username',
                                            '12345')
        self.mock_team.has_in_members.assert_called_once_with(self.test_user)
