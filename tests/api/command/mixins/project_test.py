"""Test the common business logic for the team command APIs."""
from api.command import CommandApis
from db import DBFacade
from interface.github import GithubInterface, GithubAPIException
from interface.slack import Bot, SlackAPIError
from app.model import User, Team, Project, Permissions
from unittest import mock, TestCase
from typing import List, TypeVar

T = TypeVar('T', User, Team)


class TestProjectCommandApis(TestCase):
    """Test Case for ProjectCommandApi methods."""

    def setUp(self) -> None:
        """Set up the test case environment."""
        self.mock_facade = mock.MagicMock(DBFacade)
        self.mock_github = mock.MagicMock(GithubInterface)
        self.mock_slack = mock.MagicMock(Bot)
        self.testapi = CommandApis(self.mock_facade,
                                   self.mock_github,
                                   self.mock_slack)

        self.regular_user = User("regular")
        self.regular_user.permissions_level = Permissions.member
        self.regular_user.github_id = "reg_gh_id"
        self.regular_user.github_username = "reg_username"
        self.lead_user = User("lead")
        self.lead_user.permissions_level = Permissions.team_lead
        self.lead_user.github_id = "lead_gh_id"
        self.lead_user.github_username = "lead_username"
        self.admin_user = User("admin")
        self.admin_user.permissions_level = Permissions.admin
        self.admin_user.github_id = "admin_gh_id"
        self.admin_user.github_username = "admin_username"

        self.team1 = Team("1", "gh1", "name1")
        self.team2 = Team("2", "gh2", "name2")
        self.team3 = Team("3", "gh3", "name3")
        self.team3_dup = Team("4", "gh3", "name4")
        self.nonexistent_team = Team("5", "gh5", "name5")

        self.project1 = Project(self.team1.github_team_id, [])
        self.project2 = Project("", [])

        def mock_facade_retrieve_side_effect(*args, **kwargs) -> T:
            """Mock behavior of the retrieve mock facade function."""
            if args[0] == User:
                slack_id = args[1]
                if slack_id == self.regular_user.slack_id:
                    return self.regular_user
                elif slack_id == self.lead_user.slack_id:
                    return self.lead_user
                elif slack_id == self.admin_user.slack_id:
                    return self.admin_user
                else:
                    raise LookupError
            elif args[0] == Project:
                if args[1] == self.project1.project_id:
                    return self.project1
                elif args[1] == self.project2.project_id:
                    return self.project2
                else:
                    raise LookupError
            elif args[0] == Team:
                if args[1] == self.team1.github_team_id:
                    return self.team1
                elif args[1] == self.team2.github_team_id:
                    return self.team2

        self.mock_facade.retrieve.side_effect = \
            mock_facade_retrieve_side_effect

        def mock_facade_query_side_effect(*args, **kwargs) -> List[T]:
            """Mock behavior of the query mock facade function."""
            if args[0] == Team:
                query_teams = []
                try:
                    params = args[1]
                except IndexError:
                    query_teams = [
                        self.team1,
                        self.team2,
                        self.team3,
                        self.team3_dup
                    ]
                else:
                    assert len(params) == 1, \
                        "Woops, too many parameters for this mock query!"
                    attribute, value = params[0]
                    assert attribute == "github_team_name", \
                        "Woops, this mock can only handle `github_team_name`!"

                    if value == "gh1":
                        query_teams = [self.team1]
                    elif value == "gh2":
                        query_teams = [self.team2]
                    elif value == "gh3":
                        query_teams = [
                            self.team3,
                            self.team3_dup
                        ]
            elif args[0] == Project:
                query_teams = []
                try:
                    params = args[1]
                except IndexError:
                    query_teams = [
                        self.project1
                    ]

            return query_teams

        self.mock_facade.query.side_effect = \
            mock_facade_query_side_effect

        # In most cases, store will need to return True for tests
        self.mock_facade.store.return_value = True

    def test_create_project_with_tech_lead(self):
        self.team1.add_team_lead(self.lead_user.github_id)
        self.assertTrue(self.testapi.create_project("1111", self.team1.github_team_name, {"display_name": "1111"}, self.lead_user.slack_id))

    def test_create_project_non_tech_lead(self):
        self.team1.add_team_lead(self.lead_user.github_id)
        self.assertFalse(self.testapi.create_project("1111", self.team1.github_team_name, {"display_name": "1111"}, self.regular_user.slack_id))

    def test_create_project_admin_in_project(self):
        self.team1.add_team_lead(self.admin_user.github_id)
        self.assertTrue(self.testapi.create_project("1111", self.team1.github_team_name, {"display_name": "1111"}, self.admin_user.slack_id))

    def test_create_project_admin_not_in_project(self):
        self.team1.add_team_lead(self.lead_user.github_id)
        self.assertTrue(self.testapi.create_project("1111", self.team1.github_team_name, {"display_name": "1111"}, self.admin_user.slack_id))

    def test_create_project_on_nonexistent_team(self):
        self.assertFalse(self.testapi.create_project("1111", self.nonexistent_team.github_team_name, {"display_name": "1111"}, self.admin_user.slack_id))
    
    def test_projects_list(self):
        all_projects = self.testapi.projects_list()
        self.assertListEqual(all_projects, [ self.project1 ])

    def test_project_view(self):
        project = self.testapi.project_view(self.project1.project_id)
        self.assertEqual(project, self.project1)
    
    def test_project_view_no_project(self):
        with self.assertRaises(LookupError):
          self.testapi.project_view("lol")
          self.fail
    
    def test_edit_project(self):
        self.assertTrue(self.testapi.edit_project(self.project1.project_id, {"display_name": "2222"}))
        self.assertEqual(self.project1.display_name, "2222")
        self.assertEqual(self.testapi.project_view(self.project1.project_id).display_name, "2222")

    def test_assign_team_to_project(self): 
        self.team2.add_team_lead(self.lead_user.github_id)
        self.assertTrue(self.testapi.assign_helper(self.project2.project_id, self.team2.github_team_name, self.lead_user.slack_id, False))
    
    def test_assign_team_to_existing_project(self): 
        self.assertFalse(self.testapi.assign_helper(self.project1.project_id, self.team2.github_team_name, self.lead_user.slack_id, False))

    def test_unassign_team(self): 
        self.team1.add_team_lead(self.lead_user.github_id)
        self.assertTrue(self.testapi.unassign_helper(self.project1.project_id, self.lead_user.slack_id))
        self.assertEqual(self.project1.github_team_id, "")
    
    def test_unassign_team_no_perms(self):
        self.assertFalse(self.testapi.unassign_helper(self.project1.project_id, self.regular_user.slack_id))
    
    def test_delete_project(self):
        self.team2.add_team_lead(self.lead_user.github_id)
        self.testapi.assign_helper(self.project2.project_id, self.team2.github_team_name, self.lead_user.slack_id, False)
        self.assertTrue(self.testapi.delete_helper(self.project2.project_id, self.lead_user.slack_id, True))
    
    def test_delete_project_no_perms(self):
        self.team2.add_team_lead(self.lead_user.github_id)
        self.testapi.assign_helper(self.project2.project_id, self.team2.github_team_name, self.lead_user.slack_id, False)
        self.assertFalse(self.testapi.delete_helper(self.project2.project_id, self.regular_user.slack_id, True))
