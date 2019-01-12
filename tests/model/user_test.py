"""Test the data model for a user."""
from model.permissions import Permissions
from model.user import User
from tests.util import create_test_user


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
    user = create_test_user("brussel-sprouts")
    assert User.is_valid(user)


def test_get_slack_id():
    """Test the User class method get_slack_id()."""
    user = User("U0G9QF9C6")
    assert user.get_slack_id() == "U0G9QF9C6"


def test_get_name():
    """Test the User class method get_name()."""
    user = User("U0G9QF9C6")
    assert user.get_name() == ""


def test_set_name():
    """Test the User class method set_name()."""
    user = User("U0G9QF9C6")
    user.set_name("Russell")
    assert user.get_name() == "Russell"


def test_get_email():
    """Test the User class method get_email()."""
    user = User("U0G9QF9C6")
    assert user.get_email() == ""


def test_set_email():
    """Test the User class method set_email()."""
    user = User("U0G9QF9C6")
    user.set_email("email@example.com")
    assert user.get_email() == "email@example.com"


def test_get_github_username():
    """Test the User class method get_github_username()."""
    user = User("U0G9QF9C6")
    assert user.get_github_username() == ""


def test_set_github_username():
    """Test the User class method set_github_username()."""
    user = User("U0G9QF9C6")
    user.set_github_username("username")
    assert user.get_github_username() == "username"


def test_set_github_id():
    """Test the User class method set_github_id."""
    user = User("U0G9QF9C6")
    user.set_github_id("githubid")
    assert user.get_github_id() == "githubid"


def test_get_github_id():
    """Test the User class method get_github_id."""
    user = User("U0G9QF9C6")
    assert user.get_github_id() == ""


def test_get_major():
    """Test the User class method get_major()."""
    user = User("U0G9QF9C6")
    assert user.get_major() == ""


def test_set_major():
    """Test the User class method set_major()."""
    user = User("U0G9QF9C6")
    user.set_major("Computer Science")
    assert user.get_major() == "Computer Science"


def test_get_position():
    """Test the User class method get_position()."""
    user = User("U0G9QF9C6")
    assert user.get_position() == ""


def test_set_position():
    """Test the User class method set_position()."""
    user = User("U0G9QF9C6")
    user.set_position("Developer")
    assert user.get_position() == "Developer"


def test_get_image_url():
    """Test the User class method get_image_url()."""
    user = User("U0G9QF9C6")
    assert user.get_image_url() == ""


def test_set_image_url():
    """Test the User class method set_image_url()."""
    user = User("U0G9QF9C6")
    user.set_image_url("https://example.com/image.jpg")
    assert user.get_image_url() == "https://example.com/image.jpg"


def test_get_permissions_level():
    """Test the User class method get_permissions_level()."""
    user = User("U0G9QF9C6")
    assert user.get_permissions_level() == Permissions.member


def test_set_permissions_level():
    """Test the User class method set_permissions_level()."""
    user = User("U0G9QF9C6")
    user.set_permissions_level(Permissions.admin)
    assert user.get_permissions_level() == Permissions.admin


def test_print():
    """Test print user class."""
    user = User("U0G9QF9C6")
    user.set_biography("bio test")
    user.set_email("email@email.com")
    user.set_permissions_level(Permissions.admin)
    assert str(user) == "{'_User__slack_id': 'U0G9QF9C6', '_User__name': ''," \
                        " '_User__email': 'email@email.com'," \
                        " '_User__github_username': '', '_User__github_id': '', " \
                        "'_User__major': ''," \
                        " '_User__position': '', '_User__biography':" \
                        " 'bio test', '_User__image_url': ''," \
                        " '_User__permissions_level':" \
                        " <Permissions.admin: 3>}"
