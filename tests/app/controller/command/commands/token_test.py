import jwt

from app.controller.command.commands import TokenCommand
from app.controller.command.commands.token import TokenCommandConfig
from datetime import timedelta
from tests.memorydb import MemoryDB
from tests.util import create_test_admin
from app.model import User, Permissions
from unittest import TestCase


def extract_jwt(msg):
    '''Hacky way to get returned token out when testing TokenCommand.'''
    parts = msg.split('```')
    return parts[1].strip()


class TestTokenCommand(TestCase):
    def setUp(self):
        self.u = User('U12345')
        self.admin = create_test_admin('Uadmin')
        self.db = MemoryDB(users=[self.u, self.admin])

        self.testcommand = TokenCommand(
            self.db,
            TokenCommandConfig(timedelta(days=7), 'secret')
        )

    def test_handle_nonexistent_member(self):
        ret_val, ret_code = self.testcommand.handle('', 'nonexistent')
        self.assertEqual(ret_val, TokenCommand.lookup_error)
        self.assertEqual(ret_code, 200)

    def test_handle_member_request(self):
        ret_val, ret_code = self.testcommand.handle('', self.u.slack_id)
        self.assertEqual(ret_val, TokenCommand.permission_error)
        self.assertEqual(ret_code, 200)

    def test_handle_non_member_request(self):
        ret_msg, ret_code = self.testcommand.handle('', self.admin.slack_id)
        token = extract_jwt(ret_msg)
        decoded = jwt.decode(token, 'secret', algorithms='HS256')
        self.assertEqual(decoded['user_id'], self.admin.slack_id)
        self.assertEqual(decoded['permissions'], Permissions.admin.value)
        self.assertEqual(ret_code, 200)
