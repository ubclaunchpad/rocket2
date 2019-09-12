"""Pack the modules contained in the commands directory."""
import app.controller.command.commands.team as team
import app.controller.command.commands.user as user
import app.controller.command.commands.token as token
import app.controller.command.commands.project as project

TeamCommand = team.TeamCommand
UserCommand = user.UserCommand
TokenCommand = token.TokenCommand
ProjectCommand = project.ProjectCommand
