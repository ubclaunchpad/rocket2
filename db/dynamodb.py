"""DynamoDB."""
import boto3
import logging
import toml
from boto3.dynamodb.conditions import Attr
from model.user import User
from model.team import Team
from model.permissions import Permissions


class DynamoDB:
    """
    Handles calls to database through API.

    Please do not use this class, and instead use :class:`db.facade.DBFacade`.
    This class only works on DynamoDB, and should not be used outside of the
    facade class.
    """

    def __init__(self, config):
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
        testing = config['testing']

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
            credentials = toml.load(config['aws']['creds_path'])
            access_key_id = credentials['access_key_id']
            secret_access_key = credentials['secret_access_key']
            self.ddb = boto3.resource(service_name='dynamodb',
                                      region_name=region_name,
                                      aws_access_key_id=access_key_id,
                                      aws_secret_access_key=secret_access_key)

        if not self.check_valid_table(self.users_table):
            self.__create_user_tables()

        if not self.check_valid_table(self.teams_table):
            self.__create_team_tables()

    def __str__(self):
        """Return a string representing this class."""
        return "DynamoDB"

    def __create_user_tables(self):
        """
        Create the user table.

        **Note**: This function should **not** be called externally, and should
        only be called on initialization.

        Users are only required to have a ``slack_id``. Since this is a NoSQL
        database, no other attributes are required.
        """
        logging.info("Creating table '{}'".format(self.users_table))
        self.ddb.create_table(
            TableName=self.users_table,
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

    def __create_team_tables(self):
        """
        Create the team table.

        **Note**: This function should **not** be called externally, and should
        only be called on initialization.

        Teams are only required to have a ``github_team_id``. Since this is a
        NoSQL database, no other attributes are required.
        """
        logging.info("Creating table '{}'".format(self.teams_table))
        self.ddb.create_table(
            TableName=self.teams_table,
            AttributeDefinitions=[
                {
                    'AttributeName': 'github_team_id',
                    'AttributeType': 'S'
                },
            ],
            KeySchema=[
                {
                    'AttributeName': 'github_team_id',
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
        Check if table with ``table_name`` exists.

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
            def place_if_filled(name, field):
                """Populate ``udict`` if ``field`` isn't empty."""
                if field:
                    udict[name] = field

            user_table = self.ddb.Table(self.users_table)
            udict = {
                'slack_id': user.get_slack_id(),
                'permission_level': user.get_permissions_level().name
            }
            place_if_filled('email', user.get_email())
            place_if_filled('name', user.get_name())
            place_if_filled('github', user.get_github_username())
            place_if_filled('github_user_id', user.get_github_id())
            place_if_filled('major', user.get_major())
            place_if_filled('position', user.get_position())
            place_if_filled('bio', user.get_biography())
            place_if_filled('image_url', user.get_image_url())

            logging.info("Storing user {} in table {}".
                         format(user.get_slack_id(), self.users_table))
            user_table.put_item(Item=udict)
            return True
        return False

    def store_team(self, team):
        """
        Store team into teams table.

        :param team: A team model to store
        :return: Returns true if stored succesfully; false otherwise
        """
        # Check that there are no blank fields in the team
        if Team.is_valid(team):
            def place_if_filled(name, field):
                """Populate ``tdict`` if ``field`` isn't empty."""
                if field:
                    tdict[name] = field

            teams_table = self.ddb.Table(self.teams_table)
            tdict = {
                'github_team_id': team.get_github_team_id(),
                'github_team_name': team.get_github_team_name()
            }
            place_if_filled('display_name', team.get_display_name())
            place_if_filled('platform', team.get_platform())
            place_if_filled('members', team.get_members())

            logging.info("Storing team {} in table {}".
                         format(team.get_github_team_name(), self.teams_table))
            teams_table.put_item(Item=tdict)
            return True
        return False

    def retrieve_user(self, slack_id):
        """
        Retrieve user from users table.

        :raises: raises LookupError if slack id is not found.
        :return: returns a user model if slack id is found.
        """
        user_table = self.ddb.Table(self.users_table)
        response = user_table.get_item(
            TableName=self.users_table,
            Key={
                'slack_id': slack_id
            }
        )

        if 'Item' in response.keys():
            return self.user_from_dict(response['Item'])
        else:
            raise LookupError('User "{}" not found'.format(slack_id))

    @staticmethod
    def user_from_dict(d):
        """
        Convert dict response object to user model.

        :return: returns converted user model.
        """
        user = User(d['slack_id'])
        user.set_email(d.get('email', ''))
        user.set_name(d.get('name', ''))
        user.set_github_username(d.get('github', ''))
        user.set_github_id(d.get('github_user_id', ''))
        user.set_major(d.get('major', ''))
        user.set_position(d.get('position', ''))
        user.set_biography(d.get('bio', ''))
        user.set_image_url(d.get('image_url', ''))
        user.set_permissions_level(Permissions[d.get('permission_level',
                                                     'members')])
        return user

    def retrieve_team(self, team_id):
        """
        Retrieve team from teams table.

        :param: team_name: used as key for retrieving team objects.
        :raise: raises a LookupError if team id is not found.
        :return: the team object if team_name is found.
        """
        team_table = self.ddb.Table(self.teams_table)
        response = team_table.get_item(
            TableName=self.teams_table,
            Key={
                'github_team_id': team_id
            }
        )

        if 'Item' in response.keys():
            return self.team_from_dict(response['Item'])
        else:
            raise LookupError('Team "{}" not found'.format(team_id))

    @staticmethod
    def team_from_dict(d):
        """
        Convert dict response object to team model.

        :return: returns converted team model.
        """
        team = Team(d['github_team_id'],
                    d['github_team_name'],
                    d.get('display_name', ''))
        team.set_platform(d.get('platform', ''))
        members = set(d.get('members', []))
        for member in members:
            team.add_member(member)
        return team

    def query_user(self, parameters):
        """
        Query for specific users by parameter.

        Returns list of users that have **all** of the attributes specified in
        the parameters. Every item in parameters is a tuple, where the first
        element is the user attribute, and the second is the value.

        Example: ``[('permission_level', 'admin')]``

        If parameters is an empty list, returns all the users.

        :param parameters: list of parameters (tuples)
        :return: returns a list of user models that fit the query parameters.
        """
        users = self.ddb.Table(self.users_table)
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

        Example: ``[('platform', 'slack')]``

        Special attribute: member
        The member attribute describes a set, so this function would check to
        see if an entry **contains** a certain member slack_id. You can specify
        multiple slack_id, but they must be in different parameters (one
        slack_id per tuple).

        :param parameters:
        :return: returns a list of team models that fit the query parameters.
        """
        teams = self.ddb.Table(self.teams_table)
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
        logging.info("Deleting user {} from table {}".
                     format(slack_id, self.users_table))
        user_table = self.ddb.Table(self.users_table)
        user_table.delete_item(
            Key={
                'slack_id': slack_id
            }
        )

    def delete_team(self, team_id):
        """
        Remove a team from the teams table.

        To obtain the team github id, you have to retrieve the team first.

        :param team_id: the team_id of the team to be removed
        """
        logging.info("Deleting team {} from table {}".
                     format(team_id, self.teams_table))
        team_table = self.ddb.Table(self.teams_table)
        team_table.delete_item(
            Key={
                'github_team_id': team_id
            }
        )
