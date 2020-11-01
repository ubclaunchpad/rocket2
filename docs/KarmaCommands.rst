Karma Command Reference
=======================

Command to giveth or taketh away a user's karma

Options
-------

For normal users
~~~~~~~~~~~~~~~~

Add 1 karma to user
^^^^^^^^^^^^^^^^^^^

.. code:: sh

   /rocket @user ++

View a user's karma
^^^^^^^^^^^^^^^^^^^

.. code:: sh

   /rocket karma view @user

For admin only
~~~~~~~~~~~~~~

Set user karma
^^^^^^^^^^^^^^

.. code:: sh

   /rocket karma set @user {amount}

Reset all user karma
^^^^^^^^^^^^^^^^^^^^

.. code:: sh

   /rocket karma reset --all

Examples
~~~~~~~~

.. code:: sh

   # normal user
   /rocket @coolkid1 ++ #adds 1 karma to coolkid1
   /rocket karma view @coolkid1 #view how much karma coolkid1 has

   # admin only
   /rocket karma set @coolkid1 5 #sets coolkid's karma to 5
   /rocket karma reset --all #resets all users karma to 1

Help
^^^^

Display options for karma commands
''''''''''''''''''''''''''''''''''

.. code:: sh

   /rocket karma help
