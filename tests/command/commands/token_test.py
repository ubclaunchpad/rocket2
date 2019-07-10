"""Test token command parsing."""
import jwt

from command.commands.token import TokenCommand, TokenCommandConfig
from datetime import timedelta
from db import DBFacade
from app.model import User, Permissions
from unittest import mock, TestCase


class TestTokenCommand(TestCase):
    """Test case for TokenCommand class."""

    def setUp(self):
        """Set up the test case environment."""
        self.mock_facade = mock.MagicMock(DBFacade)
        self.testcommand = TokenCommand(self.mock_facade,
                                        TokenCommandConfig(timedelta(days=7),
                                                           "secret"))

    def test_get_command_name(self):
        """Test get_name()."""
        assert self.testcommand.command_name == "token"

    def test_get_command_desc(self):
        """Test get_desc()."""
        assert self.testcommand.desc == "Generate a signed token " \
                                        "for use with the HTTP API"

    def test_handle_nonexistent_member(self):
        """Test handle() when given a nonexistent member."""
        self.mock_facade.retrieve.side_effect = LookupError
        ret_val, ret_code = self.testcommand.handle("", "nonexistent")
        assert ret_val == "Requesting user not found!"
        assert ret_code == 200

    def test_handle_member(self):
        """Test handle() when given a user with member permissions."""
        user = User("U12345")
        user.permissions_level = Permissions.member
        self.mock_facade.retrieve.return_value = user
        ret_val, ret_code = self.testcommand.handle("", user.slack_id)
        assert ret_val == "You do not have the sufficient " \
                          "permission level for this command!"
        assert ret_code == 200

    def test_handle_team_lead(self):
        """Test handle() when given a user with team lead permissions."""
        user = User("U12345")
        user.permissions_level = Permissions.team_lead
        self.mock_facade.retrieve.return_value = user
        ret_msg, ret_code = \
            self.testcommand.handle("", user.slack_id)
        token = self.__parse_token(ret_msg)
        decoded = jwt.decode(token,
                             "secret",
                             algorithms='HS256')
        assert decoded['user_id'] == user.slack_id
        assert decoded['permissions'] == Permissions.team_lead.value
        assert ret_code == 200

    def test_handle_admin(self):
        """Test handle() when given a user with admin permissions."""
        user = User("U12345")
        user.permissions_level = Permissions.admin
        self.mock_facade.retrieve.return_value = user
        ret_msg, ret_code = \
            self.testcommand.handle("", user.slack_id)
        token = self.__parse_token(ret_msg)
        decoded = jwt.decode(token,
                             "secret",
                             algorithms='HS256')
        assert decoded['user_id'] == user.slack_id
        assert decoded['permissions'] == Permissions.admin.value
        assert ret_code == 200

    def __parse_token(self, msg):
        """Hacky way to get returned token out when testing TokenCommand."""
        parts = msg.split("```")
        return parts[1].strip()
