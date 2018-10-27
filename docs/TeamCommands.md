# Team Command Reference

`@rocket team`

## Options to specify input

* `list`
    * outputs the Github team names and display names of all teams

* `view` GITHUB_TEAM_NAME
    * view information and members of a team

* `help`
    * outputs options for team commands

## TEAM LEAD or ADMIN only

* `add` GITHUB_TEAM_NAME 'DISPLAY NAME'
    * create a new team with the specified values

* `edit` GITHUB_TEAM_NAME
    * `--name` 'DISPLAY NAME'
    * `--platform` PLATFORM
        * edit properties of specified team

## ADMIN only

* `delete` GITHUB_TEAM_NAME
    * permanently delete the specified team
