# User Command Reference

Commands that manipulate user data.

## Options

```sh
@rocket user {edit, view, help, delete} ...
```

### Edit

```sh
@rocket user edit [--name NAME] [--email EMAIL] [--pos POSITION]
                  [--github GITHUB_HANDLE] [--major MAJOR]
                  [--bio BIOGRAPHY]
```

Allows user to edit their Launch Pad profile. Admins and team leads can edit
another user's Launch Pad profile by using `[--member SLACKID]` option.

```sh
# Normal use
@rocket user edit --name "Steven Universe" --email "su@gmail.com"

# Admin/Team lead use
@rocket user edit --member "U061F7AUR" --name "LOL"
```

### View

```sh
@rocket user view SLACKID
```

Display information about a user.

### Help

```sh
@rocket user help
```

Display options for the user commands.

### Delete (Admin only)

```sh
@rocket user delete MEMBER_ID
```

Permanently delete a member's Launch Pad Profile. Can only be used by admins.
