## User Command Reference


`@rocket -user`

Options to specify input: <br/>

`-edit`
    `-name` somename `-email` email `-pos` yourposition `-github` githublink `-major` yourmajor `-bio` yourbio  <br/>
    edit properties of your Launch Pad profile <br/>
    ADMIN only options: `-member` MEMBER_ID <br/>
        edit properties of another user's profile <br/>


`-view` MEMBER_ID <br/>
    view information about a user


`-add` <br/>
    `-team` TEAM_ID `-member` MEMBER_ID <br/>
    add user to team <br/>


`-rmv` <br/>
    `-team` TEAM_ID `-member` MEMBER_ID <br/>
    remove user from team <br/>


`-help` <br/>
    outputs options for user commands


ADMIN only:  <br/>

`-delete` MEMBER_ID <br/>
    permanently delete member's Launch Pad profile <br/>


`-add_admin` MEMBER_ID <br/>
    make existing user admin <br/>


`-rmv_admin` MEMBER_ID <br/>
    remove admin rights from user <br/>
