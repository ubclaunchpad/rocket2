"""Test project command parsing."""
from app.controller.command.commands import ProjectCommand
from db import DBFacade
from flask import Flask
from unittest import mock, TestCase


class TestProjectCommand(TestCase):
    """Test Case for ProjectCommand class."""

    def setUp(self):
        """Set up the test case environment."""
        self.app = Flask(__name__)
        self.mock_facade = mock.MagicMock(DBFacade)
        self.testcommand = ProjectCommand(self.mock_facade)

    def test_get_help(self):
        """Test project command get_help method."""
        assert self.testcommand.get_help() == self.testcommand.help
