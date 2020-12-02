"""Database Facade."""
from app.model import User, Team
from typing import List, Tuple, TypeVar, Type
from abc import ABC, abstractmethod

T = TypeVar('T', User, Team)


class DBFacade(ABC):
    """
    A database facade that gives an overall API for any databases.

    Currently, we plan on having DynamoDB, but other databases, such as MongoDB
    or Postgres are also being considered. Please use this class instead of
    ``db/dynamodb.py``, because we might change the databases, but the facade
    would stay the same.
    """

    @abstractmethod
    def store(self, obj: T) -> bool:
        """
        Store object into the correct table.

        Object can be of type :class:`app.model.user.User` or
        :class:`app.model.team.Team`.

        :param obj: Object to store in database
        :return: True if object was stored, and false otherwise
        """
        raise NotImplementedError

    @abstractmethod
    def retrieve(self, Model: Type[T], k: str) -> T:
        """
        Retrieve a model from the database.

        :param Model: the actual class you want to retrieve
        :param k: retrieve based on this key (or ID)
        :raises: LookupError if key is not found
        :return: a model ``Model`` if key is found
        """
        raise NotImplementedError

    @abstractmethod
    def bulk_retrieve(self, Model: Type[T], ks: List[str]) -> List[T]:
        """
        Retrieve a list of models from the database.

        Keys not found in the database will be skipped. Should be at least as
        fast as multiple calls to ``.retrieve``.

        :param Model: the actual class you want to retrieve
        :param ks: retrieve based on this key (or ID)
        :return: a list of models ``Model``
        """
        raise NotImplementedError

    @abstractmethod
    def query(self,
              Model: Type[T],
              params: List[Tuple[str, str]] = []) -> List[T]:
        """
        Query a table using a list of parameters.

        Returns a list of ``Model`` that have **all** of the attributes
        specified in the parameters. Every item in parameters is a tuple, where
        the first element is the user attribute, and the second is the value.

        Example::

            ddb = DynamoDb(config)
            users = ddb.query(User, [('platform', 'slack')])

        If you try to query a table without any parameters, the function will
        return all objects of that table.::

            teams = ddb.query(Team)

        Attributes that are sets (e.g. ``team.member``) would be treated
        differently. This function would check to see if the entry
        **contains** a certain element. You can specify multiple elements,
        but they must be in different parameters (one element per tuple).::

            teams = ddb.query(Team, [('members', 'abc123'),
                                     ('members', '231abc')])

        :param Model: type of list elements you'd want
        :param params: list of tuples to match
        :return: a list of ``Model`` that fit the query parameters
        """
        raise NotImplementedError

    @abstractmethod
    def query_or(self,
                 Model: Type[T],
                 params: List[Tuple[str, str]] = []) -> List[T]:
        """
        Query a table using a list of parameters.

        Returns a list of ``Model`` that have **one** of the attributes
        specified in the parameters. Some might say that this is a **union** of
        the parameters. Every item in parameters is a tuple, where
        the first element is the user attribute, and the second is the value.

        Example::

            ddb = DynamoDb(config)
            users = ddb.query_or(User, [('platform', 'slack')])

        If you try to query a table without any parameters, the function will
        return all objects of that table.::

            teams = ddb.query_or(Team)

        Attributes that are sets (e.g. ``team.member``) would be treated
        differently. This function would check to see if the entry
        **contains** a certain element. You can specify multiple elements,
        but they must be in different parameters (one element per tuple).::

            teams = ddb.query_or(Team, [('members', 'abc123'),
                                        ('members', '231abc')])

        The above would get you the teams that contain either member ``abc123``
        or ``231abc``.

        :param Model: type of list elements you'd want
        :param params: list of tuples to match
        :return: a list of ``Model`` that fit the query parameters
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, Model: Type[T], k: str):
        """
        Remove an object from a table.

        :param Model: table type to remove the object from
        :param k: ID or key of the object to remove (must be primary key)
        """
        raise NotImplementedError
