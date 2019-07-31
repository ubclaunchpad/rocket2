"""Command parsing for project events."""
import logging
import shlex

from argparse import ArgumentParser, _SubParsersAction
from app.controller import ResponseTuple
from app.controller.command.commands.base import Command
from db.facade import DBFacade
from flask import jsonify
from app.model import Project, Team
from typing import Dict


class ProjectCommand(Command):
    """Represent Project Command Parser."""

    # TODO: add logging

    command_name = "project"
    permission_error = "You do not have the sufficient " \
                       "permission level for this command!"
    project_lookup_error = "Lookup error! Project not found!"
    user_lookup_error = "Lookup error! User not found!"
    team_lookup_error = "Lookup error! Team not found!"
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
                                   help="(Team Lead and Admin only) Creates "
                                        "a new project from a given repo.")
        parser_create.add_argument("gh_repo", metavar="gh-repo",
                                   type=str, action="store",
                                   help="Use to specify link of the "
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
                                     help="Unassigns a given project.")
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

    def get_help(self) -> str:
        """Return command options for project events."""
        res = f"\n*{self.command_name} commands:*```"
        for argument in self.subparser.choices:
            name = argument.capitalize()
            res += f"\n*{name}*\n"
            res += self.subparser.choices[argument].format_help()
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
            return self.get_help(), 200

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
            # TODO
            return self.get_help(), 200

        elif args.which == "edit":
            param_list = {
                "display_name": args.name
            }
            return self.edit_helper(args.project_id, param_list)

        elif args.which == "assign":
            # TODO
            return self.get_help(), 200

        elif args.which == "delete":
            # TODO
            return self.get_help(), 200

        else:
            return self.get_help(), 200

    def list_helper(self) -> ResponseTuple:
        """
        Return display information of all projects.

        :return: error message if lookup error or no projects,
                 otherwise return projects' information
        """
        projects = self.facade.query(Project)
        if not projects:
            return "No Projects Exist!", 200
        attachment = [project.get_basic_attachment() for
                      project in projects]
        return jsonify({'attachments': attachment}), 200

    def view_helper(self,
                    project_id: str) -> ResponseTuple:
        """
        View project info from database.

        :param project_id: project ID of project to view
        :return: error message if project not found in database, else
                 information about the project
        """
        try:
            project = self.facade.retrieve(Project, project_id)

            return jsonify({'attachments': [project.get_attachment()]}), 200
        except LookupError:
            return self.project_lookup_error, 200

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
                 a team in the database, else permission error if the calling
                 user is not a team lead of the team to initially assign the
                 project to, else information about the project
        """
        team_list = self.facade.query(Team,
                                      [("github_team_name",
                                        github_team_name)])
        if len(team_list) != 1:
            return self.team_lookup_error, 200

        team = team_list[0]

        if user_id not in team.team_leads:
            return self.permission_error, 200

        project = Project(team.github_team_id, [gh_repo])

        if param_list["display_name"]:
            project.display_name = param_list["display_name"]

        self.facade.store(project)

        return jsonify({'attachments': [project.get_attachment()]}), 200

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
        try:
            project = self.facade.retrieve(Project, project_id)

            if param_list["display_name"]:
                project.display_name = param_list["display_name"]

            self.facade.store(project)

            return jsonify({'attachments': [project.get_attachment()]}), 200
        except LookupError:
            return self.project_lookup_error, 200
