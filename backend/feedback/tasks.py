from celery import Celery
from celery.schedules import crontab
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config.settings import settings
from backend.core.database import AsyncSessionLocal
from backend.api.courses.models import Lesson, Enrollment
from backend.api.users.models import User
from backend.api.quizzes import crud as quiz_crud
from .email_utils import send_email

celery_app = Celery(
    "feedback",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)


@celery_app.task
def send_nightly_feedback():
    async def _run():
        async with AsyncSessionLocal() as session:
            lessons = await session.execute(select(Lesson.id, Lesson.title))
            for lesson_id, lesson_title in lessons.all():
                wrong = await quiz_crud.get_top_wrong_answers(session, lesson_id)
                if not wrong:
                    continue
                lines = [f"{q} - {count} times" for q, count in wrong]
                body = "\n".join(lines)

                users = await session.execute(
                    select(User.email)
                    .join(Enrollment, Enrollment.user_id == User.id)
                    .filter(Enrollment.course_id == lesson_id)
                )
                emails = [u[0] for u in users.all()]
                if emails:
                    send_email(
                        settings.SMTP_HOST,
                        settings.SMTP_PORT,
                        settings.SMTP_USER,
                        settings.SMTP_PASSWORD,
                        emails,
                        f"Top mistakes for {lesson_title}",
                        body,
                    )

    import asyncio

    asyncio.run(_run())


celery_app.conf.beat_schedule = {
    "nightly-feedback": {
        "task": "backend.feedback.tasks.send_nightly_feedback",
        "schedule": crontab(hour=0, minute=0),
    }
}
