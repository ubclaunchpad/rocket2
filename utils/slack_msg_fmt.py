"""Utility class for formatting Slack Messages."""


class SlackMsgFmt():
    def code(self, str):
        return f"`{str}`"

    def code_block(self, str):
        return f"```\n{str}\n```"

    def quote(self, str):
        return f"> {str}\n"

    def emph(self, str):
        return f"*{str}*"
