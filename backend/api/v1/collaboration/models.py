from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...core.database import Base
from typing import List


class Whiteboard(Base):
    """Whiteboard model for real-time collaboration"""
    __tablename__ = "whiteboards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    session_data = Column(JSON, default={})

    # Relationships
    elements = relationship("DrawingElement", back_populates="whiteboard")
    collaborations = relationship("Collaboration", back_populates="whiteboard")
    creator = relationship("User")

    def __repr__(self) -> str:
        return f"<Whiteboard {self.name}>"


class DrawingElement(Base):
    """Drawing element model for whiteboard content"""
    __tablename__ = "drawing_elements"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # line, circle, rectangle, text
    data = Column(Text, nullable=False)  # JSON data for the element
    whiteboard_id = Column(Integer, ForeignKey("whiteboards.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    whiteboard = relationship("Whiteboard", back_populates="elements")
    creator = relationship("User")

    def __repr__(self) -> str:
        return f"<DrawingElement {self.type}>"


class Collaboration(Base):
    """Collaboration model for tracking user participation"""
    __tablename__ = "collaborations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    whiteboard_id = Column(Integer, ForeignKey("whiteboards.id"), nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    left_at = Column(DateTime(timezone=True), nullable=True)
    session_data = Column(JSON, default={})

    # Relationships
    user = relationship("User")
    whiteboard = relationship("Whiteboard", back_populates="collaborations")

    def __repr__(self) -> str:
        return f"<Collaboration {self.user_id} on {self.whiteboard_id}>" 