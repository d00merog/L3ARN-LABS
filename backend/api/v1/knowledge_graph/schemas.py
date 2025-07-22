from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ConceptBase(BaseModel):
    name: str
    description: Optional[str] = None
    subject: str
    difficulty_level: int
    prerequisites: Optional[List[int]] = None
    metadata: Optional[Dict[str, Any]] = None


class ConceptCreate(ConceptBase):
    pass


class Concept(ConceptBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ConceptRelationshipBase(BaseModel):
    source_concept_id: int
    target_concept_id: int
    relationship_type: str
    strength: float = 1.0


class ConceptRelationshipCreate(ConceptRelationshipBase):
    pass


class ConceptRelationship(ConceptRelationshipBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class LearningPathBase(BaseModel):
    subject: str
    path_data: Dict[str, Any]
    current_step: int = 0
    completed_steps: Optional[List[int]] = None
    progress_percentage: float = 0.0


class LearningPathCreate(LearningPathBase):
    pass


class LearningPath(LearningPathBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class KnowledgeGapBase(BaseModel):
    concept_id: int
    gap_type: str
    severity: float
    assessment_data: Optional[Dict[str, Any]] = None


class KnowledgeGapCreate(KnowledgeGapBase):
    pass


class KnowledgeGap(KnowledgeGapBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConceptMasteryBase(BaseModel):
    concept_id: int
    mastery_level: float = 0.0
    assessment_count: int = 0
    learning_style: Optional[str] = None


class ConceptMasteryCreate(ConceptMasteryBase):
    pass


class ConceptMastery(ConceptMasteryBase):
    id: int
    user_id: int
    last_assessment_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class KnowledgeGraphAnalysis(BaseModel):
    """Analysis of user's knowledge graph"""
    total_concepts: int
    mastered_concepts: int
    in_progress_concepts: int
    not_started_concepts: int
    knowledge_gaps: List[Dict[str, Any]]
    recommended_next_concepts: List[Dict[str, Any]]
    learning_path_suggestions: List[Dict[str, Any]]


class LearningPathRecommendation(BaseModel):
    """Personalized learning path recommendation"""
    subject: str
    current_level: str
    target_level: str
    estimated_duration: str
    path_steps: List[Dict[str, Any]]
    prerequisites: List[str]
    learning_style_adaptations: Dict[str, Any] 