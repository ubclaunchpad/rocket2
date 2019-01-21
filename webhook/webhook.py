"""Contain all the logic for handling webhooks in a class."""
import json
import logging


class WebhookHandler:
    """Encapsulate methods for GitHub webhook triggered events."""

    def __init__(self, db_facade):
        """Give handler access to the database."""
        self.__facade = db_facade

    def handle_organization_event(self, payload):
        """
        Handle when a user is added, removed, or invited to an organization.

        If the member is removed, they are removed as a user from rocket's db
        if they have not been removed already.

        If the member is added or invited, do nothing.
        """
        payload_dict = json.loads(payload)
        action = payload_dict["action"]
        github_user = payload_dict["membership"]["user"]
        github_id = github_user["id"]
        github_username = github_user["login"]
        organization = payload_dict["organization"]["login"]
        if action == "member_removed":
            member_list = self.__facade.\
                query_user(['github_id', github_id])
            if len(member_list) > 0:
                for member in member_list:
                    slack_id = member.get_slack_id()
                    self.__facade.delete_user(slack_id)
                    logging.info("deleted slack user {}".format(slack_id))
            else:
                logging.error("could not find user {}".format(github_id))
        elif action == "member_added":
            logging.info("user {} added to {}".
                         format(github_username, organization))
        elif action == "member_invited":
            logging.info("user {} invited to {}".
                         format(github_username, organization))
        else:
            logging.error(("organization webhook triggered,"
                           " invalid action specified: " + payload))
