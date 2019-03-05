"""Contain all the logic for handling webhooks in a class."""
import logging
from model.user import User
from model.team import Team


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
        action = payload["action"]
        github_user = payload["membership"]["user"]
        github_id = github_user["id"]
        github_username = github_user["login"]
        organization = payload["organization"]["login"]
        if action == "member_removed":
            member_list = self.__facade.\
                query(User, [('github_id', github_id)])
            if len(member_list) > 0:
                slack_ids_string = ""
                for member in member_list:
                    slack_id = member.slack_id
                    self.__facade.delete(User, slack_id)
                    logging.info("deleted slack user {}".format(slack_id))
                    slack_ids_string = slack_ids_string + " " + str(slack_id)
                return "deleted slack ID{}".format(slack_ids_string), 200
            else:
                logging.error("could not find user {}".format(github_id))
                return "could not find user {}".format(github_id), 404
        elif action == "member_added":
            logging.info("user {} added to {}".
                         format(github_username, organization))
            return "user " + github_username + " added to " + organization, 200
        elif action == "member_invited":
            logging.info("user {} invited to {}".
                         format(github_username, organization))
            return "user " + github_username + " invited to " + organization,\
                   200
        else:
            logging.error(("organization webhook triggered,"
                           " invalid action specified: {}".
                           format(str(payload))))
            return "invalid organization webhook triggered", 405

    def handle_team_event(self, payload):
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
            logging.debug("team added event triggered: {}".
                          format(str(payload)))
            try:
                team = self.__facade.retrieve(Team, github_id)
                logging.warning("team {} with id {} already exists.".
                                format(github_team_name, github_id))
                team.github_team_name = github_team_name
            except LookupError:
                logging.debug("team {} with id {} added to organization.".
                              format(github_team_name, github_id))
                team = Team(github_id, github_team_name, "")
            self.__facade.store(team)
            logging.info("team {} with id {} added to rocket db.".
                         format(github_team_name, github_id))
            return "created team with github id {}".format(github_id), 200
        elif action == "deleted":
            logging.debug("team deleted event triggered: {}".
                          format(str(payload)))
            try:
                self.__facade.retrieve(Team, github_id)
                self.__facade.delete(Team, github_id)
                logging.info("team {} with github id {} removed from db".
                             format(github_team_name, github_id))
                return "deleted team with github id {}".format(github_id), 200
            except LookupError:
                logging.error("team with github id {} not found.".
                              format(github_id))
                return "team with github id {} not found"\
                       .format(github_id), 404
        elif action == "edited":
            logging.debug("team edited event triggered: {}".
                          format(str(payload)))
            try:
                team = self.__facade.retrieve(Team, github_id)
                team.github_team_name = github_team_name
                logging.info("changed team's name with id {} from {} to {}".
                             format(github_id, github_team_name,
                                    team.github_team_name))
                self.__facade.store(team)
                logging.info("updated team with id {} in rocket db."
                             .format(github_id))
                return "updated team with id {}".format(github_id), 200
            except LookupError:
                logging.error("team with github id {} not found.".
                              format(github_id))
                return "team with github id {} not found"\
                       .format(github_id), 404
        elif action == "added_to_repository":
            repository_name = payload["repository"]["name"]
            logging.info("team with id {} added to repository {}"
                         .format(github_id, repository_name))
            return "team with id {} added to repository {}"\
                   .format(github_id, repository_name), 200
        elif action == "removed_from_repository":
            repository_name = payload["repository"]["name"]
            logging.info("team with id {} from repository {}"
                         .format(github_id, repository_name))
            return "team with id {} removed repository {}"\
                   .format(github_id, repository_name), 200
        else:
            logging.error("invalid payload received: {}".
                          format(str(payload)))
            return "invalid payload", 405
