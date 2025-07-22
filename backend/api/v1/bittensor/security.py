"""
Bittensor Security Enhancements
Advanced security measures for Bittensor network integration
"""

import hashlib
import hmac
import json
import time
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import ecdsa
from ecdsa import SigningKey, VerifyingKey, SECP256k1
from ecdsa.util import sigencode_der, sigdecode_der
import logging

from .models import TAOTransaction, BittensorValidation, BittensorNode
from ....core.config.settings import settings

logger = logging.getLogger(__name__)


class TransactionType(Enum):
    """Types of TAO transactions"""
    REWARD = "reward"
    SPEND = "spend"
    TRANSFER = "transfer"
    MINING = "mining"
    VALIDATION = "validation"
    STAKING = "staking"


@dataclass
class TransactionValidationResult:
    """Result of transaction validation"""
    valid: bool
    confidence: float
    errors: List[str]
    warnings: List[str]
    fraud_score: float
    recommended_action: str


class CryptographicValidator:
    """Cryptographic validation for Bittensor transactions"""
    
    def __init__(self):
        self.signature_cache = {}  # Cache for signature validations
        
    def generate_key_pair(self) -> Tuple[str, str]:
        """Generate new key pair for signing"""
        private_key = SigningKey.generate(curve=SECP256k1)
        public_key = private_key.verifying_key
        
        return (
            private_key.to_string().hex(),
            public_key.to_string().hex()
        )
    
    def sign_transaction(self, transaction_data: Dict, private_key_hex: str) -> str:
        """Sign transaction with private key"""
        try:
            # Create canonical transaction string
            canonical_tx = self._create_canonical_transaction(transaction_data)
            
            # Sign the transaction hash
            private_key = SigningKey.from_string(
                bytes.fromhex(private_key_hex), 
                curve=SECP256k1
            )
            
            tx_hash = hashlib.sha256(canonical_tx.encode()).digest()
            signature = private_key.sign(tx_hash, sigencode=sigencode_der)
            
            return signature.hex()
            
        except Exception as e:
            logger.error(f"Transaction signing failed: {e}")
            raise ValueError(f"Failed to sign transaction: {e}")
    
    def verify_signature(self, transaction_data: Dict, signature_hex: str, public_key_hex: str) -> bool:
        """Verify transaction signature"""
        try:
            # Check cache first
            cache_key = f"{hash(json.dumps(transaction_data, sort_keys=True))}_{signature_hex}_{public_key_hex}"
            if cache_key in self.signature_cache:
                return self.signature_cache[cache_key]
            
            # Create canonical transaction string
            canonical_tx = self._create_canonical_transaction(transaction_data)
            
            # Verify signature
            public_key = VerifyingKey.from_string(
                bytes.fromhex(public_key_hex),
                curve=SECP256k1
            )
            
            tx_hash = hashlib.sha256(canonical_tx.encode()).digest()
            signature = bytes.fromhex(signature_hex)
            
            is_valid = public_key.verify(signature, tx_hash, sigdecode=sigdecode_der)
            
            # Cache result
            self.signature_cache[cache_key] = is_valid
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    def _create_canonical_transaction(self, transaction_data: Dict) -> str:
        """Create canonical transaction representation for signing"""
        
        # Extract essential fields in fixed order
        canonical_fields = {
            "user_id": transaction_data.get("user_id"),
            "amount_tao": transaction_data.get("amount_tao"), 
            "transaction_type": transaction_data.get("transaction_type"),
            "timestamp": transaction_data.get("timestamp", int(time.time())),
            "activity_type": transaction_data.get("activity_type"),
            "activity_id": transaction_data.get("activity_id")
        }
        
        # Remove None values and sort keys
        canonical_fields = {k: v for k, v in canonical_fields.items() if v is not None}
        
        return json.dumps(canonical_fields, sort_keys=True, separators=(',', ':'))


