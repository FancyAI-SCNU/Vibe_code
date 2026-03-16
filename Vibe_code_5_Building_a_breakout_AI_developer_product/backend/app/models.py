from sqlalchemy import Boolean, Column, Integer, String, Text, Table, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Association table for many-to-many relationship between notes and tags
note_tags = Table(
    'note_tags',
    Base.metadata,
    Column('note_id', Integer, ForeignKey('notes.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    
    # Relationship to tags
    tags = relationship("Tag", secondary=note_tags, back_populates="notes")
    
    def __repr__(self):
        return f"<Note(id={self.id}, title='{self.title}')>"


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    
    # Relationship to notes
    notes = relationship("Note", secondary=note_tags, back_populates="tags")
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"


class ActionItem(Base):
    __tablename__ = "action_items"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f"<ActionItem(id={self.id}, completed={self.completed})>"