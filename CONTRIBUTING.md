# Contributing

This document contains important details for anyone contributing to Rocket 2.0.

## Opening an Issue

If you see a bug or have a feature request, please [open an issue](https://github.com/ubclaunchpad/rocket2.0/issues)!
That being said, do make sure to do a quick search first - there may
already be an issue that covers it.

When creating a new issue, please add a label describing the issue;
the most relevant are probably "Bug" and "Feature request".

If you are going to work on an issue, please assign yourself to it,
and unassign yourself if you stop working on it.

If you are not planning to work on a new issue, please also add it
to the Rocket 2.0 project; this will automatically add it to our
Kanban board's backlog, where we can review it in a future sprint.

## Submitting a Pull Request

We appreciate pull requests of any size or scope.

Please use a clear, descriptive title for your pull request and fill
out the pull request template with as much detail as you can. In
particular, all pull requests should be linked to one or more
issues - if a relevant issue does not exist, please create one as
described above.

All pull requests must be code reviewed. Currently the code is owned by the
[brussel-sprouts](https://github.com/orgs/ubclaunchpad/teams/brussel-sprouts)
team at UBC Launch Pad; at least one member of the team must approve the pull
request before it can be merged.

All pull requests must pass our Travis build before they can be merged.
The Travis build checks for:

* Passing unit tests (via [`pytest`](https://pytest.org))
* Minimum code coverage of unit tests (via [Codecov.io](https://codecov.io/))
* PEP8 code style (via [`pycodestyle`](http://pycodestyle.pycqa.org/en/latest/))
* Correctly-formatted docstrings (via [`pydocstyle`](http://www.pydocstyle.org/en/2.1.1/))
* Correctly-formatted Markdown documentation (via [`mdl`](https://github.com/markdownlint/markdownlint))

After your pull request has been approved and the Travis build passes,
it can be merged into `master`. Please do so with an ordinary merge commit,
not a rebase or squash merge.

## Updating an Outdated Pull Request

If changes have been merged between when you started work on your branch and when
your pull request was approved, you will have to update your branch.
The preferred way to do so is with a rebase.

Assuming you are on your working branch:

```bash
git pull origin master
git rebase master
```

If you have changed files that were also changed in the intervening merge,
`git rebase` may report merge conflicts. If this happens, don't panic!
Use `git status` and `git diff` to determine which files conflict and where,
use an editor to fix the conflicts, then stage the formerly-conflicting files
with `git add FILE`. Finally, use `git rebase --continue` to apply the fix and
continue rebasing. Note that you may have to fix conflicts multiple times
in a single rebase.
