from pydantic import BaseModel,Field,validator
from typing import Optional
from bson.objectid import ObjectId
class Project(BaseModel):
    id:Optional[ObjectId]=Field(None,alias="_id")
    project_id:str=Field(...,minLength=1)


    class Config:
        arbitrary_types_allowed = True   #to avoid pydantic err




    @validator("project_id")
    def validate_project_id(cls,value):
        if not value.isalnum():
            raise ValueError("project_id must be alphanumeric")
        return value
    
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key":[("project_id",1)],
                "name":"project_id_index",
                "unique":True
            }
        ]