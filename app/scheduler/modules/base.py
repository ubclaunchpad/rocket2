"""The base class for all scheduler modules."""
from abc import ABC
from typing import Dict, Any
from flask import Flask
from config import Credentials


class ModuleBase(ABC):
    """Base class for all scheduler modules."""

    NAME = 'Base Module'

    def __init__(self,
                 flask_app: Flask,
                 config: Dict[str, Any],
                 credentials: Credentials):
        """Initialize the object."""
        pass

    def do_it(self):
        """Call to execute the function to be executed."""
        pass

    def get_job_args(self) -> Dict[str, Any]:
        """Call to obtain a dictionary of job arguments."""
        pass
