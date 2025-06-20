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
    def __init__(self):
        # Ensure file is always created in src directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.key_file = os.path.join(script_dir, 'system.key')
        self._fernet = None
        self._initialize_encryption()
    
    def _initialize_encryption(self):
        # Check if key file exists
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                key = f.read()
            self._fernet = Fernet(key)
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            self._fernet = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        if not isinstance(data, str):
            raise TypeError("Data must be a string")
        
        if not data:
            return ""
        
        try:
            # Convert string to bytes and encrypt
            data_bytes = data.encode('utf-8')
            encrypted_bytes = self._fernet.encrypt(data_bytes)
            return base64.b64encode(encrypted_bytes).decode('utf-8')
        except Exception as e:
            raise RuntimeError(f"Encryption failed: {e}")
    
    def decrypt(self, encrypted_data: str) -> str:
        if not isinstance(encrypted_data, str):
            raise TypeError("Encrypted data must be a string")
        
        if not encrypted_data:
            return ""
        
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_bytes = self._fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            raise RuntimeError(f"Decryption failed: {e}")
    
    def hash_password(self, password: str, salt: str = None) -> str:
        if not isinstance(password, str):
            raise TypeError("Password must be a string")
        
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 with SHA-256
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode('utf-8'),
            iterations=100000,
        )
        
        # Generate hash
        key = kdf.derive(password.encode('utf-8'))
        hash_hex = base64.b64encode(key).decode('utf-8')
        
        return f"{salt}:{hash_hex}"
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        if not isinstance(password, str) or not isinstance(stored_hash, str):
            return False
        
        try:
            salt, hash_part = stored_hash.split(':', 1)
            new_hash = self.hash_password(password, salt)
            return secrets.compare_digest(stored_hash, new_hash)
        except (ValueError, Exception):
            return False
    
    def generate_token(self, length: int = 32) -> str:
        return secrets.token_urlsafe(length)
    
    def generate_backup_encryption_key(self) -> bytes:
        return Fernet.generate_key()
    
    def encrypt_backup_data(self, data: bytes, key: bytes) -> bytes:
        fernet = Fernet(key)
        return fernet.encrypt(data)
    
    def decrypt_backup_data(self, encrypted_data: bytes, key: bytes) -> bytes:
        fernet = Fernet(key)
        return fernet.decrypt(encrypted_data)
    
    def secure_delete_key(self):
        if os.path.exists(self.key_file):
            # Overwrite the file with random data before deletion
            with open(self.key_file, 'r+b') as f:
                length = f.seek(0, 2)
                f.seek(0)
                f.write(os.urandom(length))
                f.flush()
                os.fsync(f.fileno())

            os.remove(self.key_file)
    
    def get_key_info(self) -> dict:
        return {
            'key_file_exists': os.path.exists(self.key_file),
            'fernet_initialized': self._fernet is not None,
            'key_file_path': os.path.abspath(self.key_file) if os.path.exists(self.key_file) else None
        }
