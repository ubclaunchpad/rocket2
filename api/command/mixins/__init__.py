"""Define the APIs of the various command types."""
import api.command.mixins.user as user
import api.command.mixins.team as team

UserCommandApis = user.UserCommandApis
TeamCommandApis = team.TeamCommandApis
