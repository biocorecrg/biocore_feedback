from typing import Optional
from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name or identifier of the user submitting feedback")
    app: str = Field(..., min_length=1, max_length=150, description="Name of the application")
    message: str = Field(..., min_length=1, max_length=4000, description="Feedback message, suggestion or issue description")
    page_url: Optional[str] = Field(None, max_length=1000, description="URL of the page where feedback was submitted")
    user_agent: Optional[str] = Field(None, max_length=500, description="Browser / client user agent")


class FeedbackResponse(BaseModel):
    ok: bool
    message: str
