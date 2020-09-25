Testing
=======

   **Warning**: This is no longer the most up-to-date documentation on
   how testing is done here. You may want to head over
   `here <LocalDevelopmentGuide.html>`__ for more up-to-date
   documentation on how we test things. *You have been warned….*

Running Pytest Efficiently
--------------------------

Test Driven Development… we hear professors preach about it during
lectures but we never got an opportunity to put it to good use until
Rocket2 came along. Unfortunately we got over excited and wrote A LOT of
tests. Running them all every time is a bit painful, that’s where
``@pytest.mark`` comes in. ``pytest.mark`` allows you to label your
tests to run them in groups.

We only have tests that test the functions by themselves. Features that
involve multiple parts (such as a new command involving Slack, Github,
and the database) should be tested manually as well.

Run all the tests
~~~~~~~~~~~~~~~~~

``pytest``

Run only db tests
~~~~~~~~~~~~~~~~~

``pytest -m db``

Run all tests except database tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``pytest -m "not db"``

Testing the Database
--------------------

What are environment variables? Variables for the environment of course!
These variables set up the environment for testing. Rocket2 uses them
because we have both a local and a sever DynamoDB database and each
require an extra variable to get everything working.

Run local DynamoDB
~~~~~~~~~~~~~~~~~~

We use the ``AWS_LOCAL`` environment variable to indicate if we want to
run DynamoDB locally or on a server. Change ``AWS_LOCAL = 'True'`` to
use local DynamoDB.

If ``AWS_LOCAL == 'True'`` but you did not start an instance of local
DynamoDB, ``scripts/build_check.sh`` will automatically skip all
database tests.

This is the recommended way for unit testing.

Run server DynamoDB
~~~~~~~~~~~~~~~~~~~

To run the server DynamoDB we need to set the ``AWS_REGION`` and obtain
``AWS_ACCESS_KEYID``, ``AWS_SECRET_KEY``, and ``GITHUB_KEY``.

This is the recommended way for testing everything (not unit testing,
but testing the slack commands themselves). Click
`here <LocalDevelopmentGuide.html>`__ to learn how to set up a full
development environment (including the testing part).
