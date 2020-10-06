User Command Reference
======================

Commands that manipulate user data. Remember that parameters with
whitespace must be enclosed in quotation marks.

Options
-------

.. code:: sh

   /rocket user {add, edit, view, help, delete}

Add
~~~

.. code:: sh

   /rocket user add [-f|--force]

Add the current user into the database. This command by default does not
overwrite users that have already been entered into the database. By
using the ``-f`` flag, you force Rocket to overwrite the entry in
the database, if any.

Edit
~~~~

.. code:: sh

   /rocket user edit [--name NAME] [--email EMAIL] [--pos POSITION]
                     [--github GITHUB_HANDLE] [--major MAJOR]
                     [--bio BIOGRAPHY]
                     [--permission {member,team_lead,admin}]

Allows user to edit their Launch Pad profile. Admins and team leads can
edit another user’s Launch Pad profile by using ``[--username SLACK_ID]``
option. ``SLACK_ID`` is the ``@``-name, for easy slack autocomplete.

If a user edits their Github handle, Rocket will also add the handle to
Launch Pad’s Github organization.

.. code:: sh

   # Normal use
   /rocket user edit --name "Steven Universe" --email "su@gmail.com"

   # Admin/Team lead use
   /rocket user edit --username @s_universe --name "Steven Universe"

Admins can easily promote other admins or team leads.

.. code:: sh

   /rocket user edit --username @s_universe --permission admin
   /rocket user edit --username @s_universe --permission team_lead
   # Demotion
   /rocket user edit --username @s_universe --permission member

View
~~~~

.. code:: sh

   /rocket user view [--username SLACKID] [--github GITHUB]
                     [--email EMAIL] [--inspect]

Display information about a user. ``SLACKID`` is the ``@``-name, for
easy slack autocomplete. If ``SLACKID`` is not specified, this command
displays information about the one who ran the command instead. You can also
specify a user's Github username or a user's email.

If the `--inspect` flag is used, this command lists the teams that the user
is a part of, along with the teams that this user is leading, if any.

.. code:: sh

    # Lookup via Github username, listing teams user is a part of
    /rocket user view --github octoverse --inspect

Help
~~~~

.. code:: sh

   /rocket user help

Display options for the user commands.

Delete (Admin only)
~~~~~~~~~~~~~~~~~~~

.. code:: sh

   /rocket user delete SLACK_ID

Permanently delete a member’s Launch Pad profile. Can only be used by
admins. ``SLACK_ID`` is the ``@``-name, for easy slack autocomplete.
