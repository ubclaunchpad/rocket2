"""Test team command parsing."""
from command.commands.team import TeamCommand
from unittest import TestCase, mock


user = 'U123456789'
user2 = 'U234567891'


class TestTeamCommand(TestCase):
    """Test case for TeamCommand class."""

    def setUp(self):
        """Set up the test case environment."""
        self.gh = mock.MagicMock()
        self.db = mock.MagicMock()
        self.sc = mock.MagicMock()
        self.testcommand = TeamCommand(self.db, self.sc, self.gh)
        self.help_text = self.testcommand.help

    def test_get_name(self):
        """Test team command get_name method."""
        self.assertEqual(self.testcommand.get_name(), "team")

    def test_get_help(self):
        """Test team command get_help method."""
        print(f"\n{self.testcommand.get_help()}")
        self.assertEqual(self.testcommand.get_help(), self.help_text)

    def test_handle_list(self):
        """Test team command list parser."""
        self.assertTupleEqual(self.testcommand.handle("team list", user),
                              ("listing all teams", 200))

    def test_handle_view(self):
        """Test team command view parser."""
        self.assertTupleEqual(self.testcommand.handle("team view b-s", user),
                              ("viewing b-s", 200))

    def test_handle_help(self):
        """Test team command help parser."""
        self.assertTupleEqual(self.testcommand.handle('team help', user),
                              (self.help_text, 200))

    def test_handle_delete(self):
        """Test team command delete parser."""
        self.assertTupleEqual(self.testcommand.handle("team delete b-s", user),
                              ("b-s was deleted", 200))

    def test_handle_create(self):
        """Test team command create parser."""
        inputstring = "team create b-s --name 'B S'"
        outputstring = "new team: b-s, name: B S, "
        self.assertTupleEqual(self.testcommand.handle(inputstring, user),
                              (outputstring, 200))
        inputstring += " --platform web"
        outputstring += "platform: web, "
        self.assertTupleEqual(self.testcommand.handle(inputstring, user),
                              (outputstring, 200))
        inputstring += " --channel"
        outputstring += "add channel"

    def test_handle_add(self):
        """Test team command add parser."""
        self.assertTupleEqual(self.testcommand.handle("team add b-s ID", user),
                              ("added ID to b-s", 200))

    def test_handle_remove(self):
        """Test team command remove parser."""
        self.assertTupleEqual(
            self.testcommand.handle("team remove b-s ID", user),
            ("removed ID from b-s", 200))

    def test_handle_edit(self):
        """Test team command edit parser."""
        inputstring = "team edit b-s --name 'B S'"
        outputstring = "team edited: b-s, name: B S, "
        self.assertTupleEqual(self.testcommand.handle(inputstring, user),
                              (outputstring, 200))
        inputstring += " --platform web"
        outputstring += "platform: web, "
        self.assertTupleEqual(self.testcommand.handle(inputstring, user),
                              (outputstring, 200))
