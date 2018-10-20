"""Test the dynamodb interface (requires dynamodb running)."""
from unittest import mock
from db.dynamodb import DynamoDB
from model.user import User
from model.permissions import Permissions


def test_string_rep():
    """Test string representation of the DynamoDB class."""
    assert str(DynamoDB()) == "DynamoDB"


def create_test_user(slack_id):
    """
    Create a test user with slack id, and with all other attributes the same.

    :param slack_id: The slack id string
    :return: returns a filled-in user model (no empty strings)
    """
    u = User(slack_id)
    u.set_biography('I like puppies and kittens!')
    u.set_email('admin@ubc.ca')
    u.set_github_username('kibbles')
    u.set_image_url('https://google.ca')
    u.set_major('Computer Science')
    u.set_permissions_level(Permissions.admin)
    u.set_position('Adrenaline Junkie')
    return u


def test_store_retrieve_user():
    """Test to see if we can store and retrieve the same user."""
    ddb = DynamoDB()
    user = create_test_user('abc_123')
    ddb.store_user(user)
    another_user = ddb.retrieve_user('abc_123')

    assert user == another_user

    ddb.delete_user('abc_123')


def test_query_user():
    """Test to see if we can store and query the same user."""
    ddb = DynamoDB()
    user = create_test_user('abc_123')
    ddb.store_user(user)
    users = ddb.query_user([('permissions_level', 'admin')])

    assert user == users[0]

    ddb.delete_user('abc_123')
