"""
LiteLLM Service Layer
Core logic for AI model routing, load balancing, and API key management
"""

import asyncio
import json
import hashlib
import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
import time

import litellm
from litellm import completion, embedding, image_generation
from cryptography.fernet import Fernet
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from . import models, schemas
from ...core.config.settings import settings


logger = logging.getLogger(__name__)

# Initialize encryption for API keys
ENCRYPTION_KEY = settings.API_KEY_ENCRYPTION_KEY.encode() if hasattr(settings, 'API_KEY_ENCRYPTION_KEY') else Fernet.generate_key()
cipher_suite = Fernet(ENCRYPTION_KEY)


class LiteLLMService:
    """Main service for managing AI model requests through community-donated API keys"""
    
    def __init__(self):
        self.model_cache = {}
        self.health_cache = {}
        self.last_health_check = {}
        
        # Configure LiteLLM
        litellm.set_verbose = True
        litellm.success_callback = [self._log_success]
        litellm.failure_callback = [self._log_failure]
    
    async def donate_api_key(self, db: AsyncSession, user_id: int, donation: schemas.APIKeyDonationCreate) -> models.DonatedAPIKey:
        """Accept and store a donated API key"""
        try:
            # Validate API key by testing it
            is_valid = await self._validate_api_key(donation.provider, donation.api_key)
            if not is_valid:
                raise ValueError(f"Invalid API key for {donation.provider}")
            
            # Hash and encrypt the key
            key_hash = hashlib.sha256(donation.api_key.encode()).hexdigest()
            encrypted_key = cipher_suite.encrypt(donation.api_key.encode()).decode()
            
            # Check if key already exists
            existing = await db.execute(
                select(models.DonatedAPIKey).where(models.DonatedAPIKey.key_hash == key_hash)
            )
            if existing.scalar_one_or_none():
                raise ValueError("This API key has already been donated")
            
            # Create new donated key record
            db_key = models.DonatedAPIKey(
                donor_user_id=user_id,
                provider=donation.provider,
                key_hash=key_hash,
                encrypted_key=encrypted_key,
                nickname=donation.nickname,
                monthly_limit=donation.monthly_limit,
                status=models.APIKeyStatus.ACTIVE
            )
            
            db.add(db_key)
            await db.commit()
            await db.refresh(db_key)
            
            # Update user contribution
            await self._update_user_contribution(db, user_id, donation.monthly_limit)
            
            # Configure the key in LiteLLM
            await self._configure_litellm_key(donation.provider, donation.api_key)
            
            logger.info(f"New API key donated by user {user_id} for {donation.provider}")
            return db_key
            
        except Exception as e:
            logger.error(f"Failed to donate API key: {str(e)}")
            raise
    
    async def route_ai_request(self, db: AsyncSession, user_id: int, request: schemas.AIModelRequestCreate) -> Dict[str, Any]:
        """Route AI request through optimal API key with load balancing"""
        try:
            # Check user credits and limits
            user_contrib = await self._get_user_contribution(db, user_id)
            if not await self._can_user_make_request(user_contrib, request.model):
                raise ValueError("Insufficient credits or quota exceeded")
            
            # Get best available API key for the model
            api_key_info = await self._get_best_api_key(db, request.model, user_contrib.priority_level)
            if not api_key_info:
                raise ValueError(f"No available API keys for model {request.model}")
            
            # Make the request through LiteLLM
            start_time = time.time()
            
            # Configure LiteLLM with the selected key
            await self._configure_litellm_key(api_key_info['provider'], api_key_info['api_key'])
            
            # Build LiteLLM request
            litellm_request = {
                "model": request.model,
                "messages": request.messages,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "stream": request.stream,
                "user": str(user_id)
            }
            
            # Make the completion request
            if request.stream:
                response = await self._stream_completion(litellm_request)
            else:
                response = await completion(**litellm_request)
            
            response_time = int((time.time() - start_time) * 1000)
            
            # Calculate cost and usage
            usage_info = self._calculate_usage_cost(response, api_key_info['provider'])
            
            # Log the request
            await self._log_ai_request(
                db, user_id, api_key_info['id'], request, response, 
                usage_info, response_time, True
            )
            
            # Update API key usage
            await self._update_api_key_usage(db, api_key_info['id'], usage_info)
            
            # Update user credits
            await self._deduct_user_credits(db, user_id, usage_info['cost_usd'])
            
            return {
                "response": response,
                "provider": api_key_info['provider'],
                "cost_usd": usage_info['cost_usd'],
                "tokens_used": usage_info['total_tokens'],
                "response_time_ms": response_time
            }
            
        except Exception as e:
            logger.error(f"AI request routing failed: {str(e)}")
            # Log failed request
            await self._log_ai_request(
                db, user_id, api_key_info.get('id') if 'api_key_info' in locals() else None,
                request, None, None, 0, False, str(e)
            )
            raise
    
    async def get_available_models(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """Get list of available AI models based on donated API keys"""
        try:
            # Get all active API keys
            result = await db.execute(
                select(models.DonatedAPIKey)
                .where(models.DonatedAPIKey.status == models.APIKeyStatus.ACTIVE)
                .options(selectinload(models.DonatedAPIKey.usage_records))
            )
            api_keys = result.scalars().all()
            
            # Group by provider and check health
            available_models = []
            provider_models = {
                'openai': ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo', 'dall-e-3'],
                'anthropic': ['claude-3-haiku', 'claude-3-sonnet', 'claude-3-opus'],
                'google': ['gemini-pro', 'gemini-pro-vision'],
                'cohere': ['command', 'command-nightly'],
                'replicate': ['llama-2-70b', 'stable-diffusion-xl']
            }
            
            for api_key in api_keys:
                if api_key.provider.value in provider_models:
                    for model in provider_models[api_key.provider.value]:
                        model_info = {
                            'name': model,
                            'provider': api_key.provider.value,
                            'available': True,
                            'estimated_cost_per_1k_tokens': self._get_model_cost(model),
                            'capabilities': self._get_model_capabilities(model),
                            'popularity': await self._get_model_popularity(db, model)
                        }
                        available_models.append(model_info)
            
            return available_models
            
        except Exception as e:
            logger.error(f"Failed to get available models: {str(e)}")
            return []
    
    async def get_user_usage_stats(self, db: AsyncSession, user_id: int, days: int = 30) -> schemas.UserUsageStats:
        """Get user's AI usage statistics"""
        try:
            since_date = datetime.utcnow() - timedelta(days=days)
            
            # Get usage data
            result = await db.execute(
                select(
                    func.count(models.AIModelRequest.id).label('total_requests'),
                    func.sum(models.AIModelRequest.total_tokens).label('total_tokens'),
                    func.sum(models.AIModelRequest.cost_usd).label('total_cost_usd'),
                    func.max(models.AIModelRequest.created_at).label('last_request')
                )
                .where(
                    and_(
                        models.AIModelRequest.user_id == user_id,
                        models.AIModelRequest.created_at >= since_date,
                        models.AIModelRequest.success == True
                    )
                )
            )
            stats = result.first()
            
            # Get favorite models
            favorite_models_result = await db.execute(
                select(
                    models.AIModelRequest.model_name,
                    func.count(models.AIModelRequest.id).label('count')
                )
                .where(
                    and_(
                        models.AIModelRequest.user_id == user_id,
                        models.AIModelRequest.created_at >= since_date,
                        models.AIModelRequest.success == True
                    )
                )
                .group_by(models.AIModelRequest.model_name)
                .order_by(func.count(models.AIModelRequest.id).desc())
                .limit(5)
            )
            favorite_models = [row[0] for row in favorite_models_result.fetchall()]
            
            # Get user contribution for credits used
            user_contrib = await self._get_user_contribution(db, user_id)
            
            return schemas.UserUsageStats(
                user_id=user_id,
                total_requests=stats.total_requests or 0,
                total_tokens=stats.total_tokens or 0,
                total_cost_usd=float(stats.total_cost_usd or 0),
                credits_used=user_contrib.credits_used,
                favorite_models=favorite_models,
                last_request=stats.last_request
            )
            
        except Exception as e:
            logger.error(f"Failed to get user usage stats: {str(e)}")
            raise
    
    async def get_system_health(self, db: AsyncSession) -> schemas.SystemHealthStatus:
        """Get overall system health status"""
        try:
            # Check health of all providers
            health_checks = []
            
            result = await db.execute(
                select(models.AIModelHealth)
                .where(models.AIModelHealth.last_check >= datetime.utcnow() - timedelta(minutes=10))
            )
            recent_health = result.scalars().all()
            
            healthy_count = len([h for h in recent_health if h.status == "healthy"])
            degraded_count = len([h for h in recent_health if h.status == "degraded"])
            down_count = len([h for h in recent_health if h.status == "down"])
            
            overall_status = "healthy"
            if down_count > len(recent_health) * 0.5:
                overall_status = "down"
            elif degraded_count > len(recent_health) * 0.3:
                overall_status = "degraded"
            
            return schemas.SystemHealthStatus(
                overall_status=overall_status,
                total_models=len(recent_health),
                healthy_models=healthy_count,
                degraded_models=degraded_count,
                down_models=down_count,
                model_health=[
                    schemas.ModelHealthStatus(
                        provider=h.provider,
                        model_name=h.model_name,
                        status=h.status,
                        response_time_avg=h.response_time_avg or 0,
                        success_rate=h.success_rate or 0,
                        error_count=h.error_count,
                        last_error=h.last_error,
                        last_check=h.last_check
                    ) for h in recent_health
                ]
            )
            
        except Exception as e:
            logger.error(f"Failed to get system health: {str(e)}")
            raise
    
    # Private helper methods
    
    async def _validate_api_key(self, provider: schemas.APIKeyProvider, api_key: str) -> bool:
        """Validate an API key by making a test request"""
        try:
            test_requests = {
                'openai': lambda: completion(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "test"}], max_tokens=1, api_key=api_key),
                'anthropic': lambda: completion(model="claude-3-haiku-20240307", messages=[{"role": "user", "content": "test"}], max_tokens=1, api_key=api_key),
                'google': lambda: completion(model="gemini-pro", messages=[{"role": "user", "content": "test"}], max_tokens=1, api_key=api_key),
            }
            
            if provider.value in test_requests:
                await test_requests[provider.value]()
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"API key validation failed for {provider}: {str(e)}")
            return False
    
    async def _get_best_api_key(self, db: AsyncSession, model: str, priority_level: int) -> Optional[Dict[str, Any]]:
        """Get the best available API key for a model request"""
        try:
            # Query active keys for the model's provider
            provider = self._get_provider_for_model(model)
            
            result = await db.execute(
                select(models.DonatedAPIKey)
                .where(
                    and_(
                        models.DonatedAPIKey.provider == provider,
                        models.DonatedAPIKey.status == models.APIKeyStatus.ACTIVE,
                        models.DonatedAPIKey.usage_this_month < models.DonatedAPIKey.monthly_limit
                    )
                )
                .order_by(
                    models.DonatedAPIKey.usage_this_month.asc(),  # Prefer less used keys
                    func.random()  # Random selection among similar usage
                )
            )
            
            api_keys = result.scalars().all()
            
            if not api_keys:
                return None
            
            # Select based on priority and load balancing
            selected_key = api_keys[0]  # Simple selection for now
            
            # Decrypt the key
            decrypted_key = cipher_suite.decrypt(selected_key.encrypted_key.encode()).decode()
            
            return {
                'id': selected_key.id,
                'provider': selected_key.provider.value,
                'api_key': decrypted_key
            }
            
        except Exception as e:
            logger.error(f"Failed to get best API key: {str(e)}")
            return None
    
    def _get_provider_for_model(self, model: str) -> schemas.APIKeyProvider:
        """Determine provider based on model name"""
        model_lower = model.lower()
        
        if 'gpt' in model_lower or 'dall-e' in model_lower:
            return schemas.APIKeyProvider.OPENAI
        elif 'claude' in model_lower:
            return schemas.APIKeyProvider.ANTHROPIC
        elif 'gemini' in model_lower:
            return schemas.APIKeyProvider.GOOGLE
        elif 'command' in model_lower:
            return schemas.APIKeyProvider.COHERE
        
        # Default to OpenAI for unknown models
        return schemas.APIKeyProvider.OPENAI
    
    async def _update_user_contribution(self, db: AsyncSession, user_id: int, donated_amount: float):
        """Update user's contribution record"""
        try:
            result = await db.execute(
                select(models.UserContribution).where(models.UserContribution.user_id == user_id)
            )
            user_contrib = result.scalar_one_or_none()
            
            if not user_contrib:
                user_contrib = models.UserContribution(user_id=user_id)
                db.add(user_contrib)
            
            user_contrib.total_donated_usd += donated_amount
            user_contrib.credits_earned += donated_amount * 2  # 2x credits for donations
            user_contrib.credits_remaining += donated_amount * 2
            
            # Update tier based on total donation
            if user_contrib.total_donated_usd >= 500:
                user_contrib.contribution_tier = "benefactor"
                user_contrib.monthly_usage_limit = 100.0
                user_contrib.priority_level = 4
            elif user_contrib.total_donated_usd >= 100:
                user_contrib.contribution_tier = "patron"
                user_contrib.monthly_usage_limit = 50.0
                user_contrib.priority_level = 3
            elif user_contrib.total_donated_usd >= 25:
                user_contrib.contribution_tier = "supporter"
                user_contrib.monthly_usage_limit = 25.0
                user_contrib.priority_level = 2
            
            await db.commit()
            
        except Exception as e:
            logger.error(f"Failed to update user contribution: {str(e)}")
            raise
    
    def _calculate_usage_cost(self, response: Any, provider: str) -> Dict[str, Any]:
        """Calculate usage cost based on response and provider"""
        usage = getattr(response, 'usage', {})
        
        # Cost per 1K tokens by provider (approximate)
        costs = {
            'openai': {'input': 0.0015, 'output': 0.002},
            'anthropic': {'input': 0.00163, 'output': 0.00551},
            'google': {'input': 0.0005, 'output': 0.0015},
            'cohere': {'input': 0.0015, 'output': 0.002},
        }
        
        provider_costs = costs.get(provider, costs['openai'])
        
        prompt_tokens = getattr(usage, 'prompt_tokens', 0)
        completion_tokens = getattr(usage, 'completion_tokens', 0)
        total_tokens = prompt_tokens + completion_tokens
        
        cost_usd = (
            (prompt_tokens / 1000) * provider_costs['input'] +
            (completion_tokens / 1000) * provider_costs['output']
        )
        
        return {
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': total_tokens,
            'cost_usd': cost_usd
        }
    
    def _log_success(self, kwargs, response_obj, start_time, end_time):
        """Callback for successful LiteLLM requests"""
        logger.info(f"LiteLLM request successful: {kwargs.get('model', 'unknown')} in {end_time - start_time:.2f}s")
    
    def _log_failure(self, kwargs, response_obj, start_time, end_time):
        """Callback for failed LiteLLM requests"""
        logger.error(f"LiteLLM request failed: {kwargs.get('model', 'unknown')} - {str(response_obj)}")


# Global service instance
litellm_service = LiteLLMService()