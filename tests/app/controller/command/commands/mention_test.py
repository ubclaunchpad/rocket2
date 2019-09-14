"""Test mention command parsing."""
from app.controller.command.commands.mention import MentionCommand
from db import DBFacade
from flask import Flask
from app.model import User
from unittest import mock, TestCase

user1 = 'U123456789'
user2 = 'U234567891'


class MentionCommandTest(TestCase):
    """Test cases for mentions."""

    def setUp(self):
        """Set up test environment."""
        self.app = Flask(__name__)
        self.mock_facade = mock.MagicMock(DBFacade)
        self.testcommand = MentionCommand(self.mock_facade)

    def test_handle_no_input(self):
        """Test handle command with no additional args."""
        self.assertEqual(self.testcommand.handle(f"{user2}", user1),
                         ("invalid command", 200))

    def test_handle_wrong_input(self):
        """Test handle command with unsupported function."""
        self.assertEqual(self.testcommand.handle(f"{user2} --", user1),
                         (self.testcommand.unsupported_error, 200))

    def test_handle_add_karma_to_another_user(self):
        """Test handle command with karma to another user."""
        reciever = User('U123456789')
        reciever.name = 'U123456789'
        giver = 'UFJ42EU67'
        reciever_initial_karma = reciever.karma
        self.mock_facade.retrieve.return_value = reciever
        self.assertEqual(self.testcommand.handle("U123456789 ++", giver),
                         ("gave 1 karma to U123456789", 200))
        self.mock_facade.retrieve.assert_called_once_with(User, 'U123456789')
        self.assertEqual(reciever.karma, reciever_initial_karma +
                         self.testcommand.karma_add_amount)

    def test_handle_add_karma_to_self(self):
        """Test handle command with karma to self."""
        self.mock_facade.retrieve.return_value = user1
        self.assertEqual(self.testcommand.handle(f"{user1} ++", user1),
                         ("cannot give karma to self", 200))

    def test_handle_user_not_found(self):
        """Test handle command with karma to unknown user."""
        self.mock_facade.retrieve.side_effect = LookupError
        self.assertEqual(self.testcommand.handle(f"{user2} ++", user1),
                         (self.testcommand.lookup_error, 200))
