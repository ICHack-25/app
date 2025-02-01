from pydantic import BaseModel, EmailStr, Field
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
    reviewed_by: Optional[str] = Field(None, alias="user_id")  # Referencing User ID

class File(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user: str  # User ID as a string
    file_name: str
    file_type: str
    file_path: str
    upload_time: datetime = Field(default_factory=datetime.utcnow)
    classification_result: Optional[str] = Field(None, alias="classification_result_id")  # Reference to ClassificationResult ID

class TextAnalysis(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user: str  # User ID as a string
    text_content: str
    classification_result: Optional[str] = Field(None, alias="classification_result_id")  # Reference to ClassificationResult ID

class URLAnalysis(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user: str  # User ID as a string
    url: str
    classification_result: Optional[str] = Field(None, alias="classification_result_id")  # Reference to ClassificationResult ID

class Feedback(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user: str  # User ID as a string
    classification_result: str  # ClassificationResult ID
    feedback_text: Optional[str] = None
    helpful: bool = True
    submitted_at: datetime = Field(default_factory=datetime.utcnow)