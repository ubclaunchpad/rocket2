"""Test the dynamodb interface (requires dynamodb running)."""
from unittest import mock
from db.dynamodb import DynamoDB
from model.user import User


def test_string_rep():
    """Test string representation of the DynamoDB class."""
    assert str(DynamoDB()) == "DynamoDB"


def test_store_retrieve_user():
    """Test to see if we can store and retrieve the same user."""
    ddb = DynamoDB()
    user = User('abc_123')
    ddb.store_user(user)
    another_user = ddb.retrieve_user('abc_123')

    assert user == another_user


def test_query_user():
    """Test to see if we can store and query the same user."""
    ddb = DynamoDB()
    user = User('abc_123')

