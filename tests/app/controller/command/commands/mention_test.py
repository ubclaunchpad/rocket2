"""Test mention command parsing."""
from app.controller.command.commands.mention import MentionCommand
from db import DBFacade
from flask import jsonify, json, Flask
from interface.github import GithubInterface, GithubAPIException
from app.model import User, Permissions
from unittest import mock, TestCase

user = 'U123456789'
user2 = 'U234567891'

class MentionCommandTeset(TestCase):
    def setUp(self):
        """Set up test environment"""
        self.app = Flask(__name__)
        self.mock_facade = mock.MagicMock(DBFacade)
        self.testcommand = MentionCommand(self.mock_facade)
    
    def test_handle_no_input(self):
        """Test handle command
           with no additional args"""
        self.assertEqual(self.testcommand.handle('UFJ42EU67', user),
                         (self.testcommand.help, 200))
    
    def test_handle_help(self):
        """Test handle command help"""
        self.assertEqual(self.testcommand.handle(('help'), user),
                        (self.testcommand.help, 200))

    def test_handle_add_karma_to_another_user(self):
        """Test handle command
           with kudos to another user"""
        user = User('U123456789')
        user.name = 'U123456789'
        self.mock_facade.retrieve.return_value = user
        self.assertEqual(self.testcommand.handle(('UFJ42EU67 ++'), user),
                         ("gave 1 karma to U123456789", 200))
    
    def test_handle_add_karma_to_self(self):
        """Test handle command
           with kudos to self"""
        self.assertEqual(self.testcommand.handle(("U123456789 ++"), user),
                         ("cannot give karma to self", 200))

    def test_handle_user_not_found(self):
        """Test handle command
           with kudos to unknown user"""
        self.mock_facade.retrieve.side_effect = LookupError
        self.assertEqual(self.testcommand.handle(f"{user2} ++", user),
                         (self.testcommand.lookup_error, 200))
