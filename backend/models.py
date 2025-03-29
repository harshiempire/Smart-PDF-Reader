from typing import Optional
from pydantic import Field, BaseModel
from bson import ObjectId
import datetime

class PydanticObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class DocumentSchema(BaseModel):
    id: Optional[PydanticObjectId] = Field(default=None, alias="_id")
    filename: str
    upload_date: datetime

