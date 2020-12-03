from app.controller.command.commands import ExportCommand
from unittest import TestCase
from app.model import User, Team, Permissions
from tests.memorydb import MemoryDB
from tests.util import create_test_admin


class TestExportCommand(TestCase):
    def setUp(self):
        self.u0 = User('U0G9QF9C6')
        self.u0.email = 'immabaddy@gmail.com'
        self.u0.github_id = '305834954'

        self.u1 = User('Utheomadude')
        self.u1.email = 'theounderstars@yahoo.com'
        self.u1.github_id = '349850564'

        self.admin = create_test_admin('Uadmin')

        self.lead = User('Ualley')
        self.lead.email = 'alead@ubclaunchpad.com'
        self.lead.github_id = '2384858'
        self.lead.permissions_level = Permissions.team_lead

        self.t0 = Team('305849', 'butter-batter', 'Butter Batters')
        self.t0.add_member(self.u0.github_id)
        self.t0.add_member(self.lead.github_id)
        self.t0.add_team_lead(self.lead.github_id)

        self.t1 = Team('320484', 'aqua-scepter', 'Aqua Scepter')
        self.t1.add_member(self.u1.github_id)

        self.t2 = Team('22234', 'tiger-dear', 'Shakespearean')

        self.db = MemoryDB(users=[self.u0, self.u1, self.admin, self.lead],
                           teams=[self.t0, self.t1, self.t2])

        self.cmd = ExportCommand(self.db)

    def test_get_help_from_bad_syntax(self):
        resp, _ = self.cmd.handle('export emails hanrse', self.admin.slack_id)
        self.assertEqual(resp, self.cmd.get_help('emails'))

    def test_get_help_bad_syntax_all(self):
        resp, _ = self.cmd.handle('export blah', self.admin.slack_id)
        self.assertEqual(resp, self.cmd.get_help())

    def test_lookup_error_user_calling(self):
        resp, _ = self.cmd.handle('export emails', 'blah blah')
        self.assertEqual(resp, ExportCommand.lookup_error)

    def test_get_all_emails(self):
        resp, _ = self.cmd.handle('export emails', self.admin.slack_id)
        self.assertIn(self.u0.email, resp)
        self.assertIn(self.u1.email, resp)
        self.assertIn(self.admin.email, resp)
        self.assertIn(self.lead.email, resp)
        self.assertIn(ExportCommand.no_emails_missing_msg, resp)

    def test_lead_get_all_emails(self):
        resp, _ = self.cmd.handle('export emails', self.lead.slack_id)
        self.assertIn(self.u0.email, resp)
        self.assertIn(self.u1.email, resp)
        self.assertIn(self.admin.email, resp)
        self.assertIn(self.lead.email, resp)
        self.assertIn(ExportCommand.no_emails_missing_msg, resp)

    def test_member_get_all_emails(self):
        resp, _ = self.cmd.handle('export emails', self.u0.slack_id)
        self.assertIn(ExportCommand.permission_error, resp)

    def test_get_team_emails(self):
        resp, _ = self.cmd.handle(
            f'export emails --team {self.t0.github_team_name}',
            self.admin.slack_id)
        self.assertIn(self.u0.email, resp)
        self.assertIn(self.lead.email, resp)
        self.assertIn(ExportCommand.no_emails_missing_msg, resp)

    def test_lead_get_team_emails(self):
        resp, _ = self.cmd.handle(
            f'export emails --team {self.t0.github_team_name}',
            self.lead.slack_id)
        self.assertIn(self.u0.email, resp)
        self.assertIn(self.lead.email, resp)
        self.assertIn(ExportCommand.no_emails_missing_msg, resp)

    def test_member_get_team_emails(self):
        resp, _ = self.cmd.handle(
            f'export emails --team {self.t0.github_team_name}',
            self.u1.slack_id)
        self.assertIn(ExportCommand.permission_error, resp)

    def test_lead_get_team_emails_one_missing(self):
        self.u0.email = ''
        resp, _ = self.cmd.handle(
            f'export emails --team {self.t0.github_team_name}',
            self.lead.slack_id)
        self.assertIn(self.u0.slack_id, resp)
        self.assertIn(self.lead.email, resp)
        self.assertIn('Members who don\'t have an email:', resp)
        self.assertNotIn(ExportCommand.no_emails_missing_msg, resp)

    def test_get_emails_no_users_in_team(self):
        resp, _ = self.cmd.handle(
            f'export emails --team {self.t2.github_team_name}',
            self.admin.slack_id)
        self.assertEqual(resp, ExportCommand.no_user_msg)

    def test_get_all_emails_char_limit_reached(self):
        old_lim = ExportCommand.MAX_CHAR_LIMIT
        ExportCommand.MAX_CHAR_LIMIT = 30
        resp, _ = self.cmd.handle('export emails', self.admin.slack_id)
        self.assertIn(ExportCommand.char_limit_exceed_msg, resp)

        # reset things because python doesn't do that
        ExportCommand.MAX_CHAR_LIMIT = old_lim

    def test_get_all_emails_one_missing_char_limit_reached(self):
        old_lim = ExportCommand.MAX_CHAR_LIMIT
        ExportCommand.MAX_CHAR_LIMIT = 30
        self.u0.email = ''
        resp, _ = self.cmd.handle(
            f'export emails',
            self.lead.slack_id)
        self.assertIn(self.u0.slack_id, resp)
        self.assertIn('Members who don\'t have an email:', resp)
        self.assertNotIn(ExportCommand.no_emails_missing_msg, resp)

        # reset things because python doesn't do that
        ExportCommand.MAX_CHAR_LIMIT = old_lim
