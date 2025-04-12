import enum
from typing import Any, Dict, Optional, List
from pydantic import Field, BaseModel
from bson import ObjectId
import datetime

class ProcessingStatus(enum.Enum):
    PENDING = 1
    PROCESSING = 2 
    FAILED = 3 
    COMPLETED = 4

class SegmentType(enum.Enum):
    TITLE = "title"
    PARAGRAPH = "paragraph"
    LIST = "list"
    TABLE = "table"
    FIGURE = "figure"
    CAPTION = "caption"

class MessageRole(enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"

class PydanticObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class PositionInfo(BaseModel):
    x: float
    y: float
    width: float
    height: float
    page_width: float
    page_height: float

class DocumentSchema(BaseModel):
    id: Optional[PydanticObjectId] = Field(default=None, alias="_id")
    filename: str
    upload_date: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    pages: int
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    user_id: str
    file_size: int
    mime_type: str = "application/pdf"

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

class SegmentSchema(BaseModel):
    id: Optional[PydanticObjectId] = Field(default=None, alias="_id")
    document_id: PydanticObjectId
    page_number: int
    text_content: str
    position_info: PositionInfo
    segment_type: SegmentType
    
    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    segment_ids: List[PydanticObjectId] = []

class ChatSession(BaseModel):
    id: Optional[PydanticObjectId] = Field(default=None, alias="_id")
    document_id: PydanticObjectId
    messages: List[Message] = []
    segment_ids: List[PydanticObjectId] = []
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    title: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}