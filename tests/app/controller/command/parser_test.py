"""Test the main command parser."""
from app.controller.command import CommandParser
from app.controller.command.commands import UserCommand
from app.controller.command.commands.token import TokenCommandConfig
from datetime import datetime
from db import DBFacade
from flask import jsonify, json, Flask
from interface.slack import Bot
from interface.github import GithubInterface
from unittest import mock
from utils.slack_msg_fmt import wrap_slack_code


@mock.patch('app.controller.command.parser.logging')
def test_handle_app_command(mock_logging):
    """Test the instance of handle_app_command being called inappropriately."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_bot = mock.MagicMock(Bot)
    mock_gh = mock.MagicMock(GithubInterface)
    mock_token_config = TokenCommandConfig(datetime.utcnow(), '')
    parser = CommandParser(mock_facade, mock_bot, mock_gh, mock_token_config)
    parser.handle_app_command('hello world', 'U061F7AUR')
    expected_log_message = "app command triggered incorrectly"
    mock_logging.error.assert_called_once_with(expected_log_message)


@mock.patch('app.controller.command.parser.UserCommand')
def test_handle_invalid_command(mock_usercommand):
    """Test that invalid commands are being handled appropriately."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_bot = mock.MagicMock(Bot)
    mock_gh = mock.MagicMock(GithubInterface)
    mock_token_config = TokenCommandConfig(datetime.utcnow(), '')
    mock_usercommand.handle.side_effect = KeyError
    user = 'U061F7AUR'
    parser = CommandParser(mock_facade, mock_bot, mock_gh, mock_token_config)
    parser.handle_app_command('fake command', user)


def test_handle_help():
    """Test that a '/rocket help' brings up help."""
    app = Flask(__name__)
    mock_usercommand = mock.MagicMock(UserCommand)
    mock_usercommand.get_name.return_value = "user"
    mock_facade = mock.MagicMock(DBFacade)
    mock_bot = mock.MagicMock(Bot)
    mock_gh = mock.MagicMock(GithubInterface)
    mock_token_config = TokenCommandConfig(datetime.utcnow(), '')
    parser = CommandParser(mock_facade, mock_bot, mock_gh, mock_token_config)
    with app.app_context():
        resp, code = parser.handle_app_command("help", "U061F7AUR")
        expect = json.loads(
            jsonify({"text": "Displaying all available commands. "
                             "To read about a specific command, "
                             f"use \n"
                             f"{wrap_slack_code('/rocket [command] help')}"
                             "\n"
                             "For arguments containing spaces, "
                             "please enclose them with quotations.\n",
                     "mrkdwn": "true",
                     "attachments": [
                         {"text": "*user:* for dealing with users",
                          "mrkdwn_in": ["text"]},
                         {"text": "*team:* for dealing with teams",
                          'mrkdwn_in': ['text']},
                         {"text": "*token:* Generate a signed "
                                  "token for use with the HTTP API",
                          "mrkdwn_in": ["text"]},
                         {"text": "*karma:* for dealing with karma",
                          'mrkdwn_in': ['text']},
                         {"text": "*mention:* for dealing with mention",
                          'mrkdwn_in': ["text"]}]}).data)
        resp = json.loads(resp.data)
    assert resp == expect


@mock.patch('app.controller.command.parser.UserCommand')
def test_handle_user_command(mock_usercommand):
    """Test that UserCommand.handle is called appropriately."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_bot = mock.MagicMock(Bot)
    mock_gh = mock.MagicMock(GithubInterface)
    mock_token_config = TokenCommandConfig(datetime.utcnow(), '')
    parser = CommandParser(mock_facade, mock_bot, mock_gh, mock_token_config)
    parser.handle_app_command('user name', 'U061F7AUR')
    mock_usercommand. \
        return_value.handle. \
        assert_called_once_with("user name", "U061F7AUR")


@mock.patch('app.controller.command.parser.MentionCommand')
def test_handle_mention_command(mock_mentioncommand):
    """Test that MentionCommand was handled successfully"""
    mock_facade = mock.MagicMock(DBFacade)
    mock_bot = mock.MagicMock(Bot)
    mock_gh = mock.MagicMock(GithubInterface)
    mock_token_config = TokenCommandConfig(datetime.utcnow(), '')
    parser = CommandParser(mock_facade, mock_bot, mock_gh, mock_token_config)
    parser.handle_app_command('U061F7AUR ++', 'UFJ42EU67')
    mock_mentioncommand
    mock_mentioncommand. \
        return_value.handle. \
        assert_called_once_with('U061F7AUR ++', 'UFJ42EU67')
