"""Test the dynamodb interface (requires dynamodb running)."""
from db.dynamodb import DynamoDB
from tests.util import create_test_user, create_test_team


def test_string_rep():
    """Test string representation of the DynamoDB class."""
    assert str(DynamoDB()) == "DynamoDB"


def test_store_retrieve_user():
    """Test to see if we can store and retrieve the same user."""
    ddb = DynamoDB()
    user = create_test_user('abc_123')

    ddb.store_user(user)
    another_user = ddb.retrieve_user('abc_123')

    assert user.get_biography() == another_user.get_biography()

    ddb.delete_user('abc_123')


def test_query_user():
    """Test to see if we can store and query the same user."""
    ddb = DynamoDB()
    user = create_test_user('abc_123')
    ddb.store_user(user)
    users = ddb.query_user([('permission_level', 'admin')])

    assert len(users) == 1

    ddb.delete_user('abc_123')


def test_store_retrieve_team():
    """Test to see if we can store and retrieve the same team."""
    ddb = DynamoDB()
    team = create_test_team('rocket2.0', 'Rocket 2.0')
    ddb.store_team(team)
    another_team = ddb.retrieve_team('rocket2.0')

    assert team == another_team

    ddb.delete_team('rocket2.0')


def test_query_team():
    """Test to see if we can store and query the same team."""
    ddb = DynamoDB()
    team = create_test_team('rocket2.0', 'Rocket 2.0')
    ddb.store_team(team)
    teams = ddb.query_team('rocket2.0')

    assert len(teams) == 1

    ddb.delete_team('rocket2.0')
