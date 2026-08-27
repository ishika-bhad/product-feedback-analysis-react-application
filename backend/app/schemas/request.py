from pydantic import BaseModel, Field, UUID4, field_validator

class FeedbackSubmitRequest(BaseModel):
    request_id: UUID4 = Field(..., description="Unique client-generated request ID (UUID v4 format)")
    product_name: str = Field(..., description="Name of the product")
    product_feedback: str = Field(..., description="Feedback text to analyze")

    @field_validator("product_name")
    def validate_product_name(cls, v: str) -> str:
        val = v.strip()
        if not val:
            raise ValueError("Product name cannot be empty or only whitespace")
        if len(val) > 100:
            raise ValueError("Product name is too long (maximum 100 characters)")
        return val

    @field_validator("product_feedback")
    def validate_product_feedback(cls, v: str) -> str:
        val = v.strip()
        if not val:
            raise ValueError("Product feedback cannot be empty or only whitespace")
        if len(val) > 2000:
            raise ValueError("Product feedback is too long (maximum 2000 characters)")
        return val
