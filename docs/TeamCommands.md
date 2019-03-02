# Team Command Reference

Commands that manipulate team data. Remember that parameters with whitespace
must be enclosed by quotation marks.

## Options

```sh
/rocket team {list, view, help, create, edit, add, remove, lead, delete}
```

### List

```sh
/rocket team list
```

Display a list of Github team names and display names of all teams.

### View

```sh
/rocket team view GITHUB_TEAM_NAME
```

Display information and members of a specific team.

### Help

```sh
/rocket team help
```

Display options for team commands.

### Create (Team Lead and Admin only)

```sh
/rocket team create GITHUB_TEAM_NAME [--name DISPLAY_NAME]
                                     [--platform PLATFORM]
                                     [--channel CHANNEL]
                                     [--lead SLACK_ID]
```

Create a new team with a Github team name and optional display name. The user
who runs the command will be automatically added to team and as Team Lead. If the
`--lead` flag is used, user with `SLACK_ID` will be added as Team Lead
instead. If the `--channel` flag is used, all members in specified
channel will be added. 'SLACK_ID' is the `@`-name, for easy slack autocomplete.

The Github team name cannot contain spaces.

```sh
/rocket team create "struddle-bouts" --name "Struddle Bouts" --channel
```

### Edit (Team Lead\* and Admin only)

```sh
/rocket team edit GITHUB_TEAM_NAME [--name DISPLAY_NAME] [--platform PLATFORM]
```

Edit the properties of a specific team. Team Leads can only edit the teams that
they are a part of, but admins can edit any teams.

### Add (Team Lead\* and Admin only)

```sh
/rocket team add GITHUB_TEAM_NAME SLACK_ID
```

Add a user to the team. Team Leads can only add users into teams that they are a
part of, but admins can add users to any team. `SLACK_ID` is the `@`-name, for
easy slack autocomplete.

```sh
/rocket team add struddle-bouts @s_universe
```

### Remove (Team Lead\* and Admin only)

```sh
/rocket team remove GITHUB_TEAM_NAME SLACK_ID
```

Remove a user from a team. Team Leads can only remove users from teams that they
are a part of, but admins can remove users from any team. `SLACK_ID` is the
`@`-name, for easy slack autocomplete.

### Lead (Team Lead\* and Admin only)

```sh
/rocket team lead SLACK_ID
```

Adds a user as Team Lead, and adds them to team if not already added. Team Leads can
only promote users in teams that they are part of, but admins can promote users
in any team. 'SLACK_ID' is the `@`-name, for easy slack autocomplete.

### Delete (Team Lead\* and Admin only)

```sh
/rocket team delete GITHUB_TEAM_NAME
```

Permanently delete a team. Team Leads can only delete teams that they are a part
of, but admins can delete any team.
