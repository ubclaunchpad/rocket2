# My First Pull Request

Okay. You are a member of the Rocket 2 team. You have successfully set up your
local development environment. You have found an issue that you want to work
on. Now, what to do?

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

- All unit tests pass (`scripts/build_check.sh`)
- The travis build passes (travis will build your commit when you push it)
- Your code is presentable and you have **not** committed extra files (think
  your credentials, IDE config files, cached directories, build directories,
  etc.)
- You've written unit tests for the changes you've made, and that they cover
  all the code you wrote (or effectively all, given the circumstances)

## Making your Pull Request

We have templates on how to write you pull requests, so you should get by by
just following the template. Just make sure that you actually follow the
template.

Sometimes, it might be good to make a Work In Progress (WIP) pull request, to
let everyone know that the issue is being worked on, and the progress that you
are making. In those cases, you can add a WIP label to your PR. If not, you can
add a `Ready for Review` label.

## Receiving criticism

After receiving your healthy dose of PR criticism from reviewers, you might be
asked to make some changes. After making the changes and pushing them to the
branch, please replace the `Ready for Review` label with the `Ready for
Re-review` label.

[#153]: https://github.com/ubclaunchpad/rocket2/issues/153
