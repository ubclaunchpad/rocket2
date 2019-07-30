"""Test project command parsing."""
from app.controller.command.commands import ProjectCommand
from db import DBFacade
from flask import jsonify, json, Flask
from unittest import mock, TestCase
from app.model import Project

user = 'U123456789'


class TestProjectCommand(TestCase):
    """Test Case for ProjectCommand class."""

    def setUp(self):
        """Set up the test case environment."""
        self.app = Flask(__name__)
        self.mock_facade = mock.MagicMock(DBFacade)
        self.testcommand = ProjectCommand(self.mock_facade)

    def test_get_help(self):
        """Test project command get_help method."""
        assert self.testcommand.get_help() == self.testcommand.help

    def test_handle_view(self):
        """Test project command view parser."""
        project = Project("GTID", ["a", "b"])
        project_id = project.project_id
        project_attach = [project.get_attachment()]
        self.mock_facade.retrieve.return_value = project
        with self.app.app_context():
            resp, code = self.testcommand.handle(
                "project view %s" % project_id, user)
            expect = json.loads(jsonify({'attachments': project_attach}).data)
            resp = json.loads(resp.data)
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
        self.mock_facade.retrieve.assert_called_once_with(Project, project_id)

    def test_handle_view_lookup_error(self):
        """Test project command view parser with lookup error."""
        self.mock_facade.retrieve.side_effect = LookupError
        self.assertTupleEqual(self.testcommand.handle("project view id", user),
                              (self.testcommand.lookup_error, 200))

    def test_handle_edit_lookup_error(self):
        """Test project command edit parser with lookup error."""
        self.mock_facade.retrieve.side_effect = LookupError
        self.assertTupleEqual(self.testcommand.handle("project edit id", user),
                              (self.testcommand.lookup_error, 200))

    def test_handle_edit_name(self):
        """Test project command edit parser with name property."""
        project = Project("GTID", ["a", "b"])
        project.display_name = "name1"
        project_id = project.project_id
        self.mock_facade.retrieve.return_value = project
        with self.app.app_context():
            resp, code = self.testcommand.handle(
                "project edit %s --name name2" % project_id, user)
            project.display_name = "name2"
            project_attach = [project.get_attachment()]
            expect = json.loads(jsonify({'attachments': project_attach}).data)
            resp = json.loads(resp.data)
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
        self.mock_facade.retrieve.assert_called_once_with(Project, project_id)
        self.mock_facade.store.assert_called_once_with(project)
