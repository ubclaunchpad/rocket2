"""Some important (and often-used) utility functions."""
from app.model import User, Team, Permissions


def create_test_admin(slack_id: str) -> User:
    """
    Create a test admin user with slack id, and with all other attributes set.

    ==========  =============================
    Property    Preset
    ==========  =============================
    Slack ID    ``slack_id``
    Bio         I like puppies and kittens!
    Email       admin@ubc.ca
    Name        Iemann Atmin
    Github      kibbles
    Github ID   123453
    Image URL   https://via.placeholder.com/150
    Major       Computer Science
    Permission  Admin
    Position    Adrenaline Junkie
    ==========  =============================

    :param slack_id: The slack id string
    :return: a filled-in user model (no empty strings)
    """
    u = User(slack_id)
    u.biography = 'I like puppies and kittens!'
    u.email = 'admin@ubc.ca'
    u.name = 'Iemann Atmin'
    u.github_username = 'kibbles'
    u.github_id = '123453'
    u.image_url = 'https:///via.placeholder.com/150'
    u.major = 'Computer Science'
    u.permissions_level = Permissions.admin
    u.position = 'Adrenaline Junkie'
    u.karma = 1
    return u


def create_test_team(tid: str,
                     team_name: str,
                     display_name: str) -> Team:
    """
    Create a test team with team name, and with all other attributes the same.

    ==========  =============================
    Property    Preset
    ==========  =============================
    Github      ``tid``
    Name slug   ``team_name``
    Display     ``display_name``
    Platform    slack
    Members     ['abc_123']
    ==========  =============================

    :param tid: The github ID associated with the team
    :param team_name: The github team name slug
    :param display_name: The github team name
    :return: a filled-in team model (no empty strings)
    """
    t = Team(tid, team_name, display_name)
    t.platform = 'slack'
    t.add_member('abc_123')
    return t
