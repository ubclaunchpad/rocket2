"""Test the facade for the database."""
from unittest import mock
from db.facade import DBFacade
from tests.util import create_test_user


def test_string_rep():
    """Test string representation of the DBFacade class."""
    assert str(DBFacade()) == "Database Facade"


@mock.patch('db.facade.DynamoDB')
def test_store_user(ddb):
    """Test storing user calls correct functions."""
    dbf = DBFacade()
    test_user = create_test_user('abc_123')
    dbf.store_user(test_user)
    ddb.store_user.assert_called_with(test_user)


@mock.patch('db.facade.DynamoDB')
def test_retrieve_user(ddb):
    """Test retrieving user calls correct functions."""
    dbf = DBFacade()
    slack_id = 'abc_123'
    dbf.retrieve_user(slack_id)
    ddb.retrieve_user.assert_called_with(slack_id)


@mock.patch('db.facade.DynamoDB')
def test_query_user(ddb):
    """Test querying user calls correct functions."""
    dbf = DBFacade()
    dbf.query_user(['permission_level', 'admin'])
    ddb.query_user.assert_called_with(['permission_level', 'admin'])
