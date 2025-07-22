from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import Subscription
from ..users.models import User

async def create_subscription(db: AsyncSession, user: User, stripe_subscription_id: str, status: str, period_end):
    sub = Subscription(user_id=user.id, stripe_subscription_id=stripe_subscription_id, status=status, current_period_end=period_end)
    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    return sub

async def update_subscription_status(db: AsyncSession, stripe_subscription_id: str, status: str, period_end=None):
    result = await db.execute(select(Subscription).filter(Subscription.stripe_subscription_id == stripe_subscription_id))
    sub = result.scalar_one_or_none()
    if sub:
        sub.status = status
        if period_end:
            sub.current_period_end = period_end
        await db.commit()
    return sub
