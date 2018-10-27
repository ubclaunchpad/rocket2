"""Some important (and often-used) utility functions."""
from model.user import User
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
    u.set_github_username('kibbles')
    u.set_image_url('https://google.ca')
    u.set_major('Computer Science')
    u.set_permissions_level(Permissions.admin)
    u.set_position('Adrenaline Junkie')
    return u
