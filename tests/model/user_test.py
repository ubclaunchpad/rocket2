"""Test the data model for a user."""
from model.permissions import Permissions
from model.user import User
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


def test_get_slack_id():
    """Test the User class method get_slack_id()."""
    user = User("U0G9QF9C6")
    assert user.slack_id == "U0G9QF9C6"


def test_get_name():
    """Test the User class method get_name()."""
    user = User("U0G9QF9C6")
    assert user.name == ""


def test_set_name():
    """Test the User class method set_name()."""
    user = User("U0G9QF9C6")
    user.name = "Russell"
    assert user.name == "Russell"


def test_get_email():
    """Test the User class method get_email()."""
    user = User("U0G9QF9C6")
    assert user.email == ""


def test_set_email():
    """Test the User class method set_email()."""
    user = User("U0G9QF9C6")
    user.email = "email@example.com"
    assert user.email == "email@example.com"


def test_get_github_username():
    """Test the User class method get_github_username()."""
    user = User("U0G9QF9C6")
    assert user.github_username == ""


def test_set_github_username():
    """Test the User class method set_github_username()."""
    user = User("U0G9QF9C6")
    user.github_username = "username"
    assert user.github_username == "username"


def test_set_github_id():
    """Test the User class method set_github_id."""
    user = User("U0G9QF9C6")
    user.github_id = "githubid"
    assert user.github_id == "githubid"


def test_get_github_id():
    """Test the User class method get_github_id."""
    user = User("U0G9QF9C6")
    assert user.github_id == ""


def test_get_major():
    """Test the User class method get_major()."""
    user = User("U0G9QF9C6")
    assert user.major == ""


def test_set_major():
    """Test the User class method set_major()."""
    user = User("U0G9QF9C6")
    user.major = "Computer Science"
    assert user.major == "Computer Science"


def test_get_position():
    """Test the User class method get_position()."""
    user = User("U0G9QF9C6")
    assert user.position == ""


def test_set_position():
    """Test the User class method set_position()."""
    user = User("U0G9QF9C6")
    user.position = "Developer"
    assert user.position == "Developer"


def test_get_image_url():
    """Test the User class method get_image_url()."""
    user = User("U0G9QF9C6")
    assert user.image_url == ""


def test_set_image_url():
    """Test the User class method set_image_url()."""
    user = User("U0G9QF9C6")
    user.image_url = "https://example.com/image.jpg"
    assert user.image_url == "https://example.com/image.jpg"


def test_get_permissions_level():
    """Test the User class method get_permissions_level()."""
    user = User("U0G9QF9C6")
    assert user.permissions_level == Permissions.member


def test_set_permissions_level():
    """Test the User class method set_permissions_level()."""
    user = User("U0G9QF9C6")
    user.permissions_level = Permissions.admin
    assert user.permissions_level == Permissions.admin

def test_set_karma():
    """Test setting karma"""
    user = User("U0G9QF9C6")
    user.karma = 5
    assert user.karma == 5

def test_get_karma():
    """Test getting karma"""
    user = User("U0G9QF9C6")
    assert user.karma == 1

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
