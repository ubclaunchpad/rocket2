from unittest import mock, TestCase
from interface.gcp_utils import sync_user_email_perms, sync_team_email_perms
from app.model import User, Team
from tests.memorydb import MemoryDB
from interface.gcp import GCPInterface


class TestGCPUtils(TestCase):
    def setUp(self):
        self.u0 = User('U93758')
        self.u0.github_id = '22343'
        self.u0.github_username = 'evilguy'
        self.u0.email = 'a@gmail.com'

        self.t0 = Team('465884', 'team-plasma', 'Team Plasma')
        self.t0.add_member(self.u0.github_id)
        self.t0.folder = 'oieasotbokneawsoieomieaomiewrsdoie'

        self.t1 = Team('394783', 'team-rocket', 'Team Rocket')
        self.t1.add_member(self.u0.github_id)

        self.db = MemoryDB(users=[self.u0], teams=[self.t0, self.t1])

        self.gcp = mock.MagicMock(GCPInterface)

    def test_sync_user_email_perms(self):
        sync_user_email_perms(self.gcp, self.db, self.u0)

        self.gcp.ensure_drive_permissions.assert_called_once_with(
            self.t0.github_team_name, self.t0.folder, [self.u0.email]
        )

    def test_sync_team_email_perms_bad_email(self):
        self.u0.email = 'bad@email@some.com'
        sync_team_email_perms(self.gcp, self.db, self.t0)

        self.gcp.ensure_drive_permissions.assert_not_called()
