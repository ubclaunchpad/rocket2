"""Command to obtain signed authentication token."""
import logging
import jwt

from model.permissions import Permissions
from datetime import datetime, timedelta


class TokenCommand:
    """Token command model class."""

    command_name = "token"
    desc = "Generate a signed token for use with the HTTP API"
    permission_error = "You do not have the sufficient " \
                       "permission level for this command!"
    lookup_error = "Requesting user not found!"

    def __init__(self, db_facade):
        """
        Initialize TokenCommand.

        :param db_facade: Database connection
        """
        logging.info("Initializing TokenCommand instance")
        self.facade = db_facade
        self.key = ";alskdjf;alh;alsdjf;aklsdjfl;"

    def get_name(self):
        """Return the command's name."""
        return self.command_name

    def get_desc(self):
        """Return a description of the command."""
        return self.desc

    def handle(self, _command, user_id):
        """Handle request for token."""
        logging.debug("Handling token command")
        try:
            lead_user = self.facade.retrieve_user(user_id)
            if lead_user.get_permissions_level() == Permissions.member:
                return self.permission_error, 403
        except LookupError:
            return self.lookup_error, 404
        expiry = datetime.utcnow() + timedelta(days=7)
        payload = {
            'nbf': datetime.utcnow(),
            # TODO make this configurable
            'exp': expiry,
            'iss': 'ubclaunchpad:rocket2',
            'iat': datetime.utcnow(),
            'user_id': user_id
        }
        token = jwt.encode(payload, self.key, algorithm='HS256') \
            .decode('utf-8')
        return "This is your token:\n```\n{}".format(token) + \
               "\n```\nKeep it secret! Keep it safe!\n" \
               "It will expire at {}.".format(expiry), \
               200
