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

* `create` GITHUB_TEAM_NAME [`--name` DISPLAY_NAME] [`--platform` PLATFORM]
  * create a new team with a Github team name and optional parameters
  * the user will be automatically added to the new team

The following can only be used by a team lead in the team or an admin:

* `edit` GITHUB_TEAM_NAME
  * [`--name` DISPLAY_NAME]
  * [`--platform` PLATFORM]
    * edit properties of specified team

* `add` GITHUB_TEAM_NAME @Slack User
  * add the specified user to the team

* `remove` GITHUB_TEAM_NAME @Slack User
  * remove the specified user from the team

* `delete` GITHUB_TEAM_NAME
  * permanently delete the specified team
