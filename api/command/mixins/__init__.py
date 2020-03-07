"""Define the APIs of the various command types."""
import api.command.mixins.user as user
import api.command.mixins.team as team
import api.command.mixins.project as project
import api.command.mixins.token as token

UserCommandApis = user.UserCommandApis
TeamCommandApis = team.TeamCommandApis
ProjectCommandApis = project.ProjectCommandApis
TokenCommandApis = token.TokenCommandApis
