from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

# 1. Base schema containing properties shared across all models
class AttachmentBase(BaseModel):
    original_filename: str = Field(..., description="The original name of the file uploaded by the user")
    mime_type: Optional[str] = Field(None, description="The content type of the file, e.g., image/jpeg")


# 3. Schema for the API Response (What the client/frontend sees)
class AttachmentResponse(AttachmentBase):
    id: uuid.UUID
    session_id: uuid.UUID
    created_at: datetime
    # We can optionally include a presigned URL or a direct link if needed later
    # download_url: Optional[str] = None

    class Config:
        # If you are using Pydantic V2, use:
        # from_attributes = True
        # If you are using Pydantic V1, use:
        orm_mode = True 
