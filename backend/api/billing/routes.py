from fastapi import APIRouter, Depends, HTTPException, Request
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from ..auth import crud as auth_crud
from ...core.database import get_async_db
from . import crud as billing_crud
from ...core.config.settings import settings
import stripe

router = APIRouter()

stripe.api_key = settings.STRIPE_API_KEY

# Tiered plans would be defined in Stripe Dashboard. Price IDs stored here
TIER_PRICE_IDS = {
    "basic": settings.STRIPE_BASIC_PRICE_ID,
    "pro": settings.STRIPE_PRO_PRICE_ID,
}

@router.post("/create-checkout-session/{tier}")
async def create_checkout_session(tier: str, db: AsyncSession = Depends(get_async_db), current_user=Depends(auth_crud.get_current_user)):
    if tier not in TIER_PRICE_IDS:
        raise HTTPException(status_code=400, detail="Invalid tier")
    try:
        session = stripe.checkout.Session.create(
            success_url=settings.STRIPE_SUCCESS_URL,
            cancel_url=settings.STRIPE_CANCEL_URL,
            mode="subscription",
            line_items=[{"price": TIER_PRICE_IDS[tier], "quantity": 1}],
            client_reference_id=str(current_user.id),
        )
        return {"sessionId": session.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_async_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid payload")

    if event["type"] == "customer.subscription.created":
        data = event["data"]["object"]
        await billing_crud.create_subscription(
            db,
            user=await auth_crud.get_user(db, int(data.get("client_reference_id", 0))),
            stripe_subscription_id=data["id"],
            status=data["status"],
            period_end=datetime.fromtimestamp(data["current_period_end"]),
        )
    elif event["type"] == "customer.subscription.updated":
        data = event["data"]["object"]
        await billing_crud.update_subscription_status(
            db,
            stripe_subscription_id=data["id"],
            status=data["status"],
            period_end=datetime.fromtimestamp(data["current_period_end"]),
        )
    return {"status": "success"}
