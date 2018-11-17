"""Database Facade."""


class DBFacade:
    """
    A database facade that gives an overall API for any databases.

    Currently, we plan on having DynamoDB, but other databases, such as MongoDB
    or Postgres are also being considered. Please use this class instead of
    ``db/dynamodb.py``, because we might change the databases, but the facade
    would stay the same.
    """

    def __init__(self, db):
        """
        Initialize facade using a given class.

        Currently, we can only initialize with :class:`db.dynamodb.DynamoDB`.

        :param db: Database class for API calls
        """
        self.ddb = db

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
        Retrieve user from users table.

        :return: returns a user model if slack id is found.
        """
        return self.ddb.retrieve_user(slack_id)

    def query_user(self, parameter):
        """
        Query for specific users by parameter.

        Returns list of users that have **all** of the attributes specified in
        the parameters. Every item in parameters is a tuple, where the first
        element is the user attribute, and the second is the value.

        Example: ``[('permission_level', 'admin')]``

        :param parameters: list of parameters (tuples)
        :return: returns a list of user models that fit the query parameters.
        """
        return self.ddb.query_user(parameter)

    def store_team(self, team):
        """
        Store team into teams table.

        :param team: A team model to store
        """
        self.ddb.store_team(team)

    def retrieve_team(self, team_name):
        """
        Retrieve team from teams table.

        :return: returns a team model if slack id is found.
        """
        return self.ddb.retrieve_team(team_name)

    def query_team(self, parameter):
        """
        Query for specific teams by parameter.

        Returns list of teams that have **all** of the attributes specified in
        the parameters. Every item in parameters is a tuple, where the first
        element is the user attribute, and the second is the value.

        Example: ``[('platform', 'slack')]``

        :param parameters: list of parameters (tuples)
        :return: returns a list of team models that fit the query parameters.
        """
        return self.ddb.query_team(parameter)

    def delete_team(self, team_name):
        """
        Remove a team from the teams table.

        :param team_name: team_name: the team_name of the team to be removed
        """
        self.ddb.delete_team(team_name)

    def delete_user(self, slack_id):
        """
        Remove a user from the users table.

        :param slack_id: the slack_id of the user to be removed
        """
        self.ddb.delete_user(slack_id)
