"""Tests for factories."""
from factory import *
from db.facade import DBFacade
from command.core import Core
import pytest
from unittest import mock
from interface.github import GithubInterface


@pytest.mark.db
def test_make_core():
    """Test the make_core function."""
    test_config = {
        'testing': True,
        'aws': {
            'users_table': 'users_test',
            'teams_table': 'teams_test'
        }
    }
    core = make_core(test_config, mock.MagicMock(GithubInterface))
    assert isinstance(core, Core)
