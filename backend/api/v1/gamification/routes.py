"""
Gamification API Routes v2.0
Enhanced AI School Platform - Gamification and Engagement System
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
import logging
import random
from datetime import datetime, timedelta

from ...auth.crud import get_current_user
from ...auth.models import User
from ...core.database import get_db
from . import crud, models, schemas

router = APIRouter(prefix="/gamification", tags=["Gamification"])

# Configure logging
logger = logging.getLogger(__name__)

# Achievement definitions
ACHIEVEMENTS = {
    "first_lesson": {
        "id": "first_lesson",
        "name": "First Steps",
        "description": "Complete your first lesson",
        "points": 50,
        "icon": "🎯",
        "category": "learning"
    },
    "streak_7": {
        "id": "streak_7",
        "name": "Week Warrior",
        "description": "Maintain a 7-day learning streak",
        "points": 100,
        "icon": "🔥",
        "category": "consistency"
    },
    "streak_30": {
        "id": "streak_30",
        "name": "Monthly Master",
        "description": "Maintain a 30-day learning streak",
        "points": 500,
        "icon": "👑",
        "category": "consistency"
    },
    "perfect_score": {
        "id": "perfect_score",
        "name": "Perfect Score",
        "description": "Get 100% on any assessment",
        "points": 200,
        "icon": "⭐",
        "category": "excellence"
    },
    "collaborator": {
        "id": "collaborator",
        "name": "Team Player",
        "description": "Participate in 5 collaborative sessions",
        "points": 150,
        "icon": "🤝",
        "category": "collaboration"
    },
    "multimodal_explorer": {
        "id": "multimodal_explorer",
        "name": "Multimodal Explorer",
        "description": "Use all learning modalities in one session",
        "points": 120,
        "icon": "🎨",
        "category": "innovation"
    },
    "ai_literacy_expert": {
        "id": "ai_literacy_expert",
        "name": "AI Literacy Expert",
        "description": "Complete all AI4K12 big ideas assessments",
        "points": 300,
        "icon": "🧠",
        "category": "expertise"
    },
    "helpful_peer": {
        "id": "helpful_peer",
        "name": "Helpful Peer",
        "description": "Receive 10 positive feedback ratings",
        "points": 180,
        "icon": "💡",
        "category": "community"
    }
}

# Educational games
EDUCATIONAL_GAMES = {
    "ai_concept_matching": {
        "id": "ai_concept_matching",
        "name": "AI Concept Matching",
        "description": "Match AI concepts with their definitions",
        "difficulty_levels": ["beginner", "intermediate", "advanced"],
        "points_per_correct": 10,
        "max_points": 100
    },
    "code_debugging": {
        "id": "code_debugging",
        "name": "Code Debugging Challenge",
        "description": "Find and fix bugs in code snippets",
        "difficulty_levels": ["beginner", "intermediate", "advanced"],
        "points_per_correct": 15,
        "max_points": 150
    },
    "math_puzzle": {
        "id": "math_puzzle",
        "name": "Mathematical Puzzles",
        "description": "Solve mathematical problems with AI assistance",
        "difficulty_levels": ["beginner", "intermediate", "advanced"],
        "points_per_correct": 12,
        "max_points": 120
    },
    "language_learning": {
        "id": "language_learning",
        "name": "Language Learning Game",
        "description": "Practice language skills with AI conversation",
        "difficulty_levels": ["beginner", "intermediate", "advanced"],
        "points_per_correct": 8,
        "max_points": 80
    }
}

@router.post("/achievements/award", response_model=schemas.AchievementAward)
async def award_achievement(
    achievement_request: schemas.AchievementAwardRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Award an achievement to a user"""
    try:
        # Check if achievement exists
        if achievement_request.achievement_id not in ACHIEVEMENTS:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Achievement not found"
            )
        
        # Check if user already has this achievement
        existing_achievement = crud.get_user_achievement(
            db, current_user.id, achievement_request.achievement_id
        )
        if existing_achievement:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has this achievement"
            )
        
        # Award achievement
        achievement_data = ACHIEVEMENTS[achievement_request.achievement_id]
        db_achievement = crud.award_achievement(
            db=db,
            user_id=current_user.id,
            achievement_id=achievement_request.achievement_id,
            points=achievement_data["points"],
            context=achievement_request.context
        )
        
        # Update user points
        crud.update_user_points(db, current_user.id, achievement_data["points"])
        
        return schemas.AchievementAward(
            id=db_achievement.id,
            user_id=current_user.id,
            achievement_id=achievement_request.achievement_id,
            achievement_name=achievement_data["name"],
            achievement_description=achievement_data["description"],
            points_awarded=achievement_data["points"],
            icon=achievement_data["icon"],
            category=achievement_data["category"],
            awarded_at=db_achievement.awarded_at
        )
        
    except Exception as e:
        logger.error(f"Failed to award achievement: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to award achievement"
        )

