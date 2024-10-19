from ..users.models import User
from .models import Achievement, UserAchievement, DailyChallenge, UserDailyChallenge
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

async def award_xp(db: AsyncSession, user: User, xp: int):
    user.xp += xp
    level_up = False
    while user.xp >= calculate_xp_for_next_level(user.level):
        user.level += 1
        level_up = True
    await db.commit()
    return level_up

def calculate_xp_for_next_level(current_level: int):
    return int(100 * (current_level ** 1.5))

async def check_achievements(db: AsyncSession, user: User):
    new_achievements = []
    achievements = await db.execute(select(Achievement))
    for achievement in achievements.scalars():
        if achievement.id not in [a['id'] for a in user.achievements]:
            if await check_achievement_condition(db, user, achievement):
                user_achievement = UserAchievement(user_id=user.id, achievement_id=achievement.id)
                db.add(user_achievement)
                new_achievements.append(achievement)
                user.achievements.append({
                    'id': achievement.id,
                    'title': achievement.title,
                    'description': achievement.description,
                    'icon': achievement.icon,
                    'date_earned': datetime.utcnow().isoformat()
                })
                await award_xp(db, user, achievement.xp_reward)
    await db.commit()
    return new_achievements

async def check_achievement_condition(db: AsyncSession, user: User, achievement: Achievement):
    # Implement conditions for each achievement
    # For example:
    if achievement.title == "First Lesson Completed":
        return len(user.completed_lessons) > 0
    elif achievement.title == "5 Lessons Completed":
        return len(user.completed_lessons) >= 5
    # Add more conditions as needed
    return False

async def get_daily_challenge(db: AsyncSession, user: User):
    today = datetime.utcnow().date()
    challenge = await db.execute(
        select(DailyChallenge)
        .filter(DailyChallenge.date == today)
        .filter(~DailyChallenge.id.in_(
            select(UserDailyChallenge.challenge_id)
            .filter(UserDailyChallenge.user_id == user.id)
        ))
    )
    return challenge.scalar_one_or_none()

async def complete_daily_challenge(db: AsyncSession, user: User, challenge_id: int):
    challenge = await db.execute(select(DailyChallenge).filter(DailyChallenge.id == challenge_id))
    challenge = challenge.scalar_one_or_none()
    if challenge:
        user_challenge = UserDailyChallenge(user_id=user.id, challenge_id=challenge.id)
        db.add(user_challenge)
        level_up = await award_xp(db, user, challenge.xp_reward)
        await db.commit()
        return level_up
    return False
