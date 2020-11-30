from app.controller.command import CommandParser
from unittest import mock, TestCase
from app.model import User
from interface.cloudwatch_metrics import CWMetrics


class TestParser(TestCase):
    def setUp(self):
        self.conf = mock.Mock()
        self.dbf = mock.Mock()
        self.gh = mock.Mock()
        self.token_conf = mock.Mock()
        self.bot = mock.Mock()
        self.metrics = mock.Mock(spec=CWMetrics)
        self.parser = CommandParser(self.conf, self.dbf, self.bot, self.gh,
                                    self.token_conf, self.metrics)
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

    def test_handle_single_cmd_iquit(self):
        self.parser.handle_app_command('i-quit', 'UFJ43EU67', '')
        self.metrics.submit_cmd_mstime.assert_called_once_with(
            'i-quit', mock.ANY)

    def test_handle_single_cmd_iquit_with_dash(self):
        self.parser.handle_app_command('i-quit --help', 'UFJ43EU67', '')
        self.metrics.submit_cmd_mstime.assert_called_once_with(
            'i-quit', mock.ANY)

    @mock.patch('requests.post')
    def test_handle_make_post_req(self, post):
        self.parser.handle_app_command('i-quit', 'UFJ43EU67',
                                       'https://google.com')
        post.assert_called_once_with(url='https://google.com', json=mock.ANY)
