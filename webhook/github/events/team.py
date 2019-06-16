"""Handle GitHub team events."""
import logging
from db.facade import DBFacade
from model import Team
from command import ResponseTuple
from typing import Dict, Any, List
from .base import GitHubEventHandler


class TeamEventHandler(GitHubEventHandler):
    """Encapsulate the handler methods for GitHub team events."""

    @property
    def supported_action_list(self) -> List[str]:
        """Provide a list of all actions this handler can handle."""
        return ["created",
                "deleted",
                "edited",
                "added_to_repository",
                "removed_from_repository"]

    def handle(self, payload: Dict[str, Any]) -> ResponseTuple:
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
        logging.info("team webhook triggered")
        action = payload["action"]
        github_team = payload["team"]
        github_id = github_team["id"]
        github_team_name = github_team["name"]
        if action == "created":
            return self.team_created(github_id, github_team_name, payload)
        elif action == "deleted":
            return self.team_deleted(github_id, github_team_name, payload)
        elif action == "edited":
            return self.team_edited(github_id, github_team_name, payload)
        elif action == "added_to_repository":
            return self.team_added_to_repository(github_id,
                                                 github_team_name,
                                                 payload)
        elif action == "removed_from_repository":
            return self.team_removed_from_repository(github_id,
                                                     github_team_name,
                                                     payload)
        else:
            logging.error(f"invalid payload received: {str(payload)}")
            return "invalid payload", 405

    def team_created(self,
                     github_id: str,
                     github_team_name: str,
                     payload: Dict[str, Any]) -> ResponseTuple:
        """Help team function if payload action is created."""
        logging.debug(f"team created event triggered: {str(payload)}")
        try:
            team = self._facade.retrieve(Team, github_id)
            logging.warning(f"team {github_team_name} with "
                            f"id {github_id} already exists.")
            team.github_team_name = github_team_name
        except LookupError:
            logging.debug(f"team {github_team_name} with "
                          f"id {github_id} added to organization.")
            team = Team(github_id, github_team_name, "")
        self._facade.store(team)
        logging.info(f"team {github_team_name} with "
                     f"id {github_id} added to rocket db.")
        return f"created team with github id {github_id}", 200

    def team_deleted(self,
                     github_id: str,
                     github_team_name: str,
                     payload: Dict[str, Any]) -> ResponseTuple:
        """Help team function if payload action is deleted."""
        logging.debug(f"team deleted event triggered: {str(payload)}")
        try:
            self._facade.retrieve(Team, github_id)
            self._facade.delete(Team, github_id)
            logging.info(f"team {github_team_name} with github "
                         f"id {github_id} removed from db")
            return f"deleted team with github id {github_id}", 200
        except LookupError:
            logging.error(f"team with github id {github_id} not found.")
            return f"team with github id {github_id} not found", 404

    def team_edited(self,
                    github_id: str,
                    github_team_name: str,
                    payload: Dict[str, Any]) -> ResponseTuple:
        """Help team function if payload action is edited."""
        logging.debug(f"team edited event triggered: {str(payload)}")
        try:
            team = self._facade.retrieve(Team, github_id)
            team.github_team_name = github_team_name
            logging.info(f"changed team's name with id {github_id} from "
                         f"{github_team_name} to {team.github_team_name}")
            self._facade.store(team)
            logging.info(f"updated team with id {github_id} in"
                         " rocket db.")
            return f"updated team with id {github_id}", 200
        except LookupError:
            logging.error(f"team with github id {github_id} not found.")
            return f"team with github id {github_id} not found", 404

    def team_added_to_repository(self,
                                 github_id: str,
                                 github_team_name: str,
                                 payload: Dict[str, Any]) -> ResponseTuple:
        """Help team function if payload action is added_to_repository."""
        logging.debug(
            f"team added_to_repository event triggered: {str(payload)}")
        repository_name = payload["repository"]["name"]
        logging.info(f"team with id {github_id} added to repository"
                     f" {repository_name}")
        return (f"team with id {github_id} added to repository"
                f" {repository_name}", 200)

    def team_removed_from_repository(self,
                                     github_id: str,
                                     github_team_name: str,
                                     payload: Dict[str, Any]) -> ResponseTuple:
        """Help team function if payload action is removed_from_repository."""
        logging.debug(
            f"team removed_to_repository event triggered: {str(payload)}")
        repository_name = payload["repository"]["name"]
        logging.info(f"team with id {github_id} from repository"
                     f" {repository_name}")
        return (f"team with id {github_id} removed repository "
                f"{repository_name}", 200)
