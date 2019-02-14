"""Database Facade."""
import logging


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
        logging.info("Initializing database facade")
        self.ddb = db

    def __str__(self):
        """Return a string representing this class."""
        return "Database Facade"

    def store_user(self, user):
        """
        Store user into users table.

        :param user: A user model to store
        """
        logging.info("Storing user {}".format(user.get_slack_id()))
        self.ddb.store_user(user)

    def retrieve_user(self, slack_id):
        """
        Retrieve user from users table.

        :param slack_id: retrieve based on this slack id
        :raise: LookupError if slack id is not found.
        :return: returns a user model if slack id is found.
        """
        logging.info("Retrieving user {}".format(slack_id))
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
        logging.info("Querying users matching parameters: {}".
                     format(parameter))
        return self.ddb.query_user(parameter)

    def delete_user(self, slack_id):
        """
        Remove a user from the users table.

        :param slack_id: the slack_id of the user to be removed
        """
        logging.info("Deleting user {}".format(slack_id))
        self.ddb.delete_user(slack_id)

    def store_team(self, team):
        """
        Store team into teams table.

        :param team: A team model to store
        """
        logging.info("Storing team {}".format(team.get_github_team_name()))
        self.ddb.store_team(team)

    def retrieve_team(self, team_name):
        """
        Retrieve team from teams table.

        :param team_name: used as key for retrieving team objects.
        :raise: LookupError if team name is not found.
        :return: returns a team model if slack id is found.
        """
        logging.info("Retrieving team {}".format(team_name))
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
        logging.info("Querying teams matching parameters: {}".
                     format(parameter))
        return self.ddb.query_team(parameter)

    def delete_team(self, team_name):
        """
        Remove a team from the teams table.

        :param team_name: the team_name of the team to be removed
        """
        logging.info("Deleting team {}".format(team_name))
        self.ddb.delete_team(team_name)

    def store_project(self, project):
        """
        Store project into projects table.

        :param project: A project model to store
        """
        logging.info("Storing project " + project.get_project_id())
        self.ddb.store_project(project)

    def retrieve_project(self, project_id):
        """
        Retrieve project from projects table.

        :param project_id: used as key for retrieving project objects.
        :raise: LookupError if project id is not found.
        :return: returns a project model if slack id is found.
        """
        logging.info("Retrieving project " + project_id)
        return self.ddb.retrieve_project(project_id)

    def query_project(self, parameters):
        """
        Query for specific projects by parameter.

        Returns list of teams that have **all** of the attributes specified in
        the parameters. Every item in parameters is a tuple, where the first
        element is the project attribute, and the second is the value.

        Example: ``[('tags', 'c++')]`` would get all projects with ``c++``
        (case sensitive) in their tags.

        :param parameters: list of parameters (tuples)
        :return: returns a list of project models that fit the query parameters
        """
        logging.info("Querying projects matching parameters: {}"
                     .format(parameters))
        return self.ddb.query_project(parameters)

    def delete_project(self, project_id):
        """
        Remove a project from the projects table.

        :param project_id: the project ID of the project to be removed
        """
        logging.info("Deleting project " + project_id)
        self.ddb.delete_project(project_id)