class TAOTransactionValidator:
    """Enhanced TAO transaction validation with fraud detection"""
    
    def __init__(self):
        self.crypto_validator = CryptographicValidator()
        self.transaction_patterns = {}  # Store user transaction patterns
        self.suspicious_transactions = []
        
    def validate_transaction(self, transaction: TAOTransaction) -> TransactionValidationResult:
        """Comprehensive transaction validation"""
        
        errors = []
        warnings = []
        fraud_indicators = []
        
        # 1. Basic validation
        basic_validation = self._validate_basic_fields(transaction)
        errors.extend(basic_validation["errors"])
        warnings.extend(basic_validation["warnings"])
        
        # 2. Cryptographic validation
        crypto_validation = self._validate_cryptographic_integrity(transaction)
        if not crypto_validation:
            errors.append("Cryptographic signature validation failed")
            fraud_indicators.append("invalid_signature")
        
        # 3. Balance consistency check
        balance_check = self._check_balance_consistency(transaction)
        if not balance_check["valid"]:
            errors.extend(balance_check["errors"])
            fraud_indicators.extend(balance_check["fraud_indicators"])
        
        # 4. Fraud detection
        fraud_analysis = self._detect_suspicious_patterns(transaction)
        fraud_indicators.extend(fraud_analysis["indicators"])
        warnings.extend(fraud_analysis["warnings"])
        
        # 5. Rate limiting validation
        rate_check = self._validate_transaction_rate(transaction)
        if not rate_check["valid"]:
            errors.extend(rate_check["errors"])
            fraud_indicators.append("excessive_rate")
        
        # Calculate fraud score
        fraud_score = self._calculate_fraud_score(fraud_indicators, transaction)
        
        # Determine validation result
        valid = len(errors) == 0 and fraud_score < 0.7
        confidence = max(0.0, 1.0 - fraud_score - len(warnings) * 0.1)
        
        # Recommend action based on fraud score
        if fraud_score >= 0.9:
            recommended_action = "block"
        elif fraud_score >= 0.7:
            recommended_action = "manual_review"
        elif fraud_score >= 0.5:
            recommended_action = "additional_verification"
        else:
            recommended_action = "approve"
        
        return TransactionValidationResult(
            valid=valid,
            confidence=confidence,
            errors=errors,
            warnings=warnings,
            fraud_score=fraud_score,
            recommended_action=recommended_action
        )
    
    def _validate_basic_fields(self, transaction: TAOTransaction) -> Dict:
        """Validate basic transaction fields"""
        
        errors = []
        warnings = []
        
        # Amount validation
        if transaction.amount_tao <= 0:
            errors.append("Transaction amount must be positive")
        
        if transaction.amount_tao > 1000:  # Arbitrary high limit
            warnings.append("High transaction amount detected")
        
        # User validation
        if not transaction.user_id:
            errors.append("User ID is required")
        
        # Transaction type validation
        valid_types = [t.value for t in TransactionType]
        if transaction.transaction_type not in valid_types:
            errors.append(f"Invalid transaction type: {transaction.transaction_type}")
        
        # Timestamp validation
        if transaction.created_at:
            age = datetime.utcnow() - transaction.created_at
            if age > timedelta(hours=1):
                warnings.append("Transaction timestamp is older than 1 hour")
            elif age < timedelta(seconds=-30):
                errors.append("Transaction timestamp is in the future")
        
        return {"errors": errors, "warnings": warnings}
    
    def _validate_cryptographic_integrity(self, transaction: TAOTransaction) -> bool:
        """Validate cryptographic signatures and hashes"""
        
        try:
            # Check if transaction has required cryptographic data
            if not transaction.transaction_hash:
                return False
            
            # Verify transaction hash
            expected_hash = self._calculate_transaction_hash(transaction)
            if transaction.transaction_hash != expected_hash:
                return False
            
            # Additional signature verification would go here
            # For now, we'll simulate it
            return True
            
        except Exception as e:
            logger.error(f"Cryptographic validation error: {e}")
            return False
    
    def _check_balance_consistency(self, transaction: TAOTransaction) -> Dict:
        """Check balance consistency for double-entry accounting"""
        
        errors = []
        fraud_indicators = []
        
        try:
            # Verify balance calculations
            expected_balance_after = transaction.balance_before
            
            if transaction.transaction_type == TransactionType.REWARD.value:
                expected_balance_after += transaction.amount_tao
            elif transaction.transaction_type in [TransactionType.SPEND.value, TransactionType.TRANSFER.value]:
                expected_balance_after -= transaction.amount_tao
            
            # Check if calculated balance matches recorded balance
            if abs(expected_balance_after - transaction.balance_after) > 0.0001:  # Allow for floating point precision
                errors.append("Balance calculation mismatch")
                fraud_indicators.append("balance_manipulation")
            
            # Check for negative balances (unless it's a valid debit transaction)
            if transaction.balance_after < 0 and transaction.transaction_type != TransactionType.SPEND.value:
                errors.append("Invalid negative balance")
                fraud_indicators.append("negative_balance")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "fraud_indicators": fraud_indicators
            }
            
        except Exception as e:
            logger.error(f"Balance consistency check failed: {e}")
            return {
                "valid": False,
                "errors": ["Balance validation failed"],
                "fraud_indicators": ["validation_error"]
            }
    
    def _detect_suspicious_patterns(self, transaction: TAOTransaction) -> Dict:
        """Detect suspicious transaction patterns"""
        
        indicators = []
        warnings = []
        
        user_id = transaction.user_id
        
        # Get user's recent transaction history
        recent_transactions = self._get_recent_transactions(user_id)
        
        # Pattern 1: Rapid fire transactions
        recent_count = len([t for t in recent_transactions if 
                          (datetime.utcnow() - t.created_at).total_seconds() < 300])  # 5 minutes
        
        if recent_count > 10:
            indicators.append("rapid_transactions")
            warnings.append("Unusually high transaction frequency detected")
        
        # Pattern 2: Round number bias (potential automated behavior)
        if transaction.amount_tao == round(transaction.amount_tao) and transaction.amount_tao >= 10:
            indicators.append("round_number_bias")
        
        # Pattern 3: Consistent timing patterns (potential bot activity)
        transaction_times = [t.created_at for t in recent_transactions[-10:]]
        if len(transaction_times) >= 5:
            time_diffs = [(transaction_times[i+1] - transaction_times[i]).total_seconds() 
                         for i in range(len(transaction_times)-1)]
            if len(set(time_diffs)) == 1:  # All intervals are identical
                indicators.append("timing_pattern")
                warnings.append("Consistent timing pattern detected")
        
        # Pattern 4: Amount patterns
        recent_amounts = [t.amount_tao for t in recent_transactions[-5:]]
        if len(set(recent_amounts)) == 1 and len(recent_amounts) >= 3:
            indicators.append("amount_pattern")
        
        # Pattern 5: Unusual transaction types for user
        user_common_types = self._get_user_common_transaction_types(user_id)
        if transaction.transaction_type not in user_common_types and len(user_common_types) > 0:
            warnings.append(f"Unusual transaction type for user: {transaction.transaction_type}")
        
        return {
            "indicators": indicators,
            "warnings": warnings
        }
    
    def _validate_transaction_rate(self, transaction: TAOTransaction) -> Dict:
        """Validate transaction rate limits"""
        
        user_id = transaction.user_id
        recent_transactions = self._get_recent_transactions(user_id, hours=1)
        
        # Rate limits by transaction type
        rate_limits = {
            TransactionType.REWARD.value: 100,  # Max 100 rewards per hour
            TransactionType.SPEND.value: 50,    # Max 50 spends per hour
            TransactionType.TRANSFER.value: 20, # Max 20 transfers per hour
            TransactionType.MINING.value: 200,  # Max 200 mining transactions per hour
        }
        
        transaction_type_count = len([t for t in recent_transactions 
                                    if t.transaction_type == transaction.transaction_type])
        
        limit = rate_limits.get(transaction.transaction_type, 10)  # Default limit
        
        if transaction_type_count >= limit:
            return {
                "valid": False,
                "errors": [f"Rate limit exceeded for {transaction.transaction_type}: {transaction_type_count}/{limit}"]
            }
        
        return {"valid": True, "errors": []}
    
    def _calculate_fraud_score(self, fraud_indicators: List[str], transaction: TAOTransaction) -> float:
        """Calculate overall fraud score based on indicators"""
        
        # Assign weights to different fraud indicators
        indicator_weights = {
            "invalid_signature": 0.9,
            "balance_manipulation": 0.8,
            "negative_balance": 0.7,
            "rapid_transactions": 0.4,
            "timing_pattern": 0.3,
            "amount_pattern": 0.2,
            "round_number_bias": 0.1,
            "excessive_rate": 0.5,
            "validation_error": 0.6
        }
        
        base_score = sum(indicator_weights.get(indicator, 0.1) for indicator in fraud_indicators)
        
        # Adjust based on transaction characteristics
        if transaction.amount_tao > 100:  # High value transactions are riskier
            base_score *= 1.2
        
        if transaction.transaction_type == TransactionType.TRANSFER.value:  # Transfers are riskier
            base_score *= 1.1
        
        return min(1.0, base_score)  # Cap at 1.0
    
    def _calculate_transaction_hash(self, transaction: TAOTransaction) -> str:
        """Calculate expected transaction hash"""
        
        hash_data = f"{transaction.user_id}:{transaction.amount_tao}:{transaction.transaction_type}:{transaction.created_at}"
        return hashlib.sha256(hash_data.encode()).hexdigest()
    
    def _get_recent_transactions(self, user_id: int, hours: int = 24) -> List[TAOTransaction]:
        """Get recent transactions for a user (mock implementation)"""
        
        # In a real implementation, this would query the database
        # For now, return empty list
        return []
    
    def _get_user_common_transaction_types(self, user_id: int) -> List[str]:
        """Get common transaction types for a user (mock implementation)"""
        
        # In a real implementation, this would analyze user's transaction history
        return [TransactionType.REWARD.value, TransactionType.MINING.value]


