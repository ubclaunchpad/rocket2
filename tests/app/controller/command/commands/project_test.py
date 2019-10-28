"""Test project command parsing."""
from app.controller.command.commands import ProjectCommand
from db import DBFacade
from flask import Flask
from unittest import mock, TestCase
from app.model import Project, User, Team, Permissions

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
        subcommands = list(self.testcommand.subparser.choices.keys())
        help_message = self.testcommand.get_help()
        self.assertEqual(len(subcommands), help_message.count("usage"))

    def test_get_subcommand_help(self):
        """Test project command get_help method for specific subcommands."""
        subcommands = list(self.testcommand.subparser.choices.keys())
        for subcommand in subcommands:
            help_message = self.testcommand.get_help(subcommand=subcommand)
            self.assertEqual(1, help_message.count("usage"))

    def test_get_invalid_subcommand_help(self):
        """Test project command get_help method for invalid subcommands."""
        self.assertEqual(self.testcommand.get_help(),
                         self.testcommand.get_help(subcommand="foo"))

    def test_handle_help(self):
        """Test project command help parser."""
        ret, code = self.testcommand.handle("project help", user)
        self.assertEqual(ret, self.testcommand.get_help())
        self.assertEqual(code, 200)

    def test_handle_multiple_subcommands(self):
        """Test handling multiple observed subcommands."""
        ret, code = self.testcommand.handle("project list edit", user)
        self.assertEqual(ret, self.testcommand.get_help())
        self.assertEqual(code, 200)

    def test_handle_subcommand_help(self):
        """Test project subcommand help text."""
        subcommands = list(self.testcommand.subparser.choices.keys())
        for subcommand in subcommands:
            command = f"project {subcommand} --help"
            ret, code = self.testcommand.handle(command, user)
            self.assertEqual(1, ret.count("usage"))
            self.assertEqual(code, 200)

            command = f"project {subcommand} -h"
            ret, code = self.testcommand.handle(command, user)
            self.assertEqual(1, ret.count("usage"))
            self.assertEqual(code, 200)

            command = f"project {subcommand} --invalid argument"
            ret, code = self.testcommand.handle(command, user)
            self.assertEqual(1, ret.count("usage"))
            self.assertEqual(code, 200)

    def test_handle_view(self):
        """Test project command view parser."""
        project = Project("GTID", ["a", "b"])
        project_id = project.project_id
        project_attach = [project.get_attachment()]
        self.mock_facade.retrieve.return_value = project
        with self.app.app_context():
            resp, code = self.testcommand.handle(
                "project view %s" % project_id, user)
            expect = {'attachments': project_attach}
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
        self.mock_facade.retrieve.assert_called_once_with(Project, project_id)

    def test_handle_view_lookup_error(self):
        """Test project command view parser with lookup error."""
        self.mock_facade.retrieve.side_effect = LookupError(
            "project lookup error")
        self.assertTupleEqual(self.testcommand.handle("project view id", user),
                              ("project lookup error", 200))

    def test_handle_edit_lookup_error(self):
        """Test project command edit parser with lookup error."""
        self.mock_facade.retrieve.side_effect = LookupError(
            "project lookup error")
        self.assertTupleEqual(self.testcommand.handle("project edit id", user),
                              ("project lookup error", 200))

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
            expect = {'attachments': project_attach}
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
        self.mock_facade.retrieve.assert_called_once_with(Project, project_id)
        self.mock_facade.store.assert_called_once_with(project)

    @mock.patch('app.model.project.uuid')
    def test_handle_create_as_team_lead(self, mock_uuid):
        """Test project command create parser as a team lead."""
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
            expect = {'attachments': project_attach}
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
        self.mock_facade.query.assert_called_once_with(Team,
                                                       [("github_team_name",
                                                         "team-name")])
        self.mock_facade.store.assert_called_once_with(project)

    @mock.patch('app.model.project.uuid')
    def test_handle_create_as_admin(self, mock_uuid):
        """Test project command create parser as an admin."""
        mock_uuid.uuid4.return_value = "1"
        team = Team("GTID", "team-name", "name")
        calling_user = User(user)
        calling_user.permissions_level = Permissions.admin
        self.mock_facade.retrieve.return_value = calling_user
        self.mock_facade.query.return_value = [team]
        project = Project("GTID", ["repo-link"])
        project_attach = [project.get_attachment()]
        with self.app.app_context():
            resp, code = \
                self.testcommand.handle("project create repo-link team-name",
                                        user)
            expect = {'attachments': project_attach}
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
            ("2 teams found with GitHub team name team-name", 200))

    def test_handle_create_no_team_lookup_error(self):
        """Test project command create parser with no team lookup error."""
        self.mock_facade.query.return_value = []
        self.assertTupleEqual(
            self.testcommand.handle("project create repo-link team-name",
                                    user),
            ("0 teams found with GitHub team name team-name", 200))

    def test_handle_create_permission_error(self):
        """Test project command create parser with permission error."""
        team = Team("GTID", "team-name", "name")
        self.mock_facade.query.return_value = [team]
        self.assertTupleEqual(
            self.testcommand.handle("project create repo-link team-name",
                                    user),
            (self.testcommand.permission_error, 200))

    def test_handle_create_user_lookup_error(self):
        """Test project command create parser with no user lookup error."""
        team = Team("GTID", "team-name", "name")
        self.mock_facade.query.return_value = [team]
        self.mock_facade.retrieve.side_effect = LookupError(
            "user lookup error")
        self.assertTupleEqual(
            self.testcommand.handle("project create repo-link team-name",
                                    user),
            ("user lookup error", 200))

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
            expect = {'attachments': project_attach}
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
        self.mock_facade.query.assert_called_once_with(Team,
                                                       [("github_team_name",
                                                         "team-name")])
        self.mock_facade.store.assert_called_once_with(project)

    @mock.patch('app.model.project.uuid')
    def test_handle_list(self, mock_uuid):
        """Test project command list parser."""
        mock_uuid.uuid4.return_value = "1"
        project1 = Project("GTID1", ["a", "b"])
        project1.display_name = "project1"
        project2 = Project("GTID2", ["c", "d"])
        project2.display_name = "project2"
        self.mock_facade.query.return_value = [project1, project2]
        with self.app.app_context():
            resp, code = self.testcommand.handle("project list", user)
            expect = \
                "*PROJECT ID : GITHUB TEAM ID : PROJECT NAME*\n" \
                "1 : GTID1 : project1\n" \
                "1 : GTID2 : project2\n"
            self.assertEqual(resp, expect)
            self.assertEqual(code, 200)
        self.mock_facade.query.assert_called_once_with(Project)

    def test_handle_list_no_teams(self):
        """Test project command list with no projects found."""
        self.mock_facade.query.return_value = []
        self.assertTupleEqual(self.testcommand.handle("project list", user),
                              ("No Projects Exist!", 200))

    def test_handle_unassign_as_team_lead(self):
        """Test project command unassign parseras a team lead."""
        def facade_retrieve_side_effect(*args, **kwargs):
            """Return a side effect for the mock facade."""
            if args[0] == Project:
                return Project("GTID", [])
            elif args[0] == Team:
                team = Team("GTID", "team-name", "display-name")
                team.team_leads.add(user)
                return team
            else:
                calling_user = User(user)
                return calling_user
        self.mock_facade.retrieve.side_effect = facade_retrieve_side_effect
        with self.app.app_context():
            resp, code = \
                self.testcommand.handle("project unassign 1",
                                        user)
            assert (resp, code) == ("Project successfully unassigned!", 200)

    def test_handle_unassign_as_admin(self):
        """Test project command unassign parser as an admin."""
        def facade_retrieve_side_effect(*args, **kwargs):
            """Return a side effect for the mock facade."""
            if args[0] == Project:
                return Project("GTID", [])
            elif args[0] == Team:
                team = Team("GTID", "team-name", "display-name")
                return team
            else:
                calling_user = User(user)
                calling_user.permissions_level = Permissions.admin
                return calling_user
        self.mock_facade.retrieve.side_effect = facade_retrieve_side_effect
        with self.app.app_context():
            resp, code = \
                self.testcommand.handle("project unassign 1",
                                        user)
            assert (resp, code) == ("Project successfully unassigned!", 200)

    def test_handle_unassign_project_lookup_error(self):
        """Test project command unassign with project lookup error."""
        self.mock_facade.retrieve.side_effect = LookupError(
            "project lookup error")
        self.assertTupleEqual(self.testcommand.handle("project unassign ID",
                                                      user),
                              ("project lookup error", 200))

    def test_handle_unassign_team_lookup_error(self):
        """Test project command unassign with team lookup error."""
        def facade_retrieve_side_effect(*args, **kwargs):
            """Return a side effect for the mock facade."""
            if args[0] == Project:
                return Project("GTID", [])
            else:
                raise LookupError("team lookup error")
        self.mock_facade.retrieve.side_effect = facade_retrieve_side_effect
        self.assertTupleEqual(self.testcommand.handle("project unassign ID",
                                                      user),
                              ("team lookup error", 200))

    def test_handle_unassign_user_lookup_error(self):
        """Test project command unassign with team lookup error."""
        def facade_retrieve_side_effect(*args, **kwargs):
            """Return a side effect for the mock facade."""
            if args[0] == Project:
                return Project("GTID", [])
            elif args[0] == Team:
                return Team("GTID", "team-name", "display-name")
            else:
                raise LookupError("user lookup error")
        self.mock_facade.retrieve.side_effect = facade_retrieve_side_effect
        self.assertTupleEqual(self.testcommand.handle("project unassign ID",
                                                      user),
                              ("user lookup error", 200))

    def test_handle_unassign_permission_error(self):
        """Test project command unassign parser with permission error."""
        def facade_retrieve_side_effect(*args, **kwargs):
            """Return a side effect for the mock facade."""
            if args[0] == Project:
                return Project("GTID", [])
            elif args[0] == Team:
                return Team("GTID", "team-name", "display-name")
            else:
                return User(user)
        self.mock_facade.retrieve.side_effect = facade_retrieve_side_effect
        self.assertTupleEqual(
            self.testcommand.handle("project unassign 1",
                                    user),
            (self.testcommand.permission_error, 200))

    def test_handle_assign_as_team_lead(self):
        """Test project command assign as a team lead."""
        def facade_retrieve_side_effect(*args, **kwargs):
            """Return a side effect for the mock facade."""
            if args[0] == Project:
                return Project("", [])
            else:
                calling_user = User(user)
                return calling_user
        self.mock_facade.retrieve.side_effect = facade_retrieve_side_effect
        team = Team("GTID", "team-name", "display-name")
        team.team_leads.add(user)
        self.mock_facade.query.return_value = [team]
        self.assertTupleEqual(
            self.testcommand.handle("project assign ID team-name",
                                    user),
            ("Project successfully assigned!", 200))

    def test_handle_assign_as_admin(self):
        """Test project command assign as an admin."""
        def facade_retrieve_side_effect(*args, **kwargs):
            """Return a side effect for the mock facade."""
            if args[0] == Project:
                return Project("", [])
            else:
                calling_user = User(user)
                calling_user.permissions_level = Permissions.admin
                return calling_user
        self.mock_facade.retrieve.side_effect = facade_retrieve_side_effect
        team = Team("GTID", "team-name", "display-name")
        self.mock_facade.query.return_value = [team]
        self.assertTupleEqual(
            self.testcommand.handle("project assign ID team-name",
                                    user),
            ("Project successfully assigned!", 200))

    def test_handle_assign_project_lookup_error(self):
        """Test project command assign with project lookup error."""
        self.mock_facade.retrieve.side_effect = LookupError(
            "project lookup error")
        self.assertTupleEqual(
            self.testcommand.handle("project assign ID team-name",
                                    user),
            ("project lookup error", 200))

    def test_handle_assign_project_team_lookup_error(self):
        """Test project command assign with team lookup error."""
        self.mock_facade.retrieve.return_value = Project("", [])
        self.mock_facade.query.return_value = []
        self.assertTupleEqual(
            self.testcommand.handle("project assign ID team-name",
                                    user),
            ("0 teams found with GitHub team name team-name", 200))

    def test_handle_assign_permission_error(self):
        """Test project command assign with permission error."""
        def facade_retrieve_side_effect(*args, **kwargs):
            """Return a side effect for the mock facade."""
            if args[0] == Project:
                return Project("", [])
            else:
                calling_user = User(user)
                return calling_user
        self.mock_facade.retrieve.side_effect = facade_retrieve_side_effect
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

    def test_handle_delete_as_team_lead(self):
        """Test project command delete as a team lead."""
        def facade_retrieve_side_effect(*args, **kwargs):
            """Return a side effect for the mock facade."""
            if args[0] == Project:
                return Project("", [])
            elif args[0] == Team:
                team = Team("GTID", "team-name", "display-name")
                team.team_leads.add(user)
                return team
            else:
                calling_user = User(user)
                return calling_user
        self.mock_facade.retrieve.side_effect = facade_retrieve_side_effect
        self.assertTupleEqual(
            self.testcommand.handle("project delete ID",
                                    user),
            ("Project successfully deleted!", 200))

    def test_handle_delete_as_admin(self):
        """Test project command delete as an admin."""
        def facade_retrieve_side_effect(*args, **kwargs):
            """Return a side effect for the mock facade."""
            if args[0] == Project:
                return Project("", [])
            elif args[0] == Team:
                team = Team("GTID", "team-name", "display-name")
                return team
            else:
                calling_user = User(user)
                calling_user.permissions_level = Permissions.admin
                return calling_user
        self.mock_facade.retrieve.side_effect = facade_retrieve_side_effect
        self.assertTupleEqual(
            self.testcommand.handle("project delete ID",
                                    user),
            ("Project successfully deleted!", 200))

    def test_handle_delete_project_lookup_error(self):
        """Test project command delete with project lookup error."""
        self.mock_facade.retrieve.side_effect = LookupError(
            "project lookup error")
        self.assertTupleEqual(
            self.testcommand.handle("project delete ID",
                                    user),
            ("project lookup error", 200))

    def test_handle_delete_team_lookup_error(self):
        """Test project command delete with team lookup error."""
        def facade_retrieve_side_effect(*args, **kwargs):
            """Return a side effect for the mock facade."""
            if args[0] == Project:
                return Project("", [])
            elif args[0] == Team:
                team = Team("GTID", "team-name", "display-name")
                return team
            else:
                raise LookupError("team lookup error")
        self.mock_facade.retrieve.side_effect = facade_retrieve_side_effect
        self.assertTupleEqual(
            self.testcommand.handle("project delete ID",
                                    user),
            ("team lookup error", 200))

    def test_handle_delete_user_lookup_error(self):
        """Test project command delete with team lookup error."""
        def facade_retrieve_side_effect(*args, **kwargs):
            """Return a side effect for the mock facade."""
            if args[0] == Project:
                return Project("", [])
            elif args[0] == Team:
                raise LookupError("user lookup error")
            else:
                calling_user = User(user)
                return calling_user
        self.mock_facade.retrieve.side_effect = facade_retrieve_side_effect
        self.assertTupleEqual(
            self.testcommand.handle("project delete ID",
                                    user),
            ("user lookup error", 200))

    def test_handle_delete_assign_error(self):
        """Test project command delete with assignment error."""
        self.mock_facade.retrieve.return_value = Project("GTID", [])
        self.assertTupleEqual(
            self.testcommand.handle("project delete ID",
                                    user),
            (self.testcommand.assigned_error, 200))

    def test_handle_force_delete(self):
        """Test project command force delete."""
        def facade_retrieve_side_effect(*args, **kwargs):
            """Return a side effect for the mock facade."""
            if args[0] == Project:
                return Project("", [])
            elif args[0] == Team:
                team = Team("GTID", "team-name", "display-name")
                team.team_leads.add(user)
                return team
            else:
                calling_user = User(user)
                return calling_user
        self.mock_facade.retrieve.side_effect = facade_retrieve_side_effect
        self.assertTupleEqual(
            self.testcommand.handle("project delete ID -f",
                                    user),
            ("Project successfully deleted!", 200))
