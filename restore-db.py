"""
Restores all tables from a pickle file to database.

This is done by inserting them into the database via the db.store function.
With Amazon DynamoDB, nothing happens when the row inserted is a duplicate
(i.e. has the same primary key).

Run with pipenv run python restore-db.py
"""
from config import Config
from factory import make_dbfacade
import pickle

filename = 'db.pkl'

db = make_dbfacade(Config())

with open(filename, 'rb') as f:
    data = pickle.load(f)

    if 'teams' in data and 'users' in data:
        restored = 0

        for team in data['teams']:
            restored += 1 if db.store(team) else 0
        for user in data['users']:
            restored += 1 if db.store(user) else 0

        print('Restored %d/%d items.' %
              (restored, len(data['teams']) + len(data['users'])))
    else:
        print('Could not read data; try exporting it again. Missing keys.')
