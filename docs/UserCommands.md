# User Command Reference

Commands that manipulate user data. Remember that parameters with whitespace
must be enclosed in quotation marks.

## Options

```sh
/rocket user {add, edit, view, help, delete}
```

### Add

```sh
/rocket user add [-f|--force]
```

Add the current user into the database. This command by default does not
overwrite users that have already been entered into the database. By using the
`-f` flag, you force `rocket2` to overwrite the entry in the database, if any.

### Edit

```sh
/rocket user edit [--name NAME] [--email EMAIL] [--pos POSITION]
                  [--github GITHUB_HANDLE] [--major MAJOR]
                  [--bio BIOGRAPHY]
                  [--permission {member,team_lead,admin}]
```

Allows user to edit their Launch Pad profile. Admins and team leads can edit
another user's Launch Pad profile by using `[--member SLACKID]` option.
`SLACK_ID` is the `@`-name, for easy slack autocomplete.

If a user edits their Github handle, rocket will also add the handle to Launch
Pad's Github organization.

```sh
# Normal use
/rocket user edit --name "Steven Universe" --email "su@gmail.com"

# Admin/Team lead use
/rocket user edit --member @s_universe --name "Steven Universe"
```

Admins can easily promote other admins or team leads.

```sh
/rocket user edit --member @s_universe --permission admin
```

### View

```sh
/rocket user view [SLACKID]
```

Display information about a user. `SLACK_ID` is the `@`-name, for easy slack
autocomplete. If `SLACK_ID` is not specified, this command displays information
about the one who ran the command instead.

### Help

```sh
/rocket user help
```

Display options for the user commands.

### Delete (Admin only)

```sh
/rocket user delete MEMBER_ID
```

Permanently delete a member's Launch Pad Profile. Can only be used by admins.
`MEMBER_ID` is the `@`-name, for easy slack autocomplete.
