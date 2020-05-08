"""Test the data model for a project."""
from app.model import Project


def test_valid_project():
    """Test the Project static method is_valid()."""
    p = Project('12345', ['https://www.github.com/ubclaunchpad/rocket2'])
    assert Project.is_valid(p)


def test_project_equalities():
    """Test project __eq__ and __ne__ methods."""
    p0 = Project('12345', ['https://www.github.com/'])
    p1 = Project('12345', ['https://www.github.com/'])
    p2 = Project('1234', ['https://www.github.com/'])

    assert p0 != p1
    assert p0 != p2
    assert p1 != p2

    p0.project_id = 'abc123'
    p1.project_id = 'abc123'

    assert p0 == p1
    assert p0 != p2
    assert p1 != p2
