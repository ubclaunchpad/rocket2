"""Test the data model for a team."""
import uuid
from model.team import Team


def test_get_display_name():
    """Test the Team class method get_display_name()."""
    team = Team("team")
    assert team.get_display_name() == "team"


def test_set_display_name():
    """Test the Team class method set_display_name(display_name)."""
    team = Team("a")
    team.set_display_name("b")
    assert team.get_display_name() == "b"


def test_get_team_id():
    """Test the Team class method get_team_id()."""
    team_a = Team("a")
    team_b = Team("b")
    assert team_a.get_team_id() != team_b.get_team_id()


def test_get_platform():
    """Test the Team class method get_platform()."""
    team = Team("team")
    assert team.get_platform() == ""


def test_set_platform():
    """Test the Team class method set_platform(platform)."""
    team = Team("team")
    team.set_platform("web")
    assert team.get_platform() == "web"


def test_get_members():
    """Test the Team class method get_members()."""
    team = Team("team")
    assert team.get_members() == set()


def test_discard_member():
    """Test the Team class method discard_member(uuid)."""
    team = Team("team")
    team.discard_member(uuid.uuid4())
    assert team.get_members() == set()


def test_add_member():
    """Test the Team class method add_member(uuid)."""
    team = Team("team")
    new_uuid = uuid.uuid4()
    team.add_member(new_uuid)
    assert new_uuid in team.get_members()


def test_manage_member():
    """Test Team class method discard_member(uuid) and add_member(uuid)."""
    team = Team("team")
    new_uuid = uuid.uuid4()
    team.add_member(new_uuid)
    team.discard_member(new_uuid)
    assert (new_uuid in team.get_members()) is False


def test_is_member_1():
    """Test if is_member(uuid) can tell if a uuid is not part of the team."""
    team = Team("team")
    new_uuid = uuid.uuid4()
    assert team.is_member(new_uuid) is False


def test_is_member_2():
    """Test if is_member(uuid) can tell if a uuid is a part of the team."""
    team = Team("team")
    new_uuid = uuid.uuid4()
    team.add_member(new_uuid)
    assert team.is_member(new_uuid)


def test_get_github_team_name():
    """Test the Team class method set_github_team_name()."""
    team = Team("team")
    assert team.get_github_team_name() == ""


def test_set_github_team_name():
    """Test the Team class method set_github_team_name(github_team_name)."""
    team = Team("team")
    team.set_github_team_name("brusselsprouts")
    assert team.get_github_team_name() == "brusselsprouts"
