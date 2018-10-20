"""Test Bot Class."""
from bot.bot import Bot

def test_send_dm():
    """Test the Bot class method send_dm()."""
    bot = Bot()
    try:
        bot.send_dm("Hahahaha", "UD8UCTN05")
        assert True
    except:
        assert False

def test_send_to_channel():
    """Test the Bot class method send_to_channel()."""
    bot = Bot()
    try:
        bot.send_dm("Hahahaha", "#random")
        assert True
    except:
        assert False