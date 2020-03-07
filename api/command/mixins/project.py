"""Encapsulate the common business logic of project commands."""
import logging

from app.model import Project, User, Team, Permissions
from typing import Dict, cast, List


class ProjectCommandApis:
    """Encapsulate the various APIs for project command logic."""

    def __init__(self):
        """Declare the interfaces needed."""
        self._db_facade = None
        self._gh_interface = None
        self._slack_client = None

    def create_project(self,
                       gh_repo: str,
                       github_team_name: str,
                       param_list: Dict[str, str],
                       user_id: str) -> bool:
        """
        Create a project and store it in the database.

        :param gh_repo: link to the GitHub repository this project describes
        :param github_team_name: GitHub team name of the team to assign this
                                 project to
        :param param_list: Dict of project parameters that are to
                           be initialized
        :param user_id: user ID of the calling user
        :return: lookup error if the specified GitHub team name does not match
                 a team in the database or if the calling user could not be
                 found, else permission error if the calling user is not a
                 team lead of the team to initially assign the
                 project to, else information about the project
        """
        logging.debug("Handling project create subcommand")
        team_list = self._db_facade.query(Team,
                                          [("github_team_name",
                                            github_team_name)])
        if len(team_list) != 1:
            error = f"{len(team_list)} teams found with " \
                f"GitHub team name {github_team_name}"
            logging.error(error)
            return False

        team = team_list[0]

        user = self._db_facade.retrieve(User, user_id)

        if not (user.github_id in team.team_leads or
                user.permissions_level is Permissions.admin):
            logging.error(f"User with user ID {user_id} is not "
                          "a team lead of the specified team or an admin")
            return False

        project = Project(team.github_team_id, [gh_repo])

        if param_list["display_name"]:
            project.display_name = param_list["display_name"]

        return cast(bool, self._db_facade.store(project))

    def edit_project(self,
                     project_id: str,
                     param_list: Dict[str, str]) -> bool:
        """
        Edit project from database.

        :param project_id: project ID of the project in the database to edit
        :param param_list: Dict of project parameters that are to be edited
        :return: returns edit message if project is successfully edited, or an
                 error message if the project was not found in the database
        """
        logging.debug("Handling project edit subcommand")
        project = self._db_facade.retrieve(Project, project_id)

        if param_list["display_name"]:
            project.display_name = param_list["display_name"]
            logging.debug("Changed display "
                          f"name to {project.display_name}")
            return cast(bool, self._db_facade.store(project))
        return False

    def delete_helper(self,
                      project_id: str,
                      user_id: str,
                      force: bool) -> bool:
        """
        Delete a project from the database.

        :param project_id: project ID of project to delete
        :param user_id: user ID of the calling user
        :param force: specify if an error should be raised if the project
                      is assigned to a team
        :return: returns lookup error if the project, assigned team, or user
                 could not be found, else an assignment error if the project
                 is assigned to a team, otherwise success message
        """
        logging.debug("Handling project delete subcommand")
        project = self._db_facade.retrieve(Project, project_id)
        team = self._db_facade.retrieve(Team, project.github_team_id)
        user = self._db_facade.retrieve(User, user_id)

        if project.github_team_id != "" and not force:
            logging.error("Project is assigned to team with "
                          f"GitHub team ID {project.github_team_id}")
            return False
        elif not (user.github_id in team.team_leads or
                  user.permissions_level is Permissions.admin):
            logging.error(f"User with user ID {user_id} is not "
                          "a team lead of the specified team or an admin")
            return False
        return cast(bool, self._db_facade.delete(Project, project_id))

    def assign_helper(self,
                      project_id: str,
                      github_team_name: str,
                      user_id: str,
                      force: bool) -> bool:
        """
        Assign the team to a project.

        :param project_id: project ID of project to assign to a team
        :param github_team_name: GitHub team name of the team to assign this
                                 project to
        :param user_id: user ID of the calling user
        :param force: specify if an error should be raised if the project
                      is assigned to another team
        :return: returns lookup error if the project could not be found or no
                 team has the specified GitHub team name or if the calling
                 user is not in the database, else permission error if calling
                 user is not a team lead, else an assignment error if the
                 project is assigned to a team, otherwise success message
        """
        logging.debug("Handling project assign subcommand")
        project = self._db_facade.retrieve(Project, project_id)

        team_list = self._db_facade.query(Team,
                                          [("github_team_name",
                                            github_team_name)])
        if len(team_list) != 1:
            error = f"{len(team_list)} teams found with " \
                f"GitHub team name {github_team_name}"
            logging.error(error)
            return False

        team = team_list[0]
        user = self._db_facade.retrieve(User, user_id)

        print(project, team, user)

        if not (user.github_id in team.team_leads or
                user.permissions_level is Permissions.admin):
            logging.error(f"User with user ID {user_id} is not "
                          "a team lead of the specified team or an admin")
            return False
        elif project.github_team_id != "" and not force:
            logging.error("Project is assigned to team with "
                          f"GitHub team ID {project.github_team_id}")
            return False
        else:
            project.github_team_id = team.github_team_id
            return cast(bool, self._db_facade.store(project))

    def projects_list(self) -> List[Project]:
        """
        Return display information of all projects.

        :return: error message if lookup error or no projects,
                 otherwise return projects' information
        """
        logging.debug("Handling project list subcommand")
        projects = self._db_facade.query(Project)
        if not projects:
            logging.info("No projects found in database")
            return cast(list, [])
        return cast(list, projects)
        # project_list_str = "*PROJECT ID : GITHUB TEAM ID : PROJECT NAME*\n"
        # for project in projects:
        #     project_list_str += f"{project.project_id} : " \
        #         f"{project.github_team_id} : " \
        #         f"{project.display_name}\n"
        # return project_list_str, 200

    def unassign_helper(self,
                        project_id: str,
                        user_id: str) -> bool:
        """
        Unassign the team attached to a project from the project specified.

        :param project_id: project ID of project to unassign team from
        :param user_id: user ID of the calling user
        :return: returns lookup error if the project, assigned team or calling
                 user could not be found, else permission error if calling
                 user is not a team lead of the team to unassign,
                 otherwise success message
        """
        logging.debug("Handling project unassign subcommand")
        project = self._db_facade.retrieve(Project, project_id)
        team = self._db_facade.retrieve(Team, project.github_team_id)
        user = self._db_facade.retrieve(User, user_id)

        print(project, team, user)

        if not (user.github_id in team.team_leads or
                user.permissions_level is Permissions.admin):
            logging.error(f"User with user ID {user_id} is not "
                          "a team lead of the specified team or an admin")
            return False
        else:
            project.github_team_id = ""
            return cast(bool, self._db_facade.store(project))

    def project_view(self,
                     project_id: str) -> Project:
        """
        View project info from database.

        :param project_id: project ID of project to view
        :return: error message if project not found in database, else
                 information about the project
        """
        logging.debug("Handling project view subcommand")
        project = self._db_facade.retrieve(Project, project_id)
        return cast(Project, project)
