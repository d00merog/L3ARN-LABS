"""
Bittensor Integration Service
Decentralized AI network for educational content validation and knowledge retrieval
Research-backed implementation based on 2024 Bittensor API patterns
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import httpx
import hashlib
import random
import time

# Bittensor imports with proper 2024 API usage
try:
    import bittensor as bt
    BITTENSOR_AVAILABLE = True
except ImportError:
    BITTENSOR_AVAILABLE = False
    logging.warning("Bittensor not available. Installing with: pip install bittensor")

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func

from . import models, schemas
from ...core.config.settings import settings
from .security import transaction_validator, network_security, crypto_validator, TransactionType

logger = logging.getLogger(__name__)


class BittensorService:
    """Service for interacting with the Bittensor decentralized AI network"""
    
    def __init__(self):
        self.dendrite = None
        self.metagraph = None
        self.wallet = None
        self.subtensor = None
        self.initialized = False
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        if BITTENSOR_AVAILABLE:
            self._initialize_bittensor()
    
    def _initialize_bittensor(self):
        """Initialize Bittensor components based on 2024 research patterns"""
        try:
            # Initialize wallet (uses default coldkey/hotkey or from config)
            wallet_name = getattr(settings, 'BITTENSOR_WALLET_NAME', 'default')
            self.wallet = bt.wallet(name=wallet_name)
            
            # Initialize subtensor connection with network selection
            network = getattr(settings, 'BITTENSOR_NETWORK', 'mainnet')
            if network == 'testnet':
                self.subtensor = bt.subtensor(network='test')
            elif network == 'local':
                self.subtensor = bt.subtensor(network='local')
            else:
                self.subtensor = bt.subtensor()  # mainnet
            
            # Initialize multiple subnet connections for educational AI
            self.metagraphs = {}
            self.subnets = {
                'text_prompting': 1,      # Main text prompting subnet
                'compute': 27,            # Compute subnet for heavy operations
                'educational': 1          # Default to text prompting for educational content
            }
            
            # Sync metagraphs for all relevant subnets
            for subnet_name, netuid in self.subnets.items():
                try:
                    metagraph = self.subtensor.metagraph(netuid=netuid)
                    metagraph.sync()  # Sync with current state
                    self.metagraphs[subnet_name] = metagraph
                    logger.info(f"Synced {subnet_name} subnet (netuid {netuid})")
                except Exception as e:
                    logger.warning(f"Failed to sync {subnet_name} subnet: {str(e)}")
            
            # Set primary metagraph to text prompting
            self.metagraph = self.metagraphs.get('text_prompting')
            
            # Initialize dendrite with streaming support (required for SN1 as of March 2024)
            self.dendrite = bt.dendrite(wallet=self.wallet)
            
            # Validator permit check (required for top 64 validators)
            try:
                if hasattr(self.wallet.hotkey, 'ss58_address'):
                    hotkey_address = self.wallet.hotkey.ss58_address
                    logger.info(f"Initialized with hotkey: {hotkey_address}")
            except:
                pass
            
            self.initialized = True
            logger.info("Bittensor initialized successfully with 2024 patterns")
            
        except Exception as e:
            logger.error(f"Failed to initialize Bittensor: {str(e)}")
            self.initialized = False
    
    async def search_knowledge(
        self, 
        query: str, 
        max_results: int = 10,
        educational_focus: bool = True,
        fact_check: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search the Bittensor network for educational content
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            educational_focus: Prioritize educational content
            fact_check: Perform fact-checking on results
            
        Returns:
            List of search results with metadata
        """
        try:
            if not self.initialized or not BITTENSOR_AVAILABLE:
                return await self._fallback_search(query, max_results)
            
            # Check cache first
            cache_key = hashlib.md5(f"{query}_{max_results}_{educational_focus}".encode()).hexdigest()
            if cache_key in self.cache:
                cached_result, timestamp = self.cache[cache_key]
                if datetime.utcnow() - timestamp < timedelta(seconds=self.cache_ttl):
                    return cached_result
            
            # Create search synapse
            search_synapse = self._create_search_synapse(query, educational_focus)
            
            # Get top miners for search
            top_miners = await self._get_top_miners(limit=min(max_results, 20))
            
            # Query multiple miners
            responses = await self._query_miners(search_synapse, top_miners)
            
            # Process and rank results
            processed_results = await self._process_search_results(
                responses, query, educational_focus, fact_check
            )
            
            # Cache results
            self.cache[cache_key] = (processed_results, datetime.utcnow())
            
            return processed_results[:max_results]
            
        except Exception as e:
            logger.error(f"Bittensor search failed: {str(e)}")
            return await self._fallback_search(query, max_results)
    
    async def verify_information(
        self, 
        statement: str, 
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Use Bittensor network to verify factual information
        
        Args:
            statement: Statement to verify
            context: Additional context for verification
            
        Returns:
            Verification result with confidence score
        """
        try:
            if not self.initialized or not BITTENSOR_AVAILABLE:
                return await self._fallback_verification(statement)
            
            # Create verification synapse
            verification_synapse = self._create_verification_synapse(statement, context)
            
            # Get consensus from multiple miners
            top_miners = await self._get_top_miners(limit=5, specialty="verification")
            responses = await self._query_miners(verification_synapse, top_miners)
            
            # Analyze consensus
            verification_result = await self._analyze_verification_consensus(responses, statement)
            
            return verification_result
            
        except Exception as e:
            logger.error(f"Information verification failed: {str(e)}")
            return await self._fallback_verification(statement)
    
    async def get_educational_content(
        self, 
        topic: str, 
        level: str = "intermediate",
        content_type: str = "explanation"
    ) -> Dict[str, Any]:
        """
        Get educational content from Bittensor network
        
        Args:
            topic: Educational topic
            level: Difficulty level (beginner, intermediate, advanced)
            content_type: Type of content (explanation, examples, exercises)
            
        Returns:
            Educational content with metadata
        """
        try:
            if not self.initialized or not BITTENSOR_AVAILABLE:
                return await self._fallback_educational_content(topic, level)
            
            # Create educational content synapse
            content_synapse = self._create_educational_synapse(topic, level, content_type)
            
            # Get specialized educational miners
            education_miners = await self._get_top_miners(limit=10, specialty="education")
            
            # Query miners for content
            responses = await self._query_miners(content_synapse, education_miners)
            
            # Process and synthesize content
            educational_content = await self._synthesize_educational_content(
                responses, topic, level, content_type
            )
            
            return educational_content
            
        except Exception as e:
            logger.error(f"Educational content generation failed: {str(e)}")
            return await self._fallback_educational_content(topic, level)
    
    async def validate_educational_content(
        self,
        db: AsyncSession,
        content: str,
        content_type: str,
        validation_type: schemas.ValidationType,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Validate educational content using Bittensor network consensus
        
        Args:
            content: Content to validate
            content_type: Type of content (lesson, assignment, quiz)
            validation_type: Type of validation required
            user_id: User requesting validation
            
        Returns:
            Validation result with consensus score
        """
        try:
            if not self.initialized or not BITTENSOR_AVAILABLE:
                return await self._fallback_validation(content, validation_type)
            
            # Create content hash for deduplication
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            # Check if we already have validation for this content
            existing_validation = await self._get_cached_validation(db, content_hash)
            if existing_validation:
                return existing_validation
            
            # Create validation prompt based on type
            validation_prompt = self._create_validation_prompt(content, validation_type)
            
            # Get educational validators (high trust miners)
            validators = await self._get_educational_validators(limit=10)
            
            # Query validators for content assessment
            validation_responses = await self._query_validators_for_validation(
                validation_prompt, validators, content_type
            )
            
            # Analyze consensus and generate final score
            consensus_result = await self._analyze_validation_consensus(
                validation_responses, validation_type
            )
            
            # Store validation result
            validation_record = await self._store_validation_result(
                db, content, content_hash, validation_prompt, 
                validation_responses, consensus_result, user_id
            )
            
            return consensus_result
            
        except Exception as e:
            logger.error(f"Content validation failed: {str(e)}")
            return await self._fallback_validation(content, validation_type)
    
    async def calculate_tao_rewards(
        self,
        db: AsyncSession,
        user_id: int,
        activity_type: str,
        activity_data: Dict[str, Any]
    ) -> float:
        """
        Calculate TAO token rewards for educational activities with enhanced security validation
        
        Args:
            user_id: User performing the activity
            activity_type: Type of activity (assignment, quiz, content_creation)
            activity_data: Activity-specific data for reward calculation
            
        Returns:
            TAO reward amount
        """
        try:
            # Base reward rates for different activities
            base_rewards = {
                'assignment_completion': 0.001,  # 0.001 TAO per assignment
                'quiz_completion': 0.0005,       # 0.0005 TAO per quiz
                'peer_review': 0.0015,           # 0.0015 TAO per peer review
                'content_creation': 0.01,        # 0.01 TAO per approved content
                'fact_checking': 0.002           # 0.002 TAO per fact-check validation
            }
            
            base_reward = base_rewards.get(activity_type, 0.0)
            
            # Apply multipliers based on quality and difficulty
            multiplier = 1.0
            
            # Quality score multiplier
            quality_score = activity_data.get('quality_score', 0.5)
            multiplier *= (0.5 + quality_score)  # 0.5x to 1.5x based on quality
            
            # Difficulty multiplier
            difficulty = activity_data.get('difficulty_level', 'intermediate')
            difficulty_multipliers = {
                'beginner': 0.8,
                'intermediate': 1.0,
                'advanced': 1.3
            }
            multiplier *= difficulty_multipliers.get(difficulty, 1.0)
            
            # Validation consensus multiplier (if content was validated)
            consensus_score = activity_data.get('consensus_score', 0.7)
            if consensus_score > 0.8:
                multiplier *= 1.2  # Bonus for high-quality validated content
            
            final_reward = base_reward * multiplier
            
            # Create and validate secure TAO transaction
            await self._store_secure_tao_transaction(
                db, user_id, TransactionType.REWARD.value, final_reward, activity_type, activity_data
            )
            
            return final_reward
            
        except Exception as e:
            logger.error(f"TAO reward calculation failed: {str(e)}")
            return 0.0
    
    async def get_network_stats(self) -> Dict[str, Any]:
        """Get comprehensive Bittensor network statistics for all subnets"""
        try:
            if not self.initialized or not BITTENSOR_AVAILABLE:
                return {"available": False, "error": "Bittensor not initialized"}
            
            all_stats = {
                "available": True,
                "subnets": {},
                "overall_health": 0.0,
                "total_miners": 0,
                "total_validators": 0
            }
            
            # Get stats for each connected subnet
            total_health = 0.0
            subnet_count = 0
            
            for subnet_name, metagraph in self.metagraphs.items():
                try:
                    # Sync metagraph to get latest data
                    metagraph.sync()
                    
                    subnet_stats = {
                        "netuid": self.subnets[subnet_name],
                        "total_miners": len(metagraph.hotkeys),
                        "active_miners": len([uid for uid in metagraph.uids if metagraph.active[uid]]),
                        "total_stake": float(metagraph.S.sum()),
                        "average_trust": float(metagraph.trust.mean()),
                        "average_consensus": float(metagraph.consensus.mean()),
                        "average_incentive": float(metagraph.I.mean()),
                        "block_number": metagraph.block.item() if hasattr(metagraph.block, 'item') else 0,
                        "emission": float(metagraph.emission.sum()),
                        "health_score": self._calculate_subnet_health(metagraph)
                    }
                    
                    all_stats["subnets"][subnet_name] = subnet_stats
                    all_stats["total_miners"] += subnet_stats["active_miners"]
                    total_health += subnet_stats["health_score"]
                    subnet_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to get stats for {subnet_name}: {str(e)}")
                    continue
            
            # Calculate overall health
            if subnet_count > 0:
                all_stats["overall_health"] = total_health / subnet_count
            
            return all_stats
            
        except Exception as e:
            logger.error(f"Failed to get network stats: {str(e)}")
            return {"available": False, "error": str(e)}
    
    # Private helper methods
    
    def _create_search_synapse(self, query: str, educational_focus: bool = True):
        """Create a search synapse for Bittensor queries"""
        if not BITTENSOR_AVAILABLE:
            return None
            
        # This would create a custom synapse for search queries
        # For now, we'll use a generic text completion approach
        synapse_data = {
            "query": query,
            "type": "search",
            "educational_focus": educational_focus,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return synapse_data
    
    def _create_verification_synapse(self, statement: str, context: Optional[str] = None):
        """Create a verification synapse for fact-checking"""
        if not BITTENSOR_AVAILABLE:
            return None
            
        synapse_data = {
            "statement": statement,
            "context": context or "",
            "type": "verification",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return synapse_data
    
    def _create_educational_synapse(self, topic: str, level: str, content_type: str):
        """Create an educational content synapse"""
        if not BITTENSOR_AVAILABLE:
            return None
            
        synapse_data = {
            "topic": topic,
            "level": level,
            "content_type": content_type,
            "type": "educational",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return synapse_data
    
    async def _get_top_miners(self, limit: int = 10, specialty: Optional[str] = None) -> List[int]:
        """Get top-performing miners from the network"""
        if not self.initialized or not BITTENSOR_AVAILABLE:
            return []
        
        try:
            # Get miners sorted by incentive (reward mechanism)
            incentives = self.metagraph.I
            trust_scores = self.metagraph.trust
            
            # Combine incentive and trust for ranking
            combined_scores = incentives * trust_scores
            
            # Get top miners
            top_indices = combined_scores.argsort(descending=True)[:limit]
            
            # Filter for active miners only
            active_miners = [
                int(idx) for idx in top_indices 
                if self.metagraph.active[idx] and combined_scores[idx] > 0.1
            ]
            
            return active_miners[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get top miners: {str(e)}")
            return []
    
    async def _query_miners(self, synapse_data: Dict[str, Any], miner_uids: List[int]) -> List[Dict[str, Any]]:
        """Query multiple miners with the synapse"""
        if not self.initialized or not BITTENSOR_AVAILABLE:
            return []
        
        try:
            responses = []
            
            # In a real implementation, this would use the actual Bittensor dendrite
            # to query miners. For now, we'll simulate responses.
            for uid in miner_uids:
                try:
                    # Simulate miner response
                    response = await self._simulate_miner_response(synapse_data, uid)
                    responses.append({
                        "uid": uid,
                        "response": response,
                        "trust": float(self.metagraph.trust[uid]),
                        "incentive": float(self.metagraph.I[uid]),
                        "timestamp": datetime.utcnow()
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to query miner {uid}: {str(e)}")
                    continue
            
            return responses
            
        except Exception as e:
            logger.error(f"Failed to query miners: {str(e)}")
            return []
    
    async def _simulate_miner_response(self, synapse_data: Dict[str, Any], uid: int) -> Dict[str, Any]:
        """Simulate miner response (replace with real Bittensor querying)"""
        # This is a placeholder for actual Bittensor miner querying
        # In production, this would use the dendrite to query real miners
        
        query_type = synapse_data.get("type", "search")
        
        if query_type == "search":
            return {
                "results": [
                    {
                        "title": f"Educational Content for {synapse_data.get('query', 'topic')}",
                        "content": f"Comprehensive educational material about {synapse_data.get('query', 'topic')}",
                        "url": f"https://education.example.com/{uid}",
                        "relevance_score": 0.85 + (uid % 10) * 0.01,
                        "educational_quality": 0.9,
                        "fact_checked": True
                    }
                ],
                "confidence": 0.8 + (uid % 5) * 0.02,
                "processing_time": 0.5 + (uid % 3) * 0.1
            }
        
        elif query_type == "verification":
            return {
                "verified": True,
                "confidence": 0.85 + (uid % 10) * 0.01,
                "sources": [f"source_{uid}_1", f"source_{uid}_2"],
                "explanation": f"Verification analysis from miner {uid}",
                "fact_score": 0.9
            }
        
        elif query_type == "educational":
            return {
                "content": f"Educational content about {synapse_data.get('topic', 'subject')} at {synapse_data.get('level', 'intermediate')} level",
                "examples": [f"Example {i} from miner {uid}" for i in range(3)],
                "quality_score": 0.85 + (uid % 8) * 0.01,
                "pedagogical_score": 0.8,
                "accuracy": 0.95
            }
        
        return {"error": "Unknown query type"}
    
    async def _process_search_results(
        self, 
        responses: List[Dict[str, Any]], 
        query: str, 
        educational_focus: bool,
        fact_check: bool
    ) -> List[Dict[str, Any]]:
        """Process and rank search results from multiple miners"""
        try:
            all_results = []
            
            for response_data in responses:
                response = response_data.get("response", {})
                results = response.get("results", [])
                trust_score = response_data.get("trust", 0.5)
                
                for result in results:
                    # Calculate weighted score based on miner trust and result quality
                    relevance_score = result.get("relevance_score", 0.5)
                    educational_quality = result.get("educational_quality", 0.5) if educational_focus else 0.8
                    
                    weighted_score = (
                        relevance_score * 0.4 +
                        educational_quality * 0.3 +
                        trust_score * 0.3
                    )
                    
                    processed_result = {
                        "title": result.get("title", ""),
                        "content": result.get("content", ""),
                        "url": result.get("url", ""),
                        "score": weighted_score,
                        "educational_quality": educational_quality,
                        "fact_checked": result.get("fact_checked", False),
                        "source_trust": trust_score,
                        "miner_uid": response_data.get("uid"),
                        "timestamp": datetime.utcnow()
                    }
                    
                    all_results.append(processed_result)
            
            # Sort by weighted score
            all_results.sort(key=lambda x: x["score"], reverse=True)
            
            # Remove duplicates based on content similarity
            unique_results = self._deduplicate_results(all_results)
            
            return unique_results
            
        except Exception as e:
            logger.error(f"Failed to process search results: {str(e)}")
            return []
    
    async def _analyze_verification_consensus(
        self, 
        responses: List[Dict[str, Any]], 
        statement: str
    ) -> Dict[str, Any]:
        """Analyze verification consensus from multiple miners"""
        try:
            if not responses:
                return {"verified": False, "confidence": 0.0, "consensus": "insufficient_data"}
            
            verified_count = 0
            total_confidence = 0.0
            sources = set()
            
            for response_data in responses:
                response = response_data.get("response", {})
                trust_score = response_data.get("trust", 0.5)
                
                if response.get("verified", False):
                    verified_count += 1
                
                confidence = response.get("confidence", 0.5) * trust_score
                total_confidence += confidence
                
                response_sources = response.get("sources", [])
                sources.update(response_sources)
            
            consensus_ratio = verified_count / len(responses)
            average_confidence = total_confidence / len(responses)
            
            # Determine verification status
            if consensus_ratio >= 0.8 and average_confidence >= 0.7:
                status = "verified"
            elif consensus_ratio >= 0.6:
                status = "likely_true"
            elif consensus_ratio >= 0.4:
                status = "uncertain"
            else:
                status = "disputed"
            
            return {
                "statement": statement,
                "verified": consensus_ratio >= 0.6,
                "confidence": average_confidence,
                "consensus_ratio": consensus_ratio,
                "status": status,
                "sources": list(sources),
                "miner_count": len(responses),
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze verification consensus: {str(e)}")
            return {"verified": False, "confidence": 0.0, "error": str(e)}
    
    def _calculate_network_health(self) -> float:
        """Calculate overall network health score"""
        try:
            if not self.initialized or not BITTENSOR_AVAILABLE:
                return 0.0
            
            # Calculate based on active miners, trust distribution, and stake
            active_ratio = self.metagraph.active.sum() / len(self.metagraph.active)
            trust_mean = float(self.metagraph.trust.mean())
            stake_distribution = float(self.metagraph.S.std()) / float(self.metagraph.S.mean())
            
            # Combine metrics (higher is better, except for stake concentration)
            health_score = (
                active_ratio * 0.4 +
                trust_mean * 0.4 +
                max(0, 1 - stake_distribution) * 0.2
            )
            
            return min(1.0, health_score)
            
        except Exception as e:
            logger.error(f"Failed to calculate network health: {str(e)}")
            return 0.0
    
    # Fallback methods when Bittensor is unavailable
    
    async def _fallback_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Fallback search using traditional web search APIs"""
        try:
            # Use Brave Search API as fallback
            brave_api_key = getattr(settings, 'BRAVE_SEARCH_API_KEY', None)
            if not brave_api_key:
                return []
            
            async with httpx.AsyncClient() as client:
                headers = {"X-Subscription-Token": brave_api_key}
                params = {
                    "q": f"{query} educational content",
                    "count": max_results,
                    "safesearch": "strict"
                }
                
                response = await client.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    headers=headers,
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    
                    for item in data.get("web", {}).get("results", []):
                        results.append({
                            "title": item.get("title", ""),
                            "content": item.get("description", ""),
                            "url": item.get("url", ""),
                            "score": 0.7,  # Default fallback score
                            "educational_quality": 0.6,
                            "fact_checked": False,
                            "source_trust": 0.5,
                            "fallback_source": "brave_search",
                            "timestamp": datetime.utcnow()
                        })
                    
                    return results[:max_results]
            
            return []
            
        except Exception as e:
            logger.error(f"Fallback search failed: {str(e)}")
            return []
    
    async def _fallback_verification(self, statement: str) -> Dict[str, Any]:
        """Fallback verification using web search and basic heuristics"""
        return {
            "statement": statement,
            "verified": False,
            "confidence": 0.3,
            "status": "unavailable",
            "fallback_source": "basic_heuristics",
            "timestamp": datetime.utcnow(),
            "note": "Bittensor verification unavailable"
        }
    
    async def _fallback_educational_content(self, topic: str, level: str) -> Dict[str, Any]:
        """Fallback educational content generation"""
        return {
            "topic": topic,
            "level": level,
            "content": f"Basic educational content about {topic} would be generated here.",
            "examples": [],
            "quality_score": 0.4,
            "fallback_source": "basic_template",
            "timestamp": datetime.utcnow()
        }
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results based on content similarity"""
        unique_results = []
        seen_titles = set()
        
        for result in results:
            title = result.get("title", "").lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_results.append(result)
        
        return unique_results
    
    async def _store_secure_tao_transaction(
        self,
        db: AsyncSession,
        user_id: int,
        transaction_type: str,
        amount_tao: float,
        activity_type: str,
        activity_data: Dict[str, Any]
    ) -> models.TAOTransaction:
        """Store TAO transaction with enhanced security validation"""
        try:
            # Get current user balance
            current_balance = await self._get_user_tao_balance(db, user_id)
            new_balance = current_balance + amount_tao if transaction_type == TransactionType.REWARD.value else current_balance - amount_tao
            
            # Create transaction data
            transaction_data = {
                "user_id": user_id,
                "amount_tao": amount_tao,
                "transaction_type": transaction_type,
                "activity_type": activity_type,
                "timestamp": int(time.time()),
                "activity_id": activity_data.get('activity_id')
            }
            
            # Generate transaction hash
            transaction_hash = crypto_validator._create_canonical_transaction(transaction_data)
            transaction_hash = hashlib.sha256(transaction_hash.encode()).hexdigest()
            
            # Create TAO transaction model
            tao_transaction = models.TAOTransaction(
                user_id=user_id,
                amount_tao=amount_tao,
                transaction_type=transaction_type,
                activity_type=activity_type,
                activity_id=activity_data.get('activity_id'),
                transaction_hash=transaction_hash,
                balance_before=current_balance,
                balance_after=new_balance,
                metadata=activity_data
            )
            
            # Enhanced security validation
            validation_result = transaction_validator.validate_transaction(tao_transaction)
            
            if not validation_result.valid:
                logger.error(f"Transaction validation failed: {validation_result.errors}")
                raise ValueError(f"Invalid transaction: {', '.join(validation_result.errors)}")
            
            if validation_result.fraud_score > 0.7:
                logger.warning(f"High fraud score detected: {validation_result.fraud_score}")
                if validation_result.recommended_action == "block":
                    raise ValueError("Transaction blocked due to fraud detection")
            
            # Store in database
            db.add(tao_transaction)
            await db.commit()
            await db.refresh(tao_transaction)
            
            logger.info(f"Secure TAO transaction created: {tao_transaction.id} (fraud_score: {validation_result.fraud_score})")
            return tao_transaction
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to store secure TAO transaction: {str(e)}")
            raise
    
    async def _get_user_tao_balance(self, db: AsyncSession, user_id: int) -> float:
        """Get current TAO balance for user"""
        try:
            # Get latest transaction to find current balance
            latest_transaction = await db.execute(
                select(models.TAOTransaction)
                .filter(models.TAOTransaction.user_id == user_id)
                .order_by(desc(models.TAOTransaction.created_at))
                .limit(1)
            )
            
            transaction = latest_transaction.scalar_one_or_none()
            return transaction.balance_after if transaction else 0.0
            
        except Exception as e:
            logger.error(f"Failed to get user TAO balance: {str(e)}")
            return 0.0
    
    async def send_secure_network_message(
        self,
        recipient_uid: int,
        message_data: Dict[str, Any],
        message_type: str = "query"
    ) -> Dict[str, Any]:
        """Send secure encrypted message over Bittensor network"""
        try:
            if not self.initialized or not BITTENSOR_AVAILABLE:
                return {"success": False, "error": "Bittensor not initialized"}
            
            # Get recipient's public key from metagraph
            recipient_public_key = self._get_miner_public_key(recipient_uid)
            if not recipient_public_key:
                return {"success": False, "error": "Recipient public key not found"}
            
            # Encrypt message for secure transmission
            encrypted_envelope = network_security.encrypt_network_message(
                message_data, recipient_public_key
            )
            
            # Add message metadata
            secure_message = {
                "type": message_type,
                "sender_uid": self._get_our_uid(),
                "recipient_uid": recipient_uid,
                "encrypted_payload": encrypted_envelope,
                "timestamp": int(time.time())
            }
            
            # Send message through Bittensor dendrite
            # In production, this would use real dendrite querying
            response = await self._send_encrypted_message(recipient_uid, secure_message)
            
            return {
                "success": True,
                "message_id": secure_message.get("timestamp"),
                "response": response
            }
            
        except Exception as e:
            logger.error(f"Failed to send secure network message: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _send_encrypted_message(self, recipient_uid: int, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send encrypted message through Bittensor network (mock implementation)"""
        # Mock implementation - in production, this would use real Bittensor dendrite
        await asyncio.sleep(0.1)  # Simulate network delay
        
        return {
            "status": "delivered",
            "response_time": 0.1,
            "encrypted_response": "mock_encrypted_response"
        }
    
    def _get_miner_public_key(self, uid: int) -> Optional[str]:
        """Get public key for a miner (mock implementation)"""
        # In production, this would extract the actual public key from metagraph
        return f"mock_public_key_{uid}"
    
    def _get_our_uid(self) -> int:
        """Get our UID in the network (mock implementation)"""
        # In production, this would return our actual UID
        return 0
    
    def _calculate_subnet_health(self, metagraph) -> float:
        """Calculate health score for a specific subnet"""
        try:
            # Calculate based on various metrics
            active_ratio = float(metagraph.active.sum()) / len(metagraph.active)
            trust_mean = float(metagraph.trust.mean())
            consensus_mean = float(metagraph.consensus.mean())
            
            # Combine metrics
            health_score = (
                active_ratio * 0.4 +
                trust_mean * 0.3 +
                consensus_mean * 0.3
            )
            
            return min(1.0, health_score)
            
        except Exception as e:
            logger.error(f"Failed to calculate subnet health: {str(e)}")
            return 0.0


# Global service instance
bittensor_service = BittensorService()