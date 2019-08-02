"""Test project command parsing."""
from app.controller.command.commands import ProjectCommand
from db import DBFacade
from flask import jsonify, json, Flask
from unittest import mock, TestCase
from app.model import Project, Team

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
                              (self.testcommand.project_lookup_error, 200))

    def test_handle_edit_lookup_error(self):
        """Test project command edit parser with lookup error."""
        self.mock_facade.retrieve.side_effect = LookupError
        self.assertTupleEqual(self.testcommand.handle("project edit id", user),
                              (self.testcommand.project_lookup_error, 200))

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

    @mock.patch('app.model.project.uuid')
    def test_handle_create(self, mock_uuid):
        """Test project command create parser."""
        mock_uuid.uuid4.return_value = "1"
        team = Team("GTID", "team-name", "name")
        team.team_leads.add(user)
        self.mock_facade.query.return_value = [team]
        project = Project("GTID", ["repo-link"])
        project_attach = [project.get_attachment()]
        with self.app.app_context():
            resp, code = \
                self.testcommand.handle("project create repo-link team-name",
                                        user)
            expect = json.loads(jsonify({'attachments': project_attach}).data)
            resp = json.loads(resp.data)
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
        self.mock_facade.query.assert_called_once_with(Team,
                                                       [("github_team_name",
                                                         "team-name")])
        self.mock_facade.store.assert_called_once_with(project)

    def test_handle_create_multiple_team_lookup_error(self):
        """Test project command create parser with mult team lookup error."""
        team1 = Team("GTID1", "team-name1", "name1")
        team2 = Team("GTID2", "team-name2", "name2")
        team1.team_leads.add(user)
        team2.team_leads.add(user)
        self.mock_facade.query.return_value = [team1, team2]
        self.assertTupleEqual(
            self.testcommand.handle("project create repo-link team-name",
                                    user),
            (self.testcommand.team_lookup_error, 200))

    def test_handle_create_no_team_lookup_error(self):
        """Test project command create parser with no team lookup error."""
        self.mock_facade.query.return_value = []
        self.assertTupleEqual(
            self.testcommand.handle("project create repo-link team-name",
                                    user),
            (self.testcommand.team_lookup_error, 200))

    def test_handle_create_permission_error(self):
        """Test project command create parser with permission error."""
        team = Team("GTID", "team-name", "name")
        self.mock_facade.query.return_value = [team]
        self.assertTupleEqual(
            self.testcommand.handle("project create repo-link team-name",
                                    user),
            (self.testcommand.permission_error, 200))

    @mock.patch('app.model.project.uuid')
    def test_handle_create_with_display_name(self, mock_uuid):
        """Test project command create parser with specified display name."""
        mock_uuid.uuid4.return_value = "1"
        team = Team("GTID", "team-name", "name")
        team.team_leads.add(user)
        self.mock_facade.query.return_value = [team]
        project = Project("GTID", ["repo-link"])
        project.display_name = "display-name"
        project_attach = [project.get_attachment()]
        with self.app.app_context():
            resp, code = \
                self.testcommand.handle("project create repo-link team-name "
                                        "--name display-name",
                                        user)
            expect = json.loads(jsonify({'attachments': project_attach}).data)
            resp = json.loads(resp.data)
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
        self.mock_facade.query.assert_called_once_with(Team,
                                                       [("github_team_name",
                                                         "team-name")])
        self.mock_facade.store.assert_called_once_with(project)

    def test_handle_list(self):
        """Test project command list parser."""
        project1 = Project("GTID1", ["a", "b"])
        project2 = Project("GTID2", ["c", "d"])
        self.mock_facade.query.return_value = [project1, project2]
        attach1 = project1.get_basic_attachment()
        attach2 = project2.get_basic_attachment()
        attachment = [attach1, attach2]
        with self.app.app_context():
            resp, code = self.testcommand.handle("project list", user)
            expect = json.loads(jsonify({'attachments': attachment}).data)
            resp = json.loads(resp.data)
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
        self.mock_facade.query.assert_called_once_with(Project)

    def test_handle_list_no_teams(self):
        """Test project command list with no projects found."""
        self.mock_facade.query.return_value = []
        self.assertTupleEqual(self.testcommand.handle("project list", user),
                              ("No Projects Exist!", 200))

    def test_handle_unassign(self):
        """Test project command unassign parser with permission error."""
        def facade_retrieve_side_effect(*args, **kwargs):
            """Return a side effect for the mock facade."""
            if args[0] == Project:
                return Project("GTID", [])
            else:
                team = Team("GTID", "team-name", "display-name")
                team.team_leads.add(user)
                return team
        self.mock_facade.retrieve.side_effect = facade_retrieve_side_effect
        with self.app.app_context():
            resp, code = \
                self.testcommand.handle("project unassign 1",
                                        user)
            assert (resp, code) == ("Project successfully unassigned!", 200)

    def test_handle_unassign_project_lookup_error(self):
        """Test project command unassign with project lookup error."""
        self.mock_facade.retrieve.side_effect = LookupError
        self.assertTupleEqual(self.testcommand.handle("project unassign ID",
                                                      user),
                              (self.testcommand.project_lookup_error, 200))

    def test_handle_unassign_team_lookup_error(self):
        """Test project command unassign with team lookup error."""
        def facade_retrieve_side_effect(*args, **kwargs):
            """Return a side effect for the mock facade."""
            if args[0] == Project:
                return Project("GTID", [])
            else:
                raise LookupError
        self.mock_facade.retrieve.side_effect = facade_retrieve_side_effect
        self.assertTupleEqual(self.testcommand.handle("project unassign ID",
                                                      user),
                              (self.testcommand.team_lookup_error, 200))

    def test_handle_unassign_permission_error(self):
        """Test project command unassign parser with permission error."""
        def facade_retrieve_side_effect(*args, **kwargs):
            """Return a side effect for the mock facade."""
            if args[0] == Project:
                return Project("GTID", [])
            else:
                return Team("GTID", "team-name", "display-name")
        self.mock_facade.retrieve.side_effect = facade_retrieve_side_effect
        self.assertTupleEqual(
            self.testcommand.handle("project unassign 1",
                                    user),
            (self.testcommand.permission_error, 200))

    def test_handle_assign_assign(self):
        """Test project command assign."""
        self.mock_facade.retrieve.return_value = Project("", [])
        team = Team("GTID", "team-name", "display-name")
        team.team_leads.add(user)
        self.mock_facade.query.return_value = [team]
        self.assertTupleEqual(
            self.testcommand.handle("project assign ID team-name",
                                    user),
            ("Project successfully assigned!", 200))

    def test_handle_assign_project_lookup_error(self):
        """Test project command assign with project lookup error."""
        self.mock_facade.retrieve.side_effect = LookupError
        self.assertTupleEqual(
            self.testcommand.handle("project assign ID team-name",
                                    user),
            (self.testcommand.project_lookup_error, 200))

    def test_handle_assign_project_team_error(self):
        """Test project command assign with team lookup error."""
        self.mock_facade.retrieve.return_value = Project("", [])
        self.mock_facade.query.return_value = []
        self.assertTupleEqual(
            self.testcommand.handle("project assign ID team-name",
                                    user),
            (self.testcommand.team_lookup_error, 200))

    def test_handle_assign_permission_error(self):
        """Test project command assign with permission error."""
        self.mock_facade.retrieve.return_value = Project("", [])
        team = Team("GTID", "team-name", "display-name")
        self.mock_facade.query.return_value = [team]
        self.assertTupleEqual(
            self.testcommand.handle("project assign ID team-name",
                                    user),
            (self.testcommand.permission_error, 200))

    def test_handle_assign_assign_error(self):
        """Test project command assign with assignment error."""
        self.mock_facade.retrieve.return_value = Project("GTID", [])
        team = Team("GTID", "team-name", "display-name")
        team.team_leads.add(user)
        self.mock_facade.query.return_value = [team]
        self.assertTupleEqual(
            self.testcommand.handle("project assign ID team-name",
                                    user),
            (self.testcommand.assigned_error, 200))

    def test_handle_force_assign(self):
        """Test project command force assign."""
        self.mock_facade.retrieve.return_value = Project("GTID", [])
        team = Team("GTID", "team-name", "display-name")
        team.team_leads.add(user)
        self.mock_facade.query.return_value = [team]
        self.assertTupleEqual(
            self.testcommand.handle("project assign ID team-name -f",
                                    user),
            ("Project successfully assigned!", 200))

    def test_handle_delete(self):
        """Test project command delete."""
        self.mock_facade.retrieve.return_value = Project("", [])
        self.assertTupleEqual(
            self.testcommand.handle("project delete ID",
                                    user),
            ("Project successfully deleted!", 200))

    def test_handle_delete_project_lookup_error(self):
        """Test project command delete with project lookup error."""
        self.mock_facade.retrieve.side_effect = LookupError
        self.assertTupleEqual(
            self.testcommand.handle("project delete ID",
                                    user),
            (self.testcommand.project_lookup_error, 200))

    def test_handle_delete_assign_error(self):
        """Test project command delete with assignment error."""
        self.mock_facade.retrieve.return_value = Project("GTID", [])
        self.assertTupleEqual(
            self.testcommand.handle("project delete ID",
                                    user),
            (self.testcommand.assigned_error, 200))

    def test_handle_force_delete(self):
        """Test project command force delete."""
        self.mock_facade.retrieve.return_value = Project("GTID", [])
        self.assertTupleEqual(
            self.testcommand.handle("project delete ID -f",
                                    user),
            ("Project successfully deleted!", 200))
