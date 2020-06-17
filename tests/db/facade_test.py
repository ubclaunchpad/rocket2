"""Test the facade for the database."""
from db import DBFacade
from unittest import mock, TestCase
from app.model import Team, User, Project
from tests.util import create_test_admin, create_test_team, create_test_project


class TestDBFacade(TestCase):
    """Test DBFacade functions."""

    def setUp(self):
        """Set up mocks and whatnot."""
        self.ddb = mock.Mock()
        self.dbf = DBFacade(self.ddb)

    def test_string_rep(self):
        """Test string representation of the DBFacade class."""
        assert str(self.dbf) == "Database Facade"

    def test_store_user(self):
        """Test storing user calls correct functions."""
        test_user = create_test_admin('abc_123')
        self.dbf.store(test_user)
        self.ddb.store.assert_called_with(test_user)

    def test_retrieve_user(self):
        """Test retrieving user calls correct functions."""
        slack_id = 'abc_123'
        self.dbf.retrieve(User, slack_id)
        self.ddb.retrieve.assert_called_with(User, slack_id)

    def test_query_user(self):
        """Test querying user calls correct functions."""
        self.dbf.query(User, ['permission_level', 'admin'])
        self.ddb.query.assert_called_with(User, ['permission_level', 'admin'])

    def test_store_team(self):
        """Test storing team calls correct functions."""
        test_team = create_test_team('1', 'brussel-sprouts', 'Brussel Sprouts')
        self.dbf.store(test_team)
        self.ddb.store.assert_called_with(test_team)

    def test_retrieve_team(self):
        """Test retrieving team calls correct functions."""
        team_id = '12345'
        self.dbf.retrieve(Team, team_id)
        self.ddb.retrieve.assert_called_with(Team, team_id)

    def test_bulk_retrieve_team(self):
        """Test bulk retrieving teams."""
        team_ids = list(map(str, range(10)))
        self.dbf.bulk_retrieve(Team, team_ids)
        self.ddb.bulk_retrieve.assert_called_with(Team, team_ids)

    def test_query_or_team(self):
        """Test querying teams."""
        params = [('github_team_id', str(team_id)) for team_id in range(10)]
        self.dbf.query_or(Team, params)
        self.ddb.query_or.assert_called_with(Team, params)

    def test_query_team(self):
        """Test querying team calls correct functions."""
        self.dbf.query(Team, [('platform', 'slack')])
        self.ddb.query.assert_called_with(Team, [('platform', 'slack')])

    def test_delete_team(self):
        """Test deleting team calls correct functions."""
        team_name = 'brussel-sprouts'
        self.dbf.delete(Team, team_name)
        self.ddb.delete.assert_called_with(Team, team_name)

    def test_delete_user(self):
        """Test deleting user calls correct functions."""
        slack_id = 'abc_123'
        self.dbf.delete(User, slack_id)
        self.ddb.delete.assert_called_with(User, slack_id)

    def test_store_project(self):
        """Test storing project calls correct functions."""
        test_project = create_test_project('1', ['a'])
        self.dbf.store(test_project)
        self.ddb.store.assert_called_with(test_project)

    def test_retrieve_project(self):
        """Test retrieving project calls correct functions."""
        project_id = 'brussel-sprouts'
        self.dbf.retrieve(Project, project_id)
        self.ddb.retrieve.assert_called_with(Project, project_id)

    def test_query_project(self):
        """Test querying project calls correct functions."""
        self.dbf.query(Project, [('platform', 'slack')])
        self.ddb.query.assert_called_with(Project, [('platform', 'slack')])

    def test_delete_project(self):
        """Test deleting project calls correct functions."""
        project_id = 'brussel-sprouts'
        self.dbf.delete(Project, project_id)
        self.ddb.delete.assert_called_with(Project, project_id)
