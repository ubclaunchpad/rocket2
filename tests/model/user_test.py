"""Test the data model for a user."""
from model.permissions import Permissions
from model.user import User


def test_get_slack_id():
    """Test the User class method get_slack_id()."""
    user = User("U0G9QF9C6")
    assert user.get_slack_id() == "U0G9QF9C6"


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