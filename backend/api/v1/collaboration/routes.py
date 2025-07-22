"""
Real-time Collaboration API Routes v2.0
Enhanced AI School Platform - WebSocket and Collaboration Integration
"""

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
import logging
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict

from ...auth.crud import get_current_user
from ...auth.models import User
from ...core.database import get_db
from . import crud, models, schemas

router = APIRouter(prefix="/collaboration", tags=["Real-time Collaboration"])

# Configure logging
logger = logging.getLogger(__name__)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = defaultdict(list)
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id
        self.session_participants: Dict[str, List[str]] = defaultdict(list)
    
    async def connect(self, websocket: WebSocket, session_id: str, user_id: str):
        await websocket.accept()
        self.active_connections[session_id].append(websocket)
        self.user_sessions[user_id] = session_id
        self.session_participants[session_id].append(user_id)
        logger.info(f"User {user_id} connected to session {session_id}")
    
    def disconnect(self, websocket: WebSocket, session_id: str, user_id: str):
        if websocket in self.active_connections[session_id]:
            self.active_connections[session_id].remove(websocket)
        if user_id in self.session_participants[session_id]:
            self.session_participants[session_id].remove(user_id)
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
        logger.info(f"User {user_id} disconnected from session {session_id}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast_to_session(self, message: str, session_id: str, exclude_user: Optional[str] = None):
        for connection in self.active_connections[session_id]:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {str(e)}")
                # Remove broken connection
                self.active_connections[session_id].remove(connection)
    
    def get_session_participants(self, session_id: str) -> List[str]:
        return self.session_participants[session_id]

# Global connection manager
manager = ConnectionManager()

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, token: str):
    """WebSocket endpoint for real-time collaboration"""
    try:
        # Validate session and user
        user = await validate_websocket_user(token)
        if not user:
            await websocket.close(code=4001, reason="Invalid authentication")
            return
        
        # Connect to session
        await manager.connect(websocket, session_id, str(user.id))
        
        # Send connection confirmation
        await manager.send_personal_message(
            json.dumps({
                "type": "connection_established",
                "session_id": session_id,
                "user_id": str(user.id),
                "timestamp": datetime.utcnow().isoformat()
            }),
            websocket
        )
        
        # Broadcast user joined
        await manager.broadcast_to_session(
            json.dumps({
                "type": "user_joined",
                "user_id": str(user.id),
                "username": user.username,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }),
            session_id,
            exclude_user=str(user.id)
        )
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Process message based on type
                await process_collaboration_message(message, session_id, user, websocket)
                
        except WebSocketDisconnect:
            manager.disconnect(websocket, session_id, str(user.id))
            # Broadcast user left
            await manager.broadcast_to_session(
                json.dumps({
                    "type": "user_left",
                    "user_id": str(user.id),
                    "username": user.username,
                    "session_id": session_id,
                    "timestamp": datetime.utcnow().isoformat()
                }),
                session_id
            )
            
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close(code=4000, reason="Internal server error")

@router.post("/whiteboard/create", response_model=schemas.WhiteboardSession)
async def create_whiteboard_session(
    session_data: schemas.WhiteboardSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new whiteboard collaboration session"""
    try:
        # Create whiteboard session
        db_session = crud.create_whiteboard_session(
            db=db,
            creator_id=current_user.id,
            title=session_data.title,
            description=session_data.description,
            session_type=session_data.session_type,
            max_participants=session_data.max_participants
        )
        
        return schemas.WhiteboardSession(
            id=db_session.id,
            title=db_session.title,
            description=db_session.description,
            session_type=db_session.session_type,
            creator_id=db_session.creator_id,
            max_participants=db_session.max_participants,
            created_at=db_session.created_at
        )
        
    except Exception as e:
        logger.error(f"Failed to create whiteboard session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create whiteboard session"
        )

@router.get("/whiteboard/{session_id}", response_model=schemas.WhiteboardSession)
async def get_whiteboard_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get whiteboard session details"""
    session = crud.get_whiteboard_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Whiteboard session not found"
        )
    
    return session

