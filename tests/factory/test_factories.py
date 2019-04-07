"""Tests for factories."""
import pytest

from factory import make_core, Core
from interface.github import GithubInterface
from unittest import mock


@pytest.mark.db
def test_make_core():
    """Test the make_core function."""
    test_config = {
        'testing': True,
        'aws': {
            'users_table': 'users_test',
            'teams_table': 'teams_test',
            'projects_table': 'projects_test'
        }
    }
    core = make_core(test_config, mock.MagicMock(GithubInterface))
    assert isinstance(core, Core)
