from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.models.base import Base

class Feedback(Base):
    __tablename__ = "feedbacks"

    # request_id is the primary key as a UUID-formatted string
    request_id = Column(String(36), primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    feedback_text = Column(String, nullable=False)
    sentiment = Column(String(20), nullable=False)
    confidence_score = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Back-relationship to Product
    product = relationship("Product", back_populates="feedbacks")
