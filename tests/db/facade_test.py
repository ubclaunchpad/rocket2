"""Test the facade for the database."""
from unittest import mock
from db.facade import DBFacade
from tests.util import create_test_admin, create_test_team


@mock.patch('db.dynamodb.DynamoDB', autospec=True)
def test_string_rep(ddb):
    """Test string representation of the DBFacade class."""
    assert str(DBFacade(ddb)) == "Database Facade"


@mock.patch('db.dynamodb.DynamoDB', autospec=True)
def test_store_user(ddb):
    """Test storing user calls correct functions."""
    dbf = DBFacade(ddb)
    test_user = create_test_admin('abc_123')
    dbf.store_user(test_user)
    ddb.store_user.assert_called_with(test_user)


@mock.patch('db.dynamodb.DynamoDB', autospec=True)
def test_retrieve_user(ddb):
    """Test retrieving user calls correct functions."""
    dbf = DBFacade(ddb)
    slack_id = 'abc_123'
    dbf.retrieve_user(slack_id)
    ddb.retrieve_user.assert_called_with(slack_id)


@mock.patch('db.dynamodb.DynamoDB', autospec=True)
def test_query_user(ddb):
    """Test querying user calls correct functions."""
    dbf = DBFacade(ddb)
    dbf.query_user(['permission_level', 'admin'])
    ddb.query_user.assert_called_with(['permission_level', 'admin'])


@mock.patch('db.dynamodb.DynamoDB', autospec=True)
def test_store_team(ddb):
    """Test storing team calls correct functions."""
    dbf = DBFacade(ddb)
    test_team = create_test_team('1', 'brussel-sprouts', 'Brussel Sprouts')
    dbf.store_team(test_team)
    ddb.store_team.assert_called_with(test_team)


@mock.patch('db.dynamodb.DynamoDB', autospec=True)
def test_retrieve_team(ddb):
    """Test retrieving team calls correct functions."""
    dbf = DBFacade(ddb)
    team_name = 'brussel-sprouts'
    dbf.retrieve_team(team_name)
    ddb.retrieve_team.assert_called_with(team_name)


@mock.patch('db.dynamodb.DynamoDB', autospec=True)
def test_query_team(ddb):
    """Test querying team calls correct functions."""
    dbf = DBFacade(ddb)
    dbf.query_team([('platform', 'slack')])
    ddb.query_team.assert_called_with([('platform', 'slack')])


@mock.patch('db.dynamodb.DynamoDB', autospec=True)
def test_delete_team(ddb):
    """Test deleting team calls correct functions."""
    dbf = DBFacade(ddb)
    team_name = 'brussel-sprouts'
    dbf.delete_team(team_name)
    ddb.delete_team.assert_called_with(team_name)


@mock.patch('db.dynamodb.DynamoDB', autospec=True)
def test_delete_user(ddb):
    """Test deleting user calls correct functions."""
    dbf = DBFacade(ddb)
    slack_id = 'abc_123'
    dbf.delete_user(slack_id)
    ddb.delete_user.assert_called_with(slack_id)
