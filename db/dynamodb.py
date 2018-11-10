"""DynamoDB."""
import boto3
from boto3.dynamodb.conditions import Attr
from model.user import User
from model.team import Team
from model.permissions import Permissions


class DynamoDB:
    """Handles calls to database through API."""

    def __init__(self):
        """Initialize facade using DynamoDB settings (for now)."""
        # TODO change this to production and not localhost
        self.ddb = boto3.resource("dynamodb", region_name="",
                                  endpoint_url="http://localhost:8000")

        if not self.check_valid_table('users'):
            self.create_user_tables()

        if not self.check_valid_table('teams'):
            self.create_team_tables()

    def __str__(self):
        """Return a string representing this class."""
        return "DynamoDB"

    def create_user_tables(self):
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

    def create_team_tables(self):
        """Create the team table, for testing."""
        self.ddb.create_table(
            TableName='teams',
            AttributeDefinitions=[
                {
                    'AttributeName': 'github_team_name',
                    'AttributeType': 'S'
                },
            ],
            KeySchema=[
                {
                    'AttributeName': 'github_team_name',
                    'KeyType': 'HASH'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 50,
                'WriteCapacityUnits': 50
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

    def store_user(self, user):
        """
        Store user into users table.

        :param user: A user model to store
        :returns: Returns true if the user was stored, and false otherwise
        """
        # Check that there are no blank fields in the user
        if User.is_valid(user):
            user_table = self.ddb.Table('users')
            user_table.put_item(
                Item={
                    'slack_id': user.get_slack_id(),
                    'email': user.get_email(),
                    'name': user.get_name(),
                    'github': user.get_github_username(),
                    'major': user.get_major(),
                    'position': user.get_position(),
                    'bio': user.get_biography(),
                    'image_url': user.get_image_url(),
                    'permission_level': user.get_permissions_level().name
                }
            )
            return True
        return False

    def store_team(self, team):
        """
        Store team into teams table.

        :param team: A team model to store
        """
        teams_table = self.ddb.Table('teams')
        teams_table.put_item(
            Item={
                'github_team_name': team.get_github_team_name(),
                'display_name': team.get_display_name(),
                'platform': team.get_platform(),
                'members': team.get_members()
            }
        )

    def retrieve_user(self, slack_id):
        """
        Retrieve user from users table.

        :return: returns a user model if slack id is found.
        """
        user_table = self.ddb.Table('users')
        response = user_table.get_item(
            TableName='users',
            Key={
                'slack_id': slack_id
            }
        )

        return self.user_from_dict(response['Item'])

    @staticmethod
    def user_from_dict(d):
        """
        Convert dict response object to user model.

        :return: returns converted user model.
        """
        user = User(d['slack_id'])
        user.set_email(d['email'])
        user.set_name(d['name'])
        user.set_github_username(d['github'])
        user.set_major(d['major'])
        user.set_position(d['position'])
        user.set_biography(d['bio'])
        user.set_image_url(d['image_url'])
        user.set_permissions_level(Permissions[d['permission_level']])
        return user

    def retrieve_team(self, team_name):
        """
        Retrieve team from teams table.

        :param: team_name: used as key for retrieving team objects.
        :raise: raises a LookupError if team id is not found.
        :return: the team object if team_name is found.
        """
        team_table = self.ddb.Table('teams')
        response = team_table.get_item(
            TableName='teams',
            Key={
                'github_team_name': team_name
            }
        )
        if 'Item' in response.keys():
            return self.team_from_dict(response['Item'])
        else:
            raise LookupError('Team "{}" not found'.format(team_name))

    @staticmethod
    def team_from_dict(d):
        """
        Convert dict response object to team model.

        :return: returns converted team model.
        """
        team = Team(d['github_team_name'], d['display_name'])
        team.set_platform(d['platform'])
        members = set(d['members'])
        for member in members:
            team.add_member(member)
        return team

    def query_user(self, parameters):
        """
        Query for specific users by parameter.

        Returns list of users that have **all** of the attributes specified in
        the parameters. Every item in parameters is a tuple, where the first
        element is the user attribute, and the second is the value.

        Example: [('permission_level', 'admin')]

        If parameters is an empty list, returns all the users.

        :param parameters: list of parameters (tuples)
        :return: returns a list of user models that fit the query parameters.
        """
        users = self.ddb.Table('users')
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

        return list(map(self.user_from_dict, response['Items']))

    def query_team(self, parameters):
        """
        Query for teams using list of parameters.

        Returns list of teams that have **all** of the attributes specified in
        the parameters. Every item in parameters is a tuple, where the first
        element is the user attribute, and the second is the value.

        Example: [('permission_level', 'admin')]

        :param parameters:
        :return: returns a list of user models that fit the query parameters.
        """
        teams = self.ddb.Table('teams')
        if len(parameters) > 0:
            # There are 1 or more parameters that we should care about
            if parameters[0][0] == 'members':
                filter_expr = Attr(parameters[0][0]).contains(parameters[0][1])
            else:
                filter_expr = Attr(parameters[0][0]).eq(parameters[0][1])

            for p in parameters[1:]:
                if p[0] == 'members':
                    filter_expr &= Attr(p[0]).contains(p[1])
                else:
                    filter_expr &= Attr(p[0]).eq(p[1])

            response = teams.scan(
                FilterExpression=filter_expr
            )
        else:
            # No parameters; return all users in table
            response = teams.scan()

        return list(map(self.team_from_dict, response['Items']))

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

    def delete_team(self, team_name):
        """
        Remove a team from the teams table.

        :param team_name: the team_name of the team to be removed
        """
        team_table = self.ddb.Table('teams')
        team_table.delete_item(
            Key={
                'github_team_name': team_name
            }
        )
