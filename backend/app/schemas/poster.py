from typing import Optional
from pydantic import BaseModel, Field


class PosterPromptRequest(BaseModel):
    ad_id: int
    course: str = Field(default="AI", description="BrandMonk course: AI, Digital marketing, UI/UX")
    angle_index: int = Field(default=0, ge=0, le=2, description="0: Outcome, 1: Proof, 2: Urgency")
    size_format: str = Field(default="feed", description="square, feed, story")


class PosterPromptResponse(BaseModel):
    ad_id: int
    course: str
    angle_name: str
    headline: str
    subline: str
    cta_text: str
    prompt: str
    size_format: str


class PosterRenderRequest(BaseModel):
    ad_id: int
    course: str = "AI"
    angle_index: int = 0
    size_format: str = "feed"
    custom_headline: Optional[str] = None
    custom_subline: Optional[str] = None
    custom_cta: Optional[str] = None


class PosterRenderResponse(BaseModel):
    poster_id: int
    headline: str
    subline: str
    cta_text: str
    image_url: str
    size_format: str
    status: str

