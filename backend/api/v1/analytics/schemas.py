from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class LearningAnalyticsBase(BaseModel):
    session_id: Optional[str] = None
    activity_type: str
    subject: Optional[str] = None
    duration_minutes: Optional[float] = None
    score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class LearningAnalyticsCreate(LearningAnalyticsBase):
    pass


class LearningAnalytics(LearningAnalyticsBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class EngagementMetricsBase(BaseModel):
    date: datetime
    time_on_platform_minutes: float = 0.0
    lessons_completed: int = 0
    quizzes_taken: int = 0
    achievements_earned: int = 0
    social_interactions: int = 0


class EngagementMetricsCreate(EngagementMetricsBase):
    pass


class EngagementMetrics(EngagementMetricsBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class PerformancePredictionBase(BaseModel):
    subject: str
    predicted_score: float
    confidence_level: float
    factors: Optional[Dict[str, Any]] = None


class PerformancePredictionCreate(PerformancePredictionBase):
    pass


class PerformancePrediction(PerformancePredictionBase):
    id: int
    user_id: int
    prediction_date: datetime
    actual_score: Optional[float] = None
    accuracy: Optional[float] = None
    
    class Config:
        from_attributes = True


class InterventionRecommendationBase(BaseModel):
    recommendation_type: str
    subject: Optional[str] = None
    priority: str
    description: Optional[str] = None
    action_items: Optional[Dict[str, Any]] = None


class InterventionRecommendationCreate(InterventionRecommendationBase):
    pass


class InterventionRecommendation(InterventionRecommendationBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    implemented_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ABTestResultBase(BaseModel):
    test_name: str
    variant: str
    subject: Optional[str] = None
    metric_name: str
    metric_value: float
    test_duration_days: Optional[int] = None


class ABTestResultCreate(ABTestResultBase):
    pass


class ABTestResult(ABTestResultBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class LearningProgressSummary(BaseModel):
    """Summary of user's learning progress"""
    total_time_minutes: float
    lessons_completed: int
    quizzes_taken: int
    average_score: float
    subjects_studied: List[str]
    current_streak_days: int
    total_achievements: int


class EngagementSummary(BaseModel):
    """Summary of user engagement"""
    daily_active_days: int
    weekly_active_days: int
    monthly_active_days: int
    average_session_duration: float
    most_active_subject: str
    engagement_score: float


class PerformanceInsights(BaseModel):
    """AI-generated performance insights"""
    strengths: List[str]
    areas_for_improvement: List[str]
    recommended_focus_areas: List[str]
    predicted_performance_trend: str
    confidence_in_predictions: float 