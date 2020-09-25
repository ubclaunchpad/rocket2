Team Command Reference
======================

Commands that manipulate team data. Remember that parameters with
whitespace must be enclosed by quotation marks.

Options
-------

.. code:: sh

   /rocket team {list, view, help, create, edit, add, remove, lead, delete}

List
~~~~

.. code:: sh

   /rocket team list

Display a list of Github team names and display names of all teams.

View
~~~~

.. code:: sh

   /rocket team view GITHUB_TEAM_NAME

Display information and members of a specific team.

Help
~~~~

.. code:: sh

   /rocket team help

Display options for team commands.

Create (Team Lead and Admin only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: sh

   /rocket team create GITHUB_TEAM_NAME [--name DISPLAY_NAME]
                                        [--platform PLATFORM]
                                        [--channel CHANNEL]
                                        [--lead SLACK_ID]

Create a new team with a Github team name and optional display name. The
user who runs the command will be automatically added to team as Team
Lead. If the ``--lead`` flag is used, user with ``SLACK_ID`` will be
added as Team Lead instead. If the ``--channel`` flag is used, all
members in specified channel will be added. ‘SLACK_ID’ is the
``@``-name, for easy slack autocomplete.

We use Github API to create the team on Github.

The Github team name cannot contain spaces.

.. code:: sh

   /rocket team create "struddle-bouts" --name "Struddle Bouts" --channel @brussel_sprouts

Edit (Team Lead\* and Admin only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: sh

   /rocket team edit GITHUB_TEAM_NAME [--name DISPLAY_NAME] [--platform PLATFORM]

Edit the properties of a specific team. Team Leads can only edit the
teams that they are a part of, but admins can edit any teams.

Add (Team Lead\* and Admin only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: sh

   /rocket team add GITHUB_TEAM_NAME SLACK_ID

Add a user to the team. Team Leads can only add users into teams that
they are a part of, but admins can add users to any team. ``SLACK_ID``
is the ``@``-name, for easy slack autocomplete.

Users will be added to the teams on Github as well.

.. code:: sh

   /rocket team add struddle-bouts @s_universe

Remove (Team Lead\* and Admin only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: sh

   /rocket team remove GITHUB_TEAM_NAME SLACK_ID

Remove a user from a team, removes them as Team Lead if they were one.
Team Leads can only remove users from teams that they are a part of, but
admins can remove users from any team. ``SLACK_ID`` is the ``@``-name,
for easy slack autocomplete.

Users will be removed from the teams on Github as well.

Lead (Team Lead\* and Admin only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: sh

   /rocket team lead GITHUB_TEAM_NAME SLACK_ID [--remove]

Adds a user as Team Lead, and adds them to team if not already added. If
``--remove`` flag is used, will remove user as Team Lead, but not from
the team. Team Leads can only promote/demote users in teams that they
are part of, but admins can promote/demote users in any team. ‘SLACK_ID’
is the ``@``-name, for easy slack autocomplete.

Delete (Team Lead\* and Admin only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: sh

   /rocket team delete GITHUB_TEAM_NAME

Permanently delete a team. Team Leads can only delete teams that they
are a part of, but admins can delete any team.
