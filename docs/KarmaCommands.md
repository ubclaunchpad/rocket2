# Karma Command Reference

Command to giveth or taketh away a user's karma

## Options

### For normal users

#### Add 1 karma to user

```sh
/rocket karma @user
```

### For admin only

#### Set user karma

```sh
/rocket karma set @user {amount}
```

#### Reset user karma

```sh
/rocket karma reset @user
```

#### Reset all user karma

```sh
/rocket karma reset --all
```

### Examples

```sh
# normal user
/rocket karma @coolkid1 #adds 1 karma to coolkid1

# admin only
/rocket karma set @coolkid1 5 #sets coolkid's karma to 5
/rocket karma reset @coolkid1 #resets coolkid1's karma to 1
/rocket karma reset --all #resets all users karma to 1
```

#### Help

##### Display options for karma commands

```sh
/rocket karma help
```
