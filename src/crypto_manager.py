#!/usr/bin/env python3

import os
import base64
import hashlib
import secrets
import hmac
from typing import Union

class CryptoManager:
    """Manages cryptographic operations for the system using standard library only"""
    
    def __init__(self):
        """Initialize the crypto manager"""
        self.key_file = 'system.key'
        self._encryption_key = None
        self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Initialize encryption key"""
        # Check if key file exists
        if os.path.exists(self.key_file):
            # Load existing key
            with open(self.key_file, 'rb') as f:
                self._encryption_key = f.read()
        else:
            # Generate new key
            self._generate_new_key()
    
    def _generate_new_key(self):
        """Generate a new encryption key"""
        # Generate a 32-byte key
        key = os.urandom(32)
        
        # Save key
        with open(self.key_file, 'wb') as f:
            f.write(key)
        
        self._encryption_key = key
    
    def _xor_encrypt_decrypt(self, data: bytes, key: bytes) -> bytes:
        """Simple XOR encryption/decryption (symmetric)"""
        result = bytearray()
        key_len = len(key)
        
        for i, byte in enumerate(data):
            result.append(byte ^ key[i % key_len])
        
        return bytes(result)
    
    def encrypt(self, data: str) -> str:
        """Encrypt a string and return base64 encoded result"""
        if not isinstance(data, str):
            raise ValueError("Data must be a string")
        
        if not data:
            return ""
        
        try:
            # Convert string to bytes
            data_bytes = data.encode('utf-8')
            
            # Add a random salt at the beginning
            salt = os.urandom(16)
            data_with_salt = salt + data_bytes
            
            # Encrypt using XOR with key
            encrypted_data = self._xor_encrypt_decrypt(data_with_salt, self._encryption_key)
            
            # Return base64 encoded result
            return base64.b64encode(encrypted_data).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Encryption failed: {e}")
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt base64 encoded encrypted data"""
        if not isinstance(encrypted_data, str):
            raise ValueError("Encrypted data must be a string")
        
        if not encrypted_data:
            return ""
        
        try:
            # Decode from base64
            decoded_data = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # Decrypt using XOR with key
            decrypted_data = self._xor_encrypt_decrypt(decoded_data, self._encryption_key)
            
            # Remove salt (first 16 bytes) and decode to string
            data_without_salt = decrypted_data[16:]
            return data_without_salt.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hash a password using SHA-256 with salt"""
        if not isinstance(password, str):
            raise ValueError("Password must be a string")
        
        # Generate a random salt for this password
        salt = secrets.token_hex(16)
        
        # Hash the password with salt using SHA-256
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        
        # Return salt and hash combined
        return f"{salt}:{password_hash}"
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify a password against a stored hash"""
        if not isinstance(password, str) or not isinstance(stored_hash, str):
            return False
        
        try:
            # Split stored hash into salt and hash
            salt, hash_value = stored_hash.split(':')
            
            # Hash the provided password with the same salt
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            
            # Compare hashes using constant-time comparison
            return hmac.compare_digest(password_hash, hash_value)
        except Exception:
            return False
    
    def generate_token(self, length: int = 32) -> str:
        """Generate a secure random token"""
        return secrets.token_urlsafe(length)
    
    def hash_data(self, data: str) -> str:
        """Generate SHA-256 hash of data"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def pbkdf2_derive_key(self, password: str, salt: bytes, iterations: int = 100000) -> bytes:
        """Derive a key from password using PBKDF2"""
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)
