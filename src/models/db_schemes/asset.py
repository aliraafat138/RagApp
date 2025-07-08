from typing import Optional
from pydantic import BaseModel,Field
from bson.objectid import ObjectId
from datetime import datetime
class Asset(BaseModel):
    id:Optional[ObjectId]=Field(None,alias="_id")
    asset_project_id:ObjectId
    asset_name:str=Field(...,min_Length=1)
    asset_type:str=Field(...,min_Length=1)
    asset_size:int=Field(default=None,ge=0)
    asset_pushed_at:datetime=Field(default=datetime.utcnow)


    class Config:
        arbitrary_types_allowed = True   #to avoid pydantic err




    @classmethod
    def get_indexes(cls):
        return [{
            "key":[("asset_project_id",1)],
            "name":"asset_project_id_index",
            "unique":False
        },{
            "key":[("asset_project_id",1),("asset_name",1)],
            "name":"asset_project_id_name_index",
            "unique":True
        }]