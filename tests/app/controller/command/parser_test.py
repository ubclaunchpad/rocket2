from app.controller.command import CommandParser
from unittest import mock, TestCase
from app.model import User


class TestParser(TestCase):
    def setUp(self):
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

    @mock.patch('logging.error')
    def test_handle_app_command(self, mock_logging_error):
        self.parser.handle_app_command('hello world', 'U061F7AUR', '')
        mock_logging_error.assert_called_with(
            'app command triggered incorrectly')

    @mock.patch('logging.error')
    def test_handle_invalid_command(self, mock_logging_error):
        self.usercmd.handle.side_effect = KeyError
        user = 'U061F7AUR'
        self.parser.handle_app_command('fake command', user, '')
        mock_logging_error.assert_called_with(
            'app command triggered incorrectly')

    @mock.patch('logging.error')
    def test_handle_user_command(self, mock_logging_error):
        self.usercmd.handle.return_value = ('', 200)
        self.parser.handle_app_command('user name', 'U061F7AUR', '')
        self.usercmd.handle.\
            assert_called_once_with("user name", "U061F7AUR")
        mock_logging_error.assert_not_called()

    @mock.patch('logging.error')
    def test_handle_mention_command(self, mock_logging_error):
        user = User('U061F7AUR')
        self.dbf.retrieve.return_value = user
        self.mentioncmd.handle.return_value = ('', 200)
        self.parser.handle_app_command('U061F7AUR ++', 'UFJ42EU67', '')
        self.mentioncmd.handle.\
            assert_called_once_with('U061F7AUR ++', 'UFJ42EU67')
        mock_logging_error.assert_not_called()

    @mock.patch('logging.error')
    def test_handle_help(self, mock_logging_error):
        self.parser.handle_app_command('help', 'UFJ42EU67', '')
        mock_logging_error.assert_not_called()
