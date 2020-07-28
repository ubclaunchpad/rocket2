"""Command to obtain signed authentication token."""
import jwt
import logging

from app.controller import ResponseTuple
from app.controller.command.commands.base import Command
from datetime import datetime, timedelta
from db.facade import DBFacade
from app.model import User, Permissions
from utils.slack_msg_fmt import wrap_code_block


class TokenCommand(Command):
    """Token command model class."""

    command_name = "token"
    desc = "Generate a signed token for use with the HTTP API"
    permission_error = "You do not have the sufficient " \
                       "permission level for this command!"
    lookup_error = "Requesting user not found!"
    success_msg = f"This is your token:\n{wrap_code_block('{}')}" \
                  "\nKeep it secret! Keep it safe!\nIt will expire at {}."

    def __init__(self,
                 db_facade: DBFacade,
                 config: 'TokenCommandConfig'):
        """
        Initialize TokenCommand.

        :param db_facade: Database connection
        :param config: :class:`app.controller.command.commands
                               .TokenCommandConfig` object
        """
        logging.info("Initializing TokenCommand instance")
        self.facade = db_facade
        self.expiry = config.expiry
        self.signing_key = config.signing_key

    def handle(self,
               _command: str,
               user_id: str) -> ResponseTuple:
        """Handle request for token."""
        logging.debug("Handling token command")
        try:
            user = self.facade.retrieve(User, user_id)
            if user.permissions_level == Permissions.member:
                return self.permission_error, 200
        except LookupError:
            return self.lookup_error, 200
        expiry = datetime.utcnow() + self.expiry
        payload = {
            'nbf': datetime.utcnow(),
            'exp': expiry,
            'iss': 'ubclaunchpad:rocket2',
            'iat': datetime.utcnow(),
            'user_id': user_id,
            'permissions': user.permissions_level.value
        }
        token = jwt.encode(payload, self.signing_key, algorithm='HS256') \
            .decode('utf-8')
        return self.success_msg.format(token, expiry), 200


class TokenCommandConfig:
    """Configuration options for TokenCommand."""

    def __init__(self,
                 expiry: timedelta,
                 signing_key: str):
        """Initialize config for TokenCommand."""
        self.expiry = expiry
        self.signing_key = signing_key
