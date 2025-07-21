from pydantic import BaseModel
from typing import Optional
class pushRequest(BaseModel):
    do_reset:Optional[int]=0


class searchRequest(BaseModel):
    text:str
    limit:Optional[int]=5