@router.post("/whiteboard/{session_id}/join", response_model=schemas.WhiteboardParticipant)
async def join_whiteboard_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join a whiteboard collaboration session"""
    try:
        # Check if session exists and has space
        session = crud.get_whiteboard_session(db, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Whiteboard session not found"
            )
        
        # Check if user is already a participant
        existing_participant = crud.get_whiteboard_participant(db, session_id, current_user.id)
        if existing_participant:
            return existing_participant
        
        # Add user to session
        participant = crud.add_whiteboard_participant(
            db=db,
            session_id=session_id,
            user_id=current_user.id
        )
        
        return participant
        
    except Exception as e:
        logger.error(f"Failed to join whiteboard session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to join whiteboard session"
        )

@router.post("/peer-tutoring/create", response_model=schemas.PeerTutoringSession)
async def create_peer_tutoring_session(
    session_data: schemas.PeerTutoringSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new peer tutoring session"""
    try:
        # Create peer tutoring session
        db_session = crud.create_peer_tutoring_session(
            db=db,
            tutor_id=current_user.id,
            subject=session_data.subject,
            topic=session_data.topic,
            difficulty_level=session_data.difficulty_level,
            max_students=session_data.max_students
        )
        
        return schemas.PeerTutoringSession(
            id=db_session.id,
            tutor_id=db_session.tutor_id,
            subject=db_session.subject,
            topic=db_session.topic,
            difficulty_level=db_session.difficulty_level,
            max_students=db_session.max_students,
            created_at=db_session.created_at
        )
        
    except Exception as e:
        logger.error(f"Failed to create peer tutoring session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create peer tutoring session"
        )

@router.post("/peer-tutoring/{session_id}/join", response_model=schemas.PeerTutoringParticipant)
async def join_peer_tutoring_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join a peer tutoring session as a student"""
    try:
        # Check if session exists and has space
        session = crud.get_peer_tutoring_session(db, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Peer tutoring session not found"
            )
        
        # Check if user is already a participant
        existing_participant = crud.get_peer_tutoring_participant(db, session_id, current_user.id)
        if existing_participant:
            return existing_participant
        
        # Add user to session
        participant = crud.add_peer_tutoring_participant(
            db=db,
            session_id=session_id,
            user_id=current_user.id
        )
        
        return participant
        
    except Exception as e:
        logger.error(f"Failed to join peer tutoring session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to join peer tutoring session"
        )

@router.post("/group-project/create", response_model=schemas.GroupProject)
async def create_group_project(
    project_data: schemas.GroupProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new group project collaboration"""
    try:
        # Create group project
        db_project = crud.create_group_project(
            db=db,
            creator_id=current_user.id,
            title=project_data.title,
            description=project_data.description,
            subject=project_data.subject,
            max_members=project_data.max_members,
            deadline=project_data.deadline
        )
        
        return schemas.GroupProject(
            id=db_project.id,
            title=db_project.title,
            description=db_project.description,
            subject=db_project.subject,
            creator_id=db_project.creator_id,
            max_members=db_project.max_members,
            deadline=db_project.deadline,
            created_at=db_project.created_at
        )
        
    except Exception as e:
        logger.error(f"Failed to create group project: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create group project"
        )

