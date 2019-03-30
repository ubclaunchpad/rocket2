"""Test slack message formatting utility class."""
from utils.slack_msg_fmt import wrap_slack_code
from utils.slack_msg_fmt import wrap_code_block
from utils.slack_msg_fmt import wrap_quote
from utils.slack_msg_fmt import wrap_emph
from unittest import TestCase


class TestGithubInterface(TestCase):
    """Unittest TestCase for testing SlackMsgFmt."""

    def test_code(self):
        """Test code formatting."""
        code = 'map(lambda x: x)'
        assert wrap_slack_code(code) == f"`{code}`"

    def test_code_block(self):
        """Test code block formatting."""
        code_block = 'map(lambda x: x)\nmap(lambda x: x)'
        assert wrap_code_block(code_block) == f"```\n{code_block}\n```"

    def test_quote(self):
        """Test quote formatting."""
        quote = 'this is\na multi-line\n quote.'
        assert wrap_quote(quote) == f"> {quote}\n"

    def test_emph(self):
        """Test emph formatting."""
        emph = 'THIS IS VERY IMPORTANT!!!\nPLEASE READ IT!!!'
        assert wrap_emph(emph) == f"*{emph}*"
