# Team Command Reference

`@rocket team`

All parameters with whitespace must be enclosed by quotation marks.

## Options to specify input

* `list`
    * outputs the Github team names and display names of all teams

* `view` GITHUB_TEAM_NAME
    * view information and members of a team

* `help`
    * outputs options for team commands

## TEAM LEAD or ADMIN only

* `create` GITHUB_TEAM_NAME DISPLAY_NAME
    * create a new team with the specified values

* `edit` GITHUB_TEAM_NAME
    * `--name` DISPLAY_NAME
    * `--platform` PLATFORM
        * edit properties of specified team

* `add` GITHUB_TEAM_NAME SLACK_ID
    * add the specified user to the team

* `remove` GITHUB_TEAM_NAME SLACK_ID
    * remove the specified user from the team

## ADMIN only

* `delete` GITHUB_TEAM_NAME
    * permanently delete the specified team