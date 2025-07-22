from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class AILiteracyAssessmentBase(BaseModel):
    assessment_type: str
    score: float
    max_score: float
    responses: Optional[Dict[str, Any]] = None


class AILiteracyAssessmentCreate(AILiteracyAssessmentBase):
    pass


class AILiteracyAssessment(AILiteracyAssessmentBase):
    id: int
    user_id: int
    completed_at: datetime
    
    class Config:
        from_attributes = True


class AIEthicsTrainingBase(BaseModel):
    training_type: str
    completion_status: str
    score: Optional[float] = None


class AIEthicsTrainingCreate(AIEthicsTrainingBase):
    pass


class AIEthicsTraining(AIEthicsTrainingBase):
    id: int
    user_id: int
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AITransparencyLogBase(BaseModel):
    ai_agent_type: str
    decision_type: str
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    reasoning: Optional[str] = None


class AITransparencyLogCreate(AITransparencyLogBase):
    pass


class AITransparencyLog(AITransparencyLogBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class AILiteracyProgress(BaseModel):
    """User's AI literacy progress across all Big Ideas"""
    perception_score: float
    representation_score: float
    learning_score: float
    interaction_score: float
    societal_score: float
    overall_score: float
    completed_assessments: int
    total_assessments: int


class AIEthicsProgress(BaseModel):
    """User's AI ethics training progress"""
    bias_detection_completed: bool
    fairness_completed: bool
    transparency_completed: bool
    privacy_completed: bool
    overall_ethics_score: float 