Database Reference
==================

``users`` Table
---------------

The ``users`` table stores all the users. With DynamoDB, we only need to
specify a fixed attribute to be the primary index. In this case, the
user's ``slack_id`` is the primary index. All other attributes are
specified in the ``model/user.py`` file, and are also listed here:

==================== ===============================================
Attribute Name       Description
==================== ===============================================
``slack_id``         ``String``; The user's slack id
``email``            ``String``; The user's email address
``github``           ``String``; The user's Github handler
``github_user_id``   ``String``; The user's Github user ID
``major``            ``String``; The subject major the user is in
``position``         ``String``; The user's position in *Launch Pad*
``bio``              ``String``; A short (auto)biography
``image_url``        ``String``; The user's avatar image URL
``permission_level`` ``String``; The user's permission level
``karma``            ``Integer``; The user's karma points
==================== ===============================================

The user's permission level is one of [``member``, ``admin``,
``team_lead``].

``teams`` Table
---------------

The ``teams`` table stores all teams where ``github_team_id`` is the
primary index. All other attributes are specified in the
``model/team.py`` file, and are also listed here:

+----------------------+----------------------------------------------+
| Attribute Name       | Description                                  |
+======================+==============================================+
| ``github_team_id``   | ``String``; The team's Github ID             |
+----------------------+----------------------------------------------+
| ``github_team_name`` | ``String``; The team's Github name           |
+----------------------+----------------------------------------------+
| ``display_name``     | ``String``; The teams's display              |
+----------------------+----------------------------------------------+
| ``platform``         | ``String``; The team's working platform      |
+----------------------+----------------------------------------------+
| ``team_leads``       | ``String Set``; The team's set of team       |
|                      | leads' Github IDs                            |
+----------------------+----------------------------------------------+
| ``members``          | ``String Set``; The team's set of members'   |
|                      | Github IDs                                   |
+----------------------+----------------------------------------------+
