"""
Dumps all tables into a single python pickle file.

Run with pipenv run python dump-db.py
"""
from config import Config
from factory import make_dbfacade
from app.model import Team, User
import pickle

filename = 'db.pkl'

db = make_dbfacade(Config())
all_teams = db.query(Team)
all_users = db.query(User)

data = {
    'teams': all_teams,
    'users': all_users
}

with open(filename, 'wb') as f:
    pickle.dump(data, f)

print('Data written to file `%s`; %d teams and %d users' %
      (filename, len(all_teams), len(all_users)))
