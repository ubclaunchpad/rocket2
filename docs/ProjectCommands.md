# Project Command Reference

Commands to do with projects. Remember that parameters with whitespace
must be enclosed by quotation marks.

## Options

```sh
/rocket project {list, view, help, create, unassign, edit, assign, delete}
```

### List

```sh
/rocket project list
```

Display a list of all projects.

### View

```sh
/rocket project view PROJECT_ID
```

Displays details of project.

### Help

```sh
/rocket project help
```

Displays options for `project` command.

### Create (Team Lead and Admin only)

```sh
/rocket project create GH_REPO GITHUB_TEAM_NAME [--name DISPLAY_NAME]
```

Creates a new project from the given repo.
Fails if the caller is not the team lead of the specified team.

### Unassign

```sh
/rocket project unassign PROJECT_ID
```

Unassigns the given project.

### Edit

```sh
/rocket project edit PROJECT_ID [--name DISPLAY_NAME]
```

Edit the given project.

### Assign

```sh
/rocket project assign PROJECT_ID GITHUB_TEAM_NAME [-f]
```

Assigns the project to the team. Fails if another team is assigned the project.
If `-f` flag is given, can reassign even if
another team is already assigned the project.

### Delete

```sh
/rocket project delete PROJECT_ID [-f]
```

Delete the project from database. An error occurs if the project is currently assigned.
If `-f` flag is given, can be deleted
even if a team is assigned.
