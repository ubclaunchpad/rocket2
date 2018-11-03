"""Test the dynamodb interface (requires dynamodb running)."""
from db.dynamodb import DynamoDB
from tests.util import create_test_user
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
