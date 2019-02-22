# Getting Started

## Create an User Model for DynamoDB database

A quick guide run through how Rocket2 takes in a command to generate a model
that will be stored onto the database.

So you just joined Launchpad and want to add yourself to Rocket2. You go on
slack and starts to talk to the Rocket2 bot, but what should you say?
To get started, here's a command you can enter:

### command

A slack user calls Rocket2 to edit their information.

```sh
# SLACK_ID will be the current user's slack id.
# For this example, let's assume the slack id to be `StevenU`
/rocket user edit --name "Steven Universe" --email "su@gmail.com"
```

Yay! You have done what you were told to do, but wait! As a curious software
developer, you're curious about what makes Rocket2 tick. How exactly is your
information saved onto Rocket2? Well, for every member added to Rocket2, a user
model gets created.

### model

An User model is constructed from the information the user input. Unfilled
parameters will remain empty.

```python
# To construct a User model with Slack ID 'StevenU'
steven_universe = User('StevenU')
steven_universe.set_email('su@gmail.com')

# To check if this user is valid.
User.is_valid(steven_universe) # returns true

# To get a user's permission level.
steven_universe.permissions_level # returns Permissions_member
```

Launchpad is growing every year, so there are a lot of user, hence a lot of user
models. We have to be able to keep track and organize everyone, so that's where
database comes in. We create a table for every type of model, so in this case
we'll create a user table to store all users.

### database (db)

Instead of using `dynamodb.py` to handle our User model, we will use `facade.py`
so we avoid becoming dependent on a single database. In the future, this allows
us to easily switch to using other databases.

```python
# To store an user into the database.
facade.store(steven_universe)

# To retrieve an user from the database.
facade.retrieve(User, 'StevenU') # returns steven_universe user model

# If we try to retrieve a non-existent: user, a LookupError will be thrown.
facade.retrieve(User, 'fakeU') # returns 'User fakeU not found'

# To query an user based on a parameter, a list of matching Users will be
returned.
facade.query(User, ['name', 'Steven Universe'] # returns [steven_universe]

# To query an user based on a non-existent parameter, an empty list will be
returned.
facade.query(User, ['email', 'fakeemail@gmail.com'] # returns []

# To query an user without parameters, all the users will be returned
facade.query(User, []) # returns [steven_universe, second_user]
```
