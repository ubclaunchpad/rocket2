"""Test team command parsing."""
from command.commands.team import TeamCommand
from unittest import TestCase


help_text = TeamCommand.help
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
        self.assertEqual(testcommand.get_help(), help_text)

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
