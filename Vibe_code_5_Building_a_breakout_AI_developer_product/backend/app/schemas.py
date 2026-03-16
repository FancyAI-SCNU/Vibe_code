from typing import List, Optional
from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)


class TagResponse(BaseModel):
    id: int
    name: str
    note_count: Optional[int] = None

    class Config:
        orm_mode = True


class NoteCreate(BaseModel):
    title: str
    content: str


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    tags: List[TagResponse] = []

    class Config:
        orm_mode = True


class NoteRead(BaseModel):
    id: int
    title: str
    content: str

    class Config:
        from_attributes = True


class ActionItemCreate(BaseModel):
    description: str


class ActionItemRead(BaseModel):
    id: int
    description: str
    completed: bool

    class Config:
        orm_mode = True