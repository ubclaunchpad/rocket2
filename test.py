"""
XXX: Delete later - for testing purposes.

This file is for testing purposes, to test out some DBFacade things.
"""

from db.facade import DBFacade
from model.user import User
from model.permissions import Permissions

u = User('123456789')
dbf = DBFacade()
dbf.create_tables()

u.set_email('testing')
u.set_github_username('testing')
u.set_major('testing')
u.set_position('testing')
u.set_biography('testing')
u.set_image_url('testing')
u.set_permissions_level(Permissions.member)

dbf.store_user(u)
