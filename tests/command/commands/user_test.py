"""Test user command parsing."""
from command.commands.user import UserCommand


def test_get_command_name():
    """Test user command get_name method."""
    testcommand = UserCommand()
    assert testcommand.get_name() == "user"


def test_get_help():
    """Test user command get_help method."""
    testcommand = UserCommand()
    assert testcommand.get_help() == UserCommand.help


def test_handle_nosubs():
    """Test user with no sub-parsers."""
    testcommand = UserCommand()
    assert testcommand.handle('user') == UserCommand.help


def test_handle_bad_args():
    """Test user with invalid arguments."""
    testcommand = UserCommand()
    assert testcommand.handle('user geese-say-honk') == UserCommand.help


def test_handle_view():
    """Test user command view parser and handle method."""
    user_id = "U0G9QF9C6"
    testcommand = UserCommand()
    assert testcommand.handle('user view --slack_id asd', user_id) == "asd"
    assert testcommand.handle('user view', user_id) == "U0G9QF9C6"


def test_handle_help():
    """Test user command help parser."""
    testcommand = UserCommand()
    assert testcommand.handle('user help', "U0G9QF9C6") == UserCommand.help


def test_handle_delete():
    """Test user command delete parser."""
    testcommand = UserCommand()
    assert testcommand.handle('user delete asd', "U0G9QF9C6") == "deleting asd"


def test_handle_edit_name():
    """Test user command edit parser with one field."""
    testcommand = UserCommand()
    assert testcommand.handle("user edit --name rob", "U0G9QF9C6") == \
        "user edited: name: rob, "


def test_handle_edit():
    """Test user command edit parser with all fields."""
    result = "user edited: member: id, name: rob, email: rob@rob.com, " \
             "position: dev, github: rob@.github.com, major: Computer " \
             "Science, bio: Im a human"
    testcommand = UserCommand()
    assert testcommand.handle("user edit --name rob --member id "
                              "--email rob@rob.com --pos "
                              "dev --github rob@.github.com "
                              "--major 'Computer Science' "
                              "--bio 'Im a human'", "U0G9QF9C6") == result
