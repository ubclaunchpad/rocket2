# content of test_sample.py
import uuid
import sys
from model.team import Team
sys.path.append('..')


def test0():
    team = Team("team")
    assert team.get_display_name() == "team"


def test1():
    team = Team("a")
    team.set_display_name("b")
    assert team.get_display_name() == "b"


def test2():
    team_a = Team("a")
    team_b = Team("b")
    assert team_a.get_team_id() != team_b.get_team_id()


def test3():
    team = Team("team")
    assert team.get_platform() == ""


def test4():
    team = Team("team")
    team.set_platform("web")
    assert team.get_platform() == "web"


def test5():
    team = Team("team")
    assert team.get_members() == set()


def test6():
    team = Team("team")
    team.discard_member(uuid.uuid4())
    assert team.get_members() == set()


def test7():
    team = Team("team")
    new_uuid = uuid.uuid4()
    team.add_member(new_uuid)
    assert new_uuid in team.get_members()


def test8():
    team = Team("team")
    new_uuid = uuid.uuid4()
    team.add_member(new_uuid)
    team.discard_member(new_uuid)
    assert (new_uuid in team.get_members()) is False


def test9():
    team = Team("team")
    new_uuid = uuid.uuid4()
    assert team.is_member(new_uuid) is False


def test10():
    team = Team("team")
    new_uuid = uuid.uuid4()
    team.add_member(new_uuid)
    assert team.is_member(new_uuid)


def test11():
    team = Team("team")
    assert team.get_github_team_name() == ""


def test12():
    team = Team("team")
    team.set_github_team_name("brusselsprouts")
    assert team.get_github_team_name() == "brusselsprouts"
