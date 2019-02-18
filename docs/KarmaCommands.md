# Karma Command Reference 

Command to giveth or taketh away a user's karma

## Options
#### For normal users:
##### Add 1 karma to user
```
/rocket @user ++
```
##### Remove 1 karma from user
```
/rocket @user --
```
###### Examples:
```sh
/rocket @coolkid1 ++ #adds 1 karma to coolkid1
/rocket @coolkid1 -- #removes 1 karma from coolkid1
```

#### For admin only:
##### Set user karma
```
/rocket karma set @user {amount}
```
##### Reset user karma
```
/rocket karma reset @user
```
##### Reset all user karma
```
/rocket karma reset all
```
###### Examples:
```sh
/rocket karma set @coolkid1 5 #sets coolkid's karma to 5
/rocket karma reset @coolkid1 #resets coolkid1's karma to 1
/rocket karma reset all #resets all users karma to 1
```

#### Help
##### Display options for the karma commands.
```sh
/rocket karma help
```



