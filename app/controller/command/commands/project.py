"""Command parsing for project events."""
import logging

from argparse import ArgumentParser, _SubParsersAction
from app.controller import ResponseTuple
from app.controller.command.commands.base import Command
from db.facade import DBFacade


class ProjectCommand(Command):
    """Represent Project Command Parser."""

    command_name = "project"
    permission_error = "You do not have the sufficient " \
                       "permission level for this command!"
    lookup_error = "Lookup error! Project not found!"
    desc = f"for dealing with {command_name}s"

    def __init__(self,
                 db_facade: DBFacade) -> None:
        """Initialize project command."""
        logging.info("Initializing ProjectCommand instance")
        self.parser = ArgumentParser(prog="/rocket")
        self.parser.add_argument("project")
        self.subparser = self.init_subparsers()
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
                                     help="Use to specify project to unassign.")

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
        parser_delete = subparser.add_parser("delete")
        parser_delete.set_defaults(which="delete",
                                   help="Delete the project from database.")
        parser_delete.add_argument("project_id", metavar="project-id",
                                   type=str, action="store",
                                   help="Use to specify project to delete.")
        parser_assign.add_argument("-f", "--force", action="store_true",
                                   help="Set to delete project even if "
                                        "a team is already assigned to it.")

        return subparsers
