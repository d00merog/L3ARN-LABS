from ...core.database.db import SessionLocal
from ...api.users import crud as user_crud
from ...api.courses import crud as course_crud
from ...api.lessons import crud as lesson_crud
from ...services.language_preservation.data_collection import LanguageDataCollector
from typing import List
import random

class AdaptiveLearningPath:
    def __init__(self):
        self.db = SessionLocal()
        self.language_data_collector = LanguageDataCollector()

    def generate_learning_path(self, user_id: int) -> dict:
        user = user_crud.get_user(self.db, user_id)
        if not user:
            raise ValueError("User not found")

        # Collect user's language data
        language_data = self.language_data_collector.collect_user_language_data(user_id)

        # Get user's completed courses and lessons
        completed_courses = course_crud.get_completed_user_courses(self.db, user_id)
        completed_lessons = lesson_crud.get_completed_user_lessons(self.db, user_id)

        # Get all available courses
        all_courses = course_crud.get_courses(self.db)

        # Filter out completed courses
        available_courses = [course for course in all_courses if course not in completed_courses]

        # Sort courses based on user's proficiency and interests
        sorted_courses = self._sort_courses_by_relevance(available_courses, language_data, user.interests)

        # Select top 5 recommended courses
        recommended_courses = sorted_courses[:5]

        # Generate specific lessons for each recommended course
        recommended_path = self._generate_course_lessons(recommended_courses, completed_lessons, language_data)

        return {
            "user_id": user_id,
            "recommended_path": recommended_path
        }

    def _sort_courses_by_relevance(self, courses: List, language_data: dict, user_interests: List[str]) -> List:
        def course_relevance(course):
            # Calculate relevance based on proficiency and interests
            proficiency_match = abs(course.difficulty - language_data['proficiency_estimate'])
            interest_match = len(set(course.tags).intersection(user_interests))
            return (interest_match, -proficiency_match)  # Sort by interest match (descending) then proficiency match (ascending)

        return sorted(courses, key=course_relevance, reverse=True)

    def _generate_course_lessons(self, courses: List, completed_lessons: List, language_data: dict) -> List[dict]:
        recommended_path = []
        for course in courses:
            course_lessons = lesson_crud.get_course_lessons(self.db, course.id)
            
            # Filter out completed lessons
            available_lessons = [lesson for lesson in course_lessons if lesson not in completed_lessons]
            
            # Sort lessons based on difficulty and user's proficiency
            sorted_lessons = sorted(available_lessons, 
                                    key=lambda l: abs(l.difficulty - language_data['proficiency_estimate']))
            
            # Select top 3 lessons for each course
            recommended_lessons = sorted_lessons[:3]
            
            recommended_path.append({
                "course_id": course.id,
                "course_title": course.title,
                "lessons": [{"id": lesson.id, "title": lesson.title} for lesson in recommended_lessons]
            })

        return recommended_path

    def __del__(self):
        self.db.close()