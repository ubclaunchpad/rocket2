from app.controller.command.commands import ProjectCommand
from tests.memorydb import MemoryDB
from tests.util import create_test_project, create_test_admin
from flask import Flask
from unittest import mock, TestCase
from app.model import Project, User, Team

user = 'U123456789'


class TestProjectCommand(TestCase):
    def setUp(self):
        self.app = Flask(__name__)

        self.u0 = User('U03548940')
        self.u0.github_username = 'weirdo'
        self.u0.github_id = '534593'
        self.admin = create_test_admin('Uadmin')
        self.p0 = create_test_project('GTID', [
            'https://github.com/ubclaunchpad/rocket2'
        ])
        self.p1 = create_test_project('', [
            'https://github.com/ubclaunchpad/rocket2'
        ])
        self.t0 = Team('GTID', 'team-name', 'name')
        self.db = MemoryDB(
            users=[self.u0, self.admin],
            teams=[self.t0],
            projs=[self.p0, self.p1])

        self.testcommand = ProjectCommand(self.db)

    def test_get_help(self):
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
        self.assertEqual(self.testcommand.get_help(),
                         self.testcommand.get_help(subcommand="foo"))

    def test_handle_help(self):
        ret, _ = self.testcommand.handle("project help", self.u0.slack_id)
        self.assertEqual(ret, self.testcommand.get_help())

    def test_handle_multiple_subcommands(self):
        """Test handling multiple observed subcommands."""
        ret, _ = self.testcommand.handle("project list edit",
                                         self.u0.slack_id)
        self.assertEqual(ret, self.testcommand.get_help())

    def test_handle_subcommand_help(self):
        """Test project subcommand help text."""
        subcommands = list(self.testcommand.subparser.choices.keys())
        for subcommand in subcommands:
            for arg in ['--help', '-h', '--invalid argument']:
                command = f'project {subcommand} {arg}'
                ret, _ = self.testcommand.handle(command, self.u0.slack_id)
                self.assertEqual(1, ret.count('usage'))

    def test_handle_view(self):
        with self.app.app_context():
            resp, _ = self.testcommand.handle(
                f'project view {self.p0.project_id}', self.u0.slack_id)
            expect = {'attachments': [self.p0.get_attachment()]}
            self.assertDictEqual(resp, expect)

    def test_handle_view_lookup_error(self):
        self.assertTupleEqual(self.testcommand.handle(
            'project view rand.proj',
            self.u0.slack_id),
                              ('Project(id=rand.proj) not found', 200))

    def test_handle_edit_lookup_error(self):
        self.assertTupleEqual(self.testcommand.handle(
            'project edit rand.proj',
            self.u0.slack_id),
                              ('Project(id=rand.proj) not found', 200))

    def test_handle_edit_name(self):
        other_name = 'other_name'
        self.assertNotEqual(self.p0.display_name, other_name)
        with self.app.app_context():
            self.testcommand.handle(
                f'project edit {self.p0.project_id} --name {other_name}',
                self.u0.slack_id)
            self.assertEqual(self.p0.display_name, other_name)

    @mock.patch('app.model.project.uuid')
    def test_handle_create_as_team_lead(self, mock_uuid):
        mock_uuid.uuid4.return_value = '1'
        self.t0.add_team_lead(self.u0.github_id)
        with self.app.app_context():
            cmd = f'project create repo-link {self.t0.github_team_name}'
            self.testcommand.handle(cmd, self.u0.slack_id)

        proj = self.db.retrieve(Project, '1')
        self.assertEqual(proj.github_team_id, self.t0.github_team_id)
        self.assertEqual(proj.github_urls, ['repo-link'])

    @mock.patch('app.model.project.uuid')
    def test_handle_create_as_admin(self, mock_uuid):
        mock_uuid.uuid4.return_value = '1'
        with self.app.app_context():
            cmd = f'project create repo-link {self.t0.github_team_name}'
            self.testcommand.handle(cmd, self.admin.slack_id)

        proj = self.db.retrieve(Project, '1')
        self.assertEqual(proj.github_team_id, self.t0.github_team_id)
        self.assertEqual(proj.github_urls, ['repo-link'])

    def test_handle_create_multiple_team_lookup_error(self):
        team1 = Team('GTID1', 'team-name', 'name1')
        self.db.teams['GTID1'] = team1
        self.assertTupleEqual(
            self.testcommand.handle(
                f'project create repo-link {self.t0.github_team_name}',
                self.admin.slack_id),
            ('2 teams found with GitHub team name team-name', 200))

    def test_handle_create_permission_error(self):
        """Test project command create parser with permission error."""
        self.assertTupleEqual(
            self.testcommand.handle(
                f'project create repo-link {self.t0.github_team_name}',
                self.u0.slack_id),
            (self.testcommand.permission_error, 200))

    def test_handle_create_user_lookup_error(self):
        self.assertTupleEqual(
            self.testcommand.handle(
                f'project create repo-link {self.t0.github_team_name}',
                'rando.user'),
            ('User(id=rando.user) not found', 200))

    @mock.patch('app.model.project.uuid')
    def test_handle_create_with_display_name(self, mock_uuid):
        mock_uuid.uuid4.return_value = '1'
        with self.app.app_context():
            self.testcommand.handle(
                f'project create repo-link {self.t0.github_team_name}'
                ' --name display-name',
                self.admin.slack_id)

        proj = self.db.retrieve(Project, '1')
        self.assertEqual(proj.github_team_id, self.t0.github_team_id)
        self.assertEqual(proj.github_urls, ['repo-link'])
        self.assertEqual(proj.display_name, 'display-name')

    def test_handle_list(self):
        with self.app.app_context():
            resp, _ = self.testcommand.handle('project list', user)
            self.assertIn(self.p0.project_id, resp)
            self.assertIn(self.p1.project_id, resp)

    def test_handle_list_no_projects(self):
        self.db.projs = {}
        self.assertTupleEqual(
            self.testcommand.handle('project list', self.u0.slack_id),
            ('No Projects Exist!', 200))

    def test_handle_unassign_team_lead(self):
        self.t0.add_team_lead(self.u0.github_id)
        with self.app.app_context():
            cmd = f'project unassign {self.p0.project_id}'
            resp = self.testcommand.handle(cmd, self.u0.slack_id)
            self.assertEqual(resp, ('Project successfully unassigned!', 200))

    def test_handle_unassign_as_admin(self):
        with self.app.app_context():
            cmd = f'project unassign {self.p0.project_id}'
            resp = self.testcommand.handle(cmd, self.admin.slack_id)
            self.assertEqual(resp, ('Project successfully unassigned!', 200))

    def test_handle_unassign_project_lookup_error(self):
        self.assertEqual(
            self.testcommand.handle('project unassign rand.proj',
                                    self.admin.slack_id),
            ('Project(id=rand.proj) not found', 200))

    def test_handle_unassign_team_lookup_error(self):
        proj = Project('rando', [])
        self.db.projs[proj.project_id] = proj
        self.assertEqual(self.testcommand.handle(
            f'project unassign {proj.project_id}',
            self.admin.slack_id),
                         ('Team(id=rando) not found', 200))

    def test_handle_unassign_user_lookup_error(self):
        cmd = f'project unassign {self.p0.project_id}'
        self.assertEqual(self.testcommand.handle(cmd, 'rando.user'),
                         ('User(id=rando.user) not found', 200))

    def test_handle_unassign_permission_error(self):
        cmd = f'project unassign {self.p0.project_id}'
        self.assertEqual(
            self.testcommand.handle(cmd, self.u0.slack_id),
            (self.testcommand.permission_error, 200))

    def test_handle_assign_as_team_lead(self):
        self.t0.add_team_lead(self.u0.github_id)
        cmd = f'project assign {self.p1.project_id} {self.t0.github_team_name}'
        self.assertTupleEqual(
            self.testcommand.handle(cmd, self.u0.slack_id),
            ('Project successfully assigned!', 200))

    def test_handle_assign_as_admin(self):
        cmd = f'project assign {self.p1.project_id} {self.t0.github_team_name}'
        self.assertTupleEqual(
            self.testcommand.handle(cmd, self.admin.slack_id),
            ('Project successfully assigned!', 200))

    def test_handle_assign_project_lookup_error(self):
        cmd = f'project assign arst {self.t0.github_team_name}'
        self.assertTupleEqual(
            self.testcommand.handle(cmd, self.admin.slack_id),
            ('Project(id=arst) not found', 200))

    def test_handle_assign_project_team_lookup_error(self):
        cmd = f'project assign {self.p0.project_id} rando.id'
        self.assertTupleEqual(
            self.testcommand.handle(cmd, self.admin.slack_id),
            ('0 teams found with GitHub team name rando.id', 200))

    def test_handle_assign_permission_error(self):
        cmd = f'project assign {self.p0.project_id} {self.t0.github_team_name}'
        self.assertTupleEqual(
            self.testcommand.handle(cmd, self.u0.slack_id),
            (self.testcommand.permission_error, 200))

    def test_handle_assign_assign_error(self):
        cmd = f'project assign {self.p0.project_id} {self.t0.github_team_name}'
        self.assertTupleEqual(
            self.testcommand.handle(cmd, self.admin.slack_id),
            (self.testcommand.assigned_error, 200))

    def test_handle_force_assign(self):
        cmd = 'project assign %s %s -f' % (
            self.p0.project_id,
            self.t0.github_team_name
        )
        self.assertTupleEqual(
            self.testcommand.handle(cmd, self.admin.slack_id),
            ('Project successfully assigned!', 200))

    def test_handle_delete_as_admin(self):
        cmd = f'project delete {self.p1.project_id}'
        self.assertTupleEqual(
            self.testcommand.handle(cmd, self.admin.slack_id),
            ('Project successfully deleted!', 200))

    def test_handle_delete_project_lookup_error(self):
        cmd = 'project delete rando.id'
        self.assertTupleEqual(
            self.testcommand.handle(cmd, self.admin.slack_id),
            ('Project(id=rando.id) not found', 200))

    def test_handle_delete_user_lookup_error(self):
        cmd = f'project delete {self.p0.project_id}'
        self.assertTupleEqual(
            self.testcommand.handle(cmd, 'rando.id'),
            ('User(id=rando.id) not found', 200))

    def test_handle_delete_assign_error(self):
        cmd = f'project delete {self.p0.project_id}'
        self.assertTupleEqual(
            self.testcommand.handle(cmd, self.admin.slack_id),
            (self.testcommand.assigned_error, 200))

    def test_handle_force_delete(self):
        cmd = f'project delete {self.p0.project_id} -f'
        self.assertTupleEqual(
            self.testcommand.handle(cmd, self.admin.slack_id),
            ('Project successfully deleted!', 200))
