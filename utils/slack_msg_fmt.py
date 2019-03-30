"""Utility class for formatting Slack Messages."""


def wrap_slack_code(str):
    """Format code."""
    return f"`{str}`"


def wrap_code_block(str):
    """Format code block."""
    return f"```\n{str}\n```"


def wrap_quote(str):
    """Format quote."""
    return f"> {str}\n"


def wrap_emph(str):
    """Format emph."""
    return f"*{str}*"
