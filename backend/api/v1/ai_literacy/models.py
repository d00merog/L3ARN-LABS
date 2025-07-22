from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from main.database import Base


class AILiteracyAssessment(Base):
    """AI Literacy Assessment based on AI4K12 Big Ideas"""
    __tablename__ = "ai_literacy_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    assessment_type = Column(String, nullable=False)  # perception, representation, learning, interaction, societal
    score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    responses = Column(JSON, nullable=True)  # Store detailed responses
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="ai_literacy_assessments")


class AIEthicsTraining(Base):
    """AI Ethics and Bias Detection Training"""
    __tablename__ = "ai_ethics_trainings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    training_type = Column(String, nullable=False)  # bias_detection, fairness, transparency, privacy
    completion_status = Column(String, nullable=False)  # not_started, in_progress, completed
    score = Column(Float, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("User", back_populates="ai_ethics_trainings")


class AITransparencyLog(Base):
    """Log of AI decisions for transparency"""
    __tablename__ = "ai_transparency_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ai_agent_type = Column(String, nullable=False)
    decision_type = Column(String, nullable=False)  # content_generation, assessment, recommendation
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)
    reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="ai_transparency_logs") 