"""Database Facade."""
from .dynamodb import DynamoDB
from model.user import User


class DBFacade:
    """
    A database facade that gives an overall API for any databases.

    Currently, we plan on having DynamoDB, but other databases, such as MongoDB
    or Postgres are also being considered.
    """

    def __init__(self):
        """Initialize facade using DynamoDB settings (for now)."""
        self.ddb = DynamoDB()

    def __str__(self):
        """Return a string representing this class."""
        return "Database Facade"

    def store_user(self, user):
        """
        Store user into users table.

        :param user: A user model to store
        """
        self.ddb.store_user(user)

    def retrieve_user(self, slack_id):
        """
        TODO: Retrieve user from users table.

        :return: returns a user model if slack id is found.
        """
        return self.ddb.retrieve_user(slack_id)

    def query_user(self, parameter):
        """
        TODO: Query for specific users by parameter.

        Query using a list of parameters (tuples), where the first element of
        the tuple is the item attribute, second being the item value.

        Example: [('permission_level', 'admin')]

        :param parameters: list of parameters (tuples)
        :return: returns a list of user models that fit the query parameters.
        """
        return self.ddb.query_user(parameter)