@router.get("/achievements/user", response_model=List[schemas.UserAchievement])
async def get_user_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all achievements for the current user"""
    try:
        achievements = crud.get_user_achievements(db, current_user.id)
        return achievements
        
    except Exception as e:
        logger.error(f"Failed to get user achievements: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user achievements"
        )

@router.get("/achievements/available", response_model=List[Dict[str, Any]])
async def get_available_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all available achievements with user progress"""
    try:
        user_achievements = crud.get_user_achievements(db, current_user.id)
        user_achievement_ids = {a.achievement_id for a in user_achievements}
        
        available_achievements = []
        for achievement_id, achievement_data in ACHIEVEMENTS.items():
            available_achievements.append({
                **achievement_data,
                "unlocked": achievement_id in user_achievement_ids,
                "unlocked_at": next((a.awarded_at for a in user_achievements if a.achievement_id == achievement_id), None)
            })
        
        return available_achievements
        
    except Exception as e:
        logger.error(f"Failed to get available achievements: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available achievements"
        )

@router.get("/leaderboard", response_model=schemas.Leaderboard)
async def get_leaderboard(
    leaderboard_type: str = "points",
    time_range: str = "all_time",
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get leaderboard rankings"""
    try:
        # Get leaderboard data
        leaderboard_data = crud.get_leaderboard(
            db, leaderboard_type, time_range, limit
        )
        
        # Get user's position
        user_position = crud.get_user_leaderboard_position(
            db, current_user.id, leaderboard_type, time_range
        )
        
        return schemas.Leaderboard(
            leaderboard_type=leaderboard_type,
            time_range=time_range,
            rankings=leaderboard_data,
            user_position=user_position,
            total_participants=len(leaderboard_data)
        )
        
    except Exception as e:
        logger.error(f"Failed to get leaderboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get leaderboard"
        )

@router.post("/games/start", response_model=schemas.GameSession)
async def start_educational_game(
    game_request: schemas.GameSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start an educational game session"""
    try:
        # Check if game exists
        if game_request.game_id not in EDUCATIONAL_GAMES:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Game not found"
            )
        
        # Generate game content
        game_data = EDUCATIONAL_GAMES[game_request.game_id]
        game_content = generate_game_content(game_request.game_id, game_request.difficulty_level)
        
        # Create game session
        db_session = crud.create_game_session(
            db=db,
            user_id=current_user.id,
            game_id=game_request.game_id,
            difficulty_level=game_request.difficulty_level,
            content=game_content
        )
        
        return schemas.GameSession(
            id=db_session.id,
            game_id=game_request.game_id,
            game_name=game_data["name"],
            difficulty_level=game_request.difficulty_level,
            content=game_content,
            max_points=game_data["max_points"],
            started_at=db_session.started_at
        )
        
    except Exception as e:
        logger.error(f"Failed to start educational game: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start educational game"
        )

