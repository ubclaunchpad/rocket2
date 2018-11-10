"""Test team command parsing."""
from command.commands.team import TeamCommand


help_text = """# Team Command Reference
    `@rocket team`
    All parameters with whitespace must be enclosed by quotation marks.
    ## Options to specify input
    * `list`
        * outputs the Github team names and display names of all teams
    * `view` GITHUB_TEAM_NAME
        * view information and members of a team
    * `help`
        * outputs options for team commands
    ## TEAM LEAD or ADMIN only
    * `create` GITHUB_TEAM_NAME [`--name` DISPLAY_NAME] [`--platform` PLATFORM]
        * create a new team with a Github team name and optional parameters
        * the user will be automatically added to the new team
    The following can only be used by a team lead in the team or an admin:
    * `edit` GITHUB_TEAM_NAME
        * [`--name` DISPLAY_NAME]
        * [`--platform` PLATFORM]
            * edit properties of specified team
    * `add` GITHUB_TEAM_NAME @Slack User
        * add the specified user to the team
    * `remove` GITHUB_TEAM_NAME @Slack User
        * remove the specified user from the team
    * `delete` GITHUB_TEAM_NAME
        * permanently delete the specified team"""


def test_get_name():
    """Test team command get_name method."""
    testcommand = TeamCommand()
    assert testcommand.get_name() == "team"


def test_get_help():
    """Test team command get_help method."""
    testcommand = TeamCommand()
    assert testcommand.get_help() == help_text


def test_handle_list():
    """Test team command list parser."""
    testcommand = TeamCommand()
    assert testcommand.handle("team list") == "listing all teams"


def test_handle_view():
    """Test team command view parser."""
    testcommand = TeamCommand()
    assert testcommand.handle("team view b-s") == "viewing b-s"


def test_handle_help():
    """Test team command help parser."""
    testcommand = TeamCommand()
    assert testcommand.handle('team help') == help_text


def test_handle_delete():
    """Test team command delete parser."""
    testcommand = TeamCommand()
    assert testcommand.handle("team delete b-s") == "b-s was deleted"


def test_handle_create():
    """Test team command create parser."""
    testcommand = TeamCommand()
    inputstring = "team create b-s --name 'B S'"
    outputstring = "new team: b-s, name: B S, "
    assert testcommand.handle(inputstring) == outputstring
    inputstring += " --platform web"
    outputstring += "platform: web, "
    assert testcommand.handle(inputstring) == outputstring


def test_handle_add():
    """Test team command add parser."""
    testcommand = TeamCommand()
    assert testcommand.handle("team add b-s ID") == "added ID to b-s"


def test_handle_remove():
    """Test team command remove parser."""
    testcommand = TeamCommand()
    assert testcommand.handle("team remove b-s ID") == "removed ID from b-s"


def test_handle_edit():
    """Test team command edit parser."""
    testcommand = TeamCommand()
    inputstring = "team edit b-s --name 'B S'"
    outputstring = "team edited: b-s, name: B S, "
    assert testcommand.handle(inputstring) == outputstring
    inputstring += " --platform web"
    outputstring += "platform: web, "
    assert testcommand.handle(inputstring) == outputstring
