"""Handle GitHub membership events."""
import logging
from db.facade import DBFacade
from model import User, Team
from command import ResponseTuple
from typing import Dict, Any, List


class MembershipEventHandler:
    """Encapsulate the handler methods for GitHub membership events."""

    def __init__(self, db_facade: DBFacade) -> None:
        """Give handler access to the database facade."""
        self.__facade = db_facade

    def handle(self,
               payload: Dict[str, Any]) -> ResponseTuple:
        """Handle the event where a user is added or removed from a team."""
        action = payload["action"]
        github_user = payload["member"]
        github_username = github_user["login"]
        github_id = github_user["id"]
        team = payload["team"]
        team_id = team["id"]
        team_name = team["name"]
        selected_team = self.__facade.retrieve(Team, team_id)
        if action == "removed":
            return self.mem_remove(github_id, selected_team, team_name)
        elif action == "added":
            return self.mem_added(github_id, selected_team, team_name,
                                  github_username)
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
            query(User, [('github_user_id', github_id)])
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
        member_list = self.__facade.query(User,
                                          [('github_user_id', github_id)])
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