@router.post("/games/{session_id}/submit", response_model=schemas.GameResult)
async def submit_game_result(
    session_id: int,
    game_result: schemas.GameResultSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit game results and calculate rewards"""
    try:
        # Get game session
        game_session = crud.get_game_session(db, session_id, current_user.id)
        if not game_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Game session not found"
            )
        
        # Calculate score and rewards
        game_data = EDUCATIONAL_GAMES[game_session.game_id]
        score_result = calculate_game_score(game_result.answers, game_session.content)
        points_earned = calculate_points_earned(score_result["score"], game_data["max_points"], game_data["points_per_correct"])
        
        # Create game result
        db_result = crud.create_game_result(
            db=db,
            session_id=session_id,
            user_id=current_user.id,
            score=score_result["score"],
            points_earned=points_earned,
            time_taken=game_result.time_taken,
            answers=game_result.answers
        )
        
        # Update user points
        crud.update_user_points(db, current_user.id, points_earned)
        
        # Check for achievements
        check_and_award_achievements(db, current_user.id, game_session.game_id, score_result["score"])
        
        return schemas.GameResult(
            id=db_result.id,
            game_id=game_session.game_id,
            score=score_result["score"],
            points_earned=points_earned,
            time_taken=game_result.time_taken,
            feedback=score_result["feedback"],
            completed_at=db_result.completed_at
        )
        
    except Exception as e:
        logger.error(f"Failed to submit game result: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit game result"
        )

@router.get("/rewards/balance", response_model=schemas.UserRewards)
async def get_user_rewards(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's reward balance and history"""
    try:
        # Get user's reward data
        reward_data = crud.get_user_rewards(db, current_user.id)
        
        return schemas.UserRewards(
            user_id=current_user.id,
            total_points=reward_data["total_points"],
            current_level=calculate_user_level(reward_data["total_points"]),
            points_to_next_level=calculate_points_to_next_level(reward_data["total_points"]),
            recent_earnings=reward_data["recent_earnings"],
            reward_history=reward_data["reward_history"]
        )
        
    except Exception as e:
        logger.error(f"Failed to get user rewards: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user rewards"
        )

@router.post("/rewards/redeem", response_model=schemas.RewardRedemption)
async def redeem_reward(
    redemption_request: schemas.RewardRedemptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Redeem points for rewards"""
    try:
        # Check if user has enough points
        user_points = crud.get_user_points(db, current_user.id)
        if user_points < redemption_request.points_cost:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient points for redemption"
            )
        
        # Process redemption
        db_redemption = crud.create_reward_redemption(
            db=db,
            user_id=current_user.id,
            reward_type=redemption_request.reward_type,
            reward_description=redemption_request.reward_description,
            points_cost=redemption_request.points_cost
        )
        
        # Deduct points
        crud.update_user_points(db, current_user.id, -redemption_request.points_cost)
        
        return schemas.RewardRedemption(
            id=db_redemption.id,
            user_id=current_user.id,
            reward_type=redemption_request.reward_type,
            reward_description=redemption_request.reward_description,
            points_cost=redemption_request.points_cost,
            redeemed_at=db_redemption.redeemed_at
        )
        
    except Exception as e:
        logger.error(f"Failed to redeem reward: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to redeem reward"
        )

@router.get("/challenges/daily", response_model=schemas.DailyChallenge)
async def get_daily_challenge(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get today's daily challenge"""
    try:
        # Get or create daily challenge
        challenge = crud.get_daily_challenge(db, current_user.id)
        if not challenge:
            challenge = crud.create_daily_challenge(db, current_user.id)
        
        return challenge
        
    except Exception as e:
        logger.error(f"Failed to get daily challenge: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get daily challenge"
        )

@router.post("/challenges/daily/complete", response_model=schemas.ChallengeCompletion)
async def complete_daily_challenge(
    completion_data: schemas.DailyChallengeCompletion,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete the daily challenge"""
    try:
        # Verify challenge completion
        challenge = crud.get_daily_challenge(db, current_user.id)
        if not challenge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Daily challenge not found"
            )
        
        # Validate completion
        if not validate_challenge_completion(completion_data, challenge):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Challenge completion validation failed"
            )
        
        # Complete challenge
        db_completion = crud.complete_daily_challenge(
            db=db,
            user_id=current_user.id,
            challenge_id=challenge.id,
            completion_data=completion_data.completion_data
        )
        
        # Award points
        points_earned = 50  # Daily challenge reward
        crud.update_user_points(db, current_user.id, points_earned)
        
        return schemas.ChallengeCompletion(
            id=db_completion.id,
            challenge_id=challenge.id,
            points_earned=points_earned,
            completed_at=db_completion.completed_at
        )
        
    except Exception as e:
        logger.error(f"Failed to complete daily challenge: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete daily challenge"
        )

@router.get("/progress", response_model=schemas.GamificationProgress)
async def get_gamification_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's gamification progress and statistics"""
    try:
        # Get user's gamification data
        progress_data = crud.get_user_gamification_progress(db, current_user.id)
        
        # Calculate progress metrics
        progress_metrics = calculate_gamification_progress(progress_data)
        
        return schemas.GamificationProgress(
            user_id=current_user.id,
            total_points=progress_metrics["total_points"],
            current_level=progress_metrics["current_level"],
            achievements_unlocked=progress_metrics["achievements_unlocked"],
            games_completed=progress_metrics["games_completed"],
            challenges_completed=progress_metrics["challenges_completed"],
            streak_days=progress_metrics["streak_days"],
            leaderboard_rank=progress_metrics["leaderboard_rank"],
            next_milestones=generate_next_milestones(progress_metrics)
        )
        
    except Exception as e:
        logger.error(f"Failed to get gamification progress: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get gamification progress"
        )

# Helper functions
def generate_game_content(game_id: str, difficulty_level: str) -> Dict[str, Any]:
    """Generate game content based on game type and difficulty"""
    if game_id == "ai_concept_matching":
        return {
            "concepts": [
                {"term": "Machine Learning", "definition": "AI that learns from data"},
                {"term": "Neural Network", "definition": "AI model inspired by brain structure"},
                {"term": "Natural Language Processing", "definition": "AI for understanding human language"}
            ],
            "difficulty": difficulty_level,
            "time_limit": 300 if difficulty_level == "beginner" else 180
        }
    elif game_id == "code_debugging":
        return {
            "code_snippets": [
                {"code": "print('Hello World')", "bug": None},
                {"code": "x = 5\nprint(x", "bug": "Missing closing parenthesis"},
                {"code": "for i in range(10):\n    print(i)", "bug": None}
            ],
            "difficulty": difficulty_level,
            "time_limit": 600 if difficulty_level == "beginner" else 300
        }
    else:
        return {"content": "Game content", "difficulty": difficulty_level}

def calculate_game_score(answers: Dict[str, Any], content: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate game score based on answers"""
    total_questions = len(content.get("concepts", [])) + len(content.get("code_snippets", []))
    correct_answers = sum(1 for answer in answers.values() if answer.get("correct", False))
    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    return {
        "score": score,
        "correct_answers": correct_answers,
        "total_questions": total_questions,
        "feedback": generate_game_feedback(score, correct_answers, total_questions)
    }

def calculate_points_earned(score: float, max_points: int, points_per_correct: int) -> int:
    """Calculate points earned based on score"""
    return int((score / 100) * max_points)

def check_and_award_achievements(db: Session, user_id: int, game_id: str, score: float):
    """Check and award achievements based on game performance"""
    try:
        # Check for perfect score achievement
        if score >= 100:
            achievement_request = schemas.AchievementAwardRequest(
                achievement_id="perfect_score",
                context={"game_id": game_id, "score": score}
            )
            crud.award_achievement(db, user_id, "perfect_score", 200, achievement_request.context)
            
    except Exception as e:
        logger.error(f"Error checking achievements: {str(e)}")

def calculate_user_level(total_points: int) -> int:
    """Calculate user level based on total points"""
    return (total_points // 1000) + 1

def calculate_points_to_next_level(total_points: int) -> int:
    """Calculate points needed for next level"""
    current_level = calculate_user_level(total_points)
    points_for_next_level = current_level * 1000
    return max(0, points_for_next_level - total_points)

def validate_challenge_completion(completion_data: schemas.DailyChallengeCompletion, challenge: schemas.DailyChallenge) -> bool:
    """Validate daily challenge completion"""
    # Simple validation - in production, this would be more sophisticated
    return completion_data.completion_data is not None

def calculate_gamification_progress(progress_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate gamification progress metrics"""
    metrics = {
        "total_points": progress_data.get("total_points", 0),
        "current_level": calculate_user_level(progress_data.get("total_points", 0)),
        "achievements_unlocked": len(progress_data.get("achievements", [])),
        "games_completed": len(progress_data.get("game_results", [])),
        "challenges_completed": len(progress_data.get("challenge_completions", [])),
        "streak_days": progress_data.get("current_streak", 0),
        "leaderboard_rank": progress_data.get("leaderboard_rank", 0)
    }
    
    return metrics

def generate_next_milestones(progress_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate next milestones for the user"""
    milestones = []
    
    # Level milestone
    current_level = progress_metrics["current_level"]
    next_level_points = current_level * 1000
    milestones.append({
        "type": "level_up",
        "description": f"Reach Level {current_level + 1}",
        "progress": progress_metrics["total_points"],
        "target": next_level_points,
        "reward": f"{current_level * 100} points"
    })
    
    # Achievement milestone
    current_achievements = progress_metrics["achievements_unlocked"]
    next_achievement_target = min(current_achievements + 3, len(ACHIEVEMENTS))
    milestones.append({
        "type": "achievement",
        "description": f"Unlock {next_achievement_target} achievements",
        "progress": current_achievements,
        "target": next_achievement_target,
        "reward": "50 points per achievement"
    })
    
    # Streak milestone
    current_streak = progress_metrics["streak_days"]
    next_streak_target = current_streak + 7
    milestones.append({
        "type": "streak",
        "description": f"Maintain {next_streak_target}-day learning streak",
        "progress": current_streak,
        "target": next_streak_target,
        "reward": "100 points"
    })
    
    return milestones 