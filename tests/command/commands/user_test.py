"""Test user command parsing."""
from command.commands.user import UserCommand


help_text = "User Command Reference:\n\n @rocket user\n\n Options:\n\n" \
             " edit \n --name NAME\n" \
             " --email ADDRESS\n --pos YOURPOSITION\n" \
             " --major YOURMAJOR\n --bio YOURBIO\n" \
             " 'edit properties of your Launch Pad profile\n" \
             " surround arguments with spaces with single quotes'" \
             "\n ADMIN/TEAM LEAD ONLY option: --member MEMBER_ID\n" \
             " 'edit properties of another user's Launch Pad profile'\n\n" \
             " view MEMBER_ID\n 'view information about a user'\n\n " \
             "help\n 'outputs options for user commands'\n\n " \
             "ADMIN ONLY\n\n delete MEMBER_ID\n" \
             " 'permanently delete member's Launch Pad profile'"


def test_get_command_name():
    """Test user command get_name method."""
    testcommand = UserCommand()
    assert testcommand.get_name() == "user"


def test_get_help():
    """Test user command get_help method."""
    testcommand = UserCommand()
    assert testcommand.get_help() == help_text


def test_handle_view():
    """Test user command view parser and handle method."""
    testcommand = UserCommand()
    assert testcommand.handle('user view asd') == "asd"


def test_handle_help():
    """Test user command help parser."""
    testcommand = UserCommand()
    assert testcommand.handle('user help') == help_text


def test_handle_delete():
    """Test user command delete parser."""
    testcommand = UserCommand()
    assert testcommand.handle('user delete asd') == "deleting asd"


def test_handle_edit_name():
    """Test user command edit parser with one field."""
    testcommand = UserCommand()
    assert testcommand.handle("user edit --name rob") == \
        "user edited: name: rob, "


def test_handle_edit():
    """Test user command edit parser with all field."""
    result = "user edited: member: id, name: rob, email: rob@rob.com, " \
             "position: dev, github: rob@.github.com, major: Computer " \
             "Science, bio: Im a human"
    testcommand = UserCommand()
    assert testcommand.handle("user edit --name rob --member id "
                              "--email rob@rob.com --pos "
                              "dev --github rob@.github.com "
                              "--major 'Computer Science' "
                              "--bio 'Im a human'") == result
