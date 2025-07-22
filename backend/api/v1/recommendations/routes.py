from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...core.database import get_async_db
from ...ml.recommendation_model import RecommendationModel
from ..users.models import User
from sqlalchemy import select

router = APIRouter()
recommendation_model = RecommendationModel()

@router.post("/train")
async def train_recommendation_model(db: AsyncSession = Depends(get_async_db)):
    try:
        await recommendation_model.train(db)
        return {"message": "Recommendation model trained successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training model: {str(e)}")

@router.get("/{user_email}")
async def get_personalized_recommendations(user_email: str, db: AsyncSession = Depends(get_async_db)):
    try:
        user = await db.execute(select(User).filter(User.email == user_email))
        user = user.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail=f"User with email {user_email} not found")
        
        recommendations = await recommendation_model.get_recommendations(user.id, db)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")
