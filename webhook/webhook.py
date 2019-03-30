"""Contain all the logic for handling webhooks in a class."""
import logging
import hmac
import hashlib
from db.facade import DBFacade
from model import User, Team
from typing import Dict, Any, cast, List
from command import ResponseTuple
from config import Credentials


class WebhookHandler:
    """Encapsulate methods for GitHub webhook triggered events."""

    def __init__(self, db_facade: DBFacade, credentials: Credentials) -> None:
        """Give handler access to the database."""
        self.__facade = db_facade
        self.__secret = credentials.github_webhook_secret
        self.__organization_action_list = [
            "member_removed",
            "member_added",
            "member_invited"
        ]
        self.__team_action_list = [
            "created",
            "deleted",
            "edited",
            "added_to_repository",
            "removed_from_repository"
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
        if self.verify_hash(request_body, xhub_signature):
            # handle
            action = payload["action"]
            if action in self.__organization_action_list:
                return self.handle_organization_event(payload)
            elif action in self.__team_action_list:
                return self.handle_team_event(payload)
            else:
                logging.error("Unsupported payload received")
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

    def handle_organization_event(self,
                                  payload: Dict[str, Any]) -> ResponseTuple:
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
        member_list = self.__facade. \
            query(User, [('github_id', github_id)])
        if action == "member_removed":
            return self.org_remove(member_list, github_id, github_username)
        elif action == "member_added":
            return self.org_added(github_username, organization)
        elif action == "member_invited":
            return self.org_invited(github_username, organization)
        else:
            logging.error("organization webhook triggered,"
                          f" invalid action specified: {str(payload)}")
            return "invalid organization webhook triggered", 405

    def org_remove(self,
                   member_list: List[User],
                   github_id: str,
                   github_username: str) -> ResponseTuple:
        """Help organization function if payload action is remove."""
        if len(member_list) == 1:
            slack_ids_string = ""
            for member in member_list:
                slack_id = member.slack_id
                self.__facade.delete(User, slack_id)
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

    def org_added(self,
                  github_username: str,
                  organization: str) -> ResponseTuple:
        """Help organization function if payload action is added."""
        logging.info(f"user {github_username} added to {organization}")
        return f"user {github_username} added to {organization}", 200

    def org_invited(self,
                    github_username: str,
                    organization: str) -> ResponseTuple:
        """Help organization function if payload action is invited."""
        logging.info(f"user {github_username} invited to {organization}")
        return f"user {github_username} invited to {organization}", 200

    def handle_team_event(self, payload: Dict[str, Any]) -> ResponseTuple:
        """
        Handle team events of the organization.

        This event is fired when a team is created, deleted, edited, or
        added or removed from a repository.

        If a team is created, add or overwrite a team in rocket's db.

        If a team is deleted, delete the team from rocket's db if it exists.

        If a team is edited, overwrite the team's fields or create the
        team if necessary.

        If the team is added or removed from a repository, do nothing for now.
        """
        action = payload["action"]
        github_team = payload["team"]
        github_id = github_team["id"]
        github_team_name = github_team["name"]
        if action == "created":
            logging.debug(f"team added event triggered: {str(payload)}")
            try:
                team = self.__facade.retrieve(Team, github_id)
                logging.warning(f"team {github_team_name} with "
                                f"id {github_id} already exists.")
                team.github_team_name = github_team_name
            except LookupError:
                logging.debug(f"team {github_team_name} with "
                              f"id {github_id} added to organization.")
                team = Team(github_id, github_team_name, "")
            self.__facade.store(team)
            logging.info(f"team {github_team_name} with "
                         f"id {github_id} added to rocket db.")
            return f"created team with github id {github_id}", 200
        elif action == "deleted":
            logging.debug(f"team deleted event triggered: {str(payload)}")
            try:
                self.__facade.retrieve(Team, github_id)
                self.__facade.delete(Team, github_id)
                logging.info(f"team {github_team_name} with github "
                             f"id {github_id} removed from db")
                return f"deleted team with github id {github_id}", 200
            except LookupError:
                logging.error(f"team with github id {github_id} not found.")
                return f"team with github id {github_id} not found", 404
        elif action == "edited":
            logging.debug(f"team edited event triggered: {str(payload)}")
            try:
                team = cast(Team, self.__facade.retrieve(Team, github_id))
                team.github_team_name = github_team_name
                logging.info(f"changed team's name with id {github_id} from "
                             f"{github_team_name} to {team.github_team_name}")
                self.__facade.store(team)
                logging.info(f"updated team with id {github_id} in"
                             " rocket db.")
                return f"updated team with id {github_id}", 200
            except LookupError:
                logging.error(f"team with github id {github_id} not found.")
                return f"team with github id {github_id} not found", 404
        elif action == "added_to_repository":
            repository_name = payload["repository"]["name"]
            logging.info(f"team with id {github_id} added to repository"
                         f" {repository_name}")
            return (f"team with id {github_id} added to repository"
                    f" {repository_name}", 200)
        elif action == "removed_from_repository":
            repository_name = payload["repository"]["name"]
            logging.info(f"team with id {github_id} from repository"
                         f" {repository_name}")
            return (f"team with id {github_id} removed repository "
                    f"{repository_name}", 200)
        else:
            logging.error(f"invalid payload received: {str(payload)}")
            return "invalid payload", 405

    def handle_membership_event(self,
                                payload: Dict[str, Any]) -> ResponseTuple:
        """
        Handle when a user is added, removed, or invited to team.

        If the member is removed, they are removed as a user from rocket's db
        if they have not been removed already.

        If the member is added, they are added to rocket's db

        If invited, do nothing.
        """
        action = payload["action"]
        github_user = payload["member"]
        github_username = github_user["login"]
        github_id = github_user["id"]
        team = payload["team"]
        team_id = team["id"]
        team_name = team["name"]
        selected_team = self.__facade.retrieve(Team, team_id)
        if action == "member_removed":
            return self.mem_remove(github_id, selected_team, team_name)
        elif action == "member_added":
            return self.mem_added(github_id, selected_team, team_name,
                                  github_username)
        elif action == "member_invited":
            return self.mem_invited(github_username, team_name)
        else:
            logging.error("membership webhook triggered,"
                          f" invalid action specified: {str(payload)}")
            return "invalid membership webhook triggered", 405

    def mem_remove(self,
                   github_id: str,
                   selected_team: Team,
                   team_name: str) -> ResponseTuple:
        """Help membership function if payload action is removal."""
        member_list = self.__facade. \
            query(User, [('github_id', github_id)])
        slack_ids_string = ""
        if len(member_list) == 1:
            slack_id = member_list[0].slack_id
            if selected_team.has_member(github_id):
                selected_team.discard_member(github_id)
                logging.info(f"deleted slack user {slack_id} "
                             f"from {team_name}")
                slack_ids_string += f" {slack_id}"
                return (f"deleted slack ID{slack_ids_string} "
                        f"from {team_name}", 200)
            else:
                logging.error(f"slack user {slack_id} not in {team_name}")
                return (f"slack user {slack_id} not in {team_name}", 404)
        elif len(member_list) > 1:
            logging.error("Error: found github ID connected to"
                          " multiple slack IDs")
            return ("Error: found github ID connected to multiple"
                    " slack IDs", 412)
        else:
            logging.error(f"could not find user {github_id}")
            return f"could not find user {github_id}", 404

    def mem_added(self,
                  github_id: str,
                  selected_team: Team,
                  team_name: str,
                  github_username: str) -> ResponseTuple:
        """Help membership function if payload action is added."""
        member_list = self.__facade.query(User, [('github_id', github_id)])
        slack_ids_string = ""
        if len(member_list) > 0:
            selected_team.add_member(github_id)
            for member in member_list:
                slack_id = member.slack_id
                logging.info(f"user {github_username} added to {team_name}")
                slack_ids_string += f" {slack_id}"
            return f"added slack ID{slack_ids_string}", 200
        else:
            logging.error(f"could not find user {github_id}")
            return f"could not find user {github_username}", 404

    def mem_invited(self,
                    github_username: str,
                    team_name: str) -> ResponseTuple:
        """Help membership function if payload action is invited."""
        logging.info(f"user {github_username} invited to {team_name}")
        return f"user {github_username} invited to {team_name}", 200
