"""Pack the modules contained in the commands directory."""
import app.controller.command.commands.team as team
import app.controller.command.commands.user as user
import app.controller.command.commands.export as export
import app.controller.command.commands.token as token
import app.controller.command.commands.project as project
import app.controller.command.commands.karma as karma
import app.controller.command.commands.mention as mention
import app.controller.command.commands.iquit as iquit

TeamCommand = team.TeamCommand
UserCommand = user.UserCommand
ExportCommand = export.ExportCommand
TokenCommand = token.TokenCommand
ProjectCommand = project.ProjectCommand
KarmaCommand = karma.KarmaCommand
MentionCommand = mention.MentionCommand
IQuitCommand = iquit.IQuitCommand