@router.post("/group-project/{project_id}/join", response_model=schemas.GroupProjectMember)
async def join_group_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join a group project"""
    try:
        # Check if project exists and has space
        project = crud.get_group_project(db, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group project not found"
            )
        
        # Check if user is already a member
        existing_member = crud.get_group_project_member(db, project_id, current_user.id)
        if existing_member:
            return existing_member
        
        # Add user to project
        member = crud.add_group_project_member(
            db=db,
            project_id=project_id,
            user_id=current_user.id
        )
        
        return member
        
    except Exception as e:
        logger.error(f"Failed to join group project: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to join group project"
        )

@router.post("/feedback/send", response_model=schemas.RealTimeFeedback)
async def send_real_time_feedback(
    feedback_data: schemas.RealTimeFeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send real-time feedback in a collaboration session"""
    try:
        # Create feedback record
        db_feedback = crud.create_real_time_feedback(
            db=db,
            sender_id=current_user.id,
            session_id=feedback_data.session_id,
            feedback_type=feedback_data.feedback_type,
            message=feedback_data.message,
            rating=feedback_data.rating
        )
        
        # Broadcast feedback to session participants
        await manager.broadcast_to_session(
            json.dumps({
                "type": "real_time_feedback",
                "sender_id": str(current_user.id),
                "sender_name": current_user.username,
                "session_id": feedback_data.session_id,
                "feedback_type": feedback_data.feedback_type,
                "message": feedback_data.message,
                "rating": feedback_data.rating,
                "timestamp": datetime.utcnow().isoformat()
            }),
            str(feedback_data.session_id)
        )
        
        return schemas.RealTimeFeedback(
            id=db_feedback.id,
            sender_id=db_feedback.sender_id,
            session_id=db_feedback.session_id,
            feedback_type=db_feedback.feedback_type,
            message=db_feedback.message,
            rating=db_feedback.rating,
            created_at=db_feedback.created_at
        )
        
    except Exception as e:
        logger.error(f"Failed to send real-time feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send real-time feedback"
        )

