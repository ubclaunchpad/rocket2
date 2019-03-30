"""Utility class for formatting Slack Messages."""


class SlackMsgFmt():
    """Utils class for Slack Message Format."""

    def code(self, str):
        """Format code."""
        return f"`{str}`"

    def code_block(self, str):
        """Format code block."""
        return f"```\n{str}\n```"

    def quote(self, str):
        """Format quote."""
        return f"> {str}\n"

    def emph(self, str):
        """Format emph."""
        return f"*{str}*"
