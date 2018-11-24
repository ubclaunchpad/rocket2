"""Test the dynamodb interface (requires dynamodb running)."""
from db.dynamodb import DynamoDB
from tests.util import create_test_user, create_test_team
from model.user import User
from model.team import Team
import pytest


@pytest.mark.db
def test_string_rep():
    """Test string representation of the DynamoDB class."""
    assert str(DynamoDB()) == "DynamoDB"


@pytest.mark.db
def test_store_invalid_user():
    """Test handling of invalid user."""
    ddb = DynamoDB()
    user = User('')
    success = ddb.store_user(user)
    assert not success


@pytest.mark.db
def test_store_invalid_team():
    """Test handling of invalid team."""
    ddb = DynamoDB()
    team = Team('', 'Brussel Sprouts')
    success = ddb.store_team(team)
    assert not success


@pytest.mark.db
def test_store_same_users():
    """Test how database handles overwriting same user (same slack_id)."""
    ddb = DynamoDB()
    user = create_test_user('abc_123')
    user2 = create_test_user('abc_123')
    user2.set_name('Sprouts')
    ddb.store_user(user)
    ddb.store_user(user2)

    assert ddb.retrieve_user('abc_123') == user2

    ddb.delete_user('abc_123')


@pytest.mark.db
def test_store_retrieve_user():
    """Test to see if we can store and retrieve the same user."""
    ddb = DynamoDB()
    user = create_test_user('abc_123')

    success = ddb.store_user(user)
    another_user = ddb.retrieve_user('abc_123')

    assert success
    assert user == another_user

    ddb.delete_user('abc_123')


@pytest.mark.db
def test_retrieve_invalid_user():
    """Test to see if we can retrieve a non-existant user."""
    ddb = DynamoDB()
    try:
        user = ddb.retrieve_user('abc_123')

        assert False
    except LookupError as e:
        assert str(e) == 'User "{}" not found'.format('abc_123')


@pytest.mark.db
def test_query_user():
    """Test to see if we can store and query the same user."""
    ddb = DynamoDB()
    user = create_test_user('abc_123')
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
def test_retrieve_invalid_team():
    """Test to see if we can retrieve a non-existent team."""
    ddb = DynamoDB()
    try:
        team = ddb.retrieve_team('rocket2.0')

        assert False
    except LookupError as e:
        assert str(e) == 'Team "{}" not found'.format('rocket2.0')


@pytest.mark.db
def test_update_user():
    """Test to see if we can update a user."""
    ddb = DynamoDB()
    u = User('abc_123')
    ddb.store_user(u)

    u = ddb.retrieve_user('abc_123')
    u.set_name('Steven Universe')
    ddb.store_user(u)

    assert ddb.retrieve_user('abc_123').get_name() == 'Steven Universe'

    ddb.delete_user('abc_123')


@pytest.mark.db
def test_update_team():
    """Test to see if we can update a team."""
    ddb = DynamoDB()
    t = Team('brussel-sprouts', 'Brussel Sprouts')
    ddb.store_team(t)

    t = ddb.retrieve_team('brussel-sprouts')
    t.add_member('abc_123')
    t.add_member('123_abc')
    ddb.store_team(t)

    assert len(ddb.retrieve_team('brussel-sprouts').get_members()) == 2

    ddb.delete_team('brussel-sprouts')


@pytest.mark.db
def test_store_retrieve_team():
    """Test to see if we can store and retrieve the same team."""
    ddb = DynamoDB()
    team = create_test_team('rocket2.0', 'Rocket 2.0')
    assert ddb.store_team(team)
    another_team = ddb.retrieve_team('rocket2.0')

    assert team == another_team

    ddb.delete_team('rocket2.0')


@pytest.mark.db
def test_query_team():
    """Test to see if we can store and query the same team."""
    ddb = DynamoDB()
    team = create_test_team('rocket2.0', 'Rocket 2.0')
    team2 = create_test_team('lame-o', 'Lame-O Team')
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

    ddb.delete_team('rocket2.0')
    ddb.delete_team('lame-o')


@pytest.mark.db
def test_delete_user():
    """Test to see if we can successfully delete a user."""
    ddb = DynamoDB()
    user = create_test_user('abc_123')
    ddb.store_user(user)

    assert len(ddb.query_user([])) == 1
    ddb.delete_user('abc_123')
    assert len(ddb.query_user([])) == 0


@pytest.mark.db
def test_delete_team():
    """Test to see if we can successfully delete a team."""
    ddb = DynamoDB()
    team = create_test_team('rocket-2.0', 'Rocket 2.0')
    ddb.store_team(team)

    assert len(ddb.query_team([])) == 1
    ddb.delete_team('rocket-2.0')
    assert len(ddb.query_team([])) == 0
