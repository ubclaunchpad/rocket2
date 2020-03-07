"""Encapsulate the common business logic of token commands."""
import jwt
import logging

from datetime import datetime, timedelta
from app.model import User, Permissions
from db.facade import DBFacade


class TokenCommandApis:
    """Encapsulate the various APIs for token command logic."""

    token_permission_error = "You do not have the sufficient " \
                             "permission level for this command!"
    token_lookup_error = "Requesting user not found!"

    def __init__(self):
        """
        Initialize TokenCommand.

        :param db__db_facade: Database connection
        :param config: :class:`app.controller.command.commands
                               .TokenCommandConfig` object
        """
        logging.info("Initializing TokenCommand instance")
        self._db_facade: DBFacade = None
        self.expiry = None
        self.signing_key = None

    def handle_token_request(self,
                             user_id: str,
                             expiry: timedelta,
                             signing_key: str) -> str:
        """Handle request for token."""
        try:
            user = self._db_facade.retrieve(User, user_id)
            if user.permissions_level == Permissions.member:
                return self.token_permission_error
        except LookupError:
            return self.token_lookup_error
        exp = datetime.utcnow() + expiry
        payload = {
            'nbf': datetime.utcnow(),
            'exp': exp,
            'iss': 'ubclaunchpad:rocket2',
            'iat': datetime.utcnow(),
            'user_id': user_id,
            'permissions': user.permissions_level.value
        }
        token = jwt.encode(payload, signing_key, algorithm='HS256') \
            .decode('utf-8')
        format(token)
        return token
