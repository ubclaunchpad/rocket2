"""DynamoDB."""
import boto3
from model.user import User


class DynamoDB:
    """DynamoDB."""

    def __init__(self):
        """Initialize facade using DynamoDB settings (for now)."""
        # TODO change this to production and not localhost
        self.ddb = boto3.resource("dynamodb", region_name="",
                                  endpoint_url="http://localhost:8000")

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

    def retrieve_user(self, slack_id):
        """
        TODO: Retrieve user from users table.s

        :return: returns a user model if slack id is found.
        """
        user_table = self.ddb.Table('users')
        user = user_table.get_item(
            Key={
                'slack_id': slack_id
            }
        )
        return user

    def query_user(self, parameters):
        """
        TODO: Query for specific users by parameter.

        Query using a list of parameters (tuples), where the first element of
        the tuple is the item attribute, second being the item value.

        Example: [('permission_level', 'admin')]

        :param parameters: list of parameters (tuples)
        :return: returns a list of user models that fit the query parameters.
        """
        return []
