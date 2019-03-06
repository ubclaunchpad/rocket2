"""Test the facade for the database."""
from unittest import mock
from db.facade import DBFacade
from tests.util import *


@mock.patch('db.dynamodb.DynamoDB', autospec=True)
def test_string_rep(ddb):
    """Test string representation of the DBFacade class."""
    assert str(DBFacade(ddb)) == "Database Facade"


@mock.patch('db.dynamodb.DynamoDB', autospec=True)
def test_store_user(ddb):
    """Test storing user calls correct functions."""
    dbf = DBFacade(ddb)
    test_user = create_test_admin('abc_123')
    dbf.store(test_user)
    ddb.store.assert_called_with(test_user)


@mock.patch('db.dynamodb.DynamoDB', autospec=True)
def test_retrieve_user(ddb):
    """Test retrieving user calls correct functions."""
    dbf = DBFacade(ddb)
    slack_id = 'abc_123'
    dbf.retrieve(User, slack_id)
    ddb.retrieve.assert_called_with(User, slack_id)


@mock.patch('db.dynamodb.DynamoDB', autospec=True)
def test_query_user(ddb):
    """Test querying user calls correct functions."""
    dbf = DBFacade(ddb)
    dbf.query(User, ['permission_level', 'admin'])
    ddb.query.assert_called_with(User, ['permission_level', 'admin'])


@mock.patch('db.dynamodb.DynamoDB', autospec=True)
def test_store_team(ddb):
    """Test storing team calls correct functions."""
    dbf = DBFacade(ddb)
    test_team = create_test_team('1', 'brussel-sprouts', 'Brussel Sprouts')
    dbf.store(test_team)
    ddb.store.assert_called_with(test_team)


@mock.patch('db.dynamodb.DynamoDB', autospec=True)
def test_retrieve_team(ddb):
    """Test retrieving team calls correct functions."""
    dbf = DBFacade(ddb)
    team_name = 'brussel-sprouts'
    dbf.retrieve(Team, team_name)
    ddb.retrieve.assert_called_with(Team, team_name)


@mock.patch('db.dynamodb.DynamoDB', autospec=True)
def test_query_team(ddb):
    """Test querying team calls correct functions."""
    dbf = DBFacade(ddb)
    dbf.query(Team, [('platform', 'slack')])
    ddb.query.assert_called_with(Team, [('platform', 'slack')])


@mock.patch('db.dynamodb.DynamoDB', autospec=True)
def test_delete_team(ddb):
    """Test deleting team calls correct functions."""
    dbf = DBFacade(ddb)
    team_name = 'brussel-sprouts'
    dbf.delete(Team, team_name)
    ddb.delete.assert_called_with(Team, team_name)


@mock.patch('db.dynamodb.DynamoDB', autospec=True)
def test_delete_user(ddb):
    """Test deleting user calls correct functions."""
    dbf = DBFacade(ddb)
    slack_id = 'abc_123'
    dbf.delete(User, slack_id)
    ddb.delete.assert_called_with(User, slack_id)


@mock.patch('db.dynamodb.DynamoDB', autospec=True)
def test_store_project(ddb):
    """Test storing project calls correct functions."""
    dbf = DBFacade(ddb)
    test_project = create_test_project('1', ['a'])
    dbf.store(test_project)
    ddb.store.assert_called_with(test_project)


@mock.patch('db.dynamodb.DynamoDB', autospec=True)
def test_retrieve_project(ddb):
    """Test retrieving project calls correct functions."""
    dbf = DBFacade(ddb)
    project_id = 'brussel-sprouts'
    dbf.retrieve(Project, project_id)
    ddb.retrieve.assert_called_with(Project, project_id)


@mock.patch('db.dynamodb.DynamoDB', autospec=True)
def test_query_project(ddb):
    """Test querying project calls correct functions."""
    dbf = DBFacade(ddb)
    dbf.query(Project, [('platform', 'slack')])
    ddb.query.assert_called_with(Project, [('platform', 'slack')])


@mock.patch('db.dynamodb.DynamoDB', autospec=True)
def test_delete_project(ddb):
    """Test deleting project calls correct functions."""
    dbf = DBFacade(ddb)
    project_id = 'brussel-sprouts'
    dbf.delete(Project, project_id)
    ddb.delete.assert_called_with(Project, project_id)
