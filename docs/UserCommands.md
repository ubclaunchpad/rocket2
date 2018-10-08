## User Command Reference


`@rocket -user`

## Options to specify input:

* `-edit`
    * `-name` somename `-email` email `-pos` yourposition `-github` githublink `-major` yourmajor `-bio` yourbio <br/>
        edit properties of your Launch Pad profile
    * ADMIN only options: `-member` MEMBER_ID <br/>
        edit properties of another user's profile


* `-view` MEMBER_ID <br/>
    view information about a user


* `-add`
     * `-team` TEAM_ID `-member` MEMBER_ID <br/>
        add user to team


* `-rmv`
    * `-team` TEAM_ID `-member` MEMBER_ID <br/>
        remove user from team


* `-help` <br/>
    outputs options for user commands


## ADMIN only:

* `-delete` MEMBER_ID <br/>
    permanently delete member's Launch Pad profile


* `-add_admin` MEMBER_ID <br/>
    make existing user admin


* `-rmv_admin` MEMBER_ID <br/>
    remove admin rights from user
