"""Define the APIs of the various command types."""
import api.command.mixins.user as user
import api.command.mixins.team as team
import api.command.mixins.project as project

UserCommandApis = user.UserCommandApis
TeamCommandApis = team.TeamCommandApis
ProjectCommandApis = project.ProjectCommandApis
