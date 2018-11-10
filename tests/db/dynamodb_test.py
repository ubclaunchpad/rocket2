"""Test the dynamodb interface (requires dynamodb running)."""
from db.dynamodb import DynamoDB
from tests.util import create_test_user, create_test_team
from model.user import User
import pytest


@pytest.mark.db
def test_string_rep():
    """Test string representation of the DynamoDB class."""
    assert str(DynamoDB()) == "DynamoDB"


@pytest.mark.db
def test_store_invalid_user():
    """Test handling of invalid user."""
    ddb = DynamoDB()
    user = User('abc_123')
    success = ddb.store_user(user)
    assert not success


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
    ddb.store_user(user)
    users = ddb.query_user([('permission_level', 'admin')])
    strict_users = ddb.query_user([('permission_level', 'admin'),
                                   ('slack_id', 'abc_123')])
    all_users = ddb.query_user([])

    assert user == users[0]
    assert user == all_users[0]
    assert user == strict_users[0]

    ddb.delete_user('abc_123')


@pytest.mark.db
def test_store_retrieve_team():
    """Test to see if we can store and retrieve the same team."""
    ddb = DynamoDB()
    team = create_test_team('rocket2.0', 'Rocket 2.0')
    ddb.store_team(team)
    another_team = ddb.retrieve_team('rocket2.0')

    assert team == another_team

    ddb.delete_team('rocket2.0')


@pytest.mark.db
def test_query_team():
    """Test to see if we can store and query the same team."""
    ddb = DynamoDB()
    team = create_test_team('rocket2.0', 'Rocket 2.0')
    ddb.store_team(team)
    another_team = ddb.query_team([('display_name', 'Rocket 2.0')])
    same_team = ddb.query_team([('platform', 'slack')])
    multiple_queries = ddb.query_team([('display_name', 'Rocket 2.0'),
                                       ('platform', 'slack')])
    member_team = ddb.query_team([('members', 'abc_123')])
    all_team = ddb.query_team([])

    assert team == another_team[0]
    assert team == all_team[0]
    assert team == same_team[0]
    assert team == multiple_queries[0]
    assert team == member_team[0]
    ddb.delete_team('rocket2.0')
