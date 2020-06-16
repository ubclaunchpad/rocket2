"""Test the data model for a user."""
from app.model import User, Permissions
from unittest import TestCase


class TestUserModel(TestCase):
    """Test some functions in the user model."""

    def setUp(self):
        """Set up example models for use."""
        self.brussel_sprouts = User('brussel-sprouts')
        self.brussel_sprouts2 = User('brussel-sprouts')
        self.brussel_trouts = User('brussel-trouts')

        self.no_id = User('')
        self.admin = User('U0G9QF9C6')
        self.admin.biography = 'bio test'
        self.admin.email = 'email@email.com'
        self.admin.permissions_level = Permissions.admin

    def test_user_equality(self):
        """Test the User class method __eq__() and __ne__()."""
        self.assertEqual(self.brussel_sprouts, self.brussel_sprouts2)
        self.assertNotEqual(self.brussel_sprouts2, self.brussel_trouts)

    def test_valid_user(self):
        """Test the User static class method is_valid()."""
        self.assertFalse(User.is_valid(self.no_id))
        self.assertTrue(User.is_valid(self.admin))

    def test_print(self):
        """Test print user class."""
        expected = "{'slack_id': 'U0G9QF9C6'," \
            " 'name': ''," \
            " 'email': 'email@email.com'," \
            " 'github_username': ''," \
            " 'github_id': ''," \
            " 'major': ''," \
            " 'position': ''," \
            " 'biography': 'bio test'," \
            " 'image_url': ''," \
            " 'permissions_level': <Permissions.admin: 3>,"\
            " 'karma': 1}"
        self.assertEqual(str(self.admin), expected)
