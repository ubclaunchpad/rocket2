from app.controller.command.commands.karma import KarmaCommand
from tests.memorydb import MemoryDB
from tests.util import create_test_admin
from flask import Flask
from app.model import User
from unittest import TestCase


class KarmaCommandTest(TestCase):
    def setUp(self):
        self.app = Flask(__name__)

        self.u0 = User('U0G9QF9C6')
        self.u0.karma = KarmaCommand.karma_default_amount
        self.u1 = User('UFJ42EU67')
        self.u0.karma = KarmaCommand.karma_default_amount
        self.admin = create_test_admin('Uadmin')
        self.db = MemoryDB(users=[self.u0, self.u1, self.admin])

        self.testcommand = KarmaCommand(self.db)
        self.maxDiff = None

    def test_handle_bad_args(self):
        self.assertEqual(self.testcommand.handle('karma ggwp',
                                                 self.u0.slack_id),
                         (self.testcommand.get_help(), 200))

    def test_handle_view(self):
        self.u1.karma = 15
        cmd = f'karma view {self.u1.slack_id}'
        resp, _ = self.testcommand.handle(cmd, self.u0.slack_id)
        self.assertIn(str(self.u1.karma), resp)

    def test_handle_view_lookup_error(self):
        cmd = 'karma view ABCDE8FA9'
        self.assertTupleEqual(self.testcommand.handle(cmd, self.u0.slack_id),
                              (KarmaCommand.lookup_error, 200))

    def test_handle_reset_all_as_admin(self):
        self.u0.karma = 2019
        self.u1.karma = 2048
        with self.app.app_context():
            resp, _ = self.testcommand.handle(
                'karma reset --all', self.admin.slack_id)

        self.assertEqual(self.u0.karma, KarmaCommand.karma_default_amount)
        self.assertEqual(self.u1.karma, KarmaCommand.karma_default_amount)

    def test_handle_reset_all_not_as_admin(self):
        self.u1.karma = 20
        with self.app.app_context():
            resp, _ = self.testcommand.handle(
                'karma reset --all', self.u0.slack_id)
            self.assertEqual(KarmaCommand.permission_error, resp)

        self.assertNotEqual(self.u1.karma, KarmaCommand.karma_default_amount)

    def test_handle_set_as_admin(self):
        cmd = f'karma set {self.u0.slack_id} 10'
        self.assertNotEqual(self.u0.karma, 10)
        self.testcommand.handle(cmd, self.admin.slack_id)
        self.assertEqual(self.u0.karma, 10)

    def test_handle_set_as_non_admin(self):
        cmd = f'karma set {self.u1.slack_id} 10'
        self.assertEqual(self.testcommand.handle(cmd, self.u0.slack_id),
                         (KarmaCommand.permission_error, 200))

    def test_handle_set_lookup_error(self):
        cmd = 'karma set rando.id 10'
        self.assertEqual(self.testcommand.handle(cmd, self.admin.slack_id),
                         (KarmaCommand.lookup_error, 200))
