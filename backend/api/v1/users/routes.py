from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ...core.database import get_async_db
from . import schemas, crud, models
from ..auth import crud as auth_crud
from ..courses import schemas as course_schemas
from ...memory.adaptive_learning.learning_path import AdaptiveLearningPath
from sqlalchemy import select
from ..gamification.utils import check_achievements, get_daily_challenge, complete_daily_challenge, calculate_xp_for_next_level
from .crud import ProfileManager

router = APIRouter()
adaptive_learning_path = AdaptiveLearningPath()

@router.get("/", response_model=List[schemas.User])
async def get_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_async_db)):
    users = await crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=schemas.User)
async def get_user(user_id: int, db: AsyncSession = Depends(get_async_db)):
    db_user = await crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=schemas.User)
async def update_user(user_id: int, user: schemas.UserUpdate, db: AsyncSession = Depends(get_async_db)):
    db_user = await crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return await crud.update_user(db, db_user, user)

@router.get("/me/dashboard", response_model=schemas.UserDashboard)
async def get_user_dashboard(
    db: AsyncSession = Depends(get_async_db),
    current_user: schemas.User = Depends(auth_crud.get_current_user)
):
    enrolled_courses = await crud.get_user_enrolled_courses(db, user_id=current_user.id)
    recommended_courses = await crud.get_recommended_courses(db, user_id=current_user.id)
    return schemas.UserDashboard(
        enrolled_courses=enrolled_courses,
        recommended_courses=recommended_courses
    )

@router.get("/me/progress", response_model=List[course_schemas.CourseProgress])
async def get_user_progress(
    db: AsyncSession = Depends(get_async_db),
    current_user: schemas.User = Depends(auth_crud.get_current_user)
):
    progress = await crud.get_user_course_progress(db, user_id=current_user.id)
    return progress

@router.post("/{user_id}/progress/{lesson_id}")
async def update_user_progress(user_id: int, lesson_id: int, completed: bool, db: AsyncSession = Depends(get_async_db)):
    try:
        result = await adaptive_learning_path.update_user_progress(user_id, lesson_id, completed, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user progress: {str(e)}")

@router.get("/{user_id}/learning-path/{course_id}")
async def get_user_learning_path(user_id: int, course_id: int, db: AsyncSession = Depends(get_async_db)):
    try:
        learning_path = await adaptive_learning_path.generate_learning_path(user_id, course_id, db)
        return learning_path
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating learning path: {str(e)}")

@router.get("/profile/{user_id}", response_model=schemas.UserProfile)
async def get_user_profile(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: schemas.User = Depends(auth_crud.get_current_user)
):
    profile_manager = ProfileManager(db)
    return await profile_manager.get_user_profile(user_id)

@router.put("/profile/{user_id}", response_model=schemas.UserProfile)
async def update_user_profile(
    user_id: int,
    profile: schemas.UserProfileUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: schemas.User = Depends(auth_crud.get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this profile")
    profile_manager = ProfileManager(db)
    return await profile_manager.update_user_profile(user_id, profile.dict())

@router.get("/{email}/courses", response_model=List[schemas.Course])
async def get_user_courses(email: str, db: AsyncSession = Depends(get_async_db)):
    user = await db.execute(select(models.User).filter(models.User.email == email))
    user = user.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user.enrolled_courses

@router.get("/{email}/progress", response_model=List[schemas.CourseProgress])
async def get_user_progress(email: str, db: AsyncSession = Depends(get_async_db)):
    user = await db.execute(select(models.User).filter(models.User.email == email))
    user = user.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    progress = []
    for course in user.enrolled_courses:
        course_progress = await db.execute(
            select(models.CourseProgress).filter(
                models.CourseProgress.user_id == user.id,
                models.CourseProgress.course_id == course.id
            )
        )
        course_progress = course_progress.scalar_one_or_none()
        if course_progress:
            progress.append(schemas.CourseProgress(
                course_id=course.id,
                completed_lessons=course_progress.completed_lessons,
                total_lessons=len(course.lessons),
                progress_percentage=course_progress.progress_percentage
            ))
    
    return progress

@router.get("/{email}/achievements")
async def get_user_achievements(email: str, db: AsyncSession = Depends(get_async_db)):
    user = await db.execute(select(models.User).filter(models.User.email == email))
    user = user.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user.achievements

@router.get("/{email}/level")
async def get_user_level(email: str, db: AsyncSession = Depends(get_async_db)):
    user = await db.execute(select(models.User).filter(models.User.email == email))
    user = user.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "level": user.level,
        "xp": user.xp,
        "xpToNextLevel": calculate_xp_for_next_level(user.level)
    }

@router.get("/{email}/daily-challenge")
async def get_user_daily_challenge(email: str, db: AsyncSession = Depends(get_async_db)):
    user = await db.execute(select(models.User).filter(models.User.email == email))
    user = user.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    challenge = await get_daily_challenge(db, user)
    if challenge:
        return challenge
    raise HTTPException(status_code=404, detail="No daily challenge available")

@router.post("/{email}/daily-challenge/{challenge_id}/complete")
async def complete_user_daily_challenge(email: str, challenge_id: int, db: AsyncSession = Depends(get_async_db)):
    user = await db.execute(select(models.User).filter(models.User.email == email))
    user = user.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    level_up = await complete_daily_challenge(db, user, challenge_id)
    new_achievements = await check_achievements(db, user)
    return {
        "success": True,
        "levelUp": level_up,
        "newAchievements": new_achievements
    }
