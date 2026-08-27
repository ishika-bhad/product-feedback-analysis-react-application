from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from typing import List

class FeedbackData(BaseModel):
    request_id: UUID4 = Field(..., description="The unique request ID for the submission")
    product_name: str = Field(..., description="The product name")
    product_id: int = Field(..., description="The allocated integer product ID")
    feedback: str = Field(..., description="The feedback text submitted")
    sentiment: str = Field(..., description="Classified sentiment: positive, negative, or neutral")
    confidence: float = Field(..., description="Sentiment confidence score (0.0 to 1.0)")
    created_at: datetime = Field(..., description="Timestamp when feedback was saved")

class FeedbackRecord(BaseModel):
    request_id: UUID4 = Field(..., description="The request ID associated with this feedback")
    feedback: str = Field(..., description="Feedback text")
    sentiment: str = Field(..., description="Classified sentiment")
    confidence: float = Field(..., description="Sentiment confidence score")
    created_at: datetime = Field(..., description="Timestamp when feedback was saved")

class HistoricalData(BaseModel):
    request_id: UUID4 = Field(..., description="The request ID from the retrieval request header")
    product_id: int = Field(..., description="The product ID queried")
    product_name: str = Field(..., description="The name of the product")
    feedbacks: List[FeedbackRecord] = Field(..., description="List of historical feedback submissions")
