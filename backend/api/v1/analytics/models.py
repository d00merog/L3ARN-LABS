from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from main.database import Base


class LearningAnalytics(Base):
    """Learning analytics data"""
    __tablename__ = "learning_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(String, nullable=True)
    activity_type = Column(String, nullable=False)  # lesson_completion, quiz_taken, etc.
    subject = Column(String, nullable=True)
    duration_minutes = Column(Float, nullable=True)
    score = Column(Float, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional analytics data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="learning_analytics")


class EngagementMetrics(Base):
    """User engagement metrics"""
    __tablename__ = "engagement_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime(timezone=True), nullable=False)
    time_on_platform_minutes = Column(Float, nullable=False, default=0.0)
    lessons_completed = Column(Integer, nullable=False, default=0)
    quizzes_taken = Column(Integer, nullable=False, default=0)
    achievements_earned = Column(Integer, nullable=False, default=0)
    social_interactions = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="engagement_metrics")


class PerformancePrediction(Base):
    """AI-powered performance predictions"""
    __tablename__ = "performance_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(String, nullable=False)
    predicted_score = Column(Float, nullable=False)
    confidence_level = Column(Float, nullable=False)
    prediction_date = Column(DateTime(timezone=True), server_default=func.now())
    actual_score = Column(Float, nullable=True)  # Filled after assessment
    accuracy = Column(Float, nullable=True)  # Prediction accuracy
    factors = Column(JSON, nullable=True)  # Factors influencing prediction
    
    user = relationship("User", back_populates="performance_predictions")


class InterventionRecommendation(Base):
    """AI-generated intervention recommendations"""
    __tablename__ = "intervention_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    recommendation_type = Column(String, nullable=False)  # extra_help, advanced_content, etc.
    subject = Column(String, nullable=True)
    priority = Column(String, nullable=False)  # high, medium, low
    description = Column(Text, nullable=True)
    action_items = Column(JSON, nullable=True)  # Specific actions to take
    status = Column(String, nullable=False, default="pending")  # pending, implemented, resolved
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    implemented_at = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("User", back_populates="intervention_recommendations")


class A/BTestResult(Base):
    """A/B testing results for teaching methods"""
    __tablename__ = "ab_test_results"
    
    id = Column(Integer, primary_key=True, index=True)
    test_name = Column(String, nullable=False)
    variant = Column(String, nullable=False)  # A, B, control
    user_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(String, nullable=True)
    metric_name = Column(String, nullable=False)  # completion_rate, score, engagement
    metric_value = Column(Float, nullable=False)
    test_duration_days = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="ab_test_results") 