"""Pack the modules contained in the command directory."""
from typing import Union, Tuple
from flask import Response

ResponseTuple = Tuple[Union[str, Response], int]
