"""Pack the modules contained in the model directory."""
import app.model.user as user
import app.model.team as team
import app.model.permissions as permissions
import app.model.project as project
import app.model.base as base

User = user.User
Team = team.Team
Permissions = permissions.Permissions
Project = project.Project
BaseModel = base.RocketModel
