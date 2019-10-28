"""Pack the modules contained in the controller directory."""
from typing import Tuple, Dict, List, Any, Union

ResponseTuple = Tuple[Union[Dict[str, List[Dict[str, Any]]],
                      str,
                      Dict[str, Any]], int]
