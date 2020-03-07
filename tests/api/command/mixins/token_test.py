"""Test the common business logic for the team command APIs."""
from api.command import CommandApis
from db import DBFacade
from interface.github import GithubInterface
from interface.slack import Bot
from app.model import User, Team, Permissions
from unittest import mock, TestCase
from typing import Union
from datetime import datetime, timedelta
import jwt

T = Union[User, Team]


class TestProjectCommandApis(TestCase):
    """Test Case for TokenCommandApi methods."""

    def setUp(self) -> None:
        """Set up the test case environment."""
        self.mock_facade = mock.MagicMock(DBFacade)
        self.mock_github = mock.MagicMock(GithubInterface)
        self.mock_slack = mock.MagicMock(Bot)
        self.testapi = CommandApis(self.mock_facade,
                                   self.mock_github,
                                   self.mock_slack)

        self.regular_user = User("regular")
        self.regular_user.permissions_level = Permissions.member
        self.regular_user.github_id = "reg_gh_id"
        self.regular_user.github_username = "reg_username"
        self.lead_user = User("lead")
        self.lead_user.permissions_level = Permissions.team_lead
        self.lead_user.github_id = "lead_gh_id"
        self.lead_user.github_username = "lead_username"
        self.admin_user = User("admin")
        self.admin_user.permissions_level = Permissions.admin
        self.admin_user.github_id = "admin_gh_id"
        self.admin_user.github_username = "admin_username"

        def mock_facade_retrieve_side_effect(*args, **kwargs) -> T:
            """Mock behavior of the retrieve mock facade function."""
            if args[0] == User:
                slack_id = args[1]
                if slack_id == self.regular_user.slack_id:
                    return self.regular_user
                elif slack_id == self.lead_user.slack_id:
                    return self.lead_user
                elif slack_id == self.admin_user.slack_id:
                    return self.admin_user
            raise LookupError

        self.mock_facade.retrieve.side_effect = \
            mock_facade_retrieve_side_effect

    def generate_token(self, delta, user):
        """Generate JWT Token."""
        delta = timedelta(days=3, milliseconds=4)
        expiry = datetime.utcnow() + delta
        payload = {
            'nbf': datetime.utcnow(),
            'exp': expiry,
            'iss': 'ubclaunchpad:rocket2',
            'iat': datetime.utcnow(),
            'user_id': user.slack_id,
            'permissions': user.permissions_level.value
        }
        token = jwt.encode(payload, "testing", algorithm='HS256') \
            .decode('utf-8')
        format(token)
        return token

    def test_create_token_from_admin_user(self):
        """Testing if token can be made from admin user."""
        delta = timedelta(days=3, milliseconds=4)
        exp_token = self.generate_token(delta, self.admin_user)
        token = self.testapi.handle_token_request(self.admin_user.slack_id,
                                                  delta,
                                                  "testing")
        self.assertEqual(token, exp_token)

    def test_create_token_from_lead_user(self):
        """Testing if token can be made from lead user."""
        delta = timedelta(days=3, milliseconds=4)
        exp_token = self.generate_token(delta, self.lead_user)
        token = self.testapi.handle_token_request(self.lead_user.slack_id,
                                                  delta,
                                                  "testing")
        self.assertEqual(token, exp_token)

    def test_create_token_from_reg_user(self):
        """Testing if token can be made from regular user."""
        delta = timedelta(days=3, milliseconds=4)
        token = self.testapi.handle_token_request(self.regular_user.slack_id,
                                                  delta,
                                                  "testing")
        self.assertEqual(self.testapi.token_permission_error, token)

    def test_create_token_from_nonexistent_user(self):
        """Testing if token can be made from nonexistent user."""
        delta = timedelta(days=3, milliseconds=4)
        token = self.testapi.handle_token_request("testing", delta, "testing")
        self.assertEqual(self.testapi.token_lookup_error, token)
