from typing import Dict, Union
from pydantic import BaseModel


class JsonDict(BaseModel):
    dictt: Dict[str, Union[int, float, bool, str]]
