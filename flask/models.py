# models.py

from pydantic import BaseModel, EmailStr, Field, HttpUrl, field_validator
from typing import Optional, List
from datetime import datetime


class User(BaseModel):
    """Represents a user in the system."""
    id: Optional[str] = Field(None, alias="_id")  # MongoDB uses _id
    username: str
    email: EmailStr
    password_hash: str
    role: str = "user"  # Default role, can be changed to "admin" or similar if you wish
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ClassificationResult(BaseModel):
    """Represents a classification's results and metadata."""
    id: Optional[str] = Field(None, alias="_id")
    classification_type: str  # e.g. "misinformation" or "credible"
    confidence_score: Optional[float]
    model_version: Optional[str]
    classified_at: datetime = Field(default_factory=datetime.utcnow)
    additional_info: Optional[str] = None
    prompt: str
    # This field references the user who reviewed or is associated with the classification
    reviewed_by: Optional[str] = Field(None, alias="user_id")  


class RAGKnowledgeBase(BaseModel):
    """Represents a knowledge base entry for Retrieval-Augmented Generation (RAG)."""
    id: str = Field(None, alias="_id")
    data: str
    embeddings: Optional[List[float]]  # list of floats
    datatype: str
    source: str
    time_published: datetime
    


class Uploads(BaseModel):
    """Represents an uploaded resource (file, URL, or text)."""
    id: Optional[str] = Field(None, alias="_id")
    url: Optional[HttpUrl] = None
    image_id: Optional[str] = None  # Reference to a GridFS file _id
    text: Optional[str] = None
    user_id: str = Field(default="test")

    @field_validator("url", "image_id", "text", mode="before")
    @classmethod
    def validate_at_least_one(cls, value, info):
        """
        Ensure at least one of 'url', 'image_id', or 'text' is provided.
        """
        values = info.data or {}
        if not any([values.get("url"), values.get("image_id"), values.get("text")]):
            raise ValueError("At least one of 'url', 'image_id', or 'text' must be provided.")
        return value



class TextAnalysis(BaseModel):
    """Represents a text analysis record."""
    id: Optional[str] = Field(None, alias="_id")
    user_id: str  # The ID of the user who performed or is associated with this analysis
    text_content: str
    classification_result: Optional[str] = Field(None, alias="classification_result_id")  
    # classification_result references a ClassificationResult (by its MongoDB _id)


class URLAnalysis(BaseModel):
    """Represents a URL analysis record."""
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    url: str
    classification_result: Optional[str] = Field(None, alias="classification_result_id")


class Feedback(BaseModel):
    """Represents feedback provided by a user about a classification."""
    id: Optional[str] = Field(None, alias="_id")
    user_id: str  # The ID of the user providing feedback
    classification_result: str  # The ID of the ClassificationResult the user is giving feedback on
    feedback_text: Optional[str] = None
    helpful: bool = True
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
