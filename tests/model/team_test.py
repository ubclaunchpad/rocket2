"""Test the data model for a team."""
from model.team import Team
from tests.util import create_test_team


def test_team_equality():
    """Test the Team class method __eq__() and __ne__()."""
    team = Team("1", "brussel-sprouts", "Brussel Sprouts")
    team2 = Team("1", "brussel-sprouts", "Brussel Sprouts")
    team3 = Team("1", "brussel-trouts", "Brussel Trouts")
    assert team == team2
    assert team != team3


def test_valid_team():
    """Test the Team static class method is_valid()."""
    team = Team("1", "", "Brussel Sprouts")
    assert not Team.is_valid(team)
    team = create_test_team("1", "brussel-sprouts", "Brussel Sprouts")
    assert Team.is_valid(team)


def test_get_github_team_id():
    """Test the Team class method get_github_team_id()."""
    team = Team('1', 'brussel-sprouts', 'Brussel Sprouts')
    assert team.github_team_id == '1'


def test_set_github_team_id():
    """Test the Team class method set_github_team_id()."""
    team = Team('1', 'brussel-sprouts', 'Brussel Sprouts')
    team.github_team_id = '2'
    assert team.github_team_id == '2'


def test_get_github_team_name():
    """Test the Team class method set_github_team_name()."""
    team = Team("1", "brussel-sprouts", "Brussel Sprouts")
    assert team.github_team_name == "brussel-sprouts"


def test_get_display_name():
    """Test the Team class method get_display_name()."""
    team = Team("1", "brussel-sprouts", "Brussel Sprouts")
    assert team.display_name == "Brussel Sprouts"


def test_set_display_name():
    """Test the Team class method set_display_name(display_name)."""
    team = Team("1", "brussel-sprouts", "Brussel Sprouts")
    team.display_name = "Corn Cobs"
    assert team.display_name == "Corn Cobs"


def test_get_platform():
    """Test the Team class method get_platform()."""
    team = Team("1", "brussel-sprouts", "Brussel Sprouts")
    assert team.platform == ""


def test_set_platform():
    """Test the Team class method set_platform(platform)."""
    team = Team("1", "brussel-sprouts", "Brussel Sprouts")
    team.platform = "web"
    assert team.platform == "web"


def test_get_members():
    """Test the Team class method get_members()."""
    team = Team("1", "brussel-sprouts", "Brussel Sprouts")
    assert team.members == set()


def test_add_member():
    """Test the Team class method add_member(uuid)."""
    team = Team("1", "brussel-sprouts", "Brussel Sprouts")
    new_slack_id = "U0G9QF9C6"
    team.add_member(new_slack_id)
    assert new_slack_id in team.members


def test_discard_member():
    """Test the Team class method discard_member(slack_id)."""
    team = Team("1", "brussel-sprouts", "Brussel Sprouts")
    new_slack_id = "U0G9QF9C6"
    team.add_member(new_slack_id)
    team.discard_member(new_slack_id)
    assert team.members == set()


def test_is_member():
    """Test the Team class method is_member(slack_id)."""
    team = Team("1", "brussel-sprouts", "Brussel Sprouts")
    new_slack_id = "U0G9QF9C6"
    assert team.is_member(new_slack_id) is False
    team.add_member(new_slack_id)
    assert team.is_member(new_slack_id)


def test_print():
    """Test print team class."""
    team = Team("1", "brussel-sprouts", "Brussel Sprouts")
    new_slack_id = "U0G9QF9C6"
    team.add_member(new_slack_id)
    team.platform = "web"
    assert str(team) == "{'_Team__github_team_id': '1'," \
                        " '_Team__github_team_name': 'brussel-sprouts'," \
                        " '_Team__display_name': 'Brussel Sprouts'," \
                        " '_Team__platform': 'web'," \
                        " '_Team__members': {'U0G9QF9C6'}}"
