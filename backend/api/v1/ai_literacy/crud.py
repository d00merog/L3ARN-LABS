from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from . import models, schemas


def create_ai_literacy_assessment(db: Session, assessment: schemas.AILiteracyAssessmentCreate, user_id: int):
    """Create a new AI literacy assessment"""
    db_assessment = models.AILiteracyAssessment(
        user_id=user_id,
        assessment_type=assessment.assessment_type,
        score=assessment.score,
        max_score=assessment.max_score,
        responses=assessment.responses
    )
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    return db_assessment


def get_user_ai_literacy_assessments(db: Session, user_id: int) -> List[models.AILiteracyAssessment]:
    """Get all AI literacy assessments for a user"""
    return db.query(models.AILiteracyAssessment).filter(
        models.AILiteracyAssessment.user_id == user_id
    ).all()


def get_ai_literacy_progress(db: Session, user_id: int) -> schemas.AILiteracyProgress:
    """Calculate user's AI literacy progress across all Big Ideas"""
    assessments = get_user_ai_literacy_assessments(db, user_id)
    
    # Calculate scores for each Big Idea
    scores = {
        'perception': 0.0,
        'representation': 0.0,
        'learning': 0.0,
        'interaction': 0.0,
        'societal': 0.0
    }
    
    for assessment in assessments:
        if assessment.assessment_type in scores:
            scores[assessment.assessment_type] = assessment.score / assessment.max_score * 100
    
    overall_score = sum(scores.values()) / len(scores)
    
    return schemas.AILiteracyProgress(
        perception_score=scores['perception'],
        representation_score=scores['representation'],
        learning_score=scores['learning'],
        interaction_score=scores['interaction'],
        societal_score=scores['societal'],
        overall_score=overall_score,
        completed_assessments=len(assessments),
        total_assessments=5  # Five Big Ideas
    )


def create_ai_ethics_training(db: Session, training: schemas.AIEthicsTrainingCreate, user_id: int):
    """Create a new AI ethics training record"""
    db_training = models.AIEthicsTraining(
        user_id=user_id,
        training_type=training.training_type,
        completion_status=training.completion_status,
        score=training.score
    )
    db.add(db_training)
    db.commit()
    db.refresh(db_training)
    return db_training


def update_ai_ethics_training(db: Session, training_id: int, training_update: schemas.AIEthicsTrainingCreate):
    """Update an AI ethics training record"""
    db_training = db.query(models.AIEthicsTraining).filter(
        models.AIEthicsTraining.id == training_id
    ).first()
    
    if db_training:
        for field, value in training_update.dict(exclude_unset=True).items():
            setattr(db_training, field, value)
        
        db.commit()
        db.refresh(db_training)
    
    return db_training


def get_ai_ethics_progress(db: Session, user_id: int) -> schemas.AIEthicsProgress:
    """Get user's AI ethics training progress"""
    trainings = db.query(models.AIEthicsTraining).filter(
        models.AIEthicsTraining.user_id == user_id
    ).all()
    
    progress = {
        'bias_detection_completed': False,
        'fairness_completed': False,
        'transparency_completed': False,
        'privacy_completed': False
    }
    
    total_score = 0
    completed_count = 0
    
    for training in trainings:
        if training.training_type in progress:
            progress[f"{training.training_type}_completed"] = (
                training.completion_status == "completed"
            )
            if training.score:
                total_score += training.score
                completed_count += 1
    
    overall_ethics_score = total_score / completed_count if completed_count > 0 else 0
    
    return schemas.AIEthicsProgress(
        bias_detection_completed=progress['bias_detection_completed'],
        fairness_completed=progress['fairness_completed'],
        transparency_completed=progress['transparency_completed'],
        privacy_completed=progress['privacy_completed'],
        overall_ethics_score=overall_ethics_score
    )


def create_ai_transparency_log(db: Session, log: schemas.AITransparencyLogCreate, user_id: int):
    """Create a new AI transparency log entry"""
    db_log = models.AITransparencyLog(
        user_id=user_id,
        ai_agent_type=log.ai_agent_type,
        decision_type=log.decision_type,
        input_data=log.input_data,
        output_data=log.output_data,
        confidence_score=log.confidence_score,
        reasoning=log.reasoning
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_user_ai_transparency_logs(db: Session, user_id: int, limit: int = 50) -> List[models.AITransparencyLog]:
    """Get recent AI transparency logs for a user"""
    return db.query(models.AITransparencyLog).filter(
        models.AITransparencyLog.user_id == user_id
    ).order_by(models.AITransparencyLog.created_at.desc()).limit(limit).all() 