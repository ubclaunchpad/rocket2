# Team Command Reference

`@rocket team`

## Options to specify input

* `view` GITHUB_TEAM_NAME
    * view information and members of a team

* `help`
    * outputs options for team commands

## TEAM LEAD or ADMIN only

* `add` GITHUB_TEAM_NAME 'DISPLAY NAME'
    * create a new team with the specified values
    * display name must be a quoted string if it includes whitespace

## ADMIN only

* `delete` GITHUB_TEAM_NAME
    * permanently delete the specified team
