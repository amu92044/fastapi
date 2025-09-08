from pydantic import BaseModel, conint
from datetime import datetime
from typing import Optional

# ----------------- Posts -----------------
class PostBase(BaseModel):
    title: str
    content: str
    published: Optional[bool] = True


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None


class UserOut(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True  # replaces orm_mode in Pydantic v2


class PostSchema(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    class Config:
        from_attributes = True


class PostOut(BaseModel):
    Post: PostSchema
    votes: int

    class Config:
        from_attributes = True


# ----------------- Users -----------------
class UserCreate(BaseModel):
    email: str
    password: str


class UserSchema(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: str
    password: str


# ----------------- Authentication -----------------
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None


# ----------------- Votes -----------------
class Vote(BaseModel):
    post_id: int
    dir: conint(le=1, ge=0)  # 1 = upvote, 0 = remove vote
