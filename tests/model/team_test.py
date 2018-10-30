"""Test the data model for a team."""
from model.team import Team


def test_team_equality():
    """Test the Team class method __eq__() and __ne__()."""
    team = Team("brussel-sprouts", "Brussel Sprouts")
    team2 = Team("brussel-sprouts", "Brussel Sprouts")
    team3 = Team("brussel-trouts", "Brussel Trouts")
    assert team == team2
    assert team != team3


def test_get_github_team_name():
    """Test the Team class method set_github_team_name()."""
    team = Team("brussel-sprouts", "Brussel Sprouts")
    assert team.get_github_team_name() == "brussel-sprouts"


def test_get_display_name():
    """Test the Team class method get_display_name()."""
    team = Team("brussel-sprouts", "Brussel Sprouts")
    assert team.get_display_name() == "Brussel Sprouts"


def test_set_display_name():
    """Test the Team class method set_display_name(display_name)."""
    team = Team("brussel-sprouts", "Brussel Sprouts")
    team.set_display_name("Corn Cobs")
    assert team.get_display_name() == "Corn Cobs"


def test_get_platform():
    """Test the Team class method get_platform()."""
    team = Team("brussel-sprouts", "Brussel Sprouts")
    assert team.get_platform() == ""


def test_set_platform():
    """Test the Team class method set_platform(platform)."""
    team = Team("brussel-sprouts", "Brussel Sprouts")
    team.set_platform("web")
    assert team.get_platform() == "web"


def test_get_members():
    """Test the Team class method get_members()."""
    team = Team("brussel-sprouts", "Brussel Sprouts")
    assert team.get_members() == set()


def test_add_member():
    """Test the Team class method add_member(uuid)."""
    team = Team("brussel-sprouts", "Brussel Sprouts")
    new_slack_id = "U0G9QF9C6"
    team.add_member(new_slack_id)
    assert new_slack_id in team.get_members()


def test_discard_member():
    """Test the Team class method discard_member(slack_id)."""
    team = Team("brussel-sprouts", "Brussel Sprouts")
    new_slack_id = "U0G9QF9C6"
    team.add_member(new_slack_id)
    team.discard_member(new_slack_id)
    assert team.get_members() == set()


def test_is_member():
    """Test the Team class method is_member(slack_id)."""
    team = Team("brussel-sprouts", "Brussel Sprouts")
    new_slack_id = "U0G9QF9C6"
    assert team.is_member(new_slack_id) is False
    team.add_member(new_slack_id)
    assert team.is_member(new_slack_id)
