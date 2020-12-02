"""Pack the modules contained in the model directory."""
import app.model.user as user
import app.model.team as team
import app.model.permissions as permissions
import app.model.base as base

User = user.User
Team = team.Team
Permissions = permissions.Permissions
BaseModel = base.RocketModel
