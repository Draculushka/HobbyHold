from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- Tag Schemas ---
class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int

    class Config:
        from_attributes = True

# --- Hobby Schemas ---
class HobbyBase(BaseModel):
    title: str
    description: Optional[str] = None
    author: Optional[str] = None
    image_path: Optional[str] = None

class HobbyCreate(HobbyBase):
    tags: List[str] = [] # Имена тегов

class HobbyUpdate(HobbyBase):
    tags: List[str] = []

class Hobby(HobbyBase):
    id: int
    author_id: Optional[int] = None
    created_at: datetime
    tags: List[Tag] = []

    class Config:
        from_attributes = True
