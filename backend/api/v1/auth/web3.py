import os
import random
import string
from eth_account.messages import encode_defunct
from eth_account import Account

def generate_nonce(length=32):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def verify_signature(message, signature, address):
    message_hash = encode_defunct(text=message)
    recovered_address = Account.recover_message(message_hash, signature=signature)
    return recovered_address.lower() == address.lower()
