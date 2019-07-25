"""Test the dynamodb interface (requires dynamodb running)."""
import pytest

from app.model import User, Project, Team, Permissions
from config import Config
from unittest.mock import MagicMock
from tests.util import create_test_team, create_test_admin, create_test_project


@pytest.fixture
def ddb():
    """Create a new DynamoDb instance."""
    from db.dynamodb import DynamoDB
    test_config = MagicMock(Config)
    test_config.aws_users_tablename = 'users_test'
    test_config.aws_teams_tablename = 'teams_test'
    test_config.aws_projects_tablename = 'projects_test'
    test_config.testing = True
    yield DynamoDB(test_config)
    ts = [User, Team, Project]
    for t in ts:
        items = actual.query(t)
        for item in items:
            if t == User:
                actual.delete(t, item.slack_id)
            elif t == Team:
                actual.delete(t, item.github_team_id)
            elif t == Project:
                actual.delete(t, item.project_id)


@pytest.mark.db
def test_string_rep(ddb):
    """Test string representation of the DynamoDB class."""
    assert str(ddb) == "DynamoDB"


@pytest.mark.db
def test_store_invalid_user(ddb):
    """Test handling of invalid user."""
    user = User('')
    success = ddb.store(user)
    assert not success


@pytest.mark.db
def test_store_invalid_team(ddb):
    """Test handling of invalid team."""
    team = Team('1', '', 'Brussel Sprouts')
    success = ddb.store(team)
    assert not success


@pytest.mark.db
def test_store_invalid_project(ddb):
    """Test handling of invalid project."""
    project = Project('12456', [''])
    project.github_urls = []
    success = ddb.store(project)
    assert not success


@pytest.mark.db
def test_store_same_users(ddb):
    """Test how database handles overwriting same user (same slack_id)."""
    user = create_test_admin('abc_123')
    user2 = create_test_admin('abc_123')
    user2.name = 'Sprouts'
    ddb.store(user)
    ddb.store(user2)

    assert ddb.retrieve(User, 'abc_123') == user2


@pytest.mark.db
def test_store_retrieve_user(ddb):
    """Test to see if we can store and retrieve the same user."""
    user = create_test_admin('abc_123')

    success = ddb.store(user)
    another_user = ddb.retrieve(User, 'abc_123')

    assert success
    assert user == another_user


@pytest.mark.db
def test_store_retrieve_project(ddb):
    """Test to see if we can store and retrieve the same user."""
    project = create_test_project('123456',
                                  ['https://github.com/ubclaunchpad/rocket2'])

    success = ddb.store(project)
    another_project = ddb.retrieve(Project, project.project_id)

    assert success
    assert project == another_project


@pytest.mark.db
def test_retrieve_invalid_user(ddb):
    """Test to see if we can retrieve a non-existant user."""
    try:
        ddb.retrieve(User, 'abc_123')
        assert False
    except LookupError as e:
        assert str(e) == 'User(id=abc_123) not found'


@pytest.mark.db
def test_retrieve_invalid_project(ddb):
    """Test to see if we can retrieve a non-existant user."""
    try:
        ddb.retrieve(Project, 'abc_123')

        assert False
    except LookupError as e:
        assert str(e) == 'Project(id=abc_123) not found'


@pytest.mark.db
def test_query_user(ddb):
    """Test to see if we can store and query the same user."""
    user = create_test_admin('abc_123')
    assert ddb.store(user)
    users = ddb.query(User, [('permission_level', 'admin')])
    strict_users = ddb.query(User, [('permission_level', 'admin'),
                                    ('slack_id', 'abc_123')])
    all_users = ddb.query(User)
    assert user == users[0]
    assert user == all_users[0]
    assert user == strict_users[0]


@pytest.mark.db
def test_query_project(ddb):
    """Test to see if we can store and query the same project."""
    project = create_test_project('123456', ['abcd'])
    assert ddb.store(project)
    projects = ddb.query(Project, [('tags', 'python')])
    strict_projects = ddb.query(Project, [('tags', 'python'),
                                          ('tags', 'docker'),
                                          ('display_name', 'Rocket2')])
    all_projects = ddb.query(Project)

    assert project == projects[0]
    assert project == strict_projects[0]
    assert project == all_projects[0]


