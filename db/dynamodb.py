"""DynamoDB."""
import boto3
from boto3.dynamodb.conditions import Attr
from model.user import User
from model.permissions import Permissions
from functools import reduce


class DynamoDB:
    """DynamoDB."""

    def __init__(self):
        """Initialize facade using DynamoDB settings (for now)."""
        # TODO change this to production and not localhost
        self.ddb = boto3.resource("dynamodb", region_name="",
                                  endpoint_url="http://localhost:8000")

        if not self.check_valid_table('users'):
            self.create_tables()

    def __str__(self):
        """Return a string representing this class."""
        return "DynamoDB"

    def create_tables(self):
        """Create the user table, for testing."""
        self.ddb.create_table(
            TableName='users',
            AttributeDefinitions=[
                {
                    'AttributeName': 'slack_id',
                    'AttributeType': 'S'
                },
            ],
            KeySchema=[
                {
                    'AttributeName': 'slack_id',
                    'KeyType': 'HASH'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 50,
                'WriteCapacityUnits': 50
            }
        )

    def store_user(self, user):
        """
        Store user into users table.

        :param user: A user model to store
        """
        # Assume that the tables are already set up this way
        user_table = self.ddb.Table('users')
        user_table.put_item(
            Item={
                'slack_id': user.get_slack_id(),
                'email': user.get_email(),
                'github': user.get_github_username(),
                'major': user.get_major(),
                'position': user.get_position(),
                'bio': user.get_biography(),
                'image_url': user.get_image_url(),
                'permission_level': user.get_permissions_level().name
            }
        )

    def check_valid_table(self, table_name):
        """
        Check if table with table_name exists.

        :param table_name: table identifier
        :return: boolean value, true if table exists, false otherwise
        """
        existing_tables = self.ddb.tables.all()
        return any(map(lambda t: t.name == table_name, existing_tables))

    def retrieve_user(self, slack_id):
        """
        Retrieve user from users table.

        :return: returns a user model if slack id is found.
        """
        user = User(slack_id)
        user_table = self.ddb.Table('users')
        response = user_table.get_item(
            TableName='users',
            Key={
                'slack_id': slack_id
            }
        )
        response = response['Item']

        user.set_email(response['email'])
        user.set_github_username(response['github'])
        user.set_major(response['major'])
        user.set_position(response['position'])
        user.set_biography(response['bio'])
        user.set_image_url(response['image_url'])
        user.set_permissions_level(Permissions[response['permission_level']])

        return user

    def query_user(self, parameters):
        """
        Query for specific users by parameter.

        Query using a list of parameters (tuples), where the first element of
        the tuple is the item attribute, second being the item value.

        Example: [('permission_level', 'admin')]

        If parameters is an empty list, returns all the users.

        :param parameters: list of parameters (tuples)
        :return: returns a list of user models that fit the query parameters.
        """
        user_list = []
        users = self.ddb.Table('users')
        response = None
        if len(parameters) > 0:
            # There are 1 or more parameters that we should care about
            filter_expr = Attr(parameters[0][0]).eq(parameters[0][1])

            for p in parameters[1:]:
                filter_expr &= Attr(p[0]).eq(p[1])

            response = users.scan(
                FilterExpression=filter_expr
            )
        else:
            # No parameters; return all users in table
            response = users.scan()

        for r in response['Items']:
            slack_id = r['slack_id']
            user = User(slack_id)

            user.set_email(r['email'])
            user.set_github_username(r['github'])
            user.set_major(r['major'])
            user.set_position(r['position'])
            user.set_biography(r['bio'])
            user.set_image_url(r['image_url'])
            user.set_permissions_level(Permissions[r['permission_level']])

            user_list.append(user)
        return user_list

    def delete_user(self, slack_id):
        """
        Remove a user from the users table.

        :param slack_id: the slack_id of the user to be removed
        """
        user_table = self.ddb.Table('users')

        user_table.delete_item(
            Key={
                'slack_id': slack_id
            }
        )
