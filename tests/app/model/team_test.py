from app.model import Team
from unittest import TestCase


class TestTeamModel(TestCase):
    def setUp(self):
        self.brussel_sprouts = Team('1', 'brussel-sprouts', 'Brussel Sprouts')
        self.brussel_sprouts_copy =\
            Team('1', 'brussel-sprouts', 'Brussel Sprouts')
        self.brussel_trouts = Team('1', 'brussel-trouts', 'Brussel Trouts')

    def test_team_equality(self):
        """Test the Team class method __eq__() and __ne__()."""
        self.assertEqual(self.brussel_sprouts, self.brussel_sprouts_copy)
        self.assertNotEqual(self.brussel_sprouts, self.brussel_trouts)

    def test_valid_team(self):
        """Test the Team static class method is_valid()."""
        self.assertTrue(Team.is_valid(self.brussel_sprouts))
        self.brussel_sprouts.github_team_name = ''
        self.assertFalse(Team.is_valid(self.brussel_sprouts))

    def test_add_member(self):
        """Test the Team class method add_member(github_id)."""
        new_github_id = "U0G9QF9C6"
        self.brussel_sprouts.add_member(new_github_id)
        self.assertIn(new_github_id, self.brussel_sprouts.members)

    def test_discard_member(self):
        """Test the Team class method discard_member(github_id)."""
        new_github_id = "U0G9QF9C6"
        self.brussel_sprouts.add_member(new_github_id)
        self.brussel_sprouts.discard_member(new_github_id)
        self.assertSetEqual(self.brussel_sprouts.members, set())

    def test_is_member(self):
        """Test the Team class method is_member(github_id)."""
        new_github_id = "U0G9QF9C6"
        self.assertFalse(self.brussel_sprouts.has_member(new_github_id))
        self.brussel_sprouts.add_member(new_github_id)
        assert self.brussel_sprouts.has_member(new_github_id)

    def test_add_lead(self):
        """Test the Team class method add_team_lead(github_id)."""
        new_github_id = "U0G9QF9C6"
        self.brussel_sprouts.add_team_lead(new_github_id)
        self.assertIn(new_github_id, self.brussel_sprouts.team_leads)

    def test_is_lead(self):
        """Test the Team class method is_team_lead(github_id)."""
        new_github_id = "U0G9QF9C6"
        self.assertFalse(self.brussel_sprouts.has_team_lead(new_github_id))
        self.brussel_sprouts.add_team_lead(new_github_id)
        self.assertTrue(self.brussel_sprouts.has_team_lead(new_github_id))

    def test_print(self):
        """Test print team class."""
        new_slack_id = "U0G9QF9C6"
        self.brussel_sprouts.add_member(new_slack_id)
        self.brussel_sprouts.add_team_lead(new_slack_id)
        self.brussel_sprouts.platform = "web"
        expected = "{'github_team_id': '1'," \
            " 'github_team_name': 'brussel-sprouts'," \
            " 'displayname': 'Brussel Sprouts'," \
            " 'platform': 'web'," \
            " 'team_leads': {'U0G9QF9C6'}," \
            " 'members': {'U0G9QF9C6'}," \
            " 'folder': ''}"
        self.assertEqual(str(self.brussel_sprouts), expected)
