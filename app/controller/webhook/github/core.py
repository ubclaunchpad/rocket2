"""Handle GitHub webhooks."""
import logging
import hmac
import hashlib
from db.facade import DBFacade
from interface.github import GithubInterface
from typing import Dict, Any
from app.controller import ResponseTuple
from config import Config
from app.controller.webhook.github.events import MembershipEventHandler, \
    OrganizationEventHandler, TeamEventHandler


class GitHubWebhookHandler:
    """Encapsulate the handlers for all GitHub webhook events."""

    def __init__(self,
                 db_facade: DBFacade,
                 gh_face: GithubInterface,
                 config: Config):
        """Give handlers access to the database."""
        self.__secret = config.github_webhook_secret
        self.__event_handlers = [
            OrganizationEventHandler(db_facade, gh_face, config),
            TeamEventHandler(db_facade, gh_face, config),
            MembershipEventHandler(db_facade, gh_face, config)
        ]

    def handle(self,
               request_body: bytes,
               xhub_signature: str,
               payload: Dict[str, Any]) -> ResponseTuple:
        """
        Verify and handle the webhook event.

        :param request_body: Byte string of the request body
        :param xhub_signature: Hashed signature to validate
        :return: appropriate ResponseTuple depending on the validity and type
                 of webhook
        """
        logging.debug(f"payload: {str(payload)}")
        if self.verify_hash(request_body, xhub_signature):
            action = payload["action"]
            for event_handler in self.__event_handlers:
                if action in event_handler.supported_action_list:
                    return event_handler.handle(payload)
            return "Unsupported payload received", 500
        else:
            return "Hashed signature is not valid", 403

    def verify_hash(self, request_body: bytes, xhub_signature: str):
        """
        Verify if a webhook event comes from GitHub.

        :param request_body: Byte string of the request body
        :param xhub_signature: Hashed signature to validate
        :return: Return True if the signature is valid, False otherwise
        """
        h = hmac.new(bytes(self.__secret, encoding='utf8'),
                     request_body, hashlib.sha1)
        verified = hmac.compare_digest(
            bytes("sha1=" + h.hexdigest(), encoding='utf8'),
            bytes(xhub_signature, encoding='utf8'))
        if verified:
            logging.debug("Webhook signature verified")
        else:
            logging.warning(
                f"Webhook not from GitHub; signature: {xhub_signature}")
        return verified
