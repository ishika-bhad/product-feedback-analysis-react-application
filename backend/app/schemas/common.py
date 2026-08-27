from pydantic import BaseModel, Field
from typing import Any, Optional

class APIResponse(BaseModel):
    success: bool = Field(..., description="Flag indicating success or failure of the operation")
    status_code: int = Field(..., description="HTTP status code of the response")
    message: str = Field(..., description="Brief success or error message")
    error_message: Optional[str] = Field(None, description="Detailed error message when success is False")
    data: Optional[Any] = Field(None, description="Response payload data wrapper")
