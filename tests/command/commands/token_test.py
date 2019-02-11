"""Test token command parsing."""
from command.commands.token import TokenCommand
from unittest import mock, TestCase
from db.facade import DBFacade
from model.permissions import Permissions
from model.user import User


class TestTokenCommand(TestCase):
    """Test case for TokenCommand class."""

    def setUp(self):
        """Set up the test case environment."""
        self.mock_facade = mock.MagicMock(DBFacade)
        self.testcommand = TokenCommand(self.mock_facade)
        self.admin_user = User("U13542")
        self.admin_user.set_permissions_level(Permissions.member)

    def test_get_command_name(self):
        """Test get_name()."""
        assert self.testcommand.get_name() == "token"

    def test_get_command_desc(self):
        """Test get_desc()."""
        assert self.testcommand.get_desc() == "Generate a signed token " \
                                              "for use with the HTTP API"

    def test_handle_nonexistent_member(self):
        """Test handle() when given a nonexistent member."""
        self.mock_facade.retrieve_user.side_effect = LookupError
        ret_val, ret_code = self.testcommand.handle("", "nonexistent")
        assert ret_val == "Requesting user not found!"
        assert ret_code == 404

    def test_handle_member(self):
        """Test handle() when given a user with member permissions."""
        user = User("U12345")
        user.set_permissions_level(Permissions.member)
        self.mock_facade.retrieve_user.return_value = user
        ret_val, ret_code = self.testcommand.handle("", user.get_slack_id())
        assert ret_val == "You do not have the sufficient " \
                          "permission level for this command!"
        assert ret_code == 403

    def test_handle_team_lead(self):
        """Test handle() when given a user with team lead permissions."""
        user = User("U12345")
        user.set_permissions_level(Permissions.team_lead)
        ret_val, ret_code = \
            self.testcommand.handle("", user.get_slack_id())
        assert ret_val != "You do not have the sufficient " \
                          "permission level for this command!"
        assert ret_code == 200
