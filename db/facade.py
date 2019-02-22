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

    def store(self, obj):
        """
        Store object into the correct table.

        Object can be of type :class:`model.user.User`,
        :class:`model.team.Team`, or :class:`model.project.Project`.

        :param obj: Object to store in database
        :return: True if object was stored, and false otherwise
        """
        logging.info("Storing object {}".format(obj))
        self.ddb.store(obj)

    def retrieve(self, Model, k):
        """
        Retrieve a model from the database.

        :param Model: the actual class you want to retrieve
        :param k: retrieve based on this key (or ID)
        :raise: LookupError if key is not found
        :return: a model ``Model`` if key is found
        """
        logging.info("Retrieving {}(id={})".format(Model.__name__, k))
        return self.ddb.retrieve(Model, k)

    def query(self, Model, params=[]):
        """
        Query a table using a list of parameters.

        Returns a list of ``Model`` that have **all** of the attributes
        specified in the parameters. Every item in parameters is a tuple, where
        the first element is the user attribute, and the second is the value.

        Example::

            ddb = DynamoDb(config)
            users = ddb.query(User, [('platform', 'slack')])

        If you try to query a table without any parameters, the function returns
        all objects of that table.::

<<<<<<< HEAD
        :param project: A project model to store
        """
        logging.info("Storing project " + project.project_id)
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
=======
            projects = ddb.query(Project)
>>>>>>> Fix all pytests

        Attributes that are sets (e.g. ``team.member``, ``project.github_urls``)
        would be treated differently. This function would check to see if the
        entry **contains** a certain element. You can specify multiple elements,
        but they must be in different parameters (one element per tuple).::

            teams = ddb.query(Team, [('members', 'abc123'),
                                     ('members', '231abc')])

        :param Model: type of list elements you'd want
        :return: a list of ``Model`` that fit the query parameters
        """
        logging.info("Querying {} matching parameters: {}".
                     format(Model.__name__, params))
        return self.ddb.query(Model, params)

    def delete(self, Model, k):
        """
        Remove an object from a table.

        :param Model: table type to remove the object from
        :param k: ID or key of the object to remove (must be primary key)
        """
        logging.info("Deleting {}(id={})".format(Model.__name__, k))
        self.ddb.delete(Model, k)
