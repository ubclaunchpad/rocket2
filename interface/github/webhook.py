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

        If the member was added, the member's GitHub id is used as the primary
        key in rocket's db.

        If the member is removed, they are removed as a user from rocket's db
        if they have not been removed already.

        If the member is invited, do nothing.
        """
        payload_dict = json.loads(payload)
        action = payload_dict["action"]
        github_user = payload_dict["membership"]["user"]
        github_id = github_user["id"]
        if action == "member_added":
            github_name = github_user["login"]
            member_list = self.__facade.\
                query_user(['github_name', github_name])
            if len(member_list) < 1:
                logging.error(("GitHub user {} "
                               "could not be found").format(github_name))
            elif len(member_list) > 1:
                logging.error(("More than one user with "
                               "GitHub name {} found").format(github_name))
            else:
                member = member_list[0]
                member.set_github_id(github_id)
                logging.info(("GitHub user {}'s GitHub Id set "
                              "to {}").format(github_name, github_id))
        elif action == "member_removed":
            member_list = self.__facade.\
                query_user(['github_id', github_id])
            try:
                member = member_list[0]
                slack_id = member.get_slack_id()
                self.__facade.delete_user(slack_id)
                logging.info("deleted user {}".format(slack_id))
            except IndexError:
                logging.error("could not find user {}".format(github_id))
