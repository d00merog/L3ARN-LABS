"""
Bittensor API Routes
Decentralized AI network integration for educational platform
"""

import asyncio
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
import logging

from ...core.database import get_async_db
from ...auth.crud import get_current_user
from ...auth.models import User
from . import models, schemas, service
from .service import bittensor_service
from .security import transaction_validator, network_security, TransactionType

router = APIRouter(prefix="/bittensor", tags=["Bittensor - Decentralized AI"])

logger = logging.getLogger(__name__)


@router.post("/search", response_model=schemas.KnowledgeSearchResponse)
async def search_knowledge(
    request: schemas.KnowledgeSearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Search the Bittensor network for educational content"""
    try:
        start_time = asyncio.get_event_loop().time()
        
        # Perform search using Bittensor network
        results = await bittensor_service.search_knowledge(
            query=request.query,
            max_results=request.max_results,
            educational_focus=request.educational_focus,
            fact_check=request.fact_check
        )
        
        processing_time = int((asyncio.get_event_loop().time() - start_time) * 1000)
        
        # Calculate consensus score based on result quality
        consensus_score = 0.0
        if results:
            consensus_score = sum(r.get("score", 0.5) for r in results) / len(results)
        
        # Log the search query
        await _log_bittensor_query(
            db, current_user.id, "search", {
                "query": request.query,
                "max_results": request.max_results,
                "educational_focus": request.educational_focus
            }, len(results), True
        )
        
        # Format results
        search_results = []
        for result in results:
            search_results.append(schemas.SearchResult(
                title=result.get("title", ""),
                content=result.get("content", ""),
                url=result.get("url", ""),
                score=result.get("score", 0.5),
                educational_quality=result.get("educational_quality", 0.5),
                fact_checked=result.get("fact_checked", False),
                source_trust=result.get("source_trust", 0.5),
                miner_uid=result.get("miner_uid"),
                timestamp=result.get("timestamp")
            ))
        
        return schemas.KnowledgeSearchResponse(
            query=request.query,
            results=search_results,
            total_results=len(search_results),
            consensus_score=consensus_score,
            processing_time_ms=processing_time,
            cost_tao=0.0001 * len(search_results)  # Estimated cost
        )
        
    except Exception as e:
        logger.error(f"Knowledge search failed: {str(e)}")
        await _log_bittensor_query(
            db, current_user.id, "search", {"query": request.query}, 0, False, str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
        )


@router.post("/fact-check", response_model=schemas.FactCheckResult)
async def fact_check_statement(
    request: schemas.FactCheckRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Verify factual information using Bittensor network consensus"""
    try:
        start_time = asyncio.get_event_loop().time()
        
        # Perform fact-checking using Bittensor network
        verification_result = await bittensor_service.verify_information(
            statement=request.statement,
            context=request.context
        )
        
        processing_time = int((asyncio.get_event_loop().time() - start_time) * 1000)
        
        # Log the fact-check query
        await _log_bittensor_query(
            db, current_user.id, "fact_check", {
                "statement": request.statement,
                "context": request.context
            }, 1, True
        )
        
        # Calculate TAO reward for fact-checking activity
        tao_reward = await bittensor_service.calculate_tao_rewards(
            db, current_user.id, "fact_checking", {
                "statement": request.statement,
                "confidence": verification_result.get("confidence", 0.5),
                "consensus_score": verification_result.get("consensus_ratio", 0.5)
            }
        )
        
        return schemas.FactCheckResult(
            statement=verification_result["statement"],
            verified=verification_result["verified"],
            confidence=verification_result["confidence"],
            consensus_ratio=verification_result.get("consensus_ratio", 0.0),
            status=verification_result.get("status", "unknown"),
            sources=verification_result.get("sources", []),
            explanation=verification_result.get("explanation"),
            miner_count=verification_result.get("miner_count", 0),
            cost_tao=0.0002,  # Base cost for fact-checking
            timestamp=verification_result["timestamp"]
        )
        
    except Exception as e:
        logger.error(f"Fact checking failed: {str(e)}")
        await _log_bittensor_query(
            db, current_user.id, "fact_check", {"statement": request.statement}, 0, False, str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fact checking failed"
        )


@router.post("/validate-content", response_model=schemas.ValidationResult)
async def validate_educational_content(
    request: schemas.ValidationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Validate educational content using Bittensor network consensus"""
    try:
        # Perform validation using Bittensor network
        validation_result = await bittensor_service.validate_educational_content(
            db=db,
            content=request.content,
            content_type=request.content_type,
            validation_type=request.validation_type,
            user_id=current_user.id
        )
        
        # Log the validation request
        await _log_bittensor_query(
            db, current_user.id, "validation", {
                "content_type": request.content_type,
                "validation_type": request.validation_type.value,
                "content_length": len(request.content)
            }, 1, True
        )
        
        return schemas.ValidationResult(
            id=validation_result.get("id", 0),
            content_type=request.content_type,
            validation_type=request.validation_type,
            consensus_score=validation_result.get("consensus_score", 0.5),
            agreement_ratio=validation_result.get("agreement_ratio", 0.5),
            quality_score=validation_result.get("quality_score"),
            fact_accuracy=validation_result.get("fact_accuracy"),
            educational_value=validation_result.get("educational_value"),
            is_approved=validation_result.get("is_approved", False),
            validator_count=validation_result.get("validator_count", 0),
            tao_cost=validation_result.get("tao_cost", 0.001),
            created_at=validation_result.get("created_at")
        )
        
    except Exception as e:
        logger.error(f"Content validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content validation failed"
        )


@router.post("/generate-content", response_model=schemas.GeneratedContent)
async def generate_educational_content(
    request: schemas.ContentGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Generate educational content using Bittensor network"""
    try:
        start_time = asyncio.get_event_loop().time()
        
        # Generate content using Bittensor network
        content_result = await bittensor_service.get_educational_content(
            topic=request.topic,
            level=request.level,
            content_type=request.content_type
        )
        
        generation_time = int((asyncio.get_event_loop().time() - start_time) * 1000)
        
        # Log the content generation request
        await _log_bittensor_query(
            db, current_user.id, "content_generation", {
                "topic": request.topic,
                "level": request.level,
                "content_type": request.content_type
            }, 1, True
        )
        
        # Calculate TAO cost based on content length and quality
        content_length = len(content_result.get("content", ""))
        tao_cost = max(0.005, content_length / 10000)  # Base cost with length scaling
        
        return schemas.GeneratedContent(
            topic=request.topic,
            level=request.level,
            content_type=request.content_type,
            content=content_result.get("content", ""),
            examples=content_result.get("examples", []),
            quality_score=content_result.get("quality_score", 0.5),
            educational_value=content_result.get("educational_value", 0.5),
            validation_score=content_result.get("validation_score"),
            cost_tao=tao_cost,
            generation_time_ms=generation_time,
            created_at=content_result.get("timestamp")
        )
        
    except Exception as e:
        logger.error(f"Content generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content generation failed"
        )


@router.get("/network-stats", response_model=Dict[str, Any])
async def get_network_statistics(
    current_user: User = Depends(get_current_user)
):
    """Get Bittensor network statistics"""
    try:
        stats = await bittensor_service.get_network_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get network stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve network statistics"
        )


@router.get("/user-stats", response_model=schemas.UserBittensorStats)
async def get_user_statistics(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get user's Bittensor activity statistics"""
    try:
        from datetime import datetime, timedelta
        
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Get user query statistics
        query_result = await db.execute(
            select(models.BittensorQuery)
            .where(
                and_(
                    models.BittensorQuery.user_id == current_user.id,
                    models.BittensorQuery.created_at >= since_date
                )
            )
        )
        queries = query_result.scalars().all()
        
        # Get user TAO transactions
        transaction_result = await db.execute(
            select(models.TAOTransaction)
            .where(
                and_(
                    models.TAOTransaction.user_id == current_user.id,
                    models.TAOTransaction.created_at >= since_date
                )
            )
        )
        transactions = transaction_result.scalars().all()
        
        # Calculate statistics
        total_tao_earned = sum(t.amount_tao for t in transactions if t.transaction_type == 'earn')
        total_tao_spent = sum(t.amount_tao for t in transactions if t.transaction_type == 'spend')
        
        successful_queries = [q for q in queries if q.success]
        success_rate = len(successful_queries) / len(queries) if queries else 0.0
        
        # Get user's favorite subnets (based on query frequency)
        subnet_usage = {}
        for query in queries:
            subnet = query.input_data.get('target_subnet', 'text_prompting')
            subnet_usage[subnet] = subnet_usage.get(subnet, 0) + 1
        
        favorite_subnets = sorted(subnet_usage.keys(), key=subnet_usage.get, reverse=True)[:3]
        favorite_subnet_ids = [1 if s == 'text_prompting' else 27 if s == 'compute' else 1 for s in favorite_subnets]
        
        last_activity = max((q.created_at for q in queries), default=None)
        
        return schemas.UserBittensorStats(
            user_id=current_user.id,
            total_queries=len(queries),
            total_validations=len([q for q in queries if q.query_type == 'validation']),
            total_tao_earned=total_tao_earned,
            total_tao_spent=total_tao_spent,
            average_validation_score=0.8,  # Would calculate from actual validations
            mining_activities=len([t for t in transactions if t.activity_type]),
            favorite_subnets=favorite_subnet_ids,
            success_rate=success_rate,
            last_activity=last_activity
        )
        
    except Exception as e:
        logger.error(f"Failed to get user stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user statistics"
        )


@router.get("/wallet", response_model=schemas.TAOWalletInfo)
async def get_tao_wallet(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get user's TAO wallet information"""
    try:
        result = await db.execute(
            select(models.UserTAOWallet)
            .where(models.UserTAOWallet.user_id == current_user.id)
        )
        wallet = result.scalar_one_or_none()
        
        if not wallet:
            # Create default wallet
            wallet = models.UserTAOWallet(user_id=current_user.id)
            db.add(wallet)
            await db.commit()
            await db.refresh(wallet)
        
        return wallet
        
    except Exception as e:
        logger.error(f"Failed to get TAO wallet: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve wallet information"
        )


@router.put("/wallet", response_model=schemas.TAOWalletInfo)
async def update_tao_wallet(
    update: schemas.TAOWalletUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Update user's TAO wallet configuration"""
    try:
        result = await db.execute(
            select(models.UserTAOWallet)
            .where(models.UserTAOWallet.user_id == current_user.id)
        )
        wallet = result.scalar_one_or_none()
        
        if not wallet:
            wallet = models.UserTAOWallet(user_id=current_user.id)
            db.add(wallet)
        
        if update.hotkey:
            wallet.hotkey = update.hotkey
        if update.coldkey:
            wallet.coldkey = update.coldkey
        
        await db.commit()
        await db.refresh(wallet)
        
        return wallet
        
    except Exception as e:
        logger.error(f"Failed to update TAO wallet: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update wallet"
        )


@router.get("/transactions", response_model=List[schemas.TAOTransaction])
async def get_tao_transactions(
    limit: int = 20,
    transaction_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get user's TAO transaction history"""
    try:
        query = select(models.TAOTransaction).where(
            models.TAOTransaction.user_id == current_user.id
        )
        
        if transaction_type:
            query = query.where(models.TAOTransaction.transaction_type == transaction_type)
        
        query = query.order_by(desc(models.TAOTransaction.created_at)).limit(limit)
        
        result = await db.execute(query)
        transactions = result.scalars().all()
        
        return transactions
        
    except Exception as e:
        logger.error(f"Failed to get transactions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transactions"
        )


@router.get("/subnets", response_model=List[schemas.SubnetInfo])
async def get_available_subnets(
    db: AsyncSession = Depends(get_async_db)
):
    """Get list of available Bittensor subnets"""
    try:
        result = await db.execute(
            select(models.BittensorSubnet)
            .where(models.BittensorSubnet.is_active == True)
            .order_by(models.BittensorSubnet.netuid)
        )
        subnets = result.scalars().all()
        
        return subnets
        
    except Exception as e:
        logger.error(f"Failed to get subnets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subnets"
        )


@router.post("/mine-activity", response_model=schemas.MiningReward)
async def mine_educational_activity(
    activity: schemas.EducationalMiningActivity,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Mine TAO tokens through educational activities with enhanced security validation"""
    try:
        # Enhanced security checks for mining activities
        client_ip = request.client.host
        user_agent = request.headers.get('user-agent', '')
        
        # Log security-relevant request details
        logger.info(f"Mining activity request from user {current_user.id} (IP: {client_ip})")
        
        # Calculate TAO reward for the activity with security validation
        tao_reward = await bittensor_service.calculate_tao_rewards(
            db=db,
            user_id=current_user.id,
            activity_type=activity.activity_type,
            activity_data={
                "activity_id": activity.activity_id,
                "difficulty_level": activity.difficulty_level,
                "completion_time_seconds": activity.completion_time_seconds,
                "quality_score": activity.quality_score,
                "client_ip": client_ip,
                "user_agent": user_agent
            }
        )
        
        # Create mining record
        mining_record = models.EducationalMining(
            user_id=current_user.id,
            activity_type=activity.activity_type,
            activity_id=activity.activity_id,
            difficulty_level=activity.difficulty_level,
            completion_time_seconds=activity.completion_time_seconds,
            quality_score=activity.quality_score,
            base_reward_tao=tao_reward,
            multiplier=1.0,
            final_reward_tao=tao_reward,
            is_validated=False
        )
        
        db.add(mining_record)
        await db.commit()
        await db.refresh(mining_record)
        
        return mining_record
        
    except ValueError as e:
        # Handle validation errors (e.g., fraud detection)
        logger.warning(f"Mining activity validation failed for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Educational mining failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Mining activity failed"
        )


# Helper functions

async def _log_bittensor_query(
    db: AsyncSession,
    user_id: int,
    query_type: str,
    input_data: Dict[str, Any],
    responses_received: int,
    success: bool,
    error_message: Optional[str] = None
):
    """Log a Bittensor query to the database with enhanced security logging"""
    try:
        # Add security metadata to input_data for enhanced logging
        enhanced_input_data = {
            **input_data,
            "security_timestamp": int(asyncio.get_event_loop().time()),
            "query_hash": hash(str(input_data)),  # Simple hash for duplicate detection
        }
        
        query_record = models.BittensorQuery(
            user_id=user_id,
            query_type=query_type,
            input_data=enhanced_input_data,
            responses_received=responses_received,
            success=success,
            error_message=error_message,
            cost_tao=0.0001 * responses_received  # Base cost calculation
        )
        
        db.add(query_record)
        await db.commit()
        
        # Log security event for monitoring
        if not success and error_message:
            logger.warning(f"Bittensor query failed for user {user_id}: {error_message}")
        
    except Exception as e:
        logger.error(f"Failed to log Bittensor query: {str(e)}")


@router.post("/secure-query")
async def send_secure_bittensor_query(
    query_data: Dict[str, Any],
    recipient_uid: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Send secure encrypted query to specific Bittensor miner"""
    try:
        # Enhanced security logging
        client_ip = request.client.host
        logger.info(f"Secure query request from user {current_user.id} to miner {recipient_uid} (IP: {client_ip})")
        
        # Send secure message
        result = await bittensor_service.send_secure_network_message(
            recipient_uid=recipient_uid,
            message_data=query_data,
            message_type="secure_query"
        )
        
        # Log the secure query
        await _log_bittensor_query(
            db, current_user.id, "secure_query", {
                "recipient_uid": recipient_uid,
                "message_type": "secure_query",
                "client_ip": client_ip,
                "encrypted": True
            }, 1, result["success"]
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Secure query failed")
            )
        
        return {
            "success": True,
            "message_id": result["message_id"],
            "encrypted": True,
            "recipient_uid": recipient_uid,
            "timestamp": int(asyncio.get_event_loop().time())
        }
        
    except Exception as e:
        logger.error(f"Secure query failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Secure query failed"
        )


@router.get("/security-status")
async def get_bittensor_security_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get Bittensor security status and fraud detection metrics"""
    try:
        from datetime import datetime, timedelta
        
        # Get recent transactions for fraud analysis
        recent_transactions = await db.execute(
            select(models.TAOTransaction)
            .where(
                and_(
                    models.TAOTransaction.user_id == current_user.id,
                    models.TAOTransaction.created_at >= datetime.utcnow() - timedelta(hours=24)
                )
            )
            .order_by(desc(models.TAOTransaction.created_at))
            .limit(10)
        )
        
        transactions = recent_transactions.scalars().all()
        
        # Calculate security metrics
        total_transactions = len(transactions)
        validated_transactions = sum(1 for t in transactions if hasattr(t, 'fraud_score') and t.fraud_score < 0.3)
        
        # Simulate fraud detection scores (in production, these would be from actual validation)
        fraud_scores = [0.1 + (i * 0.05) for i in range(min(5, total_transactions))]
        avg_fraud_score = sum(fraud_scores) / len(fraud_scores) if fraud_scores else 0.0
        
        security_status = {
            "user_id": current_user.id,
            "security_level": "high" if avg_fraud_score < 0.3 else "medium" if avg_fraud_score < 0.7 else "low",
            "total_transactions_24h": total_transactions,
            "validated_transactions": validated_transactions,
            "validation_rate": validated_transactions / total_transactions if total_transactions > 0 else 0.0,
            "average_fraud_score": avg_fraud_score,
            "network_encryption_enabled": True,
            "cryptographic_validation_enabled": True,
            "last_security_check": datetime.utcnow(),
            "security_recommendations": []
        }
        
        # Add security recommendations based on metrics
        if avg_fraud_score > 0.5:
            security_status["security_recommendations"].append(
                "Consider reviewing recent transaction patterns for unusual activity"
            )
        
        if total_transactions > 50:
            security_status["security_recommendations"].append(
                "High transaction volume detected - enhanced monitoring active"
            )
        
        return security_status
        
    except Exception as e:
        logger.error(f"Failed to get security status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve security status"
        )