@pytest.mark.db
def test_retrieve_invalid_team(ddb):
    """Test to see if we can retrieve a non-existent team."""
    ddb = ddb
    try:
        ddb.retrieve(Team, '1')
        assert False
    except LookupError as e:
        assert str(e) == 'Team(id=1) not found'


@pytest.mark.db
def test_update_user(ddb):
    """Test to see if we can update a user."""
    u = User('abc_123')
    ddb.store(u)

    u = ddb.retrieve(User, 'abc_123')
    u.name = 'Steven Universe'
    ddb.store(u)

    assert ddb.retrieve(User, 'abc_123').name == 'Steven Universe'


@pytest.mark.db
def test_update_team(ddb):
    """Test to see if we can update a team."""
    t = Team('1', 'brussel-sprouts', 'Brussel Sprouts')
    ddb.store(t)

    t = ddb.retrieve(Team, '1')
    t.add_member('abc_123')
    t.add_member('123_abc')
    ddb.store(t)

    assert len(ddb.retrieve(Team, '1').members) == 2


@pytest.mark.db
def test_store_retrieve_team(ddb):
    """Test to see if we can store and retrieve the same team."""
    team = create_test_team('1', 'rocket2.0', 'Rocket 2.0')
    assert ddb.store(team)
    another_team = ddb.retrieve(Team, '1')

    assert team == another_team


@pytest.mark.db
def test_bulk_retrieve_users(ddb):
    """Test to see if we can store and bulk retrieve."""
    uids = list(map(str, range(10)))
    users = [create_test_admin(i) for i in uids]
    for user in users:
        assert ddb.store(user)

    retrieved_users = ddb.bulk_retrieve(User, list(uids))
    for user in retrieved_users:
        assert user in users


@pytest.mark.db
def test_query_or_users(ddb):
    """Test to see if we can query users using union of parameters."""
    uids = list(map(str, range(10)))
    users = [create_test_admin(i) for i in uids]

    for user in users[:5]:
        user.permissions_level = Permissions.member

    for user in users:
        assert ddb.store(user)

    params = [('slack_id', str(uid)) for uid in uids]
    queried_users = ddb.query_or(User, params)
    for user in queried_users:
        assert user in users

    params = [('permissions_level', lvl) for lvl in ['admin', 'member']]
    queried_users = ddb.query_or(User, params)
    for user in queried_users:
        assert user in users


@pytest.mark.db
def test_query_team(ddb):
    """Test to see if we can store and query the same team."""
    team = create_test_team('1', 'rocket2.0', 'Rocket 2.0')
    team2 = create_test_team('2', 'lame-o', 'Lame-O Team')
    team2.add_member('apple')
    ddb.store(team)
    ddb.store(team2)

    another_team = ddb.query(Team, [('display_name', 'Rocket 2.0')])
    same_team = ddb.query(Team, [('platform', 'slack')])
    multiple_queries = ddb.query(Team, [('display_name', 'Rocket 2.0'),
                                        ('platform', 'slack')])
    member_team = ddb.query(Team, [('members', 'abc_123'),
                                   ('members', 'apple')])
    all_team = ddb.query(Team)

    assert team == another_team[0]
    assert team == all_team[0]
    assert team == same_team[0]
    assert team == multiple_queries[0]
    assert team2 == member_team[0]


@pytest.mark.db
def test_delete_user(ddb):
    """Test to see if we can successfully delete a user."""
    user = create_test_admin('abc_123')
    ddb.store(user)

    assert len(ddb.query(User)) == 1
    ddb.delete(User, 'abc_123')
    assert len(ddb.query(User)) == 0


@pytest.mark.db
def test_delete_team(ddb):
    """Test to see if we can successfully delete a team."""
    team = create_test_team('1', 'rocket-2.0', 'Rocket 2.0')
    ddb.store(team)

    assert len(ddb.query(Team)) == 1
    ddb.delete(Team, '1')
    assert len(ddb.query(Team)) == 0


@pytest.mark.db
def test_delete_project(ddb):
    """Test to see if we can successfully delete a team."""
    project = create_test_project('abc_123', ['a'])
    ddb.store(project)

    assert len(ddb.query(Project)) == 1
    ddb.delete(Project, project.project_id)
    assert len(ddb.query(Project)) == 0
