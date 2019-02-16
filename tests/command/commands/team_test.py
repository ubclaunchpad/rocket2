"""Test team command parsing."""
from command.commands.team import TeamCommand
from unittest import TestCase


help_text = "\n*team commands:*```\n*list commands*\nusage: /rocket team " \
            "list [-h]\n\noptional arguments:\n  -h, --help  show this " \
            "help message and exit\n\n*view commands*\nusage: /rocket team " \
            "view [-h] team_name\n\npositional arguments:\n  " \
            "team_name\n\noptional arguments:\n  -h, --help  show this " \
            "help message and exit\n\n*delete commands*\nusage: /rocket " \
            "team delete [-h] team_name\n\npositional arguments:\n  " \
            "team_name\n\noptional arguments:\n  -h, --help  show this " \
            "help message and exit\n\n*create commands*\nusage: /rocket " \
            "team create [-h] [--name NAME] [--platform PLATFORM]\n        " \
            "                   [--channel]\n                           " \
            "team_name\n\npositional arguments:\n  team_name            " \
            "Github name of your team (required)\n\noptional arguments:\n  " \
            "-h, --help           show this help message and exit\n  " \
            "--name NAME          display name of your team\n  --platform " \
            "PLATFORM  the team's main platform\n  --channel            " \
            "add all members of this channel to the created team\n\n*add " \
            "commands*\nusage: /rocket team add [-h] team_name " \
            "slack_id\n\npositional arguments:\n  team_name   team to add " \
            "the user to\n  slack_id    user to be added to " \
            "team\n\noptional arguments:\n  -h, --help  show this help " \
            "message and exit\n\n*remove commands*\nusage: /rocket team " \
            "remove [-h] team_name slack_id\n\npositional arguments:\n  " \
            "team_name   team to remove user from\n  slack_id    user to " \
            "be removed from team\n\noptional arguments:\n  -h, --help  " \
            "show this help message and exit\n\n*edit commands*\nusage: " \
            "/rocket team edit [-h] [--name NAME] [--platform PLATFORM] " \
            "team_name\n\npositional arguments:\n  team_name            " \
            "name of team to edit\n\noptional arguments:\n  -h, --help     " \
            "      show this help message and exit\n  --name NAME          " \
            "display name the team should have\n  --platform PLATFORM  " \
            "platform the team should have\n```"
user = 'U123456789'
user2 = 'U234567891'


class TestTeamCommand(TestCase):
    """Test case for TeamCommand class."""

    def test_get_name(self):
        """Test team command get_name method."""
        testcommand = TeamCommand()
        self.assertEqual(testcommand.get_name(), "team")

    def test_get_help(self):
        """Test team command get_help method."""
        testcommand = TeamCommand()
        self.assertEqual(testcommand.help, help_text)

    def test_handle_list(self):
        """Test team command list parser."""
        testcommand = TeamCommand()
        self.assertTupleEqual(testcommand.handle("team list", user),
                              ("listing all teams", 200))

    def test_handle_view(self):
        """Test team command view parser."""
        testcommand = TeamCommand()
        self.assertTupleEqual(testcommand.handle("team view b-s", user),
                              ("viewing b-s", 200))

    def test_handle_help(self):
        """Test team command help parser."""
        testcommand = TeamCommand()
        self.assertTupleEqual(testcommand.handle('team help', user),
                              (help_text, 200))

    def test_handle_delete(self):
        """Test team command delete parser."""
        testcommand = TeamCommand()
        self.assertTupleEqual(testcommand.handle("team delete b-s", user),
                              ("b-s was deleted", 200))

    def test_handle_create(self):
        """Test team command create parser."""
        testcommand = TeamCommand()
        inputstring = "team create b-s --name 'B S'"
        outputstring = "new team: b-s, name: B S, "
        self.assertTupleEqual(testcommand.handle(inputstring, user),
                              (outputstring, 200))
        inputstring += " --platform web"
        outputstring += "platform: web, "
        self.assertTupleEqual(testcommand.handle(inputstring, user),
                              (outputstring, 200))
        inputstring += " --channel"
        outputstring += "add channel"

    def test_handle_add(self):
        """Test team command add parser."""
        testcommand = TeamCommand()
        self.assertTupleEqual(testcommand.handle("team add b-s ID", user),
                              ("added ID to b-s", 200))

    def test_handle_remove(self):
        """Test team command remove parser."""
        testcommand = TeamCommand()
        self.assertTupleEqual(testcommand.handle("team remove b-s ID", user),
                              ("removed ID from b-s", 200))

    def test_handle_edit(self):
        """Test team command edit parser."""
        testcommand = TeamCommand()
        inputstring = "team edit b-s --name 'B S'"
        outputstring = "team edited: b-s, name: B S, "
        self.assertTupleEqual(testcommand.handle(inputstring, user),
                              (outputstring, 200))
        inputstring += " --platform web"
        outputstring += "platform: web, "
        self.assertTupleEqual(testcommand.handle(inputstring, user),
                              (outputstring, 200))
