"""Some important (and often-used) utility functions."""
from model.user import User
from model.team import Team
from model.permissions import Permissions


def create_test_user(slack_id):
    """
    Create a test user with slack id, and with all other attributes the same.

    :param slack_id: The slack id string
    :return: returns a filled-in user model (no empty strings)
    """
    u = User(slack_id)
    u.set_biography('I like puppies and kittens!')
    u.set_email('admin@ubc.ca')
    u.set_name('Iemann Atmin')
    u.set_github_username('kibbles')
    u.set_image_url('https://google.ca')
    u.set_major('Computer Science')
    u.set_permissions_level(Permissions.admin)
    u.set_position('Adrenaline Junkie')
    return u


def create_test_team(tid, team_name, display_name):
    """
    Create a test team with team name, and with all other attributes the same.

    :param team_name: The github team name string
    :return: returns a filled-in user model (no empty strings)
    """
    t = Team(tid, team_name, display_name)
    t.set_platform('slack')
    t.add_member('abc_123')
    return t
