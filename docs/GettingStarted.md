# Getting Started

## Create an User Model for DynamoDB database

### command

A slack user calls Rocket2 to edit their information.

```sh
# SLACK_ID will be the current user's slack id.
# For this example, let's assume the slack id to be `StevenU`
@rocket user edit --name "Steven Universe" --email "su@gmail.com"
```

### model

An User model is constructed from the information the user input.
Unfilled parameters will remain empty.

```python
# To construct a User model.
steven_universe = User('StevenU')
steven_universe.set_email('su@gmail.com')

# To check if this user is valid.
User.is_valid(steven_universe) # returns true

# To get a user's permission level.
steven_universe.get_permissions_level() # returns Permissions_member
```

### database (db)

Instead of using `dynamodb.py` to handle our User model, we will use `facade.py`
so we avoid becoming dependent on a single database. In the future, this allows
us to easily switch to using other databases.

```python
# To store an user into the database.
facade.store_user(steven_universe)

# To retrieve an user from the database.
facade.retrieve_user('StevenU') # returns steven_universe user model

# If we try to retrieve a non-existent: user, a LookupError will be thrown.
facade.retrieve_user('fakeU') # returns 'User fakeU not found'

# To query an user based on a parameter, a list of matching Users will be
returned.
facade.query_user(['name', 'Steven Universe'] # returns [steven_universe]

# To query an user based on a non-existent parameter, an empty list will be
returned.
facade.query_user(['email', 'fakeemail@gmail.com'] # returns []

# To query an user without parameters, all the users will be returned
second_user = User('secondU')
facade.query_user(['']) # returns [steven_universe, second_user]
```
