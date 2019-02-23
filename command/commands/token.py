"""Command to obtain signed authentication token."""
import jwt
import logging

from datetime import datetime
from model.permissions import Permissions


class TokenCommand:
    """Token command model class."""

    command_name = "token"
    desc = "Generate a signed token for use with the HTTP API"
    permission_error = "You do not have the sufficient " \
                       "permission level for this command!"
    lookup_error = "Requesting user not found!"
    success_msg = "This is your token:\n```\n{}\n```" \
                  "\nKeep it secret! Keep it safe!\nIt will expire at {}."

    def __init__(self, db_facade, config):
        """
        Initialize TokenCommand.

        :param db_facade: Database connection
        :param config: :class:`command.commands.TokenCommandConfig` object
        """
        logging.info("Initializing TokenCommand instance")
        self.facade = db_facade
        self.expiry = config.get_expiry()
        self.signing_key = config.get_signing_key()

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
            user = self.facade.retrieve_user(user_id)
            if user.get_permissions_level() == Permissions.member:
                return self.permission_error, 403
        except LookupError:
            return self.lookup_error, 404
        expiry = datetime.utcnow() + self.expiry
        payload = {
            'nbf': datetime.utcnow(),
            'exp': expiry,
            'iss': 'ubclaunchpad:rocket2',
            'iat': datetime.utcnow(),
            'user_id': user_id,
            'permissions': user.get_permissions_level().value
        }
        token = jwt.encode(payload, self.signing_key, algorithm='HS256') \
            .decode('utf-8')
        format(token)
        return self.success_msg.format(token, expiry), 200


class TokenCommandConfig:
    """Configuration options for TokenCommand."""

    def __init__(self, expiry, signing_key):
        """Initialize config for TokenCommand."""
        self.expiry = expiry
        self.signing_key = signing_key

    def get_expiry(self):
        """Return expiry offset, expressed as a `timedelta`."""
        return self.expiry

    def get_signing_key(self):
        """Return string containing secret authentication signing key."""
        return self.signing_key
