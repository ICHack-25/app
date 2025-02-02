from pydantic import BaseModel, EmailStr, Field, HttpUrl, field_validator
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")  # MongoDB uses _id
    username: str
    email: EmailStr
    password_hash: str
    role: str = Field("user", Literal=True)  # Default role
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ClassificationResult(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    classification_type: str  # Either "misinformation" or "credible"
    confidence_score: float
    model_version: str
    classified_at: datetime = Field(default_factory=datetime.utcnow)
    additional_info: Optional[str] = None
    prompt: str
    reviewed_by: Optional[str] = Field(None, alias="user_id")  # Referencing User ID

class RAGKnowledgeBase(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    data: str
    embeddings: List[float] # list of floats
    datatype: str
    source: str
    time_published: datetime

class Uploads(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    url: Optional[HttpUrl] = None
    image_id: Optional[str] = None  # Reference to GridFS file _id
    text: Optional[str] = None
    user_id: str = Field(default="test")

    @field_validator("url", "image_id", "text", mode="before")
    @classmethod
    def at_least_one(cls, v, values):
        if not any([values.get("url"), values.get("image_id"), values.get("text")]):
            raise ValueError("At least one of url, image, or text must be provided.")
        return v

class TextAnalysis(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str  # User ID instead of Username
    text_content: str
    classification_result: Optional[str] = Field(None, alias="classification_result_id")  # Reference to ClassificationResult ID

class URLAnalysis(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str  # User ID instead of Username
    url: str
    classification_result: Optional[str] = Field(None, alias="classification_result_id")  # Reference to ClassificationResult ID

class Feedback(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str  # User ID instead of Username
    classification_result: str  # ClassificationResult ID
    feedback_text: Optional[str] = None
    helpful: bool = True
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