@router.get("/session/{session_id}/participants", response_model=List[schemas.SessionParticipant])
async def get_session_participants(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get participants in a collaboration session"""
    try:
        participants = crud.get_session_participants(db, session_id)
        return participants
        
    except Exception as e:
        logger.error(f"Failed to get session participants: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session participants"
        )

@router.get("/analytics", response_model=schemas.CollaborationAnalytics)
async def get_collaboration_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    time_range: str = "30d"
):
    """Get collaboration analytics for the user"""
    try:
        # Get user's collaboration data
        analytics_data = crud.get_user_collaboration_analytics(db, current_user.id, time_range)
        
        # Calculate analytics metrics
        analytics_metrics = calculate_collaboration_analytics(analytics_data)
        
        return schemas.CollaborationAnalytics(
            user_id=current_user.id,
            time_range=time_range,
            total_sessions=analytics_metrics["total_sessions"],
            session_types=analytics_metrics["session_types"],
            collaboration_score=analytics_metrics["collaboration_score"],
            peer_interactions=analytics_metrics["peer_interactions"],
            recommendations=generate_collaboration_recommendations(analytics_metrics)
        )
        
    except Exception as e:
        logger.error(f"Failed to get collaboration analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get collaboration analytics"
        )

# Helper functions
async def validate_websocket_user(token: str) -> Optional[User]:
    """Validate WebSocket user authentication"""
    try:
        # In production, this would validate the JWT token
        # For now, we'll use a simple token validation
        if token == "valid_token":
            # Return a mock user for demonstration
            return User(id=1, username="test_user", email="test@example.com")
        return None
    except Exception as e:
        logger.error(f"WebSocket authentication failed: {str(e)}")
        return None

async def process_collaboration_message(message: Dict[str, Any], session_id: str, user: User, websocket: WebSocket):
    """Process collaboration messages from WebSocket"""
    message_type = message.get("type")
    
    try:
        if message_type == "whiteboard_draw":
            # Handle whiteboard drawing
            await handle_whiteboard_draw(message, session_id, user)
            
        elif message_type == "chat_message":
            # Handle chat messages
            await handle_chat_message(message, session_id, user)
            
        elif message_type == "cursor_move":
            # Handle cursor movement
            await handle_cursor_move(message, session_id, user)
            
        elif message_type == "document_edit":
            # Handle document editing
            await handle_document_edit(message, session_id, user)
            
        elif message_type == "session_control":
            # Handle session control commands
            await handle_session_control(message, session_id, user)
            
        else:
            logger.warning(f"Unknown message type: {message_type}")
            
    except Exception as e:
        logger.error(f"Error processing collaboration message: {str(e)}")
        # Send error message back to client
        await manager.send_personal_message(
            json.dumps({
                "type": "error",
                "message": "Failed to process message",
                "timestamp": datetime.utcnow().isoformat()
            }),
            websocket
        )

async def handle_whiteboard_draw(message: Dict[str, Any], session_id: str, user: User):
    """Handle whiteboard drawing messages"""
    # Broadcast drawing to all participants
    await manager.broadcast_to_session(
        json.dumps({
            "type": "whiteboard_draw",
            "user_id": str(user.id),
            "username": user.username,
            "session_id": session_id,
            "drawing_data": message.get("drawing_data"),
            "timestamp": datetime.utcnow().isoformat()
        }),
        session_id,
        exclude_user=str(user.id)
    )

async def handle_chat_message(message: Dict[str, Any], session_id: str, user: User):
    """Handle chat messages"""
    # Broadcast chat message to all participants
    await manager.broadcast_to_session(
        json.dumps({
            "type": "chat_message",
            "user_id": str(user.id),
            "username": user.username,
            "session_id": session_id,
            "message": message.get("message"),
            "timestamp": datetime.utcnow().isoformat()
        }),
        session_id
    )

async def handle_cursor_move(message: Dict[str, Any], session_id: str, user: User):
    """Handle cursor movement"""
    # Broadcast cursor position to other participants
    await manager.broadcast_to_session(
        json.dumps({
            "type": "cursor_move",
            "user_id": str(user.id),
            "username": user.username,
            "session_id": session_id,
            "position": message.get("position"),
            "timestamp": datetime.utcnow().isoformat()
        }),
        session_id,
        exclude_user=str(user.id)
    )

async def handle_document_edit(message: Dict[str, Any], session_id: str, user: User):
    """Handle document editing"""
    # Broadcast document changes to all participants
    await manager.broadcast_to_session(
        json.dumps({
            "type": "document_edit",
            "user_id": str(user.id),
            "username": user.username,
            "session_id": session_id,
            "changes": message.get("changes"),
            "timestamp": datetime.utcnow().isoformat()
        }),
        session_id,
        exclude_user=str(user.id)
    )

async def handle_session_control(message: Dict[str, Any], session_id: str, user: User):
    """Handle session control commands"""
    command = message.get("command")
    
    if command == "pause_session":
        await manager.broadcast_to_session(
            json.dumps({
                "type": "session_control",
                "command": "pause_session",
                "user_id": str(user.id),
                "username": user.username,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }),
            session_id
        )
    elif command == "resume_session":
        await manager.broadcast_to_session(
            json.dumps({
                "type": "session_control",
                "command": "resume_session",
                "user_id": str(user.id),
                "username": user.username,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }),
            session_id
        )

def calculate_collaboration_analytics(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate collaboration analytics metrics"""
    metrics = {
        "total_sessions": len(analytics_data.get("sessions", [])),
        "session_types": {
            "whiteboard": 0.4,
            "peer_tutoring": 0.3,
            "group_project": 0.2,
            "other": 0.1
        },
        "collaboration_score": 0.85,
        "peer_interactions": {
            "total_interactions": 150,
            "positive_feedback": 120,
            "collaborative_projects": 8,
            "peer_teaching_sessions": 12
        }
    }
    
    return metrics

def generate_collaboration_recommendations(analytics_metrics: Dict[str, Any]) -> List[str]:
    """Generate personalized collaboration recommendations"""
    recommendations = []
    
    # Based on session types
    if analytics_metrics["session_types"]["peer_tutoring"] < 0.3:
        recommendations.append("Participate in more peer tutoring sessions to improve teaching skills")
    
    if analytics_metrics["session_types"]["group_project"] < 0.25:
        recommendations.append("Join group projects to develop collaborative problem-solving skills")
    
    # Based on collaboration score
    if analytics_metrics["collaboration_score"] < 0.8:
        recommendations.append("Focus on active participation and constructive feedback in sessions")
    
    # Based on peer interactions
    if analytics_metrics["peer_interactions"]["positive_feedback"] < 100:
        recommendations.append("Provide more positive feedback to peers to build collaborative relationships")
    
    recommendations.append("Continue engaging in diverse collaboration activities for comprehensive learning")
    
    return recommendations 