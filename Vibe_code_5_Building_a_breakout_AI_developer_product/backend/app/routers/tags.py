from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Note, Tag
from ..schemas import TagCreate, TagResponse

router = APIRouter(tags=["tags"])


@router.get("/tags", response_model=list[TagResponse])
def list_tags(db: Session = Depends(get_db)) -> list[TagResponse]:
    """
    获取所有标签，包含每个标签的笔记数量
    """
    # Query tags with note count
    query = select(
        Tag,
        func.count(Note.id).label('note_count')
    ).outerjoin(Tag.notes).group_by(Tag.id)
    
    results = db.execute(query).all()
    
    tags = []
    for tag, note_count in results:
        tag_dict = {
            "id": tag.id,
            "name": tag.name,
            "note_count": note_count
        }
        tags.append(TagResponse(**tag_dict))
    
    return tags


@router.post("/tags", response_model=TagResponse, status_code=201)
def create_tag(payload: TagCreate, db: Session = Depends(get_db)) -> TagResponse:
    """
    创建新标签，如果已存在则返回现有标签
    """
    # Check if tag already exists
    existing_tag = db.execute(
        select(Tag).where(Tag.name == payload.name)
    ).scalar_one_or_none()
    
    if existing_tag:
        # Return existing tag with note count
        note_count = db.execute(
            select(func.count(Note.id))
            .select_from(Tag)
            .outerjoin(Tag.notes)
            .where(Tag.id == existing_tag.id)
        ).scalar() or 0
        
        return TagResponse(
            id=existing_tag.id,
            name=existing_tag.name,
            note_count=note_count
        )
    
    # Create new tag
    tag = Tag(name=payload.name)
    db.add(tag)
    db.flush()
    db.refresh(tag)
    
    return TagResponse(id=tag.id, name=tag.name, note_count=0)


@router.delete("/tags/{tag_id}", status_code=204)
def delete_tag(tag_id: int, db: Session = Depends(get_db)) -> None:
    """
    删除标签及其所有关联关系
    """
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    db.delete(tag)
    db.flush()


@router.post("/notes/{note_id}/tags", response_model=TagResponse, status_code=201)
def add_tag_to_note(
    note_id: int,
    payload: TagCreate,
    db: Session = Depends(get_db)
) -> TagResponse:
    """
    为笔记添加标签，如果标签不存在则自动创建
    """
    # Check if note exists
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Get or create tag
    tag = db.execute(
        select(Tag).where(Tag.name == payload.name)
    ).scalar_one_or_none()
    
    if not tag:
        tag = Tag(name=payload.name)
        db.add(tag)
        db.flush()
    
    # Add tag to note if not already associated
    if tag not in note.tags:
        note.tags.append(tag)
        db.add(note)
        db.flush()
    
    # Get note count for response
    note_count = db.execute(
        select(func.count(Note.id))
        .select_from(Tag)
        .outerjoin(Tag.notes)
        .where(Tag.id == tag.id)
    ).scalar() or 0
    
    return TagResponse(id=tag.id, name=tag.name, note_count=note_count)


@router.delete("/notes/{note_id}/tags/{tag_id}", status_code=204)
def remove_tag_from_note(
    note_id: int,
    tag_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    移除笔记的标签
    """
    # Check if note exists
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Check if tag exists
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Remove tag from note
    if tag in note.tags:
        note.tags.remove(tag)
        db.add(note)
        db.flush()


