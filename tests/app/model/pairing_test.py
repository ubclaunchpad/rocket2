"""Test the data model for a project."""
from app.model import Pairing
from unittest import TestCase


class TestPairingModel(TestCase):
    """Test pairing model functions."""

    def setUp(self):
        """Set up pairing variables for testing."""
        self.p0 = Pairing('user1', 'user2')
        self.p1 = Pairing('user1', 'user3')
        self.p2 = Pairing('user2', 'user3')

    def test_valid_pairing(self):
        """Test the pairing static method is_valid()."""
        self.assertTrue(Pairing.is_valid(self.p0))

    def test_pairing_equalities(self):
        """Test pairing __eq__ and __ne__ methods."""
        self.assertNotEqual(self.p0, self.p1)
        self.assertNotEqual(self.p0, self.p2)
        self.assertNotEqual(self.p1, self.p2)
