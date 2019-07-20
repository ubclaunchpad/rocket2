"""Test karma command parsing."""
from app.controller.command.commands.karma import KarmaCommand
from db import DBFacade
from flask import Flask
from app.model import User, Permissions
from unittest import mock, TestCase


class MentionCommandTest(TestCase):
    """Test cases for using the karma command."""

    def setUp(self):
        """Set up test environment."""
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
        resp, code = self.testcommand.handle('karma view UFJ42EU67', user_id)
        self.assertIn('15', resp)
        self.assertEqual(code, 200)
        self.mock_facade.retrieve.assert_called_once_with(User, "UFJ42EU67")

    def test_handle_view_lookup_error(self):
        """Test karma command view handle with user not in database."""
        user_id = "U0G9QF9C6"
        command = 'karma view ABCDE8FA9'
        self.mock_facade.retrieve.side_effect = LookupError
        self.assertTupleEqual(self.testcommand.handle(command, user_id),
                              (KarmaCommand.lookup_error, 200))
        self.mock_facade.retrieve.assert_called_once_with(User, "ABCDE8FA9")

    def test_handle_reset_as_admin(self):
        """Test karma command resets all users."""
        user = User("ABCDEFG2F")
        user.permissions_level = Permissions.admin
        self.mock_facade.retrieve.return_value = user
        user_a = User("MMMM1234")
        user_b = User("YYYY1234")
        user_a.karma = 2019
        user_b.karma = 2048
        self.mock_facade.query.return_value = [user_a, user_b]
        with self.app.app_context():
            resp, code = self.testcommand.handle(
                "karma reset --all", "ABCDEFG2F")
            self.assertEqual(code, 200)
        store_calls = [mock.call(user_a), mock.call(user_b)]
        self.mock_facade.query.assert_called_once_with(User, [])
        self.mock_facade.retrieve.assert_called_once_with(User, "ABCDEFG2F")
        self.mock_facade.store.assert_has_calls(store_calls)

    def test_handle_reset_not_as_admin(self):
        """Test karma command resets all users."""
        user = User("ABCDEFG2F")
        user.permissions_level = Permissions.member
        self.mock_facade.retrieve.return_value = user
        with self.app.app_context():
            resp, code = self.testcommand.handle(
                "karma reset --all", "ABCDEFG2F")
            self.assertEqual(code, 200)
            self.assertEqual(KarmaCommand.permission_error, resp)
        self.mock_facade.assert_not_called()

    def test_handle_set_as_admin(self):
        """Test setting karma as admin."""
        user = User("ABCDEFG2F")
        destuser = User("MMMM1234")
        user.permissions_level = Permissions.admin
        self.mock_facade.retrieve.side_effect = [user, destuser]
        self.testcommand.handle("karma set MMMM1234 10", "ABCDEFG2F")
        retrieve_calls = [mock.call(User, "ABCDEFG2F"),
                          mock.call(User, "MMMM1234")]
        self.mock_facade.retrieve.assert_has_calls(retrieve_calls)
        self.mock_facade.store.assert_called_once_with(destuser)

    def test_handle_set_as_non_admin(self):
        """Test setting karma as non admin."""
        user = User("ABCDEFG2F")
        destuser = User("MMMM1234")
        user.permissions_level = Permissions.member
        self.mock_facade.retrieve.side_effect = [user, destuser]
        self.assertEqual(self.testcommand.handle("karma set MMMM1234 10",
                                                 "ABCDEFG2F"),
                         (KarmaCommand.permission_error, 200))
        self.mock_facade.retrieve.assert_called_once_with(User, "ABCDEFG2F")

    def test_handle_set_lookup_error(self):
        """Test setting karma with lookup error."""
        user = User("ABCDEFG2F")
        user.permissions_level = Permissions.admin
        self.mock_facade.retrieve.side_effect = [user, LookupError]
        self.assertEqual(self.testcommand.handle("karma set MMMM1234 10",
                                                 "ABCDEFG2F"),
                         (KarmaCommand.lookup_error, 200))
        retrieve_calls = [mock.call(User, "ABCDEFG2F"),
                          mock.call(User, "MMMM1234")]
        self.mock_facade.retrieve.assert_has_calls(retrieve_calls)
        self.mock_facade.store.asser_not_called()

    def test_add_karma_to_another_person(self):
        """Test to give karma to someone else."""
        recieveuser = User("SAKURA19")
        self.mock_facade.retrieve.return_value = recieveuser
        self.testcommand.add_karma("NARUTO19", "SAKURA19")
        self.mock_facade.retrieve.assert_called_once_with(User, "SAKURA19")
        self.mock_facade.store.assert_called_with(recieveuser)

    def test_add_karma_to_self(self):
        """Testing if adding karma to yourself is possible."""
        self.assertEqual(
            self.testcommand.add_karma("NARUTO19", "NARUTO19"),
            ("cannot give karma to self", 200))
        self.mock_facade.store.assert_not_called()
        self.mock_facade.retrieve.assert_not_called()

    def test_add_karma_to_not_found_person(self):
        """Testing to add karma to person not found."""
        self.mock_facade.retrieve.side_effect = LookupError
        self.assertEqual(
            self.testcommand.add_karma("NARUTO19", "SAKURA19"),
            (KarmaCommand.lookup_error, 200)
        )
        self.mock_facade.retrieve.called_once_with(User, "SAKURA19")
        self.mock_facade.store.assert_not_called()
