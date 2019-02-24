"""Test the dynamodb interface (requires dynamodb running)."""
from tests.util import *
from model.user import User
from model.team import Team
from model.project import Project
import pytest


@pytest.fixture
def ddb():
    """Create a new DynamoDb instance."""
    from db.dynamodb import DynamoDB
    test_config = {
        'aws': {
            'users_table': 'users_test',
            'teams_table': 'teams_test',
            'projects_table': 'projects_test'
        },
        'testing': True
    }
    return DynamoDB(test_config)


@pytest.mark.db
def test_string_rep(ddb):
    """Test string representation of the DynamoDB class."""
    assert str(ddb) == "DynamoDB"


@pytest.mark.db
def test_store_invalid_user(ddb):
    """Test handling of invalid user."""
    user = User('')
    success = ddb.store_user(user)
    assert not success


@pytest.mark.db
def test_store_invalid_team(ddb):
    """Test handling of invalid team."""
    team = Team('1', '', 'Brussel Sprouts')
    success = ddb.store_team(team)
    assert not success


@pytest.mark.db
def test_store_invalid_project(ddb):
    """Test handling of invalid project."""
    project = Project('12456', [''])
    project.github_urls = []
    success = ddb.store_project(project)
    assert not success


@pytest.mark.db
def test_store_same_users(ddb):
    """Test how database handles overwriting same user (same slack_id)."""
    user = create_test_admin('abc_123')
    user2 = create_test_admin('abc_123')
    user2.name = 'Sprouts'
    ddb.store_user(user)
    ddb.store_user(user2)

    assert ddb.retrieve_user('abc_123') == user2

    ddb.delete_user('abc_123')


@pytest.mark.db
def test_store_retrieve_user(ddb):
    """Test to see if we can store and retrieve the same user."""
    user = create_test_admin('abc_123')

    success = ddb.store_user(user)
    another_user = ddb.retrieve_user('abc_123')

    assert success
    assert user == another_user

    ddb.delete_user('abc_123')


@pytest.mark.db
def test_store_retrieve_project(ddb):
    """Test to see if we can store and retrieve the same user."""
    project = create_test_project('123456',
                                  ['https://github.com/ubclaunchpad/rocket2'])

    success = ddb.store_project(project)
    another_project = ddb.retrieve_project(project.project_id)

    assert success
    assert project == another_project

    ddb.delete_project(project.project_id)


@pytest.mark.db
def test_retrieve_invalid_user(ddb):
    """Test to see if we can retrieve a non-existant user."""
    try:
        user = ddb.retrieve_user('abc_123')

        assert False
    except LookupError as e:
        assert str(e) == 'User "abc_123" not found'


@pytest.mark.db
def test_retrieve_invalid_project(ddb):
    """Test to see if we can retrieve a non-existant user."""
    try:
        project = ddb.retrieve_project('abc_123')

        assert False
    except LookupError as e:
        assert str(e) == 'Project "abc_123" not found'


@pytest.mark.db
def test_query_user(ddb):
    """Test to see if we can store and query the same user."""
    user = create_test_admin('abc_123')
    assert ddb.store_user(user)
    users = ddb.query_user([('permission_level', 'admin')])
    strict_users = ddb.query_user([('permission_level', 'admin'),
                                   ('slack_id', 'abc_123')])
    all_users = ddb.query_user([])

    assert user == users[0]
    assert user == all_users[0]
    assert user == strict_users[0]

    ddb.delete_user('abc_123')


@pytest.mark.db
def test_query_project(ddb):
    """Test to see if we can store and query the same project."""
    project = create_test_project('123456', ['abcd'])
    assert ddb.store_project(project)
    projects = ddb.query_project([('tags', 'python')])
    strict_projects = ddb.query_project([('tags', 'python'),
                                         ('tags', 'docker'),
                                         ('display_name', 'Rocket2')])
    all_projects = ddb.query_project([])

    assert project == projects[0]
    assert project == strict_projects[0]
    assert project == all_projects[0]

    ddb.delete_project(project.project_id)


@pytest.mark.db
def test_retrieve_invalid_team(ddb):
    """Test to see if we can retrieve a non-existent team."""
    ddb = ddb
    try:
        team = ddb.retrieve_team('1')

        assert False
    except LookupError as e:
        assert str(e) == 'Team "{}" not found'.format('1')


@pytest.mark.db
def test_update_user(ddb):
    """Test to see if we can update a user."""
    u = User('abc_123')
    ddb.store_user(u)

    u = ddb.retrieve_user('abc_123')
    u.name = 'Steven Universe'
    ddb.store_user(u)

    assert ddb.retrieve_user('abc_123').name == 'Steven Universe'

    ddb.delete_user('abc_123')


@pytest.mark.db
def test_update_team(ddb):
    """Test to see if we can update a team."""
    t = Team('1', 'brussel-sprouts', 'Brussel Sprouts')
    ddb.store_team(t)

    t = ddb.retrieve_team('1')
    t.add_member('abc_123')
    t.add_member('123_abc')
    ddb.store_team(t)

    assert len(ddb.retrieve_team('1').members) == 2

    ddb.delete_team('1')


@pytest.mark.db
def test_store_retrieve_team(ddb):
    """Test to see if we can store and retrieve the same team."""
    team = create_test_team('1', 'rocket2.0', 'Rocket 2.0')
    assert ddb.store_team(team)
    another_team = ddb.retrieve_team('1')

    assert team == another_team

    ddb.delete_team('1')


@pytest.mark.db
def test_query_team(ddb):
    """Test to see if we can store and query the same team."""
    team = create_test_team('1', 'rocket2.0', 'Rocket 2.0')
    team2 = create_test_team('2', 'lame-o', 'Lame-O Team')
    team2.add_member('apple')
    ddb.store_team(team)
    ddb.store_team(team2)

    another_team = ddb.query_team([('display_name', 'Rocket 2.0')])
    same_team = ddb.query_team([('platform', 'slack')])
    multiple_queries = ddb.query_team([('display_name', 'Rocket 2.0'),
                                       ('platform', 'slack')])
    member_team = ddb.query_team([('members', 'abc_123'),
                                  ('members', 'apple')])
    all_team = ddb.query_team([])

    assert team == another_team[0]
    assert team == all_team[0]
    assert team == same_team[0]
    assert team == multiple_queries[0]
    assert team2 == member_team[0]

    ddb.delete_team('1')
    ddb.delete_team('2')


@pytest.mark.db
def test_delete_user(ddb):
    """Test to see if we can successfully delete a user."""
    user = create_test_admin('abc_123')
    ddb.store_user(user)

    assert len(ddb.query_user([])) == 1
    ddb.delete_user('abc_123')
    assert len(ddb.query_user([])) == 0


@pytest.mark.db
def test_delete_team(ddb):
    """Test to see if we can successfully delete a team."""
    team = create_test_team('1', 'rocket-2.0', 'Rocket 2.0')
    ddb.store_team(team)

    assert len(ddb.query_team([])) == 1
    ddb.delete_team('1')
    assert len(ddb.query_team([])) == 0


@pytest.mark.db
def test_delete_project(ddb):
    """Test to see if we can successfully delete a team."""
    project = create_test_project('abc_123', ['a'])
    ddb.store_project(project)

    assert len(ddb.query_project([])) == 1
    ddb.delete_project(project.project_id)
    assert len(ddb.query_project([])) == 0
