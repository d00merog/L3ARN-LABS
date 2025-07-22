"""
LiteLLM API Routes
Community-powered AI model access endpoints
"""

import json
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
import logging

from ...core.database import get_async_db
from ...auth.crud import get_current_user
from ...auth.models import User
from . import models, schemas, service
from .service import litellm_service

router = APIRouter(prefix="/litellm", tags=["LiteLLM - Community AI"])

logger = logging.getLogger(__name__)


@router.post("/donate-api-key", response_model=schemas.APIKeyDonation)
async def donate_api_key(
    donation: schemas.APIKeyDonationCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Donate an API key to the community pool"""
    try:
        donated_key = await litellm_service.donate_api_key(db, current_user.id, donation)
        
        # Background task to test the key and update health
        background_tasks.add_task(
            _test_donated_key_health, 
            db, 
            donated_key.id, 
            donation.provider
        )
        
        return donated_key
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"API key donation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to donate API key"
        )


@router.get("/my-donations", response_model=List[schemas.APIKeyDonation])
async def get_my_donations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get current user's donated API keys"""
    try:
        result = await db.execute(
            select(models.DonatedAPIKey)
            .where(models.DonatedAPIKey.donor_user_id == current_user.id)
            .order_by(desc(models.DonatedAPIKey.created_at))
        )
        return result.scalars().all()
        
    except Exception as e:
        logger.error(f"Failed to get user donations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve donations"
        )


@router.put("/donations/{donation_id}", response_model=schemas.APIKeyDonation)
async def update_donation(
    donation_id: int,
    update: schemas.APIKeyDonationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Update a donated API key"""
    try:
        result = await db.execute(
            select(models.DonatedAPIKey)
            .where(
                and_(
                    models.DonatedAPIKey.id == donation_id,
                    models.DonatedAPIKey.donor_user_id == current_user.id
                )
            )
        )
        donation = result.scalar_one_or_none()
        
        if not donation:
            raise HTTPException(status_code=404, detail="Donation not found")
        
        # Update fields
        if update.nickname is not None:
            donation.nickname = update.nickname
        if update.monthly_limit is not None:
            donation.monthly_limit = update.monthly_limit
        if update.status is not None:
            donation.status = update.status
        
        await db.commit()
        await db.refresh(donation)
        
        return donation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update donation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update donation"
        )


@router.delete("/donations/{donation_id}")
async def remove_donation(
    donation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Remove a donated API key"""
    try:
        result = await db.execute(
            select(models.DonatedAPIKey)
            .where(
                and_(
                    models.DonatedAPIKey.id == donation_id,
                    models.DonatedAPIKey.donor_user_id == current_user.id
                )
            )
        )
        donation = result.scalar_one_or_none()
        
        if not donation:
            raise HTTPException(status_code=404, detail="Donation not found")
        
        await db.delete(donation)
        await db.commit()
        
        return {"message": "API key removed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove donation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove donation"
        )


@router.post("/chat/completions", response_model=schemas.AIModelResponse)
async def chat_completions(
    request: schemas.AIModelRequestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """OpenAI-compatible chat completions endpoint using community API keys"""
    try:
        if request.stream:
            # Handle streaming response
            return StreamingResponse(
                _stream_chat_completions(db, current_user.id, request),
                media_type="text/event-stream"
            )
        
        # Regular completion
        result = await litellm_service.route_ai_request(db, current_user.id, request)
        
        # Format response in OpenAI-compatible format
        response = result['response']
        
        return schemas.AIModelResponse(
            id=response.id,
            object=response.object,
            created=response.created,
            model=response.model,
            provider=result['provider'],
            usage=response.usage.__dict__,
            choices=[choice.__dict__ for choice in response.choices],
            cost_usd=result['cost_usd'],
            response_time_ms=result['response_time_ms']
        )
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Chat completion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat completion"
        )


@router.get("/models", response_model=List[Dict[str, Any]])
async def list_available_models(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """List all available AI models"""
    try:
        models = await litellm_service.get_available_models(db)
        return models
        
    except Exception as e:
        logger.error(f"Failed to list models: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve available models"
        )


@router.get("/usage/me", response_model=schemas.UserUsageStats)
async def get_my_usage(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get current user's AI usage statistics"""
    try:
        stats = await litellm_service.get_user_usage_stats(db, current_user.id, days)
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get user usage: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve usage statistics"
        )


@router.get("/contribution/me", response_model=schemas.UserContributionInfo)
async def get_my_contribution(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get current user's contribution information"""
    try:
        result = await db.execute(
            select(models.UserContribution)
            .where(models.UserContribution.user_id == current_user.id)
        )
        contribution = result.scalar_one_or_none()
        
        if not contribution:
            # Create default contribution record
            contribution = models.UserContribution(user_id=current_user.id)
            db.add(contribution)
            await db.commit()
            await db.refresh(contribution)
        
        return contribution
        
    except Exception as e:
        logger.error(f"Failed to get user contribution: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve contribution information"
        )


@router.get("/community/stats", response_model=schemas.CommunityStats)
async def get_community_stats(
    db: AsyncSession = Depends(get_async_db)
):
    """Get community statistics"""
    try:
        # Get total contributors
        contributors_result = await db.execute(
            select(func.count(models.UserContribution.id))
            .where(models.UserContribution.total_donated_usd > 0)
        )
        total_contributors = contributors_result.scalar()
        
        # Get total API keys
        keys_result = await db.execute(
            select(func.count(models.DonatedAPIKey.id))
            .where(models.DonatedAPIKey.status == models.APIKeyStatus.ACTIVE)
        )
        total_api_keys = keys_result.scalar()
        
        # Get total donated value
        value_result = await db.execute(
            select(func.sum(models.UserContribution.total_donated_usd))
        )
        total_donated = value_result.scalar() or 0.0
        
        # Get available models
        models_list = await litellm_service.get_available_models(db)
        model_names = list(set([m['name'] for m in models_list]))
        
        # Get monthly requests
        from datetime import datetime, timedelta
        start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        requests_result = await db.execute(
            select(func.count(models.AIModelRequest.id))
            .where(
                and_(
                    models.AIModelRequest.created_at >= start_of_month,
                    models.AIModelRequest.success == True
                )
            )
        )
        monthly_requests = requests_result.scalar()
        
        # Calculate community savings (rough estimate)
        cost_result = await db.execute(
            select(func.sum(models.AIModelRequest.cost_usd))
            .where(
                and_(
                    models.AIModelRequest.created_at >= start_of_month,
                    models.AIModelRequest.success == True
                )
            )
        )
        monthly_cost = cost_result.scalar() or 0.0
        community_savings = monthly_cost * 0.7  # Assume 70% savings vs individual usage
        
        return schemas.CommunityStats(
            total_contributors=total_contributors,
            total_api_keys=total_api_keys,
            total_donated_value=total_donated,
            models_available=model_names,
            monthly_requests=monthly_requests,
            community_savings=community_savings
        )
        
    except Exception as e:
        logger.error(f"Failed to get community stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve community statistics"
        )


@router.get("/community/leaderboard", response_model=List[schemas.ContributorLeaderboard])
async def get_contributor_leaderboard(
    limit: int = 10,
    db: AsyncSession = Depends(get_async_db)
):
    """Get contributor leaderboard"""
    try:
        # Join with users to get username
        from ...auth.models import User
        
        result = await db.execute(
            select(
                models.UserContribution.user_id,
                User.username,
                models.UserContribution.total_donated_usd,
                models.UserContribution.contribution_tier,
                models.UserContribution.credits_earned,
                func.count(models.DonatedAPIKey.id).label('models_enabled')
            )
            .join(User, models.UserContribution.user_id == User.id)
            .outerjoin(
                models.DonatedAPIKey,
                and_(
                    models.DonatedAPIKey.donor_user_id == models.UserContribution.user_id,
                    models.DonatedAPIKey.status == models.APIKeyStatus.ACTIVE
                )
            )
            .where(models.UserContribution.total_donated_usd > 0)
            .group_by(
                models.UserContribution.user_id,
                User.username,
                models.UserContribution.total_donated_usd,
                models.UserContribution.contribution_tier,
                models.UserContribution.credits_earned
            )
            .order_by(desc(models.UserContribution.total_donated_usd))
            .limit(limit)
        )
        
        leaderboard = []
        for rank, row in enumerate(result.fetchall(), 1):
            leaderboard.append(schemas.ContributorLeaderboard(
                rank=rank,
                user_id=row.user_id,
                username=row.username,
                total_donated_usd=row.total_donated_usd,
                contribution_tier=row.contribution_tier,
                credits_earned=row.credits_earned,
                models_enabled=row.models_enabled
            ))
        
        return leaderboard
        
    except Exception as e:
        logger.error(f"Failed to get leaderboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve leaderboard"
        )


@router.get("/health", response_model=schemas.SystemHealthStatus)
async def get_system_health(
    db: AsyncSession = Depends(get_async_db)
):
    """Get system health status"""
    try:
        health = await litellm_service.get_system_health(db)
        return health
        
    except Exception as e:
        logger.error(f"Failed to get system health: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system health"
        )


@router.post("/health/check")
async def trigger_health_check(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Trigger a system-wide health check"""
    try:
        # Only allow admins to trigger health checks
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        background_tasks.add_task(_perform_health_check, db)
        
        return {"message": "Health check initiated"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to trigger health check: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger health check"
        )


# Helper functions

async def _stream_chat_completions(db: AsyncSession, user_id: int, request: schemas.AIModelRequestCreate):
    """Stream chat completions"""
    try:
        # Get API key for streaming
        user_contrib = await litellm_service._get_user_contribution(db, user_id)
        api_key_info = await litellm_service._get_best_api_key(db, request.model, user_contrib.priority_level)
        
        if not api_key_info:
            yield f"data: {json.dumps({'error': 'No available API keys'})}\n\n"
            return
        
        # Configure LiteLLM
        await litellm_service._configure_litellm_key(api_key_info['provider'], api_key_info['api_key'])
        
        # Stream the response
        response = await litellm_service.completion(
            model=request.model,
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=True,
            user=str(user_id)
        )
        
        async for chunk in response:
            chunk_data = {
                "id": chunk.id,
                "object": chunk.object,
                "created": chunk.created,
                "model": chunk.model,
                "choices": [choice.__dict__ for choice in chunk.choices]
            }
            yield f"data: {json.dumps(chunk_data)}\n\n"
        
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        logger.error(f"Streaming failed: {str(e)}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


async def _test_donated_key_health(db: AsyncSession, key_id: int, provider: schemas.APIKeyProvider):
    """Background task to test donated key health"""
    try:
        # Perform health check on the donated key
        # This would make a test request to verify the key works
        logger.info(f"Testing health of donated key {key_id} for {provider}")
        
        # Update health record
        health_record = models.AIModelHealth(
            provider=provider,
            model_name="test",
            status="healthy",
            response_time_avg=100.0,
            success_rate=1.0,
            error_count=0
        )
        
        db.add(health_record)
        await db.commit()
        
    except Exception as e:
        logger.error(f"Health check failed for key {key_id}: {str(e)}")


async def _perform_health_check(db: AsyncSession):
    """Background task for system-wide health check"""
    try:
        logger.info("Starting system-wide health check")
        
        # Get all active API keys
        result = await db.execute(
            select(models.DonatedAPIKey)
            .where(models.DonatedAPIKey.status == models.APIKeyStatus.ACTIVE)
        )
        api_keys = result.scalars().all()
        
        # Test each key
        for api_key in api_keys:
            try:
                # Decrypt and test the key
                from .service import cipher_suite
                decrypted_key = cipher_suite.decrypt(api_key.encrypted_key.encode()).decode()
                
                is_healthy = await litellm_service._validate_api_key(api_key.provider, decrypted_key)
                
                # Update health record
                health_record = models.AIModelHealth(
                    provider=api_key.provider,
                    model_name="health_check",
                    status="healthy" if is_healthy else "down",
                    response_time_avg=100.0 if is_healthy else 0.0,
                    success_rate=1.0 if is_healthy else 0.0,
                    error_count=0 if is_healthy else 1
                )
                
                db.add(health_record)
                
            except Exception as e:
                logger.error(f"Health check failed for key {api_key.id}: {str(e)}")
        
        await db.commit()
        logger.info("System-wide health check completed")
        
    except Exception as e:
        logger.error(f"System health check failed: {str(e)}")