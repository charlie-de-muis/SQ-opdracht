#!/usr/bin/env python3

import os
import base64
import hashlib
import secrets
from typing import Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class CryptoManager:
    """Manages cryptographic operations for the system using the cryptography library"""
    
    def __init__(self):
        """Initialize the crypto manager"""
        self.key_file = 'system.key'
        self._fernet = None
        self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Initialize encryption using Fernet (symmetric encryption)"""
        # Check if key file exists
        if os.path.exists(self.key_file):
            # Load existing key
            with open(self.key_file, 'rb') as f:
                key = f.read()
            self._fernet = Fernet(key)
        else:
            # Generate new Fernet key
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            self._fernet = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data using Fernet symmetric encryption"""
        if not isinstance(data, str):
            raise TypeError("Data must be a string")
        
        if not data:
            return ""
        
        try:
            # Convert string to bytes and encrypt
            data_bytes = data.encode('utf-8')
            encrypted_bytes = self._fernet.encrypt(data_bytes)
            # Return base64 encoded string for database storage
            return base64.b64encode(encrypted_bytes).decode('utf-8')
        except Exception as e:
            raise RuntimeError(f"Encryption failed: {e}")
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data using Fernet symmetric encryption"""
        if not isinstance(encrypted_data, str):
            raise TypeError("Encrypted data must be a string")
        
        if not encrypted_data:
            return ""
        
        try:
            # Decode from base64 and decrypt
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_bytes = self._fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            raise RuntimeError(f"Decryption failed: {e}")
    
    def hash_password(self, password: str, salt: str = None) -> str:
        """Hash a password using PBKDF2 with SHA-256"""
        if not isinstance(password, str):
            raise TypeError("Password must be a string")
        
        if salt is None:
            # Generate a random salt
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 with SHA-256
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode('utf-8'),
            iterations=100000,  # OWASP recommended minimum
        )
        
        # Generate hash
        key = kdf.derive(password.encode('utf-8'))
        hash_hex = base64.b64encode(key).decode('utf-8')
        
        # Return salt:hash format
        return f"{salt}:{hash_hex}"
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify a password against a stored hash"""
        if not isinstance(password, str) or not isinstance(stored_hash, str):
            return False
        
        try:
            # Split stored hash into salt and hash
            salt, hash_part = stored_hash.split(':', 1)
            
            # Hash the provided password with the same salt
            new_hash = self.hash_password(password, salt)
            
            # Compare hashes (timing-safe comparison)
            return secrets.compare_digest(stored_hash, new_hash)
        except (ValueError, Exception):
            return False
    
    def generate_token(self, length: int = 32) -> str:
        """Generate a cryptographically secure random token"""
        return secrets.token_urlsafe(length)
    
    def generate_backup_encryption_key(self) -> bytes:
        """Generate a key for backup encryption"""
        return Fernet.generate_key()
    
    def encrypt_backup_data(self, data: bytes, key: bytes) -> bytes:
        """Encrypt backup data with a specific key"""
        fernet = Fernet(key)
        return fernet.encrypt(data)
    
    def decrypt_backup_data(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt backup data with a specific key"""
        fernet = Fernet(key)
        return fernet.decrypt(encrypted_data)
    
    def secure_delete_key(self):
        """Securely delete the encryption key file"""
        if os.path.exists(self.key_file):
            # Overwrite the file with random data before deletion
            with open(self.key_file, 'r+b') as f:
                length = f.seek(0, 2)  # Get file length
                f.seek(0)
                f.write(os.urandom(length))
                f.flush()
                os.fsync(f.fileno())
            
            # Delete the file
            os.remove(self.key_file)
    
    def get_key_info(self) -> dict:
        """Get information about the encryption key"""
        return {
            'key_file_exists': os.path.exists(self.key_file),
            'fernet_initialized': self._fernet is not None,
            'key_file_path': os.path.abspath(self.key_file) if os.path.exists(self.key_file) else None
        }
