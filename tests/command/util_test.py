"""Some tests for utility functions in commands utility."""
import command.util as util


def test_regularize_char_standard():
    """Test how this function reacts to normal operation."""
    assert util.regularize_char('a') == 'a'
    assert util.regularize_char(' ') == ' '
    assert util.regularize_char('\'') == '\''
    assert util.regularize_char('‘') == '\''
    assert util.regularize_char('’') == '\''
    assert util.regularize_char('“') == '"'
    assert util.regularize_char('”') == '"'


def test_escaped_id_conversion():
    """Test how this function reacts to normal operation."""
    CMDS = [
        # Normal operation
        ('/rocket user edit --member <@U1234|user> --name "User"',
         '/rocket user edit --member U1234 --name "User"'),
        # No users
        ('/rocket user view',
         '/rocket user view'),
        # Multiple users
        ('/rocket foo <@U1234|user> <@U4321|ruse> <@U3412|sure> -h',
         '/rocket foo U1234 U4321 U3412 -h')
    ]

    for inp, expect in CMDS:
        assert util.escaped_id_to_id(inp) == expect
