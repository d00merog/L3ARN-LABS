import os
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from .core.database import get_async_db
from .core.config.settings import settings
from .api.auth.routes import router as auth_router
from .api.users.routes import router as user_router
from .api.courses.routes import router as course_router
from .api.lessons.routes import router as lesson_router
from .api.notifications.routes import router as notification_router
from .api.analytics.routes import router as analytics_router
from .api.recommendations.routes import router as recommendation_router
from .api.billing.routes import router as billing_router
from .teacher_agents.history_agent import HistoryTeacher
from .teacher_agents.science_agent import ScienceAgent
from .teacher_agents.tech_agent import TechTeacherAgent
from .memory.adaptive_learning.learning_path import AdaptiveLearningPath
from .ml.recommendation_model import RecommendationModel
import logging
from sqlalchemy import select
from .api.users.models import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI-Powered Learning Platform")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(user_router, prefix="/api/users", tags=["Users"])
app.include_router(course_router, prefix="/api/courses", tags=["Courses"])
app.include_router(lesson_router, prefix="/api/lessons", tags=["Lessons"])
app.include_router(notification_router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(recommendation_router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(billing_router, prefix="/api/billing", tags=["Billing"])

# Initialize components
history_teacher = HistoryTeacher(model="gpt-3.5-turbo")
science_teacher = ScienceAgent(model_name="gpt-3.5-turbo")
tech_teacher = TechTeacherAgent(model_name="gpt-3.5-turbo")
adaptive_learning_path = AdaptiveLearningPath()
recommendation_model = RecommendationModel()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."}
    )

@app.get("/learning-path/{user_email}/{course_id}")
async def get_learning_path(user_email: str, course_id: int, db: AsyncSession = Depends(get_async_db)):
    try:
        user = await db.execute(select(User).filter(User.email == user_email))
        user = user.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return await adaptive_learning_path.generate_learning_path(user.id, course_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating learning path: {str(e)}")

@app.get("/history/audio-lesson")
async def get_audio_lesson(topic: str, era: str):
    return await history_teacher.create_audio_lesson(topic, era)

@app.get("/science/question")
async def get_science_question(topic: str, difficulty: str):
    return await science_teacher.generate_science_question(topic, difficulty)

@app.get("/science/infographic")
async def get_science_infographic(topic: str):
    return await science_teacher.create_science_infographic(topic)

@app.get("/tech/coding-challenge")
async def get_coding_challenge(language: str, difficulty: str):
    return await tech_teacher.generate_coding_challenge(language, difficulty)

@app.get("/")
async def root():
    return {"message": "Welcome to the AI-Powered Learning Platform API"}

@app.post("/train-recommendation-model")
async def train_recommendation_model(db: AsyncSession = Depends(get_async_db)):
    try:
        await recommendation_model.train(db)
        return {"message": "Recommendation model trained successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training model: {str(e)}")

@app.get("/personalized-recommendations/{user_email}")
async def get_personalized_recommendations(user_email: str, db: AsyncSession = Depends(get_async_db)):
    try:
        user = await db.execute(select(User).filter(User.email == user_email))
        user = user.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        recommendations = await recommendation_model.get_recommendations(user.id, db)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")

@app.post("/update-progress/{user_email}/{lesson_id}")
async def update_user_progress(user_email: str, lesson_id: int, completed: bool, db: AsyncSession = Depends(get_async_db)):
    try:
        user = await db.execute(select(User).filter(User.email == user_email))
        user = user.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return await adaptive_learning_path.update_user_progress(user.id, lesson_id, completed, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user progress: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
