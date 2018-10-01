"""Data model to represent permissions."""
from enum import Enum


class Permissions(Enum):
    """Enum to represent possible permissions levels."""

    member = 1
    team_lead = 2
    admin = 3
