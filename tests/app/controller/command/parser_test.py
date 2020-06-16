"""Test the main command parser."""
from app.controller.command import CommandParser
from unittest import mock, TestCase
from app.model import User


class TestParser(TestCase):
    """Test command parser functions."""

    def setUp(self):
        """Set up mocks and variables."""
        self.conf = mock.Mock()
        self.dbf = mock.Mock()
        self.gh = mock.Mock()
        self.token_conf = mock.Mock()
        self.bot = mock.Mock()
        self.parser = CommandParser(self.conf, self.dbf, self.bot, self.gh,
                                    self.token_conf)
        self.usercmd = mock.Mock()
        self.mentioncmd = mock.Mock()
        self.mentioncmd.get_help.return_value = ('', 200)
        self.parser.commands['mention'] = self.mentioncmd
        self.parser.commands['user'] = self.usercmd
        self.parser.get_help = mock.Mock()
        self.parser.get_help.return_value = ('', 200)

    def test_handle_app_command(self):
        """Test handle_app_command being called inappropriately."""
        self.parser.handle_app_command('hello world', 'U061F7AUR', '')

    def test_handle_invalid_command(self):
        """Test that invalid commands are being handled appropriately."""
        self.usercmd.handle.side_effect = KeyError
        user = 'U061F7AUR'
        self.parser.handle_app_command('fake command', user, '')

    def test_handle_user_command(self):
        """Test that UserCommand.handle is called appropriately."""
        self.usercmd.handle.return_value = ('', 200)
        self.parser.handle_app_command('user name', 'U061F7AUR', '')
        self.usercmd.handle.\
            assert_called_once_with("user name", "U061F7AUR")

    def test_handle_mention_command(self):
        """Test that MentionCommand was handled successfully."""
        user = User('U061F7AUR')
        self.dbf.retrieve.return_value = user
        self.mentioncmd.handle.return_value = ('', 200)
        self.parser.handle_app_command('U061F7AUR ++', 'UFJ42EU67', '')
        self.mentioncmd.handle.\
            assert_called_once_with('U061F7AUR ++', 'UFJ42EU67')
