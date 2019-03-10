"""Pack the modules contained in the model directory."""
from model.user import User
from model.team import Team
from model.project import Project
from typing import Union, Type


UnionModelTypes = Union[Type[User], Type[Team], Type[Project]]
UnionModels = Union[User, Team, Project]
