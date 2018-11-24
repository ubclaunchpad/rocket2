"""Tests for factories."""
from factory import *
from db.facade import DBFacade
from command.core import Core
import pytest


@pytest.mark.db
def test_make_core():
    """Test the make_core function."""
    core = make_core()
    assert isinstance(core, Core)
