from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Set, Dict, Any
from main.database import get_db
from main.api.v1.auth.crud import get_current_user
from main.api.v1.auth.models import User
from . import models, schemas, services

router = APIRouter(prefix="/knowledge-graph", tags=["Knowledge Graph"])


@router.post("/concepts", response_model=schemas.Concept)
async def create_concept(
    concept: schemas.ConceptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new concept in the knowledge graph"""
    db_concept = models.Concept(**concept.dict())
    db.add(db_concept)
    db.commit()
    db.refresh(db_concept)
    return db_concept


@router.get("/concepts", response_model=List[schemas.Concept])
async def get_concepts(
    subject: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get concepts from the knowledge graph"""
    query = db.query(models.Concept)
    if subject:
        query = query.filter(models.Concept.subject == subject)
    return query.all()


@router.post("/concept-relationships", response_model=schemas.ConceptRelationship)
async def create_concept_relationship(
    relationship: schemas.ConceptRelationshipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a relationship between concepts"""
    db_relationship = models.ConceptRelationship(**relationship.dict())
    db.add(db_relationship)
    db.commit()
    db.refresh(db_relationship)
    return db_relationship


@router.get("/learning-path/{subject}", response_model=List[Dict[str, Any]])
async def get_learning_path(
    subject: str,
    target_concepts: Set[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get personalized learning path for user"""
    return await services.knowledge_graph_service.find_learning_path(
        db, current_user.id, subject, target_concepts
    )


@router.get("/knowledge-gaps/{subject}", response_model=List[Dict[str, Any]])
async def get_knowledge_gaps(
    subject: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Identify knowledge gaps for user in a subject"""
    return await services.knowledge_graph_service.identify_knowledge_gaps(
        db, current_user.id, subject
    )


@router.get("/recommendations/{subject}", response_model=List[Dict[str, Any]])
async def get_concept_recommendations(
    subject: str,
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recommended next concepts for user"""
    return await services.knowledge_graph_service.recommend_next_concepts(
        db, current_user.id, subject, limit
    )


@router.get("/learning-style-analysis", response_model=Dict[str, Any])
async def analyze_learning_style(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze user's learning style"""
    return await services.knowledge_graph_service.analyze_learning_style(
        db, current_user.id
    )


@router.post("/concept-mastery", response_model=schemas.ConceptMastery)
async def create_concept_mastery(
    mastery: schemas.ConceptMasteryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or update concept mastery for user"""
    # Check if mastery record already exists
    existing_mastery = db.query(models.ConceptMastery).filter(
        models.ConceptMastery.user_id == current_user.id,
        models.ConceptMastery.concept_id == mastery.concept_id
    ).first()
    
    if existing_mastery:
        # Update existing record
        for field, value in mastery.dict(exclude_unset=True).items():
            setattr(existing_mastery, field, value)
        existing_mastery.assessment_count += 1
        db.commit()
        db.refresh(existing_mastery)
        return existing_mastery
    else:
        # Create new record
        db_mastery = models.ConceptMastery(
            user_id=current_user.id,
            **mastery.dict()
        )
        db.add(db_mastery)
        db.commit()
        db.refresh(db_mastery)
        return db_mastery


@router.get("/concept-mastery", response_model=List[schemas.ConceptMastery])
async def get_user_concept_mastery(
    subject: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's concept mastery levels"""
    query = db.query(models.ConceptMastery).filter(
        models.ConceptMastery.user_id == current_user.id
    )
    
    if subject:
        query = query.join(models.Concept).filter(models.Concept.subject == subject)
    
    return query.all()


@router.get("/subject-graph/{subject}")
async def get_subject_graph(
    subject: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get knowledge graph for a specific subject"""
    graph = await services.knowledge_graph_service.build_subject_graph(db, subject)
    
    # Convert NetworkX graph to JSON-serializable format
    graph_data = {
        "nodes": [],
        "edges": []
    }
    
    for node, data in graph.nodes(data=True):
        graph_data["nodes"].append({
            "id": node,
            "name": data.get("name", ""),
            "description": data.get("description", ""),
            "difficulty_level": data.get("difficulty_level", 1),
            "subject": data.get("subject", "")
        })
    
    for source, target, data in graph.edges(data=True):
        graph_data["edges"].append({
            "source": source,
            "target": target,
            "relationship_type": data.get("relationship_type", ""),
            "strength": data.get("strength", 1.0)
        })
    
    return graph_data


@router.post("/learning-paths", response_model=schemas.LearningPath)
async def create_learning_path(
    learning_path: schemas.LearningPathCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a personalized learning path for user"""
    db_learning_path = models.LearningPath(
        user_id=current_user.id,
        **learning_path.dict()
    )
    db.add(db_learning_path)
    db.commit()
    db.refresh(db_learning_path)
    return db_learning_path


@router.get("/learning-paths", response_model=List[schemas.LearningPath])
async def get_user_learning_paths(
    subject: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's learning paths"""
    query = db.query(models.LearningPath).filter(
        models.LearningPath.user_id == current_user.id
    )
    
    if subject:
        query = query.filter(models.LearningPath.subject == subject)
    
    return query.all()


@router.put("/learning-paths/{path_id}", response_model=schemas.LearningPath)
async def update_learning_path(
    path_id: int,
    learning_path_update: schemas.LearningPathCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a learning path"""
    db_learning_path = db.query(models.LearningPath).filter(
        models.LearningPath.id == path_id,
        models.LearningPath.user_id == current_user.id
    ).first()
    
    if not db_learning_path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    
    for field, value in learning_path_update.dict(exclude_unset=True).items():
        setattr(db_learning_path, field, value)
    
    db.commit()
    db.refresh(db_learning_path)
    return db_learning_path 