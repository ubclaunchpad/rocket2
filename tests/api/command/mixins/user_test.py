"""Test the common business logic for the user command APIs."""
from api.command import CommandApis
from db import DBFacade
from interface.github import GithubInterface, GithubAPIException
from interface.slack import Bot
from app.model import User, Permissions
from unittest import mock, TestCase


class TestUserCommandApis(TestCase):
    """Test Case for UserCommandApi methods."""

    def setUp(self) -> None:
        """Set up the test case environment."""
        self.mock_facade = mock.MagicMock(DBFacade)
        self.mock_github = mock.MagicMock(GithubInterface)
        self.mock_slack = mock.MagicMock(Bot)
        self.testapi = CommandApis(self.mock_facade,
                                   self.mock_github,
                                   self.mock_slack)

        self.test_user_id = "USERID"
        self.test_user = User(self.test_user_id)

    def test_edit_missing_calling_user(self) -> None:
        """Test edit user command API with missing calling user."""
        self.mock_facade.retrieve.side_effect = LookupError
        try:
            self.testapi.user_edit(self.test_user_id)
        except LookupError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_edit_no_user_properties(self) -> None:
        """Test edit user command API while editing no properties."""
        self.mock_facade.retrieve.return_value = self.test_user
        self.testapi.user_edit(self.test_user_id)
        edited_user = User(self.test_user_id)
        self.mock_facade.store.assert_called_with(edited_user)

    def test_edit_user_name(self) -> None:
        """Test edit user command API to edit user's name."""
        self.mock_facade.retrieve.return_value = self.test_user
        self.testapi.user_edit(self.test_user_id, name="rocketeer")
        edited_user = User(self.test_user_id)
        edited_user.name = "rocketeer"
        self.mock_facade.store.assert_called_once_with(edited_user)

    def test_edit_user_email(self) -> None:
        """Test edit user command API to edit user's email."""
        self.mock_facade.retrieve.return_value = self.test_user
        self.testapi.user_edit(
            self.test_user_id,
            email="<mailto:test@rocket.com|test@rocket.com>")
        edited_user = User(self.test_user_id)
        edited_user.email = "test@rocket.com"
        self.mock_facade.store.assert_called_once_with(edited_user)

    def test_edit_user_github(self) -> None:
        """Test edit user command API to edit user's github."""
        self.mock_facade.retrieve.return_value = self.test_user
        self.mock_github.org_add_member.return_value = "GITHUBID"
        self.testapi.user_edit(self.test_user_id, github="GITHUBUSERNAME")
        edited_user = User(self.test_user_id)
        edited_user.github_username = "GITHUBUSERNAME"
        edited_user.github_id = "GITHUBID"
        self.mock_facade.store.assert_called_once_with(edited_user)

    def test_edit_user_github_with_exception(self) -> None:
        """Test edit user command API to edit user's github with exception."""
        self.mock_facade.retrieve.return_value = self.test_user
        self.mock_github.org_add_member.side_effect = GithubAPIException(None)
        try:
            self.testapi.user_edit(self.test_user_id, github="GITHUBUSERNAME")
        except GithubAPIException:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_edit_user_position(self) -> None:
        """Test edit user command API to edit user's position."""
        self.mock_facade.retrieve.return_value = self.test_user
        self.testapi.user_edit(self.test_user_id, pos="dev")
        edited_user = User(self.test_user_id)
        edited_user.position = "dev"
        self.mock_facade.store.assert_called_once_with(edited_user)

    def test_edit_user_major(self) -> None:
        """Test edit user command API to edit user's major."""
        self.mock_facade.retrieve.return_value = self.test_user
        self.testapi.user_edit(self.test_user_id, major="cpen")
        edited_user = User(self.test_user_id)
        edited_user.major = "cpen"
        self.mock_facade.store.assert_called_once_with(edited_user)

    def test_edit_user_biography(self) -> None:
        """Test edit user command API to edit user's biography."""
        self.mock_facade.retrieve.return_value = self.test_user
        self.testapi.user_edit(self.test_user_id, bio="I'm testing")
        edited_user = User(self.test_user_id)
        edited_user.biography = "I'm testing"
        self.mock_facade.store.assert_called_once_with(edited_user)

    def test_edit_user_permission(self) -> None:
        """Test edit user command API to edit user's permissions."""
        self.test_user.permissions_level = Permissions.admin
        self.mock_facade.retrieve.return_value = self.test_user
        self.testapi.user_edit(self.test_user_id,
                               permission=Permissions.team_lead)
        edited_user = User(self.test_user_id)
        edited_user.permissions_level = Permissions.team_lead
        self.mock_facade.store.assert_called_once_with(edited_user)

    def test_edit_user_permission_insufficient_perm(self) -> None:
        """Test edit user command API to edit user's perms w/o permission."""
        self.mock_facade.retrieve.return_value = self.test_user
        try:
            self.testapi.user_edit(self.test_user_id,
                                   permission=Permissions.team_lead)
        except PermissionError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_edit_other_user(self) -> None:
        """Test edit user command API to edit other user."""
        self.test_user.permissions_level = Permissions.admin
        test_other_id = "OTHERID"
        other_user = User(test_other_id)

        def mock_facade_retrieve_side_effect(*args, **kwargs) -> User:
            """Mock the behavior of the retrieve mock facade function."""
            user_id = args[1]
            if user_id == self.test_user_id:
                return self.test_user
            elif user_id == test_other_id:
                return other_user
            else:
                raise RuntimeError

        self.mock_facade.retrieve.side_effect \
            = mock_facade_retrieve_side_effect
        self.testapi.user_edit(self.test_user_id,
                               member=test_other_id,
                               name="rocketeer")
        edited_user = User(test_other_id)
        edited_user.name = "rocketeer"
        self.mock_facade.store.assert_called_once_with(edited_user)

    def test_edit_other_missing_user(self) -> None:
        """Test edit user command API to edit a missing other user."""
        self.test_user.permissions_level = Permissions.admin
        test_other_id = "OTHERID"

        def mock_facade_retrieve_side_effect(*args, **kwargs) -> User:
            """Mock the behavior of the retrieve mock facade function."""
            user_id = args[1]
            if user_id == self.test_user_id:
                return self.test_user
            elif user_id == test_other_id:
                raise LookupError
            else:
                raise RuntimeError

        self.mock_facade.retrieve.side_effect \
            = mock_facade_retrieve_side_effect
        try:
            self.testapi.user_edit(self.test_user_id,
                                   member=test_other_id,
                                   name="rocketeer")
        except LookupError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_edit_other_user_insufficient_perm(self) -> None:
        """Test edit user command API to edit other user w/o permisssion."""
        test_other_id = "OTHERID"
        other_user = User(test_other_id)

        def mock_facade_retrieve_side_effect(*args, **kwargs) -> User:
            """Mock the behavior of the retrieve mock facade function."""
            user_id = args[1]
            if user_id == self.test_user_id:
                return self.test_user
            elif user_id == test_other_id:
                return other_user
            else:
                raise RuntimeError

        self.mock_facade.retrieve.side_effect \
            = mock_facade_retrieve_side_effect
        try:
            self.testapi.user_edit(self.test_user_id,
                                   member=test_other_id,
                                   name="rocketeer")
        except PermissionError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_delete_existing_user(self) -> None:
        """Test delete user command API with existing user."""
        self.test_user.permissions_level = Permissions.admin
        self.mock_facade.retrieve.return_value = self.test_user
        self.testapi.user_delete(self.test_user_id, self.test_user_id)
        self.mock_facade.delete.assert_called_once_with(User,
                                                        self.test_user_id)

    def test_delete_missing_calling_user(self) -> None:
        """Test delete user command API with missing calling user."""
        self.mock_facade.retrieve.side_effect = LookupError
        try:
            self.testapi.user_delete(self.test_user_id, self.test_user_id)
        except LookupError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_delete_insufficient_perm_user(self) -> None:
        """Test delete user command API with insufficient permissions."""
        self.test_user.permissions_level = Permissions.member
        self.mock_facade.retrieve.return_value = self.test_user
        try:
            self.testapi.user_delete(self.test_user_id, self.test_user_id)
        except PermissionError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_view_existing_user(self) -> None:
        """Test view user command API with existing user."""
        self.mock_facade.retrieve.return_value = self.test_user
        viewed_user = self.testapi.user_view(self.test_user_id)
        self.assertEqual(viewed_user, self.test_user)

    def test_view_non_existant_user(self) -> None:
        """Test view user command API with non-existant user."""
        self.mock_facade.retrieve.side_effect = LookupError
        try:
            self.testapi.user_view(self.test_user_id)
        except LookupError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_add_new_user(self) -> None:
        """Test add user command API with new user."""
        self.mock_facade.retrieve.side_effect = LookupError
        try:
            self.testapi.user_add(self.test_user_id)
        except RuntimeError:
            self.assertTrue(False)
        self.mock_facade.store.assert_called_once_with(self.test_user)

    def test_add_existing_user(self) -> None:
        """Test add user command API with existing user."""
        try:
            self.testapi.user_add(self.test_user_id)
        except RuntimeError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_force_add_user(self) -> None:
        """Test add user command API with force."""
        self.testapi.user_add(self.test_user_id, use_force=True)
        self.mock_facade.retrieve.side_effect = LookupError
        self.testapi.user_add(self.test_user_id, use_force=True)
        self.assertEqual(self.mock_facade.store.call_count, 2)
