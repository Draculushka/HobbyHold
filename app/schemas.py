from pydantic import BaseModel
from datetime import datetime


class PostCreate(BaseModel):
    title: str
    description: str | None = None


class Post(BaseModel):
    id: int
    title: str
    description: str | None = None
    image_path: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True

