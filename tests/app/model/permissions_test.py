from app.model import Permissions
from unittest import TestCase


class TestPermissionsModel(TestCase):
    def test_admin_the_biggest(self):
        self.assertGreater(Permissions.admin, Permissions.team_lead)
        self.assertGreaterEqual(Permissions.admin, Permissions.member)
        self.assertGreaterEqual(Permissions.admin, Permissions.admin)

    def test_invalid_typing(self):
        with self.assertRaises(TypeError):
            Permissions.member < 0
        with self.assertRaises(TypeError):
            Permissions.team_lead <= 0
        with self.assertRaises(TypeError):
            Permissions.team_lead > 12
        with self.assertRaises(TypeError):
            Permissions.admin >= 13

    def test_member_the_smallest(self):
        self.assertLess(Permissions.member, Permissions.team_lead)
        self.assertLessEqual(Permissions.member, Permissions.member)
        self.assertLessEqual(Permissions.member, Permissions.admin)
