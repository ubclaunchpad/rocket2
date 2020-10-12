Contributing
============

This document contains important details for anyone contributing to
Rocket 2.

Opening an Issue
----------------

If you see a bug or have a feature request, please `open an
issue <https://github.com/ubclaunchpad/rocket2/issues>`__! That being
said, make sure to do a quick search first - there may already be an
issue that covers it.

When creating a new issue, please use the existing templates, and make sure
the appropriate labels are attached to the issue. **If you are going to work
on an issue, please assign yourself to it, and unassign yourself if you stop
working on it.**

Task Triage and Planning
------------------------

All newly created issues are automatically added to the
`Rocket 2 project board <https://github.com/ubclaunchpad/rocket2/projects/1>`_.
The life of an issue goes roughly as follows:

Issues start in *Needs triage*. From here, they are moved to either:

- *Icebox*: deprioritized tasks are tracked here
- *Backlog*: this means that we want to get around to this task at some point

From the *Backlog*, we start moving tasks into *Planned*, which is typically
around when discussions around design and potential implementation happens.
When work begins in earnest, the issue should be moved to *In progress*,
where it will stay until a pull request lands closing the issue, at which
point it will automatically be moved to *Done*.

Development Documentation
-------------------------

Please refer to the `local development guide <https://rocket2.readthedocs.io/en/latest/docs/LocalDevelopmentGuide.html>`_
to get started! 

Before-Pull-Request checklist
-----------------------------

-  All tests and style and docs checks pass (``scripts/build_check.sh``)
-  The GitHub build passes (GitHub will build your commit when you push
   it)
-  Your code is presentable and you have **not** committed extra files
   (think your credentials, IDE config files, cached directories, build
   directories, etc.)
-  You’ve written unit tests for the changes you’ve made, and that they
   cover all the code you wrote (or effectively all, given the
   circumstances)

We use `codecov <https://codecov.io/gh/ubclaunchpad/rocket2>`_ to check
code coverage, but you can easily check the code coverage using the
``scripts/build_check.sh`` script. The coverage should be displayed after
the unit tests are run.

Submitting a Pull Request
-------------------------

We appreciate pull requests of any size or scope.

Please use a clear, descriptive title for your pull request and fill out
the pull request template with as much detail as you can. In particular,
all pull requests should be linked to one or more issues - if a relevant
issue does not exist, please create one as described above.

Note that you may open a pull request at any point during your progress -
if a pull request is being opened as a request for feedback and help rather
than a request for review and merge, then please open the pull request as
a `draft pull request <https://docs.github.com/en/free-pro-team@latest/github/collaborating-with-issues-and-pull-requests/about-pull-requests#draft-pull-requests>`.

All pull requests must be code reviewed before being merged. Currently the
code is primarily owned by the
`rocket2 <https://github.com/orgs/ubclaunchpad/teams/rocket2>`__
team at UBC Launch Pad.

All pull requests must pass our GitHub build before they can be merged.
The GitHub build checks for:

-  Passing unit tests (via `pytest <https://pytest.org>`__)
-  Minimum code coverage of unit tests (via
   `Codecov.io <https://codecov.io/>`__)
-  Code linting (via
   `flake8 <https://flake8.readthedocs.io/en/latest/>`__)
-  PEP8 code style (via
   `pycodestyle <http://pycodestyle.pycqa.org/en/latest/>`__)
-  Correctly-formatted docstrings (via
   `pydocstyle <http://www.pydocstyle.org/en/2.1.1/>`__)

All of these checks are conveniently done using the
``scripts/build_check.sh`` as mentioned above.

Remember to add the label ``Ready for Review``.

After your pull request has been approved and the GitHub build passes,
it can be merged into ``master``. Please do so with an ordinary merge
commit, not a rebase or squash merge.

Updating an Outdated Pull Request
---------------------------------

If changes have been merged between when you started work on your branch
and when your pull request was approved, you will have to update your
branch. The preferred way to do so is with a rebase.

Assuming you are on your working branch:

.. code:: bash

   git pull origin master
   git rebase master

If you have changed files that were also changed in the intervening
merge, ``git rebase`` may report merge conflicts. If this happens, don’t
panic! Use ``git status`` and ``git diff`` to determine which files
conflict and where, use an editor to fix the conflicts, then stage the
formerly-conflicting files with ``git add FILE``. Finally, use
``git rebase --continue`` to apply the fix and continue rebasing. Note
that you may have to fix conflicts multiple times in a single rebase.

It is also a good idea to replace the label ``Ready for Review`` with
``Ready for Re-Review`` for clarity.
