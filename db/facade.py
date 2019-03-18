"""Database Facade."""
from model.user import User
from model.team import Team
from model.project import Project
from typing import List, Tuple, TypeVar, Type
from db.dynamodb import DynamoDB
import logging


T = TypeVar('T', User, Team, Project)


class DBFacade:
    """
    A database facade that gives an overall API for any databases.

    Currently, we plan on having DynamoDB, but other databases, such as MongoDB
    or Postgres are also being considered. Please use this class instead of
    ``db/dynamodb.py``, because we might change the databases, but the facade
    would stay the same.
    """

    def __init__(self, db: DynamoDB) -> None:
        """
        Initialize facade using a given class.

        Currently, we can only initialize with :class:`db.dynamodb.DynamoDB`.

        :param db: Database class for API calls
        """
        logging.info("Initializing database facade")
        self.ddb = db

    def __str__(self) -> str:
        """Return a string representing this class."""
        return "Database Facade"

    def store(self, obj: T) -> bool:
        """
        Store object into the correct table.

        Object can be of type :class:`model.user.User`,
        :class:`model.team.Team`, or :class:`model.project.Project`.

        :param obj: Object to store in database
        :return: True if object was stored, and false otherwise
        """
        logging.info(f"Storing object {obj}")
        return self.ddb.store(obj)

    def retrieve(self,
                 Model: Type[T],
                 k: str) -> T:
        """
        Retrieve a model from the database.

        :param Model: the actual class you want to retrieve
        :param k: retrieve based on this key (or ID)
        :raise: LookupError if key is not found
        :return: a model ``Model`` if key is found
        """
        logging.info(f"Retrieving {Model.__name__}(id={k})")
        return self.ddb.retrieve(Model, k)

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

            projects = ddb.query(Project)

        Attributes that are sets (e.g. ``team.member``,
        ``project.github_urls``) would be treated differently. This function
        would check to see if the entry **contains** a certain element. You can
        specify multiple elements, but they must be in different parameters
        (one element per tuple).::

            teams = ddb.query(Team, [('members', 'abc123'),
                                     ('members', '231abc')])

        :param Model: type of list elements you'd want
        :param params: list of tuples to match
        :return: a list of ``Model`` that fit the query parameters
        """
        logging.info(f"Querying {Model.__name__} matching "
                     f"parameters: {params}")
        return self.ddb.query(Model, params)

    def delete(self,
               Model: Type[T],
               k: str) -> None:
        """
        Remove an object from a table.

        :param Model: table type to remove the object from
        :param k: ID or key of the object to remove (must be primary key)
        """
        logging.info(f"Deleting {Model.__name__}(id={k})")
        self.ddb.delete(Model, k)
