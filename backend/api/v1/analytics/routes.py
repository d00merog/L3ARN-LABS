from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Dict, Any
from datetime import datetime, timedelta
from main.database import get_db
from main.api.v1.auth.crud import get_current_user
from main.api.v1.auth.models import User
from . import models, schemas

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.post("/learning-analytics", response_model=schemas.LearningAnalytics)
async def create_learning_analytics(
    analytics: schemas.LearningAnalyticsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create learning analytics entry"""
    db_analytics = models.LearningAnalytics(
        user_id=current_user.id,
        **analytics.dict()
    )
    db.add(db_analytics)
    db.commit()
    db.refresh(db_analytics)
    return db_analytics


@router.get("/learning-progress", response_model=schemas.LearningProgressSummary)
async def get_learning_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's learning progress summary"""
    # Get analytics data for the user
    analytics = db.query(models.LearningAnalytics).filter(
        models.LearningAnalytics.user_id == current_user.id
    ).all()
    
    # Calculate summary metrics
    total_time_minutes = sum(a.duration_minutes or 0 for a in analytics)
    lessons_completed = len([a for a in analytics if a.activity_type == "lesson_completion"])
    quizzes_taken = len([a for a in analytics if a.activity_type == "quiz_taken"])
    
    # Calculate average score
    scores = [a.score for a in analytics if a.score is not None]
    average_score = sum(scores) / len(scores) if scores else 0.0
    
    # Get unique subjects
    subjects_studied = list(set(a.subject for a in analytics if a.subject))
    
    # Calculate streak (simplified)
    current_streak_days = 7  # Placeholder
    
    # Get achievements count
    total_achievements = 5  # Placeholder
    
    return schemas.LearningProgressSummary(
        total_time_minutes=total_time_minutes,
        lessons_completed=lessons_completed,
        quizzes_taken=quizzes_taken,
        average_score=average_score,
        subjects_studied=subjects_studied,
        current_streak_days=current_streak_days,
        total_achievements=total_achievements
    )


@router.post("/engagement-metrics", response_model=schemas.EngagementMetrics)
async def create_engagement_metrics(
    metrics: schemas.EngagementMetricsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create engagement metrics entry"""
    db_metrics = models.EngagementMetrics(
        user_id=current_user.id,
        **metrics.dict()
    )
    db.add(db_metrics)
    db.commit()
    db.refresh(db_metrics)
    return db_metrics


@router.get("/engagement-summary", response_model=schemas.EngagementSummary)
async def get_engagement_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's engagement summary"""
    # Get engagement metrics for the last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    metrics = db.query(models.EngagementMetrics).filter(
        and_(
            models.EngagementMetrics.user_id == current_user.id,
            models.EngagementMetrics.date >= thirty_days_ago
        )
    ).all()
    
    # Calculate engagement metrics
    daily_active_days = len(set(m.date.date() for m in metrics))
    weekly_active_days = len(set(m.date.date() for m in metrics if m.date >= datetime.now() - timedelta(days=7)))
    monthly_active_days = len(set(m.date.date() for m in metrics if m.date >= datetime.now() - timedelta(days=30)))
    
    # Calculate average session duration
    total_time = sum(m.time_on_platform_minutes for m in metrics)
    average_session_duration = total_time / len(metrics) if metrics else 0.0
    
    # Find most active subject
    subject_activity = {}
    for m in metrics:
        if m.lessons_completed > 0:
            # This is simplified - in reality you'd track subject per lesson
            subject_activity["math"] = subject_activity.get("math", 0) + m.lessons_completed
    
    most_active_subject = max(subject_activity.keys()) if subject_activity else "general"
    
    # Calculate engagement score
    engagement_score = min(100.0, (daily_active_days / 30.0) * 100)
    
    return schemas.EngagementSummary(
        daily_active_days=daily_active_days,
        weekly_active_days=weekly_active_days,
        monthly_active_days=monthly_active_days,
        average_session_duration=average_session_duration,
        most_active_subject=most_active_subject,
        engagement_score=engagement_score
    )


@router.post("/performance-prediction", response_model=schemas.PerformancePrediction)
async def create_performance_prediction(
    prediction: schemas.PerformancePredictionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create performance prediction"""
    db_prediction = models.PerformancePrediction(
        user_id=current_user.id,
        **prediction.dict()
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction


@router.get("/performance-predictions", response_model=List[schemas.PerformancePrediction])
async def get_performance_predictions(
    subject: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's performance predictions"""
    query = db.query(models.PerformancePrediction).filter(
        models.PerformancePrediction.user_id == current_user.id
    )
    
    if subject:
        query = query.filter(models.PerformancePrediction.subject == subject)
    
    return query.order_by(models.PerformancePrediction.prediction_date.desc()).all()


@router.post("/intervention-recommendation", response_model=schemas.InterventionRecommendation)
async def create_intervention_recommendation(
    recommendation: schemas.InterventionRecommendationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create intervention recommendation"""
    db_recommendation = models.InterventionRecommendation(
        user_id=current_user.id,
        **recommendation.dict()
    )
    db.add(db_recommendation)
    db.commit()
    db.refresh(db_recommendation)
    return db_recommendation


@router.get("/intervention-recommendations", response_model=List[schemas.InterventionRecommendation])
async def get_intervention_recommendations(
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's intervention recommendations"""
    query = db.query(models.InterventionRecommendation).filter(
        models.InterventionRecommendation.user_id == current_user.id
    )
    
    if status:
        query = query.filter(models.InterventionRecommendation.status == status)
    
    return query.order_by(models.InterventionRecommendation.created_at.desc()).all()


@router.post("/ab-test-result", response_model=schemas.ABTestResult)
async def create_ab_test_result(
    result: schemas.ABTestResultCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create A/B test result"""
    db_result = models.ABTestResult(
        user_id=current_user.id,
        **result.dict()
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result


@router.get("/ab-test-results", response_model=List[schemas.ABTestResult])
async def get_ab_test_results(
    test_name: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get A/B test results"""
    query = db.query(models.ABTestResult).filter(
        models.ABTestResult.user_id == current_user.id
    )
    
    if test_name:
        query = query.filter(models.ABTestResult.test_name == test_name)
    
    return query.order_by(models.ABTestResult.created_at.desc()).all()


@router.get("/performance-insights", response_model=schemas.PerformanceInsights)
async def get_performance_insights(
    subject: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI-generated performance insights"""
    # This would typically use ML models to generate insights
    # For now, return placeholder insights
    
    strengths = ["Strong problem-solving skills", "Consistent study habits"]
    areas_for_improvement = ["Time management", "Advanced concepts"]
    recommended_focus_areas = ["Practice exercises", "Concept review"]
    predicted_performance_trend = "improving"
    confidence_in_predictions = 0.85
    
    return schemas.PerformanceInsights(
        strengths=strengths,
        areas_for_improvement=areas_for_improvement,
        recommended_focus_areas=recommended_focus_areas,
        predicted_performance_trend=predicted_performance_trend,
        confidence_in_predictions=confidence_in_predictions
    )


@router.get("/analytics-dashboard")
async def get_analytics_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive analytics dashboard data"""
    # Get learning progress
    progress = await get_learning_progress(db, current_user)
    
    # Get engagement summary
    engagement = await get_engagement_summary(db, current_user)
    
    # Get performance insights
    insights = await get_performance_insights(None, db, current_user)
    
    # Get recent activity
    recent_analytics = db.query(models.LearningAnalytics).filter(
        models.LearningAnalytics.user_id == current_user.id
    ).order_by(models.LearningAnalytics.created_at.desc()).limit(10).all()
    
    return {
        "learning_progress": progress,
        "engagement_summary": engagement,
        "performance_insights": insights,
        "recent_activity": recent_analytics
    }
