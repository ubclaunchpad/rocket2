"""Test the common business logic for the team command APIs."""
from api.command import CommandApis
from db import DBFacade
from interface.github import GithubInterface, GithubAPIException
from interface.slack import Bot, SlackAPIError
from app.model import User, Team, Permissions
from unittest import mock, TestCase


class TestTeamCommandApis(TestCase):
    """Test Case for TeamCommandApi methods."""

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

        def mock_facade_retrieve_side_effect(*args, **kwargs):
            """Mock behavior of the retrieve mock facade function."""
            slack_id = args[1]
            if slack_id == self.regular_user.slack_id:
                return self.regular_user
            elif slack_id == self.lead_user.slack_id:
                return self.lead_user
            elif slack_id == self.admin_user.slack_id:
                return self.admin_user
            else:
                raise LookupError

        self.mock_facade.retrieve.side_effect = \
            mock_facade_retrieve_side_effect

        def mock_facade_query_side_effect(*args, **kwargs):
            """Mock behavior of the query mock facade function."""
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

            return query_teams

        self.mock_facade.query.side_effect = \
            mock_facade_query_side_effect

        # In most cases, store will need to return True for tests
        self.mock_facade.store.return_value = True

    def test_list(self) -> None:
        """Test list team command API."""
        all_teams = self.testapi.team_list()
        self.assertListEqual(all_teams,
                             [
                                 self.team1,
                                 self.team2,
                                 self.team3,
                                 self.team3_dup
                             ])

    def test_view_missing_team(self) -> None:
        """Test view team command API with missing team."""
        self.mock_facade.query.return_value = []
        try:
            self.testapi.team_view("no_team")
        except LookupError:
            pass
        else:
            self.assertTrue(False)

    def test_view_multiple_teams(self) -> None:
        """Test view team command API with multiple matching teams."""
        try:
            self.testapi.team_view("gh3")
        except RuntimeError:
            pass
        else:
            self.assertTrue(False)

    def test_view_single_team(self) -> None:
        """Test view team command API with singular matching team."""
        team = self.testapi.team_view("gh1")
        self.assertEqual(team, self.team1)

    def test_create_missing_creator(self) -> None:
        """Test create team command API with missing calling user."""
        try:
            self.testapi.team_create("no_user", "team_name")
        except LookupError:
            pass
        else:
            self.assertTrue(False)

    def test_create_non_lead_creator(self) -> None:
        """Test create team command API with non lead calling user."""
        try:
            self.testapi.team_create("regular", "team_name")
        except PermissionError:
            pass
        else:
            self.assertTrue(False)

    def test_create_gh_team_creation_error(self) -> None:
        """Test create team command API with Github team creation error."""
        self.mock_github.org_create_team.side_effect = GithubAPIException("")
        try:
            self.testapi.team_create("lead", "team_name")
        except GithubAPIException:
            pass
        else:
            self.assertTrue(False)

    def test_create_gh_team_add_member_error(self) -> None:
        """Test create team command API with Github team member add error."""
        self.mock_github.add_team_member.side_effect = GithubAPIException("")
        try:
            self.testapi.team_create("lead", "team_name")
        except GithubAPIException:
            pass
        else:
            self.assertTrue(False)

    def test_create_success(self) -> None:
        """Test create team command API with successful creation."""
        self.mock_github.org_create_team.return_value = "team_gh_id"
        created = self.testapi.team_create("lead", "team_name")
        self.assertTrue(created)
        stored_team = Team("team_gh_id", "team_name", "")
        stored_team.add_member(self.lead_user.github_id)
        stored_team.add_team_lead(self.lead_user.github_id)
        self.mock_github.add_team_member.assert_called_once_with(
            self.lead_user.github_username, "team_gh_id")
        self.mock_facade.store.assert_called_once_with(stored_team)

    def test_create_with_display_name(self) -> None:
        """Test create team command API with display name."""
        self.mock_github.org_create_team.return_value = "team_gh_id"
        created = self.testapi.team_create("lead",
                                           "team_name",
                                           display_name="display_name")
        self.assertTrue(created)
        stored_team = Team("team_gh_id", "team_name", "display_name")
        stored_team.add_member(self.lead_user.github_id)
        stored_team.add_team_lead(self.lead_user.github_id)
        self.mock_facade.store.assert_called_with(stored_team)

    def test_create_with_platform(self) -> None:
        """Test create team command API with platform."""
        self.mock_github.org_create_team.return_value = "team_gh_id"
        created = self.testapi.team_create("lead",
                                           "team_name",
                                           platform="platform")
        self.assertTrue(created)
        stored_team = Team("team_gh_id", "team_name", "")
        stored_team.platform = "platform"
        stored_team.add_member(self.lead_user.github_id)
        stored_team.add_team_lead(self.lead_user.github_id)
        self.mock_facade.store.assert_called_with(stored_team)

    def test_create_get_channel_members_error(self) -> None:
        """Test create team command API with error getting channel users."""
        self.mock_slack.get_channel_users.side_effect = SlackAPIError("")
        try:
            self.testapi.team_create("lead", "team_name", channel="channel")
        except SlackAPIError:
            pass
        else:
            self.assertTrue(False)

    def test_create_missing_slack_user_from_channel(self) -> None:
        """Test create team command API with missing channel member."""
        self.mock_slack.get_channel_users.return_value = {"missing": None}
        try:
            self.testapi.team_create("lead", "team_name", channel="channel")
        except LookupError:
            self.assertTrue(False)
        else:
            self.assertEqual(self.mock_github.add_team_member.call_count, 0)

    def test_create_add_channel_member_gh_team_error(self) -> None:
        """Test create team command API adding channel member to Github."""
        self.mock_slack.get_channel_users.return_value = \
            {self.regular_user.slack_id: self.regular_user}
        self.mock_facade.bulk_retrieve.return_value = [self.regular_user]

        self.mock_github.add_team_member.side_effect = GithubAPIException("")

        try:
            self.testapi.team_create("lead", "team_name", channel="channel")
        except GithubAPIException:
            pass
        else:
            self.assertTrue(False)

    def test_create_add_channel_members(self) -> None:
        """Test create team command API with specified channel."""
        self.mock_slack.get_channel_users.return_value = \
            {self.regular_user.slack_id: self.regular_user}
        self.mock_facade.bulk_retrieve.return_value = [self.regular_user]
        self.mock_github.org_create_team.return_value = "team_gh_id"
        created = self.testapi.team_create(
            "lead", "team_name", channel="channel")
        self.assertTrue(created)
        stored_team = Team("team_gh_id", "team_name", "")
        stored_team.add_member(self.regular_user.github_id)
        stored_team.add_team_lead(self.lead_user.github_id)
        self.mock_github.add_team_member.assert_called_with(
            self.regular_user.github_username, "team_gh_id")
        self.mock_facade.store.assert_called_once_with(stored_team)

    def test_create_missing_lead(self) -> None:
        """Test create team command API with missing team lead."""
        try:
            self.testapi.team_create(
                "lead", "team_name", lead_id="missing")
        except LookupError:
            pass
        else:
            self.assertTrue(False)

    def test_create_with_lead_check_team_error(self) -> None:
        """Test create team command API with error from checking team."""
        self.mock_github.has_team_member.side_effect = GithubAPIException("")
        try:
            self.testapi.team_create(
                "admin", "team_name", lead_id="lead")
        except GithubAPIException:
            pass
        else:
            self.assertTrue(False)

    def test_create_with_lead_not_in_gh_team(self) -> None:
        """Test create team command API with lead not in Github team."""
        self.mock_github.org_create_team.return_value = "team_gh_id"
        self.mock_github.has_team_member.return_value = False
        self.testapi.team_create(
            "admin", "team_name", lead_id="lead")
        self.mock_github.add_team_member.assert_called_with(
            self.lead_user.github_username, "team_gh_id")

    def test_create_with_lead_in_gh_team(self) -> None:
        """Test create team command API with lead in Github team."""
        self.mock_github.org_create_team.return_value = "team_gh_id"
        self.mock_github.has_team_member.return_value = True
        self.testapi.team_create(
            "admin", "team_name", lead_id="lead")
        self.assertEqual(self.mock_github.add_team_member.call_count, 1)

    def test_create_with_non_lead_lead(self) -> None:
        """Test create team command API with non-lead lead."""
        self.mock_github.org_create_team.return_value = "team_gh_id"
        try:
            self.testapi.team_create("admin",
                                     "team_name",
                                     lead_id="regular")
        except PermissionError:
            pass
        else:
            self.assertTrue(False)

    def test_create_with_lead(self) -> None:
        """Test create team command API with lead."""
        self.mock_github.org_create_team.return_value = "team_gh_id"
        created = self.testapi.team_create(
            "admin", "team_name", lead_id="lead")
        self.assertTrue(created)
        stored_team = Team("team_gh_id", "team_name", "")
        stored_team.add_member(self.admin_user.github_id)
        stored_team.add_member(self.lead_user.github_id)
        stored_team.add_team_lead(self.lead_user.github_id)
        self.mock_facade.store.assert_called_once_with(stored_team)

    def test_create_store_fail(self) -> None:
        """Test create team command API with failing store."""
        self.mock_facade.store.return_value = False
        self.mock_github.org_create_team.return_value = "team_gh_id"
        created = self.testapi.team_create("lead", "team_name")
        self.assertFalse(created)
        stored_team = Team("team_gh_id", "team_name", "")
        stored_team.add_member(self.lead_user.github_id)
        stored_team.add_team_lead(self.lead_user.github_id)
        self.mock_github.add_team_member.assert_called_once_with(
            self.lead_user.github_username, "team_gh_id")
        self.mock_facade.store.assert_called_once_with(stored_team)

    def test_add_missing_adder(self) -> None:
        """Test add team command API with missing calling user."""
        try:
            self.testapi.team_add("no_user", "no_user_2", "team_name")
        except LookupError:
            pass
        else:
            self.assertTrue(False)

    def test_add_missing_team(self) -> None:
        """Test add team command API with missing team to add to."""
        try:
            self.testapi.team_add("lead", "regular", "missing_team")
        except LookupError:
            pass
        else:
            self.assertTrue(False)

    def test_add_non_unique_team(self) -> None:
        """Test add team command API with non unique Github team name."""
        try:
            self.testapi.team_add("lead", "regular", "gh3")
        except RuntimeError:
            pass
        else:
            self.assertTrue(False)

    def test_add_permission_error(self) -> None:
        """Test add team command API with caller without permissions."""
        try:
            self.testapi.team_add("regular", "lead", "gh1")
        except PermissionError:
            pass
        else:
            self.assertTrue(False)

    def test_add_missing_new_member(self) -> None:
        """Test add team command API with missing user."""
        self.team1.add_team_lead(self.lead_user.github_id)
        try:
            self.testapi.team_add("lead", "no_user", "gh1")
        except LookupError:
            pass
        else:
            self.assertTrue(False)

    def test_add_gh_team_add_member_error(self) -> None:
        """Test add team command API w/ error adding to Github team."""
        self.team1.add_team_lead(self.lead_user.github_id)
        self.mock_github.add_team_member.side_effect = GithubAPIException("")
        try:
            self.testapi.team_add("lead", "regular", "gh1")
        except GithubAPIException:
            pass
        else:
            self.assertTrue(False)

    def test_add_success(self) -> None:
        """Test add team command API successful execution."""
        self.team1.add_team_lead(self.lead_user.github_id)
        added = self.testapi.team_add("lead", "regular", "gh1")
        self.assertTrue(added)
        self.assertTrue(self.team1.has_member(self.regular_user.github_id))
        self.mock_github.add_team_member.assert_called_once_with(
            self.regular_user.github_username,
            self.team1.github_team_id
        )

    def test_add_fail(self) -> None:
        """Test add team command API when store fails."""
        self.team1.add_team_lead(self.lead_user.github_id)
        self.mock_facade.store.return_value = False
        added = self.testapi.team_add("lead", "regular", "gh1")
        self.assertFalse(added)

    def test_remove_missing_remover(self) -> None:
        """Test remove team command API with missing remover."""
        try:
            self.testapi.team_remove("no_user", "gh1", "regular")
        except LookupError:
            pass
        else:
            self.assertTrue(False)

    def test_remove_missing_team(self) -> None:
        """Test remove team command API with missing team."""
        try:
            self.testapi.team_remove("lead", "no_team", "regular")
        except LookupError:
            pass
        else:
            self.assertTrue(False)

    def test_remove_non_unique_team(self) -> None:
        """Test remove team command API with non unique Github team name."""
        try:
            self.testapi.team_remove("lead", "gh3", "regular")
        except RuntimeError:
            pass
        else:
            self.assertTrue(False)

    def test_remove_permission_error(self) -> None:
        """Test remove team command API with caller without permissions."""
        try:
            self.testapi.team_remove("regular", "gh1", "lead")
        except PermissionError:
            pass
        else:
            self.assertTrue(False)

    def test_remove_missing_user_to_remove(self) -> None:
        """Test remove team command API with missing member to remove."""
        try:
            self.testapi.team_remove("lead", "gh1", "no_user")
        except PermissionError:
            pass
        else:
            self.assertTrue(False)

    def test_remove_gh_team_not_has_member(self) -> None:
        """Test remove team command API when member not in Github team."""
        self.team1.add_team_lead(self.lead_user.github_id)
        self.mock_github.has_team_member.return_value = False
        try:
            self.testapi.team_remove("lead", "gh1", "regular")
        except GithubAPIException:
            pass
        else:
            self.assertTrue(False)

    def test_remove_gh_team_gh_exception(self) -> None:
        """Test remove team command API when GithubAPIException is raised."""
        self.team1.add_team_lead(self.lead_user.github_id)
        self.mock_github.has_team_member.side_effect = GithubAPIException("")
        try:
            self.testapi.team_remove("lead", "gh1", "regular")
        except GithubAPIException:
            pass
        else:
            self.assertTrue(False)

    def test_remove_store_fail(self) -> None:
        """Test remove team command API when db store fails."""
        self.team1.add_team_lead(self.lead_user.github_id)
        self.mock_github.has_team_member.return_value = True
        self.mock_facade.store.return_value = False
        removed = self.testapi.team_remove("lead", "gh1", "regular")
        self.assertFalse(removed)

    def test_remove_success(self) -> None:
        """Test remove team command API successful execution."""
        self.team1.add_team_lead(self.lead_user.github_id)
        self.mock_github.has_team_member.return_value = True
        removed = self.testapi.team_remove("lead", "gh1", "regular")
        self.assertTrue(removed)
        self.assertFalse(self.team1.has_member(self.regular_user.github_id))
        self.mock_github.remove_team_member.assert_called_once_with(
            self.regular_user.github_username,
            self.team1.github_team_id
        )

    def test_remove_lead_success(self) -> None:
        """Test remove team command API on lead successful execution."""
        self.team1.add_team_lead(self.lead_user.github_id)
        self.mock_github.has_team_member.return_value = True
        removed = self.testapi.team_remove("lead", "gh1", "lead")
        self.assertTrue(removed)
        self.assertFalse(self.team1.has_member(self.lead_user.github_id))
        self.assertFalse(self.team1.has_team_lead(self.lead_user.github_id))
        self.mock_github.remove_team_member.assert_called_once_with(
            self.lead_user.github_username,
            self.team1.github_team_id
        )

    def test_edit_missing_editor(self) -> None:
        """Test edit team command API with missing calling user."""
        try:
            self.testapi.team_edit("no_user", "gh1")
        except LookupError:
            pass
        else:
            self.assertTrue(False)

    def test_edit_missing_team(self) -> None:
        """Test edit team command API with missing team."""
        try:
            self.testapi.team_edit("lead", "no_team")
        except LookupError:
            pass
        else:
            self.assertTrue(False)

    def test_edit_non_unique_team(self) -> None:
        """Test edit team command API with non unique Github team name."""
        try:
            self.testapi.team_edit("lead", "gh3")
        except RuntimeError:
            pass
        else:
            self.assertTrue(False)

    def test_edit_permission_error(self) -> None:
        """Test edit team command API with caller without permissions."""
        try:
            self.testapi.team_edit("regular", "gh1")
        except PermissionError:
            pass
        else:
            self.assertTrue(False)

    def test_edit_store_fail(self) -> None:
        """Test edit team command API when db store fails."""
        self.mock_facade.store.return_value = False
        self.team1.add_team_lead(self.lead_user.github_id)
        edited = self.testapi.team_edit("lead",
                                        "gh1",
                                        display_name="tempname")
        self.assertFalse(edited)

    def test_edit_display_name(self) -> None:
        """Test edit team command API to edit team display name."""
        self.team1.add_team_lead(self.lead_user.github_id)
        edited = self.testapi.team_edit("lead",
                                        "gh1",
                                        display_name="tempname")
        self.assertTrue(edited)
        self.assertEqual("tempname", self.team1.display_name)

    def test_edit_platform(self) -> None:
        """Test edit team command API to edit platform."""
        self.team1.add_team_lead(self.lead_user.github_id)
        edited = self.testapi.team_edit("lead",
                                        "gh1",
                                        platform="tempplat")
        self.assertTrue(edited)
        self.assertEqual("tempplat", self.team1.platform)

    def test_lead_missing_lead_assigner(self) -> None:
        """Test lead team command API with missing calling user."""
        try:
            self.testapi.team_lead("no_user", "lead", "gh1")
        except LookupError:
            pass
        else:
            self.assertTrue(False)

    def test_lead_missing_team(self) -> None:
        """Test lead team command API with missing team."""
        try:
            self.testapi.team_lead("lead", "regular", "no_team")
        except LookupError:
            pass
        else:
            self.assertTrue(False)

    def test_lead_non_unique_team(self) -> None:
        """Test lead team command API with non unique Github team name."""
        try:
            self.testapi.team_lead("lead", "regular", "gh3")
        except RuntimeError:
            pass
        else:
            self.assertTrue(False)

    def test_lead_permission_error(self) -> None:
        """Test lead team command API with caller without permissions."""
        try:
            self.testapi.team_lead("regular", "lead", "gh1")
        except PermissionError:
            pass
        else:
            self.assertTrue(False)

    def test_lead_missing_intended_lead(self) -> None:
        """Test lead team command API with missing intended lead."""
        self.team1.add_team_lead(self.lead_user.github_id)
        try:
            self.testapi.team_lead("lead", "no_user", "gh1")
        except LookupError:
            pass
        else:
            self.assertTrue(False)

    def test_lead_gh_team_add_member_error(self) -> None:
        """Test lead team command API with Github team member add error."""
        self.mock_github.add_team_member.side_effect = GithubAPIException("")
        self.team1.add_team_lead(self.lead_user.github_id)
        try:
            self.testapi.team_lead("lead", "regular", "gh1")
        except GithubAPIException:
            pass
        else:
            self.assertTrue(False)

    def test_lead_store_fail(self) -> None:
        """Test lead command API failing store."""
        self.mock_facade.store.return_value = False
        self.team1.add_team_lead(self.lead_user.github_id)
        lead_assigned = self.testapi.team_lead("lead", "regular", "gh1")
        self.assertFalse(lead_assigned)

    def test_lead_successful(self) -> None:
        """Test lead team command API setting team lead successfully."""
        self.team1.add_team_lead(self.lead_user.github_id)
        lead_assigned = self.testapi.team_lead("lead", "regular", "gh1")
        self.mock_github.add_team_member.assert_called_once_with(
            self.regular_user.github_username,
            self.team1.github_team_id
        )
        self.assertTrue(lead_assigned)
        self.assertTrue(self.team1.has_member(self.regular_user.github_id))
        self.assertTrue(self.team1.has_team_lead(self.regular_user.github_id))

    def test_lead_remove_not_in_team(self) -> None:
        """Test lead team command API remove a member not in a team."""
        self.team1.add_team_lead(self.lead_user.github_id)
        try:
            self.testapi.team_lead("lead", "regular", "gh1", remove=True)
        except LookupError:
            pass
        else:
            self.assertTrue(False)

    def test_lead_remove_not_lead_of_team(self) -> None:
        """Test lead team command API remove a member not lead of team."""
        self.team1.add_team_lead(self.lead_user.github_id)
        self.team1.add_member(self.regular_user.github_id)
        try:
            self.testapi.team_lead("lead", "regular", "gh1", remove=True)
        except LookupError:
            pass
        else:
            self.assertTrue(False)

    def test_lead_remove_store_fail(self) -> None:
        """Test lead command API removal failing store."""
        self.mock_facade.store.return_value = False
        self.team1.add_team_lead(self.lead_user.github_id)
        self.team1.add_member(self.regular_user.github_id)
        self.team1.add_team_lead(self.regular_user.github_id)
        lead_removed = self.testapi.team_lead("lead", "regular", "gh1",
                                              remove=True)
        self.assertFalse(lead_removed)

    def test_lead_remove_successful(self) -> None:
        """Test lead team command API successfully remove lead from team."""
        self.team1.add_team_lead(self.lead_user.github_id)
        self.team1.add_member(self.regular_user.github_id)
        self.team1.add_team_lead(self.regular_user.github_id)
        lead_removed = self.testapi.team_lead("lead", "regular", "gh1",
                                              remove=True)
        self.assertTrue(lead_removed)
        self.assertTrue(self.team1.has_member(self.regular_user.github_id))
        self.assertFalse(self.team1.has_team_lead(self.regular_user.github_id))

    def test_delete_missing_deleter(self) -> None:
        """Test delete team command API with missing calling user."""
        try:
            self.testapi.team_delete("no_user", "gh1")
        except LookupError:
            pass
        else:
            self.assertTrue(False)

    def test_delete_missing_team(self) -> None:
        """Test delete team command API with missing team."""
        try:
            self.testapi.team_delete("lead", "no_team")
        except LookupError:
            pass
        else:
            self.assertTrue(False)

    def test_delete_non_unique_team(self) -> None:
        """Test delete team command API with non unique Github team name."""
        try:
            self.testapi.team_delete("lead", "gh3")
        except RuntimeError:
            pass
        else:
            self.assertTrue(False)

    def test_delete_permission_error(self) -> None:
        """Test delete team command API with caller without permissions."""
        try:
            self.testapi.team_delete("regular", "gh1")
        except PermissionError:
            pass
        else:
            self.assertTrue(False)

    def test_delete_gh_team_delete_team_error(self) -> None:
        """Test delete team command API with Github team delete error."""
        self.mock_github.org_delete_team.side_effect = GithubAPIException("")
        self.team1.add_team_lead(self.lead_user.github_id)
        try:
            self.testapi.team_delete("lead", "gh1")
        except GithubAPIException:
            pass
        else:
            self.assertTrue(False)

    def test_delete_successful(self) -> None:
        """Test delete team command API deleting team successfully."""
        self.team1.add_team_lead(self.lead_user.github_id)
        self.testapi.team_delete("lead", "gh1")
        self.mock_github.org_delete_team.assert_called_once_with(
            int(self.team1.github_team_id))
        self.mock_facade.delete.assert_called_once_with(
            Team,
            self.team1.github_team_id)

    def test_refresh_missing_refresher(self) -> None:
        """Test refresh team command API with missing calling user."""
        try:
            self.testapi.team_refresh("no_user")
        except LookupError:
            pass
        else:
            self.assertTrue(False)

    def test_refresh_permission_error(self) -> None:
        """Test refresh team command API with caller without permissions."""
        try:
            self.testapi.team_refresh("regular")
        except PermissionError:
            pass
        else:
            self.assertTrue(False)

    def test_refresh_gh_get_teams_error(self) -> None:
        """Test refresh team command API with Github error getting teams."""
        self.mock_github.org_get_teams.side_effect = GithubAPIException("")
        try:
            self.testapi.team_refresh("admin")
        except GithubAPIException:
            pass
        else:
            self.assertTrue(False)

    def test_refresh_github_deleted(self) -> None:
        """Test refresh team command API with teams removed from Github."""
        self.mock_github.org_get_teams.return_value = [
            self.team2,
            self.team3,
            self.team3_dup
        ]
        refreshed = self.testapi.team_refresh("admin")
        self.assertTrue(refreshed)
        self.mock_facade.delete.assert_called_once_with(
            Team, self.team1.github_team_id)

    def test_refresh_github_added_failed_store(self) -> None:
        """Test refresh team command API unable to store new Github teams."""
        team5 = Team("5", "gh5", "name5")
        self.mock_github.org_get_teams.return_value = [
            self.team1,
            self.team2,
            self.team3,
            self.team3_dup,
            team5
        ]
        self.mock_facade.store.return_value = False
        refreshed = self.testapi.team_refresh("admin")
        self.assertFalse(refreshed)
        self.mock_facade.store.assert_called_once_with(team5)

    def test_refresh_github_added_success(self) -> None:
        """Test refresh team command API storing new Github teams."""
        team5 = Team("5", "gh5", "name5")
        self.mock_github.org_get_teams.return_value = [
            self.team1,
            self.team2,
            self.team3,
            self.team3_dup,
            team5
        ]
        refreshed = self.testapi.team_refresh("admin")
        self.assertTrue(refreshed)
        self.mock_facade.store.assert_called_once_with(team5)

    def test_refresh_github_changed_failed_store(self) -> None:
        """Test refresh team command API unable to edit teams."""
        new_team1 = Team("1", "newgh1", "name1")
        new_team1.add_member(self.regular_user.github_id)
        self.mock_github.org_get_teams.return_value = [
            new_team1,
            self.team2,
            self.team3,
            self.team3_dup,
        ]
        self.mock_facade.store.return_value = False
        refreshed = self.testapi.team_refresh("admin")
        self.assertFalse(refreshed)
        self.team1.github_team_name = "newgh1"
        self.team1.add_member(self.regular_user.github_id)
        self.mock_facade.store.assert_called_once_with(self.team1)

    def test_refresh_github_changed_success(self) -> None:
        """Test refresh team command API to edit teams."""
        new_team1 = Team("1", "newgh1", "name1")
        new_team1.add_member(self.regular_user.github_id)
        self.mock_github.org_get_teams.return_value = [
            new_team1,
            self.team2,
            self.team3,
            self.team3_dup,
        ]
        refreshed = self.testapi.team_refresh("admin")
        self.assertTrue(refreshed)
        self.team1.github_team_name = "newgh1"
        self.team1.add_member(self.regular_user.github_id)
        self.mock_facade.store.assert_called_once_with(self.team1)
