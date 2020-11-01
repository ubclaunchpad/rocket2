import boto3
import logging

from boto3.dynamodb.conditions import Attr
from functools import reduce, wraps
from app.model import User, Team, Project, Pairing
from typing import Tuple, List, Type, TypeVar
from config import Config
from db.facade import DBFacade

T = TypeVar('T', User, Team, Project, Pairing)


def fragment(items_per_call=100):
    def decor_fragment(func):
        @wraps(func)
        def wrapper_fragment(*args, **kwargs):
            results = []
            for i in range(0, len(args[2]), items_per_call):
                results.extend(
                    func(args[0],
                         args[1],
                         args[2][i: i + items_per_call])
                )
            return results
        return wrapper_fragment
    return decor_fragment


class DynamoDB(DBFacade):
    """
    Handles calls to database through API.

    Please do not use this class, and instead use :class:`db.facade.DBFacade`.
    This class only works on DynamoDB, and should not be used outside of the
    facade class.
    """

    class Const:
        """
        A bunch of static constants and functions.

        Used to convert between Python objects and the DDB table names, object
        attributes and table column names.
        """

        def __init__(self, config: Config):
            """Initialize the constants."""
            self.users_table: str = config.aws_users_tablename
            self.teams_table: str = config.aws_teams_tablename
            self.projects_table: str = config.aws_projects_tablename
            self.pairings_table: str = config.aws_pairings_tablename

        def get_table_name(self, cls: Type[T]) -> str:
            """
            Convert class into corresponding table name.

            :param cls: Either ``User``, ``Team``, or ``Project``
            :raises: TypeError if it is not either User, Team, or Project
            :return: table name string
            """
            if cls == User:
                return self.users_table
            elif cls == Team:
                return self.teams_table
            elif cls == Project:
                return self.projects_table
            elif cls == Pairing:
                return self.pairings_table
            else:
                raise TypeError('Type of class one of [User, Team, Project]')

        def get_key(self, table_name: str) -> str:
            """
            Get primary key of the table name.

            :param cls: the name of the table
            :raises: TypeError if table does not exist
            :return: primary key of the table
            """
            if table_name == self.users_table:
                return 'slack_id'
            elif table_name == self.teams_table:
                return 'github_team_id'
            elif table_name == self.projects_table:
                return 'project_id'
            elif table_name == self.pairings_table:
                return 'pairing_id'
            else:
                raise TypeError('Table name does not correspond to anything')

        def get_set_attrs(self, table_name: str) -> List[str]:
            """
            Get class attributes that are sets.

            :param cls: the table name
            :raises: TypeError if table does not exist
            :return: set attributes
            """
            if table_name == self.users_table or \
               table_name == self.pairings_table:
                return []
            elif table_name == self.teams_table:
                return ['team_leads', 'members']
            elif table_name == self.projects_table:
                return ['tags', 'github_urls']
            else:
                raise TypeError('Table name does not correspond to anything')

    def __init__(self, config: Config):
        """
        Initialize facade using DynamoDB settings.

        To avoid local tests failure when the DynamoDb server is used,
        an environment variable ``config.aws_local`` is read.

        .. code:: python

            if config.aws_local:
                # Connect to locally-run instance of DynamoDB
                pass
            else:
                # Connect to remote instance of DynamoDB
                pass

        :param config: configuration used to initialize
        """
        logging.info("Initializing DynamoDb")
        self.users_table = config.aws_users_tablename
        self.teams_table = config.aws_teams_tablename
        self.projects_table = config.aws_projects_tablename
        self.pairings_table = config.aws_pairings_tablename
        self.CONST = DynamoDB.Const(config)

        if config.aws_local:
            logging.info("Connecting to local DynamoDb")
            self.ddb = boto3.resource(service_name="dynamodb",
                                      region_name="",
                                      aws_access_key_id="",
                                      aws_secret_access_key="",
                                      endpoint_url="http://localhost:8000")
        else:
            logging.info("Connecting to remote DynamoDb")
            region_name = config.aws_region
            access_key_id = config.aws_access_keyid
            secret_access_key = config.aws_secret_key
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
        if not self.check_valid_table(self.pairings_table):
            self.__create_table(self.pairings_table)
            self.__enable_ttl(self.pairings_table)

    def __create_table(self, table_name: str, key_type: str = 'S'):
        """
        Create a table.

        **Note**: This function should **not** be called externally, and should
        only be called on initialization.

        :param table_name: name of the table to create
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

    def __enable_ttl(self, table_name: str):
        """
        Enable automatically dropping entries on TTL expiry

        **Note**: This function should **not** be called externally, and should
        only be called on initialization.

        :param table_name: name of the table to enable ttl for
        """
        # Stub

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
        Model = obj.__class__
        if Model not in [User, Team, Project, Pairing]:
            logging.error(f"Cannot store object {str(obj)}")
            raise RuntimeError(f'Cannot store object{str(obj)}')

        # Check if object is valid
        if Model.is_valid(obj):
            table_name = self.CONST.get_table_name(Model)
            table = self.ddb.Table(table_name)
            d = Model.to_dict(obj)

            logging.info(f"Storing obj {obj} in table {table_name}")
            table.put_item(Item=d)
            return True
        return False

    def retrieve(self, Model: Type[T], k: str) -> T:
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
        table_name = self.CONST.get_table_name(Model)
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

    @fragment(100)
    def query_or(self,
                 Model: Type[T],
                 params: List[Tuple[str, str]] = []) -> List[T]:

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

    def delete(self, Model: Type[T], k: str):
        logging.info(f"Deleting {Model.__name__}(id={k})")
        table_name = self.CONST.get_table_name(Model)
        table = self.ddb.Table(table_name)
        table.delete_item(
            Key={
                self.CONST.get_key(table_name): k
            }
        )

    def delete_all(self, Model: Type[T]):
        logging.info(f"Deleting {Model.__name__}")
        table_name = self.CONST.get_table_name(Model)
        table = self.ddb.Table(table_name)
        table.delete()
        table.wait_until_not_exists()
        self.__create_table(table_name)
