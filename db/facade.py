"""Database Facade."""
import boto3


class DBFacade:
    """Self-explanatory."""

    def __init__(self):
        """Initialize facade using DynamoDB settings (for now)."""
        # TODO change this to production and not localhost
        self.ddb = boto3.resource("dynamodb", region_name="",
                                  endpoint_url="http://localhost:8000")

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
        """Store user into users table."""
        # Assume that the tables are already set up this way
        user_table = self.ddb.Table('users')
        user_table.put_item(
                Item={
                    'slack_id':         user.get_slack_id(),
                    'email':            user.get_email(),
                    'github':           user.get_github_username(),
                    'major':            user.get_major(),
                    'position':         user.get_position(),
                    'bio':              user.get_biography(),
                    'image_url':        user.get_image_url(),
                    'permission_level': user.get_permissions_level().name
                    }
                )

    def retrieve_user(self, slack_id):
        """
        TODO: Retrieve user from users table.

        Returns a user model if slack id is found.
        """
        pass

    def query_user(self, parameter):
        """
        TODO: Query for specific users by parameter.

        Returns a list of user models that fit the query parameters.
        """
        pass
