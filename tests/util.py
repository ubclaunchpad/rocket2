"""Some important (and often-used) utility functions."""
from model.user import User
from model.team import Team
from model.project import Project
from model.permissions import Permissions


def create_test_admin(slack_id):
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
    u.image_url = 'https:///via.placeholder.com/150'
    u.major = 'Computer Science'
    u.permissions_level = Permissions.admin
    u.position = 'Adrenaline Junkie'
    return u


def create_test_team(tid, team_name, display_name):
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


def create_test_project(github_team_id, github_urls):
    r"""
    Create a test project with project ID, URLs, and all other attributes set.

    ==========      =============================
    Property        Preset
    ==========      =============================
    ID              ``SHA1(github_urls[0], time.time())``
    Team ID         ``github_team_id``
    Github URLs     ``github_urls``
    Display Name    Rocket2
    Short Descrip.  Slack bot, team management, and onboarding system for...
    Long Descrip.   Slack bot, team management, and onboarding system for...
    Tags            python, docker, pipenv, waterboarding
    Website         https://github.com/ubclaunchpad/rocket2
    Appstore URL    ¯\_(ツ)_/¯
    Playstore URL   ¯\_(ツ)_/¯
    ==========      =============================

    :param github_team_id: The Github team ID
    :param github_urls: The URLs to all connected projects
    :return: a filled-in project model (no empty strings)
    """
    p = Project(github_team_id, github_urls)
    p.display_name = 'Rocket2'
    p.short_description = \
        'Slack bot, team management, and onboarding system for UBC Launch Pad'
    p.long_description = '''
        Slack bot, team management, and onboarding system for UBC Launch Pad
    '''
    p.tags = ['python', 'docker', 'pipenv', 'waterboarding']
    p.website_url = 'https://github.com/ubclaunchpad/rocket2'
    p.appstore_url = '¯\\_(ツ)_/¯'
    p.playstore_url = '¯\\_(ツ)_/¯'

    return p
