"""Handle GitHub organization events."""
import logging
from app.model import User
from app.controller import ResponseTuple
from typing import Dict, Any, List
from app.controller.webhook.github.events.base import GitHubEventHandler


class OrganizationEventHandler(GitHubEventHandler):
    """Encapsulate the handler methods for GitHub organization events."""

    @property
    def supported_action_list(self) -> List[str]:
        """Provide a list of all actions this handler can handle."""
        return ["member_removed",
                "member_added"]

    def handle(self, payload: Dict[str, Any]) -> ResponseTuple:
        """
        Handle when a user is added, removed, or invited to an organization.

        If the member is removed, they are removed as a user from rocket's db
        if they have not been removed already.

        If the member is added or invited, do nothing.
        """
        action = payload["action"]
        github_user = payload["membership"]["user"]
        github_id = github_user["id"]
        github_username = github_user["login"]
        organization = payload["organization"]["login"]
        logging.info("Github Organization webhook triggered with"
                     f"{{action: {action}, user: {github_username}, "
                     f"user_id: {github_id}, organization: {organization}}}")
        member_list = self._facade. \
            query(User, [('github_user_id', github_id)])
        if action == "member_removed":
            return self.handle_remove(member_list, github_id, github_username)
        elif action == "member_added":
            return self.handle_added(github_username, organization)
        elif action == "member_invited":
            return self.handle_invited(github_username, organization)
        else:
            logging.error("organization webhook triggered,"
                          f" invalid action specified: {str(payload)}")
            return "invalid organization webhook triggered", 405

    def handle_remove(self,
                      member_list: List[User],
                      github_id: str,
                      github_username: str) -> ResponseTuple:
        """Help organization function if payload action is remove."""
        if len(member_list) == 1:
            slack_ids_string = ""
            for member in member_list:
                slack_id = member.slack_id
                self._facade.delete(User, slack_id)
                logging.info(f"deleted slack user {slack_id}")
                slack_ids_string += f" {slack_id}"
            return f"deleted slack ID{slack_ids_string}", 200
        elif len(member_list) > 1:
            logging.error("Error: found github ID connected to"
                          " multiple slack IDs")
            return ("Error: found github ID connected to multiple slack"
                    " IDs", 412)
        else:
            logging.error(f"could not find user {github_id}")
            return f"could not find user {github_username}", 404

    def handle_added(self,
                     github_username: str,
                     organization: str) -> ResponseTuple:
        """Help organization function if payload action is added."""
        logging.info(f"user {github_username} added to {organization}")
        return f"user {github_username} added to {organization}", 200

    def handle_invited(self,
                       github_username: str,
                       organization: str) -> ResponseTuple:
        """Help organization function if payload action is invited."""
        logging.info(f"user {github_username} invited to {organization}")
        return f"user {github_username} invited to {organization}", 200
