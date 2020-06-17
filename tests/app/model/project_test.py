"""Test the data model for a project."""
from app.model import Project
from unittest import TestCase


class TestProjectModel(TestCase):
    """Test project model functions."""

    def setUp(self):
        """Set up project variables for testing."""
        self.rocket2 = Project(
            '12345',
            ['https://www.github.com/ubclaunchpad/rocket2'])
        self.p0 = Project('12345', ['https://www.github.com/'])
        self.p1 = Project('12345', ['https://www.github.com/'])
        self.p2 = Project('1234', ['https://www.github.com/'])

    def test_valid_project(self):
        """Test the Project static method is_valid()."""
        self.assertTrue(Project.is_valid(self.rocket2))

    def test_project_equalities(self):
        """Test project __eq__ and __ne__ methods."""
        self.assertNotEqual(self.p0, self.p1)
        self.assertNotEqual(self.p0, self.p2)
        self.assertNotEqual(self.p1, self.p2)

        self.p0.project_id = 'abc123'
        self.p1.project_id = 'abc123'

        self.assertEqual(self.p0, self.p1)
        self.assertNotEqual(self.p0, self.p2)
        self.assertNotEqual(self.p1, self.p2)
