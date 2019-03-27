"""DynamoDB."""
import boto3
import logging
import toml

from boto3.dynamodb.conditions import Attr
from functools import reduce
from model import User, Team, Project, Permissions
from typing import Dict, Optional, Any, Tuple, List, Type, Sequence, TypeVar

T = TypeVar('T', User, Team, Project)


class DynamoDB:
    """
    Handles calls to database through API.

    Please do not use this class, and instead use :class:`db.facade.DBFacade`.
    This class only works on DynamoDB, and should not be used outside of the
    facade class.
    """

    class Const:
        """A bunch of static constants and functions."""

        def __init__(self, config: Dict[str, str]) -> None:
            """Initialize the constants."""
            self.users_table = config['users_table']
            self.teams_table = config['teams_table']
            self.projects_table = config['projects_table']

        def get_table_name(self,
                           cls: Type[T]) -> str:
            """
            Convert class into corresponding table name.

            :param cls: Either ``User``, ``Team``, or ``Project``
            :raise: TypeError if it is not either User, Team, or Project
            :return: table name string
            """
            if cls == User:
                return self.users_table
            elif cls == Team:
                return self.teams_table
            elif cls == Project:
                return self.projects_table
            else:
                raise TypeError('Type of class one of [User, Team, Project]')

        def get_key(self, table_name: str) -> str:
            """
            Get primary key of the table name.

            :param cls: the name of the table
            :raise: TypeError if table does not exist
            :return: primary key of the table
            """
            if table_name == self.users_table:
                return 'slack_id'
            elif table_name == self.teams_table:
                return 'github_team_id'
            elif table_name == self.projects_table:
                return 'project_id'
            else:
                raise TypeError('Table name does not correspond to anything')

        def get_set_attrs(self, table_name: str) -> List[str]:
            """
            Get class attributes that are sets.

            :param cls: the table name
            :raise: TypeError if table does not exist
            :return: list of strings of set attributes
            """
            if table_name == self.users_table:
                return []
            elif table_name == self.teams_table:
                return ['members']
            elif table_name == self.projects_table:
                return ['tags', 'github_urls']
            else:
                raise TypeError('Table name does not correspond to anything')

    def __init__(self, config: Dict[str, Any], credentials) -> None:
        """Initialize facade using DynamoDB settings.

        To avoid local tests failure when the DynamoDb server is used,
        a testing environment variable is set.
        When testing environmental variable is true,
        the local dynamodb is run.
        When testing environmental variable is true,
        the server dynamodb is run.

        boto3.resource() takes in a service_name, region_name, and endpoint_url
        (only for local dynamodb).
        service_name: The name of a service, "dynamodb" in this case.
        region_name:  The name of the region associated with the client.
        A list of different regions can be obtained online.
        endpoint_url: The complete URL to use for the constructed client.

        Boto3 server require environmental variables for credentials:
        AWS_ACCESS_KEY_ID: The access key for your AWS account.
        AWS_SECRET_ACCESS_KEY: The secret key for the AWS account
        AWS_SESSION_TOKEN: The session key for your AWS account.
        This is only needed when you are using temporary credentials.
        """
        logging.info("Initializing DynamoDb")
        self.users_table = config['aws']['users_table']
        self.teams_table = config['aws']['teams_table']
        self.projects_table = config['aws']['projects_table']
        testing = config['testing']
        self.CONST = DynamoDB.Const({'users_table': self.users_table,
                                     'teams_table': self.teams_table,
                                     'projects_table': self.projects_table})

        if testing:
            logging.info("Connecting to local DynamoDb")
            self.ddb = boto3.resource(service_name="dynamodb",
                                      region_name="",
                                      aws_access_key_id="",
                                      aws_secret_access_key="",
                                      endpoint_url="http://localhost:8000")
        else:
            logging.info("Connecting to remote DynamoDb")
            region_name = config['aws']['region']
            access_key_id = credentials.aws_access_key_id
            secret_access_key = credentials.aws_secret_access_key
            self.ddb = boto3.resource(service_name='dynamodb',
                                      region_name=region_name,
                                      aws_access_key_id=access_key_id,
                                      aws_secret_access_key=secret_access_key)

        # Check for missing tables
        if not self.check_valid_table(self.users_table):
            self.__create_table(self.users_table)
        if not self.check_valid_table(self.teams_table):
            self.__create_table(self.teams_table)
        if not self.check_valid_table(self.projects_table):
            self.__create_table(self.projects_table)

    def __str__(self) -> str:
        """Return a string representing this class."""
        return "DynamoDB"

    def __create_table(self, table_name: str, key_type: str = 'S') -> None:
        """
        Create a table.

        **Note**: This function should **not** be called externally, and should
        only be called on initialization.

        :param table_name: name of the table to create
        :param primary_key: name of the primary key for the table
        :param key_type: type of primary key (S, N, B)
        """
        logging.info(f"Creating table '{table_name}'")
        primary_key = self.CONST.get_key(table_name)
        self.ddb.create_table(
            TableName=table_name,
            AttributeDefinitions=[
                {
                    'AttributeName': primary_key,
                    'AttributeType': key_type
                },
            ],
            KeySchema=[
                {
                    'AttributeName': primary_key,
                    'KeyType': 'HASH'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        )

    def check_valid_table(self, table_name: str) -> bool:
        """
        Check if table with ``table_name`` exists.

        :param table_name: table identifier
        :return: boolean value, true if table exists, false otherwise
        """
        existing_tables = self.ddb.tables.all()
        return any(map(lambda t: bool(t.name == table_name),
                       existing_tables))

    def store(self, obj: T) -> bool:
        """
        Store object into the correct table.

        Object can be of type :class:`model.user.User`,
        :class:`model.team.Team`, or :class:`model.project.Project`.

        :param obj: Object to store in database
        :return: True if object was stored, and false otherwise
        """
        Model: Optional[Type[T]] = None
        if isinstance(obj, User):
            Model = User
        elif isinstance(obj, Team):
            Model = Team
        elif isinstance(obj, Project):
            Model = Project
        else:
            logging.error(f"Cannot store object {str(obj)}")
            raise RuntimeError(f'Cannot store object{str(obj)}')

        # Check if object is valid
        if Model.is_valid(obj):  # type: ignore
            table_name = self.CONST.get_table_name(Model)
            table = self.ddb.Table(table_name)
            d = Model.to_dict(obj)  # type: ignore

            logging.info(f"Storing obj {obj} in table {table_name}")
            table.put_item(Item=d)
            return True
        return False

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
        table_name = self.CONST.get_table_name(Model)
        table = self.ddb.Table(table_name)
        resp = table.get_item(
            TableName=table_name,
            Key={
                self.CONST.get_key(table_name): k
            }
        )

        if 'Item' in resp.keys():
            return Model.from_dict(resp['Item'])
        else:
            err_msg = f'{Model.__name__}(id={k}) not found'
            logging.info(err_msg)
            raise LookupError(err_msg)

    def bulk_retrieve(self, Model: Type[T], ks: List[str]) -> List[T]:
        """
        Retrieve a list of models from the database.

        Keys not found in the database will be skipped.

        :param Model: the actual class you want to retrieve
        :param ks: retrieve based on this key (or ID)
        :return: a list of models ``Model``
        """
        table_name = self.CONST.get_table_name(Model)
        table = self.ddb.Table(table_name)
        resp = self.ddb.batch_get_item(
            RequestItems={
                table_name: {
                    'Keys': [{self.CONST.get_key(table_name): k} for k in ks]
                }
            }
        )

        if 'Responses' not in resp:
            return []

        resp_models = resp['Responses'].get(table_name, [])
        return list(map(Model.from_dict, resp_models))

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
        table_name = self.CONST.get_table_name(Model)
        table = self.ddb.Table(table_name)
        set_attrs = self.CONST.get_set_attrs(table_name)
        if len(params) > 0:
            def f(x):
                if x[0] in set_attrs:
                    return Attr(x[0]).contains(x[1])
                else:
                    return Attr(x[0]).eq(x[1])

            filter_expr = reduce(lambda a, x: a & x, map(f, params))
            resp = table.scan(FilterExpression=filter_expr)
        else:
            resp = table.scan()

        return list(map(Model.from_dict, resp['Items']))

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

            projects = ddb.query_or(Project)

        Attributes that are sets (e.g. ``team.member``,
        ``project.github_urls``) would be treated differently. This function
        would check to see if the entry **contains** a certain element. You can
        specify multiple elements, but they must be in different parameters
        (one element per tuple).::

            teams = ddb.query_or(Team, [('members', 'abc123'),
                                        ('members', '231abc')])

        The above would get you the teams that contain either member ``abc123``
        or ``231abc``.

        :param Model: type of list elements you'd want
        :param params: list of tuples to match
        :return: a list of ``Model`` that fit the query parameters
        """
        table_name = self.CONST.get_table_name(Model)
        table = self.ddb.Table(table_name)
        set_attrs = self.CONST.get_set_attrs(table_name)
        if len(params) > 0:
            def f(x):
                if x[0] in set_attrs:
                    return Attr(x[0]).contains(x[1])
                else:
                    return Attr(x[0]).eq(x[1])

            filter_expr = reduce(lambda a, x: a | x, map(f, params))
            resp = table.scan(FilterExpression=filter_expr)
        else:
            resp = table.scan()

        return list(map(Model.from_dict, resp['Items']))

    def delete(self,
               Model: Type[T],
               k: str) -> None:
        """
        Remove an object from a table.

        :param Model: table type to remove the object from
        :param k: ID or key of the object to remove (must be primary key)
        """
        logging.info(f"Deleting {Model.__name__}(id={k})")
        table_name = self.CONST.get_table_name(Model)
        table = self.ddb.Table(table_name)
        table.delete_item(
            Key={
                self.CONST.get_key(table_name): k
            }
        )
