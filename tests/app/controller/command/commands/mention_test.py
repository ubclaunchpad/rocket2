"""Test mention command parsing."""
from app.controller.command.commands.mention import MentionCommand
from tests.memorydb import MemoryDB
from flask import Flask
from app.model import User
from unittest import mock, TestCase


class MentionCommandTest(TestCase):
    def setUp(self):
        self.app = Flask(__name__)

        self.u0 = User('UFJ42EU67')
        self.u0.name = 'steve'
        self.u1 = User('U12346456')
        self.u1.name = 'maria'
        self.db = MemoryDB(users=[self.u0, self.u1])

        self.testcommand = MentionCommand(self.db)

    def test_handle_no_input(self):
        self.assertEqual(self.testcommand.handle(f'{self.u0.slack_id}',
                                                 self.u1.slack_id),
                         ('invalid command', 200))

    def test_handle_unimplemented_fn(self):
        self.assertEqual(self.testcommand.handle(f"{self.u0.slack_id} --",
                                                 self.u1.slack_id),
                         (self.testcommand.unsupported_error, 200))

    def test_handle_add_karma_to_another_user(self):
        self.assertEqual(self.testcommand.handle(f'{self.u0.slack_id} ++',
                                                 self.u1.slack_id),
                         (f'gave 1 karma to {self.u0.name}', 200))
        self.assertEqual(self.u0.karma, 2)

    def test_handle_add_karma_to_self(self):
        self.assertEqual(self.testcommand.handle(f'{self.u0.slack_id} ++',
                                                 self.u0.slack_id),
                         ('cannot give karma to self', 200))

    def test_handle_user_not_found(self):
        self.assertEqual(self.testcommand.handle('rando.id ++',
                                                 self.u0.slack_id),
                         (self.testcommand.lookup_error, 200))
