.. image:: docs/rocket-logo.png
    :width: 25%
    :align: center

.. raw:: html

    <h1 align="center">Rocket 2</h1>

.. rst-class:: center

Rocket 2 is the official `UBC Launch Pad`_ Slack bot and team management platform.

.. raw:: html

   <p align="center">
      <a href="https://github.com/ubclaunchpad/rocket2/actions?query=workflow%3APipeline">
         <img src="https://github.com/ubclaunchpad/rocket2/workflows/Pipeline/badge.svg">
      </a>
      <a href="https://codecov.io/gh/ubclaunchpad/rocket2">
         <img src="https://codecov.io/gh/ubclaunchpad/rocket2/branch/master/graph/badge.svg">
      </a>
      <a href="https://github.com/ubclaunchpad/inertia">
         <img src="https://img.shields.io/badge/deploying%20with-inertia-blue.svg">
      </a>
      <a href="https://rocket2.readthedocs.io">
         <img src="https://readthedocs.org/projects/rocket2/badge/?version=latest">
      </a>
   </p>

|

Rocket 2 is a from-the-ground-up rewrite of the `original Rocket`_,
and it is a Slack bot that aims to be a ChatOps-style tool for team management
across platforms like GitHub and Google Drive, with extensive configuration
options so that it can be used by other organizations as well. Rocket 2 is used,
built, and maintained with ❤️ by `UBC Launch Pad`_, UBC's student-run software
engineering club.

.. _UBC Launch Pad: https://ubclaunchpad.com
.. _original Rocket: https://github.com/ubclaunchpad/rocket

.. list-table::
   :widths: 3 50
   :header-rows: 1

   * -
     - Main features
   * - 💬
     - **Unix-style command system in Slack** - invoke commands with a simple ``/rocket`` in Slack
   * - 🔗
     - **Platform integrations** - easily configure GitHub organization invites and teams, Google Drive permissions, and more
   * - 🗂
     - **Team directory** - provide and manage member information such as emails and other accounts
   * - 🔒
     - **Permissions system** - control access to Rocket functionality with a tiered set of permissions
   * - 🔨
     - **Hackable and extensible** - an open codebase makes it easy to add commands, scheduled modules, and more!

|

.. rst-class:: invisible

🚀 Rocket 2
-----------

.. Nothing in here is seen because it is invisible. But it is necessary because we want the breadcrumb above
.. to read "Rocket 2".

📦 Usage
--------

Check out our `command reference pages`_ to get started interacting with
Rocket, or take a look at how Rocket is used at UBC Launch Pad in
the `Launch Pad handbook`_.

To set up a Rocket instance for your organization, refer to the `deployment`_
and `configuration`_ documentation.

.. _deployment: docs/Deployment.html
.. _configuration: docs/Config.html
.. _command reference pages: docs/UserCommands.html
.. _Launch Pad handbook: https://docs.ubclaunchpad.com/handbook/tools/slack#rocket

|

📚 Contributing
---------------

Any contribution (pull requests, feedback, bug reports, ideas, etc.) is welcome!

Please refer to our `contribution guide`_ for contribution guidelines as well as
detailed guides to help you get started with Rocket 2's codebase.

.. _contribution guide: CONTRIBUTING.html

|
