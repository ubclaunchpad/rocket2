"""Command parsing for project events."""
import logging
import shlex

from argparse import ArgumentParser, _SubParsersAction
from app.controller import ResponseTuple
from app.controller.command.commands.base import Command
from db.facade import DBFacade
from flask import jsonify
from app.model import Project, User, Team, Permissions
from typing import Dict


class ProjectCommand(Command):
    """Represent Project Command Parser."""

    command_name = "project"
    permission_error = "You do not have the sufficient " \
                       "permission level for this command!"
    assigned_error = "Assign error! Project already assigned to a team!"
    desc = f"for dealing with {command_name}s"

    def __init__(self,
                 db_facade: DBFacade) -> None:
        """Initialize project command."""
        logging.info("Initializing ProjectCommand instance")
        self.parser = ArgumentParser(prog="/rocket")
        self.parser.add_argument("project")
        self.subparser = self.init_subparsers()
        self.help = self.get_help()
        self.facade = db_facade

    def init_subparsers(self) -> _SubParsersAction:
        """Initialize subparsers for project command."""
        subparsers = self.parser.add_subparsers(dest="which")

        """Parser for list command."""
        parser_list = subparsers.add_parser("list")
        parser_list.set_defaults(which="list",
                                 help="Display a list of all projects.")

        """Parser for view command."""
        parser_view = subparsers.add_parser("view")
        parser_view.set_defaults(which="view",
                                 help="Displays details of project.")
        parser_view.add_argument("project_id", metavar="project-id",
                                 type=str, action="store",
                                 help="Use to specify project to view.")

        """Parser for create command."""
        parser_create = subparsers.add_parser("create")
        parser_create.set_defaults(which="create",
                                   help="(Team Lead and Admin only) Create "
                                        "a new project from a given repo.")
        parser_create.add_argument("gh_repo", metavar="gh-repo",
                                   type=str, action="store",
                                   help="Use to specify link to "
                                        "GitHub repository.")
        parser_create.add_argument("github_team_name",
                                   metavar="github-team-name",
                                   type=str, action="store",
                                   help="Use to specify GitHub team to "
                                        "assign project to.")
        parser_create.add_argument("--name", metavar="DISPLAY-NAME",
                                   type=str, action="store",
                                   help="Add to set the displayed "
                                        "name of the project.")

        """Parser for unassign command."""
        parser_unassign = subparsers.add_parser("unassign")
        parser_unassign.set_defaults(which="unassign",
                                     help="Unassign a given project.")
        parser_unassign.add_argument("project_id", metavar="project-id",
                                     type=str, action="store",
                                     help="Use to specify project "
                                          "to unassign.")

        """Parser for edit command."""
        parser_edit = subparsers.add_parser("edit")
        parser_edit.set_defaults(which="edit",
                                 help="Edit the given project.")
        parser_edit.add_argument("project_id", metavar="project-id",
                                 type=str, action="store",
                                 help="Use to specify project to edit.")
        parser_edit.add_argument("--name", metavar="DISPLAY-NAME",
                                 type=str, action="store",
                                 help="Add to change the displayed "
                                      "name of the project.")

        """Parser for assign command."""
        parser_assign = subparsers.add_parser("assign")
        parser_assign.set_defaults(which="assign",
                                   help="Assigns a project to a team.")
        parser_assign.add_argument("project_id", metavar="project-id",
                                   type=str, action="store",
                                   help="Use to specify project to assign.")
        parser_assign.add_argument("github_team_name",
                                   metavar="github-team-name",
                                   type=str, action="store",
                                   help="Use to specify GitHub team to "
                                        "assign project to.")
        parser_assign.add_argument("-f", "--force", action="store_true",
                                   help="Set to assign project even if "
                                        "another team is already "
                                        "assigned to it.")

        """Parser for delete command."""
        parser_delete = subparsers.add_parser("delete")
        parser_delete.set_defaults(which="delete",
                                   help="Delete the project from database.")
        parser_delete.add_argument("project_id", metavar="project-id",
                                   type=str, action="store",
                                   help="Use to specify project to delete.")
        parser_delete.add_argument("-f", "--force", action="store_true",
                                   help="Set to delete project even if "
                                        "a team is already assigned to it.")

        return subparsers

    def get_help(self, subcommand: str = None) -> str:
        """Return command options for project events with Slack formatting."""
        def get_subcommand_help(sc: str) -> str:
            """Return the help message of a specific subcommand."""
            message = f"\n*{sc.capitalize()}*\n"
            message += self.subparser.choices[sc].format_help()
            return message

        if subcommand is None or subcommand not in self.subparser.choices:
            res = f"\n*{self.command_name} commands:*```"
            for argument in self.subparser.choices:
                res += get_subcommand_help(argument)
            return res + "```"
        else:
            res = "\n```"
            res += get_subcommand_help(subcommand)
            return res + "```"

    def handle(self,
               command: str,
               user_id: str) -> ResponseTuple:
        """Handle command by splitting into substrings and giving to parser."""
        logging.debug("Handling ProjectCommand")
        command_arg = shlex.split(command)
        args = None

        try:
            args = self.parser.parse_args(command_arg)
        except SystemExit:
            all_subcommands = list(self.subparser.choices.keys())
            present_subcommands = [subcommand for subcommand in
                                   all_subcommands
                                   if subcommand in command_arg]
            present_subcommand = None
            if len(present_subcommands) == 1:
                present_subcommand = present_subcommands[0]
            return self.get_help(subcommand=present_subcommand), 200

        if args.which == "list":
            return self.list_helper()

        elif args.which == "view":
            return self.view_helper(args.project_id)

        elif args.which == "create":
            param_list = {
                "display_name": args.name
            }
            return self.create_helper(args.gh_repo,
                                      args.github_team_name,
                                      param_list,
                                      user_id)

        elif args.which == "unassign":
            return self.unassign_helper(args.project_id, user_id)

        elif args.which == "edit":
            param_list = {
                "display_name": args.name
            }
            return self.edit_helper(args.project_id, param_list)

        elif args.which == "assign":
            return self.assign_helper(args.project_id,
                                      args.github_team_name,
                                      user_id,
                                      args.force)

        elif args.which == "delete":
            return self.delete_helper(args.project_id,
                                      user_id,
                                      args.force)

        else:
            return self.get_help(), 200

    def list_helper(self) -> ResponseTuple:
        """
        Return display information of all projects.

        :return: error message if lookup error or no projects,
                 otherwise return projects' information
        """
        logging.debug("Handling project list subcommand")
        projects = self.facade.query(Project)
        if not projects:
            logging.info("No projects found in database")
            return "No Projects Exist!", 200
        project_list_str = "*PROJECT ID : GITHUB TEAM ID : PROJECT NAME*\n"
        for project in projects:
            project_list_str += f"{project.project_id} : " \
                f"{project.github_team_id} : " \
                f"{project.display_name}\n"
        return project_list_str, 200

    def view_helper(self,
                    project_id: str) -> ResponseTuple:
        """
        View project info from database.

        :param project_id: project ID of project to view
        :return: error message if project not found in database, else
                 information about the project
        """
        logging.debug("Handling project view subcommand")
        try:
            project = self.facade.retrieve(Project, project_id)

            return jsonify({'attachments': [project.get_attachment()]}), 200
        except LookupError as e:
            logging.error(str(e))
            return str(e), 200

    def create_helper(self,
                      gh_repo: str,
                      github_team_name: str,
                      param_list: Dict[str, str],
                      user_id: str) -> ResponseTuple:
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
        team_list = self.facade.query(Team,
                                      [("github_team_name",
                                        github_team_name)])
        if len(team_list) != 1:
            error = f"{len(team_list)} teams found with " \
                f"GitHub team name {github_team_name}"
            logging.error(error)
            return error, 200

        team = team_list[0]
        try:
            user = self.facade.retrieve(User, user_id)

            if not (user_id in team.team_leads or
                    user.permissions_level is Permissions.admin):
                logging.error(f"User with user ID {user_id} is not "
                              "a team lead of the specified team or an admin")
                return self.permission_error, 200

            project = Project(team.github_team_id, [gh_repo])

            if param_list["display_name"]:
                project.display_name = param_list["display_name"]

            self.facade.store(project)

            return jsonify({'attachments': [project.get_attachment()]}), 200
        except LookupError as e:
            logging.error(str(e))
            return str(e), 200

    def unassign_helper(self,
                        project_id: str,
                        user_id: str) -> ResponseTuple:
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
        try:
            project = self.facade.retrieve(Project, project_id)
            team = self.facade.retrieve(Team, project.github_team_id)
            user = self.facade.retrieve(User, user_id)

            if not (user_id in team.team_leads or
                    user.permissions_level is Permissions.admin):
                logging.error(f"User with user ID {user_id} is not "
                              "a team lead of the specified team or an admin")
                return self.permission_error, 200
            else:
                project.github_team_id = ""
                self.facade.store(project)
                return "Project successfully unassigned!", 200
        except LookupError as e:
            logging.error(str(e))
            return str(e), 200

    def edit_helper(self,
                    project_id: str,
                    param_list: Dict[str, str]) -> ResponseTuple:
        """
        Edit project from database.

        :param project_id: project ID of the project in the database to edit
        :param param_list: Dict of project parameters that are to be edited
        :return: returns edit message if project is successfully edited, or an
                 error message if the project was not found in the database
        """
        logging.debug("Handling project edit subcommand")
        try:
            project = self.facade.retrieve(Project, project_id)

            if param_list["display_name"]:
                project.display_name = param_list["display_name"]
                logging.debug("Changed display "
                              f"name to {project.display_name}")

            self.facade.store(project)

            return jsonify({'attachments': [project.get_attachment()]}), 200
        except LookupError as e:
            logging.error(str(e))
            return str(e), 200

    def assign_helper(self,
                      project_id: str,
                      github_team_name: str,
                      user_id: str,
                      force: bool) -> ResponseTuple:
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
        try:
            project = self.facade.retrieve(Project, project_id)

            team_list = self.facade.query(Team,
                                          [("github_team_name",
                                            github_team_name)])
            if len(team_list) != 1:
                error = f"{len(team_list)} teams found with " \
                    f"GitHub team name {github_team_name}"
                logging.error(error)
                return error, 200

            team = team_list[0]
            user = self.facade.retrieve(User, user_id)

            if not (user_id in team.team_leads or
                    user.permissions_level is Permissions.admin):
                logging.error(f"User with user ID {user_id} is not "
                              "a team lead of the specified team or an admin")
                return self.permission_error, 200
            elif project.github_team_id != "" and not force:
                logging.error("Project is assigned to team with "
                              f"GitHub team ID {project.github_team_id}")
                return self.assigned_error, 200
            else:
                project.github_team_id = team.github_team_id
                self.facade.store(project)
                return "Project successfully assigned!", 200
        except LookupError as e:
            logging.error(str(e))
            return str(e), 200

    def delete_helper(self,
                      project_id: str,
                      user_id: str,
                      force: bool) -> ResponseTuple:
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
        try:
            project = self.facade.retrieve(Project, project_id)
            team = self.facade.retrieve(Team, project.github_team_id)
            user = self.facade.retrieve(User, user_id)

            if project.github_team_id != "" and not force:
                logging.error("Project is assigned to team with "
                              f"GitHub team ID {project.github_team_id}")
                return self.assigned_error, 200
            elif not (user_id in team.team_leads or
                      user.permissions_level is Permissions.admin):
                logging.error(f"User with user ID {user_id} is not "
                              "a team lead of the specified team or an admin")
                return self.permission_error, 200
            else:
                self.facade.delete(Project, project_id)
                return "Project successfully deleted!", 200

        except LookupError as e:
            logging.error(str(e))
            return str(e), 200
