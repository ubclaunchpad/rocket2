# Getting Started

## Create an User Model for DynamoDB database

### command

A slack user calls Rocket2 to edit their information.

```sh
# SLACK_ID will be the current user's slack id.
# For this example, let's set the slack id to be `StevenU`
@rocket user edit --name "Steven Universe" --email "su@gmail.com"
```

### model

A User model is constructed from the information the user input.
Unfilled parameters will remain empty.

```python
# To construct a User model.
steven_universe = User(StevenU)
steven_universe.set_email('su@gmail.com')

# To check if this user is valid.
User.is_valid(steven_universe) # returns true

# To get a user's permission level.
steven_universe.get_permissions_level() # returns Permissions_member
```

### database (db)

Instead of using `dynamodb.py` to handle our User model, we'll use `facade.py`.

```python
# To store a user into the database.
facade.store_user(steven_universe)

# To retrieve a user from the database.
facade.retrieve_user(StevenU) # returns steven_universe user model

# If we try to retrieve a non-existant user, a LookupError will be thrown.
facade.retrieve_user(fakeU) # returns 'User fakeU not found'

# To query a user based on a parameter, a list of matching Users will be returned.
facade.query_user(['name', 'Steven'] # returns [steven_universe]

# To query a user based on a non-existant parameter, an empty list will be returned.
facade.query_user(['email', 'fakeemail@gmail.com'] # returns []

# To query a user without parameters, all the users will be returned
second_user = User(secondU)
facade.query_user(['name', '']) # returns [steven_universe, second_user]
```
