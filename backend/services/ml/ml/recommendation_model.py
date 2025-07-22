from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..api.courses.models import Course
from ..api.users.models import User
import logging

logger = logging.getLogger(__name__)

class RecommendationModel:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.classifier = MultinomialNB()

    async def train(self, db: AsyncSession):
        try:
            # Fetch all courses and users
            courses = await db.execute(select(Course))
            users = await db.execute(select(User))

            # Prepare training data
            X = [course.description for course in courses.scalars()]
            y = [user.interests for user in users.scalars()]

            if not X or not y:
                logger.warning("No training data available")
                return

            # Train the model
            X_vectorized = self.vectorizer.fit_transform(X)
            self.classifier.fit(X_vectorized, y)
            logger.info("Recommendation model trained successfully")
        except Exception as e:
            logger.error(f"Error training recommendation model: {str(e)}", exc_info=True)
            raise

    async def get_recommendations(self, user_id: int, db: AsyncSession):
        try:
            # Fetch user interests
            user = await db.execute(select(User).filter(User.id == user_id))
            user = user.scalar_one_or_none()
            if not user:
                raise ValueError(f"User with id {user_id} not found")

            # Fetch all courses
            courses = await db.execute(select(Course))
            courses = courses.scalars().all()

            if not courses:
                logger.warning("No courses available for recommendations")
                return []

            # Predict probabilities for each course
            X = [course.description for course in courses]
            X_vectorized = self.vectorizer.transform(X)
            probabilities = self.classifier.predict_proba(X_vectorized)

            # Get the index of the user's interests
            interest_index = self.classifier.classes_.tolist().index(user.interests)

            # Sort courses by probability and return top 5
            recommendations = sorted(
                [(course, prob[interest_index]) for course, prob in zip(courses, probabilities)],
                key=lambda x: x[1],
                reverse=True
            )[:5]

            return [{"course_id": course.id, "title": course.title, "probability": float(prob)} for course, prob in recommendations]
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}", exc_info=True)
            raise
