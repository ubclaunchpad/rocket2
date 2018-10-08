# User Command Reference

`@rocket user`

## Options to specify input

* `edit`
  * `--name` yourname
  * `--email` emailaddress
  * `--pos` yourposition
  * `--github` yourrepo
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

* `admin`
  * `--add` MEMBER_ID
    * make existing user admin
  * `--remove` MEMBER_ID
    * remove admin rights from user

* `lead`
  * `--add` MEMBER_ID
    * make existing user team lead
  * `--remove` MEMBER_ID
    * remove existing user as team lead

* `add`
  * `--team` TEAM_ID `--member` MEMBER_ID
    * add user to team

* `remove`
  * `--team` TEAM_ID `--member` MEMBER_ID
    * remove user from team