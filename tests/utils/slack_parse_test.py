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
        ('/rocket user edit --member <@U1234|user> --name "User"',
         '/rocket user edit --member U1234 --name "User"'),
        # No users
        ('/rocket user view',
         '/rocket user view'),
        # Multiple users
        ('/rocket foo <@U1234|user> <@U4321|ruse> <@U3412|sure> -h',
         '/rocket foo U1234 U4321 U3412 -h')
    ]

    for inp, expect in CMDS:
        assert util.escaped_id_to_id(inp) == expect


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
