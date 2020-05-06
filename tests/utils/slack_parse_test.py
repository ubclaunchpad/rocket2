"""Some tests for utility functions in slack parsing utility."""
import utils.slack_parse as util
from app.model.user import User
from app.model.team import Team
from app.model.permissions import Permissions


def test_regularize_char_standard():
    """Test how this function reacts to normal operation."""
    assert util.regularize_char('a') == 'a'
    assert util.regularize_char(' ') == ' '
    assert util.regularize_char('\'') == '\''
    assert util.regularize_char('‘') == '\''
    assert util.regularize_char('’') == '\''
    assert util.regularize_char('“') == '"'
    assert util.regularize_char('”') == '"'


def test_escaped_id_conversion():
    """Test how this function reacts to normal operation."""
    CMDS = [
        # Normal operation
        ('/rocket user edit --username <@U1234|user> --name "User"',
         '/rocket user edit --username U1234 --name "User"'),
        # No users
        ('/rocket user view',
         '/rocket user view'),
        # Multiple users
        ('/rocket foo <@U1234|user> <@U4321|ruse> <@U3412|sure> -h',
         '/rocket foo U1234 U4321 U3412 -h')
    ]

    for inp, expect in CMDS:
        assert util.escaped_id_to_id(inp) == expect


def test_ios_dash():
    """Test how this function reacts to normal operation."""
    CMDS = [
        # Normal operation with iOS
        ('/rocket user edit —username U1234 —name "User"',
         '/rocket user edit --username U1234 --name "User"'),
        ('/rocket user edit —name "Steven Universe"',
         '/rocket user edit --name "Steven Universe"'),
        ('/rocket user edit ——name "Steven Universe"',
         '/rocket user edit ----name "Steven Universe"'),
        ('/rocket foo U1234 U4321 U3412 -h',
         '/rocket foo U1234 U4321 U3412 -h'),
        # Normal operation without iOS
        ('/rocket user edit --username U1234 --name "User"',
         '/rocket user edit --username U1234 --name "User"'),
        ('/rocket user edit --name "Steven Universe"',
         '/rocket user edit --name "Steven Universe"'),
        ('/rocket foo U1234 U4321 U3412 -h',
         '/rocket foo U1234 U4321 U3412 -h')
    ]

    for inp, expect in CMDS:
        assert util.ios_dash(inp) == expect


def test_check_credentials_admin():
    """Test checking to see if user is admin."""
    user = User("USFAS689")
    user.permissions_level = Permissions.admin
    assert util.check_permissions(user, None)


def test_check_credentials_not_admin():
    """Test checking to see if user is not admin."""
    user = User("USFAS689")
    user.permissions_level = Permissions.member
    assert not util.check_permissions(user, None)


def test_check_credentials_lead():
    """Test checking to see if user is lead for certain team."""
    user = User("USFAS689")
    user.github_id = "IDGithub"
    team = Team("brussels", "team", "id")
    team.add_member(user.github_id)
    team.add_team_lead(user.github_id)
    user.permissions_level = Permissions.team_lead
    assert util.check_permissions(user, team)


def test_check_credentials_not_lead():
    """Test checking to see if user is lead for certain team."""
    user = User("USFAS689")
    user.github_id = "IDGithub"
    team = Team("brussels", "team", "id")
    team.add_member(user.github_id)
    user.permissions_level = Permissions.team_lead
    assert not util.check_permissions(user, team)


def test_check_string_is_not_slack_id():
    """Test checking to see if a string is not a slack id."""
    string_to_test = "ABCDEFG"
    assert not util.is_slack_id(string_to_test)


def test_check_string_is_slack_id():
    """Test checking to see if string is a slack id."""
    string_to_test = "UFJ42EU67"
    assert util.is_slack_id(string_to_test)


def test_escape_email():
    """Test parsing escaped emails."""
    email = "<mailto:email@a.com|email@a.com>"
    ret = util.escape_email(email)
    assert ret == "email@a.com"
