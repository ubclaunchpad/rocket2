Development Tutorials
=====================

Create an User Model for DynamoDB database
------------------------------------------

A quick guide run through how Rocket2 takes in a command to generate a
model that will be stored onto the database.

So you just joined Launchpad and want to add yourself to Rocket2. You go
on slack and starts to talk to the Rocket2 bot, but what should you say?
To get started, here's a command you can enter:

command
~~~~~~~

A slack user calls Rocket2 to edit their information.

.. code:: sh

   # SLACK_ID will be the current user's slack id.
   # For this example, let's assume the slack id to be `StevenU`
   /rocket user edit --name "Steven Universe" --email "su@gmail.com"

Yay! You have done what you were told to do, but wait! As a curious
software developer, you're curious about what makes Rocket2 tick. How
exactly is your information saved onto Rocket2? Well, for every member
added to Rocket2, a user model gets created.

model
~~~~~

An User model is constructed from the information the user input.
Unfilled parameters will remain empty.

.. code:: python

   # To construct a User model with Slack ID 'StevenU'
   steven_universe = User('StevenU')
   steven_universe.email = 'su@gmail.com'

   # To check if this user is valid.
   User.is_valid(steven_universe) # returns true

   # To get a user's permission level.
   steven_universe.permissions_level # returns Permissions.member

Launchpad is growing every year, so there are a lot of user, hence a lot
of user models. We have to be able to keep track and organize everyone,
so that's where database comes in. We create a table for every type of
model, so in this case we'll create a user table to store all users.

database (db)
~~~~~~~~~~~~~

Instead of using ``dynamodb.py`` to handle our User model, we will use
``facade.py`` so we avoid becoming dependent on a single database. In
the future, this allows us to easily switch to using other databases.

.. code:: python

   # To store an user into the database.
   facade.store(steven_universe)

   # To retrieve an user from the database.
   facade.retrieve(User, 'StevenU') # returns steven_universe user model

   # If we try to retrieve a non-existent: user, a LookupError will be thrown.
   facade.retrieve(User, 'fakeU') # returns 'User fakeU not found'

   # To query an user based on a parameter, a list of matching Users will be
   # returned.
   facade.query(User, [('name', 'Steven Universe')]) # returns [steven_universe]

   # To query an user based on a non-existent parameter, an empty list will be
   # returned.
   facade.query(User, [('email', 'fakeemail@gmail.com')]) # returns []

   # To query an user without parameters, all the users will be returned
   facade.query(User, []) # returns [steven_universe, second_user]

Create a Scheduler Module
-------------------------

So, you want to write a module and add it to the ever-growing list of
modules that run periodically for rocket 2? Well, you have come to the
right place.

A very good example module can be found in the
``app/scheduler/modules/random_channel.py`` source file. I recommend
that you read it before starting development (don't worry, it's very
short).

Structure
~~~~~~~~~

All scheduler modules are to be placed in the ``app/scheduler/modules/``
directory. As Python source files, of course. These files should house
the module class. Every class must inherit ``ModuleBase``.

Since you inherit the ``ModuleBase`` class, you must implement the
following methods:

**get_job_args**: A dictionary of job configuration arguments to be
passed into the scheduler.

**do_it**: A function that actually does the thing you want to do every
time the conditions you specified in the job configuration mentioned
above.

Job arguments
~~~~~~~~~~~~~

As you can see from the example, the following job arguments are
returned:

.. code:: js

   {'trigger':      'cron',
    'day_of_week':  'sat',
    'hour':         12,
    'name':         self.NAME}

Our trigger type is ``cron``, meaning that it is supposed to fire once
every time the rest of the arguments fit. ``day_of_week`` means which
day it is supposed to fire. ``hour`` means which hour on that day it is
supposed to fire. And every job has to have a name, which is specified
in the ``name`` argument. For a more detailed look at the different
types of arguments and different trigger types that aren't discussed
here, have a look at the `APScheduler
documentation <https://apscheduler.readthedocs.io/en/latest/modules/triggers/interval.html?highlight=intervaltrigger#apscheduler.triggers.interval.IntervalTrigger>`__.

Firing the module
~~~~~~~~~~~~~~~~~

The function ``do_it`` is called whenever it is time to execute the job.
You can use it to periodically message people, periodically check
statistics, poll Github, you name it.

Adding your module to the scheduler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To actually have the scheduler execute and remember your module (and
job), you must add the job to the scheduler. This can be achieved by
adding your module into the scheduler via the function ``__add_job``
within the function ``__init_periodic_tasks``. You can see that we
already have initialized our beloved ``RandomChannelPromoter`` in that
function, so just follow along with your own module.

And look! That wasn't all that bad now wasn't it??
