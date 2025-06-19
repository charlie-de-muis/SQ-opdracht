#!/usr/bin/env python3

import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class AuthManager:
    """Manages authentication and authorization"""
    
    def __init__(self, database_manager, logger):
        """Initialize the authentication manager"""
        self.db_manager = database_manager
        self.logger = logger
        
        # Track failed login attempts
        self.failed_attempts = {}  # username -> {'count': int, 'last_attempt': datetime}
        self.max_failed_attempts = 3
        self.lockout_duration = 300  # 5 minutes in seconds
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with rate limiting and logging"""
        
        # Check if user is locked out
        if self._is_user_locked_out(username):
            self.logger.log_activity(
                username,
                "Login blocked",
                f"Login attempt blocked due to too many failed attempts",
                suspicious=True
            )
            return None
        
        # Attempt authentication
        user_info = self.db_manager.authenticate_user(username, password)
        
        if user_info:
            # Successful login - clear failed attempts
            if username in self.failed_attempts:
                del self.failed_attempts[username]
            
            self.logger.log_activity(username, "Successful login", "User authenticated successfully")
            return user_info
        else:
            # Failed login - track attempt
            self._record_failed_attempt(username)
            
            # Log with appropriate suspicion level
            failed_count = self.failed_attempts.get(username, {}).get('count', 0)
            suspicious = failed_count >= 2
            
            self.logger.log_activity(
                username,
                "Failed login",
                f"Authentication failed for user: {username} (Attempt {failed_count})",
                suspicious=suspicious
            )
            
            return None
    
    def _is_user_locked_out(self, username: str) -> bool:
        """Check if user is currently locked out"""
        if username not in self.failed_attempts:
            return False
        
        attempt_info = self.failed_attempts[username]
        
        # Check if user has exceeded max attempts
        if attempt_info['count'] < self.max_failed_attempts:
            return False
        
        # Check if lockout period has expired
        lockout_end = attempt_info['last_attempt'] + timedelta(seconds=self.lockout_duration)
        
        if datetime.now() >= lockout_end:
            # Lockout period has expired - clear failed attempts
            del self.failed_attempts[username]
            return False
        
        return True
    
    def _record_failed_attempt(self, username: str):
        """Record a failed login attempt"""
        now = datetime.now()
        
        if username in self.failed_attempts:
            # Check if this is a new attempt sequence (more than 1 hour since last attempt)
            last_attempt = self.failed_attempts[username]['last_attempt']
            if now - last_attempt > timedelta(hours=1):
                # Reset counter for new sequence
                self.failed_attempts[username] = {'count': 1, 'last_attempt': now}
            else:
                # Increment existing counter
                self.failed_attempts[username]['count'] += 1
                self.failed_attempts[username]['last_attempt'] = now
        else:
            # First failed attempt for this user
            self.failed_attempts[username] = {'count': 1, 'last_attempt': now}
    
    def check_authorization(self, user_role: str, required_role: str) -> bool:
        """Check if user has required authorization level"""
        
        # Define role hierarchy
        role_hierarchy = {
            'super_admin': 3,
            'system_admin': 2,
            'service_engineer': 1
        }
        
        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
    
    def check_permission(self, user_role: str, action: str, resource: str = None) -> bool:
        """Check specific permission for user role"""
        
        permissions = {
            'super_admin': {
                'create_user': ['system_admin', 'service_engineer'],
                'update_user': ['system_admin', 'service_engineer'],
                'delete_user': ['system_admin', 'service_engineer'],
                'reset_password': ['system_admin', 'service_engineer'],
                'view_logs': True,
                'create_traveller': True,
                'update_traveller': True,
                'delete_traveller': True,
                'search_traveller': True,
                'create_scooter': True,
                'update_scooter': True,
                'delete_scooter': True,
                'search_scooter': True,
                'backup_system': True,
                'restore_system': True,
                'generate_restore_code': True,
                'revoke_restore_code': True
            },
            'system_admin': {
                'create_user': ['service_engineer'],
                'update_user': ['service_engineer', 'self'],
                'delete_user': ['service_engineer', 'self'],
                'reset_password': ['service_engineer'],
                'view_logs': True,
                'create_traveller': True,
                'update_traveller': True,
                'delete_traveller': True,
                'search_traveller': True,
                'create_scooter': True,
                'update_scooter': True,
                'delete_scooter': True,
                'search_scooter': True,
                'backup_system': True,
                'restore_system': 'with_code',
                'update_password': 'self'
            },
            'service_engineer': {
                'update_scooter': 'limited',  # Only certain attributes
                'search_scooter': True,
                'update_password': 'self'
            }
        }
        
        role_permissions = permissions.get(user_role, {})
        return role_permissions.get(action, False)
    
    def get_scooter_update_permissions(self, user_role: str) -> Dict[str, bool]:
        """Get which scooter attributes can be updated by user role"""
        
        if user_role in ['super_admin', 'system_admin']:
            return {
                'brand': True,
                'model': True,
                'serial_number': True,
                'top_speed': True,
                'battery_capacity': True,
                'state_of_charge': True,
                'target_range_soc_min': True,
                'target_range_soc_max': True,
                'latitude': True,
                'longitude': True,
                'out_of_service_status': True,
                'mileage': True,
                'last_maintenance_date': True
            }
        elif user_role == 'service_engineer':
            return {
                'brand': False,
                'model': False,
                'serial_number': False,
                'top_speed': False,
                'battery_capacity': False,
                'state_of_charge': True,
                'target_range_soc_min': True,
                'target_range_soc_max': True,
                'latitude': True,
                'longitude': True,
                'out_of_service_status': True,
                'mileage': True,
                'last_maintenance_date': True
            }
        else:
            return {}
    
    def validate_session(self, username: str, role: str) -> bool:
        """Validate if user session is still valid"""
        # In a real application, this would check session tokens, timeouts, etc.
        # For this assignment, we'll do a basic check
        
        try:
            # Verify user still exists and is active
            user_info = self.db_manager.authenticate_user(username, "dummy_password_for_check")
            # We don't expect this to succeed, but it will verify user exists
            
            # Check if user exists in database (without password verification)
            conn = self.db_manager._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT role, is_active FROM users 
                WHERE username = ? AND is_active = 1
            ''', (username,))
            
            user_row = cursor.fetchone()
            if user_row and user_row['role'] == role:
                return True
            
            return False
            
        except Exception as e:
            self.logger.log_activity(
                username,
                "Session validation error",
                str(e),
                suspicious=True
            )
            return False
    
    def log_authorization_attempt(self, username: str, action: str, success: bool, details: str = ""):
        """Log authorization attempts"""
        if success:
            self.logger.log_activity(
                username,
                f"Authorization granted: {action}",
                details
            )
        else:
            self.logger.log_activity(
                username,
                f"Authorization denied: {action}",
                details,
                suspicious=True
            )
    
    def get_lockout_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Get lockout information for a user"""
        if username not in self.failed_attempts:
            return None
        
        attempt_info = self.failed_attempts[username]
        
        if attempt_info['count'] >= self.max_failed_attempts:
            lockout_end = attempt_info['last_attempt'] + timedelta(seconds=self.lockout_duration)
            remaining_time = lockout_end - datetime.now()
            
            if remaining_time.total_seconds() > 0:
                return {
                    'is_locked': True,
                    'failed_attempts': attempt_info['count'],
                    'lockout_end': lockout_end,
                    'remaining_seconds': int(remaining_time.total_seconds())
                }
        
        return {
            'is_locked': False,
            'failed_attempts': attempt_info['count'],
            'max_attempts': self.max_failed_attempts
        }
    
    def clear_user_lockout(self, username: str, admin_username: str) -> bool:
        """Manually clear user lockout (admin function)"""
        if username in self.failed_attempts:
            del self.failed_attempts[username]
            
            self.logger.log_activity(
                admin_username,
                "Lockout cleared",
                f"Manually cleared lockout for user: {username}"
            )
            return True
        
        return False