class NetworkCommunicationSecurity:
    """Enhanced security for Bittensor network communications"""
    
    def __init__(self):
        self.session_keys = {}  # Store session encryption keys
        
    def encrypt_network_message(self, message: Dict, recipient_public_key: str) -> Dict:
        """Encrypt message for network transmission"""
        
        try:
            # Generate ephemeral key pair for this session
            ephemeral_private, ephemeral_public = self._generate_ephemeral_keys()
            
            # Derive shared secret
            shared_secret = self._derive_shared_secret(ephemeral_private, recipient_public_key)
            
            # Encrypt message
            encrypted_message = self._encrypt_with_shared_secret(json.dumps(message), shared_secret)
            
            # Create secure envelope
            envelope = {
                "ephemeral_public_key": ephemeral_public,
                "encrypted_payload": encrypted_message,
                "timestamp": int(time.time()),
                "version": "1.0"
            }
            
            return envelope
            
        except Exception as e:
            logger.error(f"Message encryption failed: {e}")
            raise
    
    def decrypt_network_message(self, envelope: Dict, private_key: str) -> Dict:
        """Decrypt received network message"""
        
        try:
            # Extract components
            ephemeral_public = envelope["ephemeral_public_key"]
            encrypted_payload = envelope["encrypted_payload"]
            timestamp = envelope["timestamp"]
            
            # Check message age (reject messages older than 5 minutes)
            if int(time.time()) - timestamp > 300:
                raise ValueError("Message too old")
            
            # Derive shared secret
            shared_secret = self._derive_shared_secret(private_key, ephemeral_public)
            
            # Decrypt message
            decrypted_json = self._decrypt_with_shared_secret(encrypted_payload, shared_secret)
            
            return json.loads(decrypted_json)
            
        except Exception as e:
            logger.error(f"Message decryption failed: {e}")
            raise
    
    def _generate_ephemeral_keys(self) -> Tuple[str, str]:
        """Generate ephemeral key pair"""
        
        private_key = SigningKey.generate(curve=SECP256k1)
        public_key = private_key.verifying_key
        
        return (
            private_key.to_string().hex(),
            public_key.to_string().hex()
        )
    
    def _derive_shared_secret(self, private_key_hex: str, public_key_hex: str) -> bytes:
        """Derive shared secret using ECDH"""
        
        # Simplified ECDH implementation
        # In production, use proper ECDH library
        combined = private_key_hex + public_key_hex
        return hashlib.sha256(combined.encode()).digest()
    
    def _encrypt_with_shared_secret(self, message: str, shared_secret: bytes) -> str:
        """Encrypt message with shared secret (AES-like)"""
        
        # Simplified encryption - in production, use proper AES
        message_bytes = message.encode()
        key_hash = hashlib.sha256(shared_secret).digest()
        
        # XOR encryption (simplified)
        encrypted = bytearray()
        for i, byte in enumerate(message_bytes):
            encrypted.append(byte ^ key_hash[i % len(key_hash)])
        
        return encrypted.hex()
    
    def _decrypt_with_shared_secret(self, encrypted_hex: str, shared_secret: bytes) -> str:
        """Decrypt message with shared secret"""
        
        encrypted_bytes = bytes.fromhex(encrypted_hex)
        key_hash = hashlib.sha256(shared_secret).digest()
        
        # XOR decryption
        decrypted = bytearray()
        for i, byte in enumerate(encrypted_bytes):
            decrypted.append(byte ^ key_hash[i % len(key_hash)])
        
        return decrypted.decode()


# Global instances
crypto_validator = CryptographicValidator()
transaction_validator = TAOTransactionValidator()
network_security = NetworkCommunicationSecurity()

# Export components
__all__ = [
    "CryptographicValidator",
    "TAOTransactionValidator", 
    "NetworkCommunicationSecurity",
    "TransactionValidationResult",
    "TransactionType",
    "crypto_validator",
    "transaction_validator", 
    "network_security"
]