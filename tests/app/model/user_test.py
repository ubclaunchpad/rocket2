"""Test the data model for a user."""
from app.model import User, Permissions
from tests.util import create_test_admin


def test_user_equality():
    """Test the User class method __eq__() and __ne__()."""
    user = User("brussel-sprouts")
    user2 = User("brussel-sprouts")
    user3 = User("brussel-trouts")
    assert user == user2
    assert user != user3


def test_valid_user():
    """Test the User static class method is_valid()."""
    user = User("")
    assert not User.is_valid(user)
    user = create_test_admin("brussel-sprouts")
    assert User.is_valid(user)


def test_print():
    """Test print user class."""
    user = User("U0G9QF9C6")
    user.biography = "bio test"
    user.email = "email@email.com"
    user.permissions_level = Permissions.admin
    assert str(user) == "{'slack_id': 'U0G9QF9C6'," \
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
