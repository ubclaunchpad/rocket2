"""Test the facade for the database."""
from db.facade import DBFacade
from model.user import User


def test_string_rep():
    """Test string representation of the DBFacade class."""
    assert str(DBFacade()) == "Database Facade"


def test_store_user():
    """Test no errors in storing a user."""
    dbf = DBFacade()
    try:
        dbf.store_user(User('abc_123'))
    except Exception:
        assert False
    assert True


def test_retrieve_user():
    """Test the type of the returned user as a model.user.User."""
    dbf = DBFacade()
    assert isinstance(dbf.retrieve_user('abc_123'), User)


def test_query_user():
    """Test the type of the returned query as a list."""
    dbf = DBFacade()
    assert isinstance(dbf.query_user('abc_123'), list)
