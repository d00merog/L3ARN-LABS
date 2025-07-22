from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from main.database import get_db
from main.api.v1.auth.crud import get_current_user
from main.api.v1.auth.models import User
from . import crud, schemas

router = APIRouter(prefix="/ai-literacy", tags=["AI Literacy"])


@router.post("/assessment", response_model=schemas.AILiteracyAssessment)
async def create_ai_literacy_assessment(
    assessment: schemas.AILiteracyAssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new AI literacy assessment"""
    return crud.create_ai_literacy_assessment(db, assessment, current_user.id)


@router.get("/assessment/{assessment_type}", response_model=List[schemas.AILiteracyAssessment])
async def get_user_assessments(
    assessment_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's AI literacy assessments by type"""
    assessments = crud.get_user_ai_literacy_assessments(db, current_user.id)
    return [a for a in assessments if a.assessment_type == assessment_type]


@router.get("/progress", response_model=schemas.AILiteracyProgress)
async def get_ai_literacy_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's AI literacy progress across all Big Ideas"""
    return crud.get_ai_literacy_progress(db, current_user.id)


@router.post("/ethics-training", response_model=schemas.AIEthicsTraining)
async def create_ai_ethics_training(
    training: schemas.AIEthicsTrainingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new AI ethics training record"""
    return crud.create_ai_ethics_training(db, training, current_user.id)


@router.put("/ethics-training/{training_id}", response_model=schemas.AIEthicsTraining)
async def update_ai_ethics_training(
    training_id: int,
    training_update: schemas.AIEthicsTrainingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an AI ethics training record"""
    return crud.update_ai_ethics_training(db, training_id, training_update)


@router.get("/ethics-progress", response_model=schemas.AIEthicsProgress)
async def get_ai_ethics_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's AI ethics training progress"""
    return crud.get_ai_ethics_progress(db, current_user.id)


@router.post("/transparency-log", response_model=schemas.AITransparencyLog)
async def create_ai_transparency_log(
    log: schemas.AITransparencyLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new AI transparency log entry"""
    return crud.create_ai_transparency_log(db, log, current_user.id)


@router.get("/transparency-logs", response_model=List[schemas.AITransparencyLog])
async def get_ai_transparency_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's recent AI transparency logs"""
    return crud.get_user_ai_transparency_logs(db, current_user.id, limit)


@router.get("/big-ideas-assessment/{idea_type}")
async def get_big_ideas_assessment(
    idea_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI4K12 Big Ideas assessment questions"""
    # AI4K12 Big Ideas assessment questions
    assessments = {
        "perception": {
            "title": "AI Perception",
            "description": "How AI perceives and understands the world",
            "questions": [
                {
                    "id": 1,
                    "question": "How does AI 'see' and process visual information?",
                    "type": "multiple_choice",
                    "options": [
                        "Through cameras and image processing",
                        "By reading text descriptions",
                        "Through human observation",
                        "By guessing randomly"
                    ],
                    "correct_answer": 0
                },
                {
                    "id": 2,
                    "question": "What is computer vision?",
                    "type": "multiple_choice",
                    "options": [
                        "AI's ability to process and analyze visual information",
                        "Human vision enhanced by computers",
                        "A type of camera technology",
                        "A programming language"
                    ],
                    "correct_answer": 0
                }
            ]
        },
        "representation": {
            "title": "AI Representation & Reasoning",
            "description": "How AI represents knowledge and makes decisions",
            "questions": [
                {
                    "id": 1,
                    "question": "How does AI represent knowledge?",
                    "type": "multiple_choice",
                    "options": [
                        "Through mathematical models and data structures",
                        "By writing essays",
                        "Through physical objects",
                        "By memorizing everything"
                    ],
                    "correct_answer": 0
                }
            ]
        },
        "learning": {
            "title": "AI Learning",
            "description": "How AI learns from data and improves over time",
            "questions": [
                {
                    "id": 1,
                    "question": "What is machine learning?",
                    "type": "multiple_choice",
                    "options": [
                        "AI systems that improve through experience",
                        "Humans learning from machines",
                        "A type of computer hardware",
                        "A programming technique"
                    ],
                    "correct_answer": 0
                }
            ]
        },
        "interaction": {
            "title": "Natural Interaction",
            "description": "How AI communicates with humans",
            "questions": [
                {
                    "id": 1,
                    "question": "How does AI understand human language?",
                    "type": "multiple_choice",
                    "options": [
                        "Through natural language processing",
                        "By reading minds",
                        "Through telepathy",
                        "By guessing"
                    ],
                    "correct_answer": 0
                }
            ]
        },
        "societal": {
            "title": "Societal Impact",
            "description": "How AI affects society and ethical considerations",
            "questions": [
                {
                    "id": 1,
                    "question": "What is AI bias?",
                    "type": "multiple_choice",
                    "options": [
                        "Unfair treatment based on training data",
                        "AI being mean to humans",
                        "A type of computer error",
                        "A programming bug"
                    ],
                    "correct_answer": 0
                }
            ]
        }
    }
    
    if idea_type not in assessments:
        raise HTTPException(status_code=404, detail="Assessment type not found")
    
    return assessments[idea_type] 