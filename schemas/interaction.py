from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CommentBase(BaseModel):
    text: str = Field(..., max_length=1000)

class CommentCreate(CommentBase):
    persona_id: Optional[int] = None
    parent_id: Optional[int] = None

class CommentUpdate(CommentBase):
    pass

class NotificationResponse(BaseModel):
    id: int
    type: str
    message: str
    link: Optional[str]
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class CommentReactionResponse(BaseModel):
    id: int
    comment_id: int
    persona_id: int
    created_at: datetime

    model_config = {"from_attributes": True}

class CommentResponse(CommentBase):
    id: int
    hobby_id: int
    persona_id: int
    parent_id: Optional[int] = None
    created_at: datetime
    reactions: list[CommentReactionResponse] = []

    model_config = {"from_attributes": True}

class ReactionBase(BaseModel):
    emoji_type: str = Field(default="heart", max_length=50)

class ReactionCreate(ReactionBase):
    pass

class ReactionResponse(ReactionBase):
    id: int
    hobby_id: int
    persona_id: int
    created_at: datetime

    model_config = {"from_attributes": True}

class FollowResponse(BaseModel):
    follower_persona_id: int
    followed_persona_id: int
    created_at: datetime

    model_config = {"from_attributes": True}

class PersonaStatsResponse(BaseModel):
    followers_count: int
    is_following: bool
