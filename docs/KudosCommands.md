# Kudos Command Reference 

Command to give or take away a user's karma

## Options
#### For normal users:
##### Add karma to user
```
/rocket @user ++
```
##### Remove karma from user
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
/rocket kudos set @user {amount}
```
##### Reset user karma
```
/rocket kudos reset @user
```
##### Reset all user karma
```
/rocket kudos reset all
```
###### Examples:
```sh
/rocket kudos set @coolkid1 5 #sets coolkid's karma to 5
/rocket kudos reset @coolkid1 #resets coolkid1's karma to 1
/rocket kudos reset all #resets all users karma to 1
```

### Help

```sh
/rocket kudos help
```

Display options for the kudos commands.

