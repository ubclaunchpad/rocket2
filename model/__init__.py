"""Pack the modules contained in the model directory."""
import model.user
import model.team
import model.permissions
import model.project

User = model.user.User
Team = model.team.Team
Permissions = model.permissions.Permissions
Project = model.project.Project
