"""Test slack message formatting utility class."""
from utils.slack_msg_fmt import SlackMsgFmt
from unittest import TestCase


class TestGithubInterface(TestCase):
    def setUp(self):
        self.sfmt = SlackMsgFmt()

    def test_code(self):
        code = 'map(lambda x: x)'
        assert self.sfmt.code(code) == f"`{code}`"

    def test_code_block(self):
        code_block = 'map(lambda x: x)\nmap(lambda x: x)'
        assert self.sfmt.code_block(code_block) == f"```\n{code_block}\n```"

    def test_quote(self):
        quote = 'this is\na multi-line\n quote.'
        assert self.sfmt.quote(quote) == f"> {quote}\n"

    def test_emph(self):
        emph = 'THIS IS VERY IMPORTANT!!!\nPLEASE READ IT!!!'
        assert self.sfmt.emph(emph) == f"*{emph}*"
