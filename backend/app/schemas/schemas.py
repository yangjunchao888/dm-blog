from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=64)


class UserOut(UserBase):
    id: int
    nickname: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LoginRequest(UserBase):
    password: str = Field(min_length=6, max_length=128)


class TagOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class ArticleBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content_md: str = ""
    tags: Optional[List[str]] = None


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    content_md: Optional[str] = None
    tags: Optional[List[str]] = None


class ArticleOut(BaseModel):
    id: int
    title: str
    content_md: str
    summary: Optional[str] = None
    author_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tags: List[TagOut] = []

    class Config:
        from_attributes = True
