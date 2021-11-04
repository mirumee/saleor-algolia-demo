from typing import Any, Dict, List, Union

from pydantic import BaseModel


class ResponseModel(BaseModel):
    success: bool
    message: str
    data: Union[List[str], Dict[str, Any]]
