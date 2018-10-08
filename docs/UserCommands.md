#User Command Reference

`@rocket -user`

Options to specify input:

`-edit`
    `-name` STRING `-email` STRING `-pos` STRING `-github` STRING `-major` STRING `-bio` STRING
    edit properties of your Launch Pad profile
    ADMIN only options: `-member` MEMBER_ID
        edit properties of another user's profile

`-view` MEMBER_ID
    view information about a user

`-add`
    `-team` TEAM_ID `-member` MEMBER_ID
    add user to team

`-rmv`
    `-team` TEAM_ID `-member` MEMBER_ID
    remove user from team

`-help`
    outputs options for user commands

ADMIN only:

`-delete` MEMBER_ID
    permanently delete member's Launch Pad profile

`-add_admin` MEMBER_ID
    make existing user admin

`-rmv_admin` MEMBER_ID
    remove admin rights from user
