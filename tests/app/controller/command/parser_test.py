"""Test the main command parser."""
from app.controller.command import CommandParser
from app.controller.command.commands.token import TokenCommandConfig
from datetime import datetime
from db import DBFacade
from interface.slack import Bot
from interface.github import GithubInterface
from unittest import mock


def test_handle_app_command():
    """Test the instance of handle_app_command being called inappropriately."""
    conf = mock.MagicMock()
    mock_facade = mock.MagicMock(DBFacade)
    mock_bot = mock.MagicMock(Bot)
    mock_gh = mock.MagicMock(GithubInterface)
    mock_token_config = TokenCommandConfig(datetime.utcnow(), '')
    parser = CommandParser(conf, mock_facade, mock_bot, mock_gh,
                           mock_token_config)
    parser.handle_app_command('hello world', 'U061F7AUR', '')


@mock.patch('app.controller.command.parser.UserCommand')
def test_handle_invalid_command(mock_usercommand):
    """Test that invalid commands are being handled appropriately."""
    conf = mock.MagicMock()
    mock_facade = mock.MagicMock(DBFacade)
    mock_bot = mock.MagicMock(Bot)
    mock_gh = mock.MagicMock(GithubInterface)
    mock_token_config = TokenCommandConfig(datetime.utcnow(), '')
    mock_usercommand.handle.side_effect = KeyError
    user = 'U061F7AUR'
    parser = CommandParser(conf, mock_facade, mock_bot, mock_gh,
                           mock_token_config)
    parser.handle_app_command('fake command', user, '')


@mock.patch('app.controller.command.parser.UserCommand')
def test_handle_user_command(mock_usercommand):
    """Test that UserCommand.handle is called appropriately."""
    conf = mock.MagicMock()
    mock_facade = mock.MagicMock(DBFacade)
    mock_bot = mock.MagicMock(Bot)
    mock_gh = mock.MagicMock(GithubInterface)
    mock_token_config = TokenCommandConfig(datetime.utcnow(), '')
    parser = CommandParser(conf, mock_facade, mock_bot, mock_gh,
                           mock_token_config)
    parser.handle_app_command('user name', 'U061F7AUR', '')
    mock_usercommand. \
        return_value.handle. \
        assert_called_once_with("user name", "U061F7AUR")


@mock.patch('app.controller.command.parser.MentionCommand')
def test_handle_mention_command(mock_mentioncommand):
    """Test that MentionCommand was handled successfully."""
    conf = mock.MagicMock()
    mock_facade = mock.MagicMock(DBFacade)
    mock_bot = mock.MagicMock(Bot)
    mock_gh = mock.MagicMock(GithubInterface)
    mock_token_config = TokenCommandConfig(datetime.utcnow(), '')
    parser = CommandParser(conf, mock_facade, mock_bot, mock_gh,
                           mock_token_config)
    parser.handle_app_command('U061F7AUR ++', 'UFJ42EU67', '')
    mock_mentioncommand
    mock_mentioncommand. \
        return_value.handle. \
        assert_called_once_with('U061F7AUR ++', 'UFJ42EU67')
