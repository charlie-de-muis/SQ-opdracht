#!/usr/bin/env python3

import os
import sys

def test_imports():
    """Test all module imports"""
    try:
        import urban_mobility_system
        import crypto_manager
        import input_validator
        import auth_manager
        import database_manager
        import logger
        import backup_manager
        import user_interface
        print("✓ All modules imported successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_crypto():
    """Test cryptographic functions"""
    try:
        from crypto_manager import CryptoManager
        crypto = CryptoManager()
        
        # Test encryption/decryption
        test_data = "Hello, Urban Mobility!"
        encrypted = crypto.encrypt(test_data)
        decrypted = crypto.decrypt(encrypted)
        
        assert decrypted == test_data, "Encryption/decryption failed"
        
        # Test password hashing
        password = "TestPassword123!"
        hashed = crypto.hash_password(password)
        verified = crypto.verify_password(password, hashed)
        
        assert verified, "Password hashing/verification failed"
        
        print("✓ Cryptographic functions working")
        return True
    except Exception as e:
        print(f"✗ Crypto test failed: {e}")
        return False

def test_input_validation():
    """Test input validation"""
    try:
        from input_validator import InputValidator
        validator = InputValidator()
        
        # Test username validation
        valid, msg = validator.validate_username("test_user")
        assert valid, f"Username validation failed: {msg}"
        
        # Test password validation
        valid, msg = validator.validate_password("TestPassword123!")
        assert valid, f"Password validation failed: {msg}"
        
        # Test email validation
        valid, msg = validator.validate_email("test@example.com")
        assert valid, f"Email validation failed: {msg}"
        
        print("✓ Input validation working")
        return True
    except Exception as e:
        print(f"✗ Input validation test failed: {e}")
        return False

def test_database_initialization():
    """Test database initialization"""
    try:
        from crypto_manager import CryptoManager
        from logger import SystemLogger
        from database_manager import DatabaseManager
        
        crypto = CryptoManager()
        logger = SystemLogger(crypto)
        db_manager = DatabaseManager(crypto, logger)
        
        # Initialize database
        db_manager.initialize_database()
        
        # Check if super admin exists
        user_info = db_manager.authenticate_user("super_admin", "Admin_123?")
        assert user_info is not None, "Super admin authentication failed"
        assert user_info['role'] == 'super_admin', "Super admin role incorrect"
        
        # Clean up test database
        db_manager.close_connection()
        if os.path.exists('urban_mobility.db'):
            os.remove('urban_mobility.db')
        if os.path.exists('system.key'):
            os.remove('system.key')
        if os.path.exists('system_logs.dat'):
            os.remove('system_logs.dat')
        
        print("✓ Database initialization working")
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Urban Mobility System - Quick Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_crypto,
        test_input_validation,
        test_database_initialization
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All tests passed! System is ready.")
        return 0
    else:
        print("✗ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
