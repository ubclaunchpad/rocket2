"""Test karma command parsing."""
from app.controller.command.commands.karma import KarmaCommand
from db import DBFacade
from flask import jsonify, json, Flask
from interface.github import GithubInterface, GithubAPIException
from app.model import User, Permissions
from unittest import mock, TestCase


class MentionCommandTest(TestCase):
    def setUp(self):
        """Set up test environment"""
        self.app = Flask(__name__)
        self.mock_facade = mock.MagicMock(DBFacade)
        self.testcommand = KarmaCommand(self.mock_facade)
        self.maxDiff = None

    def test_get_help(self):
        """Test karma command get_help method."""
        assert self.testcommand.get_help() == self.testcommand.help

    def test_handle_bad_args(self):
        """Test karma with invalid arguments."""
        self.assertEqual(self.testcommand.handle('karma ggwp', "U0G9QF9C6"),
                         (self.testcommand.help, 200))
    
    def test_handle_view(self):
        """Test karma command view method."""
        user_id = "U0G9QF9C6"
        user = User(user_id)
        user.karma = 15
        self.mock_facade.retrieve.return_value = user
        with self.app.app_context():
            # jsonify requires translating the byte-string
            resp, code = self.testcommand.handle('karma view UFJ42EU67', user_id)
            self.assertIn('15', resp)
            self.assertEqual(code, 200)
        self.mock_facade.retrieve.assert_called_once_with(User, "UFJ42EU67")

    def test_handle_reset(self):
        pass

    def test_handle_set(self):
        pass