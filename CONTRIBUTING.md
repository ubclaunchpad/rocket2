# Contributing

This document contains important details for anyone contributing to Rocket 2.

## Opening an Issue

If you see a bug or have a feature request, please [open an issue][issues]!
That being said, make sure to do a quick search first - there may already be an
issue that covers it.

When creating a new issue, please add a label describing the issue; the most
relevant are probably "Bug" and "Feature request".

**If you are going to work on an issue, please assign yourself to it, and
unassign yourself if you stop working on it.**

If you are not planning to work on a new issue, please also add it to the
Rocket 2.0 project; this will automatically add it to our Kanban board's
backlog, where we can review it in a future sprint.

## Setting up branches

Before you make any changes, you should first set up your own branch. It is
common convention to name your branch:

```
<username>/#<issue-number>-<description-of-fix>
```

So if your issue is [#153 Read from configuration][#153], you would name it
`rwblickhan/#153-read-from-config`. The name needs to be concise, descriptive,
and, well, have your name and number, so to speak.

## Before-Pull-Request checklist

- All tests and style and docs checks pass (`scripts/build_check.sh`)
- The Github build passes (Github will build your commit when you push it)
- Your code is presentable and you have **not** committed extra files (think
  your credentials, IDE config files, cached directories, build directories,
  etc.)
- You've written unit tests for the changes you've made, and that they cover
  all the code you wrote (or effectively all, given the circumstances)

We use `codecov` to check code coverage, but you can easily check the code
coverage using the `scripts/build_check.sh` script. The coverage should be
displayed after the unit tests are run.

## Submitting a Pull Request

We appreciate pull requests of any size or scope.

Please use a clear, descriptive title for your pull request and fill out the
pull request template with as much detail as you can. In particular, all pull
requests should be linked to one or more issues - if a relevant issue does not
exist, please create one as described above.

All pull requests must be code reviewed. Currently the code is owned by the
[brussel-sprouts][bs] team at UBC Launch Pad; at least one member of the team
must approve the pull request before it can be merged.

All pull requests must pass our Github build before they can be merged. The
Github build checks for:

- Passing unit tests (via [pytest](https://pytest.org))
- Minimum code coverage of unit tests (via [Codecov.io](https://codecov.io/))
- Code linting (via [flake8](https://flake8.readthedocs.io/en/latest/))
- PEP8 code style (via [pycodestyle](http://pycodestyle.pycqa.org/en/latest/))
- Correctly-formatted docstrings (via [pydocstyle](http://www.pydocstyle.org/en/2.1.1/))
- Correctly-formatted Markdown documentation (via [mdl](https://github.com/markdownlint/markdownlint))

All of these checks are conveniently done using the `scripts/build_check.sh` as
mentioned above.

Remember to add the label `Ready for Review`.

After your pull request has been approved and the Github build passes, it can
be merged into `master`. Please do so with an ordinary merge commit, not a
rebase or squash merge.

### Work in progress (WIP) pull requests

Sometimes, it may be more appropriate to submit a pull request that you are
working on, just to say that you are working on something (or so that you can
get some initial feedback on your work). In that case, it can be a good idea to
submit a pull request marked WIP. The convention here is to prepend `[WIP]` in
the title of the request, and to further mark it with the label `WIP`.

## Updating an Outdated Pull Request

If changes have been merged between when you started work on your branch and
when your pull request was approved, you will have to update your branch. The
preferred way to do so is with a rebase.

Assuming you are on your working branch:

```bash
git pull origin master
git rebase master
```

If you have changed files that were also changed in the intervening merge, `git
rebase` may report merge conflicts. If this happens, don't panic!  Use `git
status` and `git diff` to determine which files conflict and where, use an
editor to fix the conflicts, then stage the formerly-conflicting files with
`git add FILE`. Finally, use `git rebase --continue` to apply the fix and
continue rebasing. Note that you may have to fix conflicts multiple times in a
single rebase.

It is also a good idea to replace the label `Ready for Review` with `Ready for
Re-Review` for clarity.

[prs]: https://rocket2.rtfd.io/en/latest/docs/MyFirstPullRequest.html
[issues]: https://github.com/ubclaunchpad/rocket2/issues
[#153]: https://github.com/ubclaunchpad/rocket2/issues/153
[bs]: https://github.com/orgs/ubclaunchpad/teams/brussel-sprouts
