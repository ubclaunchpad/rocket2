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
        member_list = self.__facade.\
            query(User, [('github_id', github_id)])
        if action == "member_removed":
            if len(member_list) == 1:
                slack_ids_string = ""
                for member in member_list:
                    slack_id = member.slack_id
                    self.__facade.delete(User, slack_id)
                    logging.info("deleted slack user {}".format(slack_id))
                    slack_ids_string += " " + str(slack_id)
                return "deleted slack ID{}".format(slack_ids_string), 200
            elif len(member_list) > 1:
                logging.error("Error: found github ID connected to"
                              " multiple slack IDs")
                return ("Error: found github ID connected to multiple slack"
                        " IDs", 412)
            else:
                logging.error("could not find user {}".format(github_id))
                return "could not find user {}".format(github_username), 404
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

    def handle_membership_event(self, payload):
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
            logging.error(("membership webhook triggered,"
                           " invalid action specified: {}".
                           format(str(payload))))
            return "invalid membership webhook triggered", 405

    def mem_remove(self, github_id, selected_team, team_name):
        """
        Helper function for membership if payload action is removal
        """
        member_list = self.__facade. \
            query(User, [('github_id', github_id)])
        slack_ids_string = ""
        if len(member_list) == 1:
            slack_id = member_list[0].slack_id
            if selected_team.is_member(github_id):
                selected_team.discard_member(github_id)
                logging.info("deleted slack user {} from {}"
                             .format(slack_id, team_name))
                slack_ids_string += str(slack_id)
                return "deleted slack ID {} from {}"\
                    .format(slack_ids_string, team_name), 200
            else:
                logging.error("slack user {} not in {}"
                              .format(slack_id, team_name))
                return "slack user {} not in {}"\
                    .format(slack_id, team_name), 404
        elif len(member_list) > 1:
            logging.error("Error: found github ID connected to"
                          " multiple slack IDs")
            return ("Error: found github ID connected to multiple"
                    " slack IDs", 412)
        else:
            logging.error("could not find user {}".format(github_id))
            return "could not find user {}".format(github_id), 404

    def mem_added(self, github_id, selected_team, team_name, github_username):
        """
        Helper function for membership if payload action is added
        """
        member_list = self.__facade.query(User, [('github_id', github_id)])
        slack_ids_string = ""
        if len(member_list) > 0:
            selected_team.add_member(github_id)
            for member in member_list:
                slack_id = member.slack_id
                logging.info("user {} added to {}".
                             format(github_username, team_name))
                slack_ids_string += " " + str(slack_id)
                return "added slack ID{}".format(slack_ids_string), 200
        else:
            logging.error("could not find user {}".format(github_id))
            return "could not find user {}".format(github_username), 404

    def mem_invited(self, github_username, team_name):
        """
        Helper function for membership if payload action is invited
        """
        logging.info("user {} invited to {}".
                     format(github_username, team_name))
        return "user " + github_username + " invited to " + team_name,\
               200
