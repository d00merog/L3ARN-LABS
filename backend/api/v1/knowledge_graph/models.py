from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from main.database import Base


class Concept(Base):
    """Knowledge graph concepts"""
    __tablename__ = "concepts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    subject = Column(String, nullable=False)  # math, science, history, etc.
    difficulty_level = Column(Integer, nullable=False)  # 1-10 scale
    prerequisites = Column(JSON, nullable=True)  # List of prerequisite concept IDs
    metadata = Column(JSON, nullable=True)  # Additional concept metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ConceptRelationship(Base):
    """Relationships between concepts in the knowledge graph"""
    __tablename__ = "concept_relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    source_concept_id = Column(Integer, ForeignKey("concepts.id"))
    target_concept_id = Column(Integer, ForeignKey("concepts.id"))
    relationship_type = Column(String, nullable=False)  # prerequisite, related, builds_on, etc.
    strength = Column(Float, nullable=False, default=1.0)  # Relationship strength 0-1
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    source_concept = relationship("Concept", foreign_keys=[source_concept_id])
    target_concept = relationship("Concept", foreign_keys=[target_concept_id])


class LearningPath(Base):
    """User's personalized learning path"""
    __tablename__ = "learning_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(String, nullable=False)
    path_data = Column(JSON, nullable=False)  # Structured learning path
    current_step = Column(Integer, nullable=False, default=0)
    completed_steps = Column(JSON, nullable=True)  # List of completed step IDs
    progress_percentage = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="learning_paths")


class KnowledgeGap(Base):
    """Identified knowledge gaps for users"""
    __tablename__ = "knowledge_gaps"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    concept_id = Column(Integer, ForeignKey("concepts.id"))
    gap_type = Column(String, nullable=False)  # missing_prerequisite, weak_understanding, etc.
    severity = Column(Float, nullable=False)  # 0-1 scale
    assessment_data = Column(JSON, nullable=True)  # Assessment results
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="knowledge_gaps")
    concept = relationship("Concept")


class ConceptMastery(Base):
    """User's mastery level for concepts"""
    __tablename__ = "concept_mastery"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    concept_id = Column(Integer, ForeignKey("concepts.id"))
    mastery_level = Column(Float, nullable=False, default=0.0)  # 0-1 scale
    assessment_count = Column(Integer, nullable=False, default=0)
    last_assessment_date = Column(DateTime(timezone=True), nullable=True)
    learning_style = Column(String, nullable=True)  # visual, auditory, kinesthetic
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="concept_mastery")
    concept = relationship("Concept") 