from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Note
from ..schemas import NoteCreate, NoteRead

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/", response_model=list[NoteRead])
def list_notes(db: Session = Depends(get_db)) -> list[NoteRead]:
    rows = db.execute(select(Note)).scalars().all()
    return [NoteRead.model_validate(row) for row in rows]


from ..services.extract import extract_tags
from ..models import Tag

@router.post("/", response_model=NoteRead, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteRead:
    note = Note(title=payload.title, content=payload.content)
    db.add(note)
    db.flush()  # 让note获得id

    # 自动提取标签
    tag_names = extract_tags(note.content)
    tags: list[Tag] = []
    for tag_name in tag_names:
        # 标准化处理：strip，限制50字符，防注入
        tag_name_norm = tag_name.strip()
        if not (1 <= len(tag_name_norm) <= 50):
            continue
        # 标签名唯一
        tag = db.execute(
            select(Tag).where(Tag.name == tag_name_norm)
        ).scalar_one_or_none()
        if not tag:
            tag = Tag(name=tag_name_norm)
            db.add(tag)
            db.flush()
        tags.append(tag)

    note.tags = tags
    db.add(note)  # 重新add（可选）
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.get("/search")
def search_notes(
    q: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    sort: str = Query("created_desc", description="排序方式"),
    db: Session = Depends(get_db)
):
    """
    搜索笔记 - 支持分页和排序
    
    参数:
    - q: 搜索关键词（可选）
    - page: 页码，从1开始
    - page_size: 每页数量，1-100之间
    - sort: 排序方式（created_desc, created_asc, title_asc, title_desc）
    
    返回:
    - items: 笔记列表
    - total: 总数
    - page: 当前页
    - page_size: 每页数量
    - total_pages: 总页数
    """
    try:
        # 构建基础查询
        query = select(Note)
        
        # 如果有搜索关键词，添加过滤条件（不区分大小写）
        if q:
            search_pattern = f"%{q}%"
            query = query.where(
                or_(
                    Note.title.ilike(search_pattern),
                    Note.content.ilike(search_pattern)
                )
            )
        
        # 添加排序
        if sort == "created_desc":
            query = query.order_by(Note.created_at.desc())
        elif sort == "created_asc":
            query = query.order_by(Note.created_at.asc())
        elif sort == "title_asc":
            query = query.order_by(Note.title.asc())
        elif sort == "title_desc":
            query = query.order_by(Note.title.desc())
        
        # 计算总数
        total_query = select(func.count()).select_from(Note)
        if q:
            search_pattern = f"%{q}%"
            total_query = total_query.where(
                or_(
                    Note.title.ilike(search_pattern),
                    Note.content.ilike(search_pattern)
                )
            )
        total = db.execute(total_query).scalar() or 0
        
        # 计算总页数
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        
        # 应用分页
        offset = (page - 1) * page_size
        items = db.execute(query.offset(offset).limit(page_size)).scalars().all()
        
        # 返回字典格式
        return {
            "items": [NoteRead.model_validate(item) for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    except Exception as e:
        # 如果出错，返回详细错误信息
        raise HTTPException(status_code=500, detail=f"搜索出错: {str(e)}")


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteRead.model_validate(note)
