# User Command Reference

`@rocket user`

## Options to specify input

* `edit`
  * `--name` yourname
  * `--email` emailaddress
  * `--pos` yourposition
  * `--github` repolink
  * `--major` yourmajor
  * `--bio` yourbio
    * edit properties of your Launch Pad profile
  * ADMIN only option: `--member` MEMBER_ID
    * edit properties of another user's Launch Pad profile

* `view` MEMBER_ID
  * view information about a user

* `help`
  * outputs options for user commands

## ADMIN only

* `delete` MEMBER_ID
  * permanently delete member's Launch Pad profile

* `add_admin` MEMBER_ID
  * make existing user admin

* `remove_admin` MEMBER_ID
  * remove admin rights from user

* `add`
  * `--team` TEAM_ID `--member` MEMBER_ID
    * add user to team

* `remove`
  * `--team` TEAM_ID `--member` MEMBER_ID
    * remove user from team

* `add_lead`
  * `--team` TEAM_ID `--member` MEMBER_ID
    * set user as team lead for specified team

* `remove_lead`
  * `--team` TEAM_ID `--member` MEMBER_ID
    * remove user as team lead for specified team