#!/usr/bin/env python3
"""
Database Manager for Urban Mobility System
Handles all database operations with encryption and SQL injection protection.
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

class DatabaseManager:
    """Manages all database operations with security features"""
    
    def __init__(self, crypto_manager, logger):
        """Initialize the database manager"""
        self.crypto = crypto_manager
        self.logger = logger
        self.db_file = 'urban_mobility.db'
        self.connection = None
        
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with security settings"""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_file, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            
            # Enable foreign key constraints
            self.connection.execute("PRAGMA foreign_keys = ON")
            
        return self.connection
    
    def initialize_database(self):
        """Initialize database schema"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('super_admin', 'system_admin', 'service_engineer')),
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    registration_date TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1 CHECK (is_active IN (0, 1)),
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create travellers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS travellers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id TEXT UNIQUE NOT NULL,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    birthday TEXT NOT NULL,
                    gender TEXT NOT NULL CHECK (gender IN ('male', 'female')),
                    street_name TEXT NOT NULL,
                    house_number TEXT NOT NULL,
                    zip_code TEXT NOT NULL,
                    city TEXT NOT NULL,
                    email_address TEXT NOT NULL,
                    mobile_phone TEXT NOT NULL,
                    driving_license_number TEXT NOT NULL,
                    registration_date TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create scooters table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scooters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    brand TEXT NOT NULL,
                    model TEXT NOT NULL,
                    serial_number TEXT UNIQUE NOT NULL,
                    top_speed REAL NOT NULL,
                    battery_capacity REAL NOT NULL,
                    state_of_charge REAL NOT NULL CHECK (state_of_charge >= 0 AND state_of_charge <= 100),
                    target_range_soc_min REAL NOT NULL CHECK (target_range_soc_min >= 0 AND target_range_soc_min <= 100),
                    target_range_soc_max REAL NOT NULL CHECK (target_range_soc_max >= 0 AND target_range_soc_max <= 100),
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    out_of_service_status INTEGER DEFAULT 0 CHECK (out_of_service_status IN (0, 1)),
                    mileage REAL DEFAULT 0,
                    last_maintenance_date TEXT,
                    in_service_date TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create restore_codes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS restore_codes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE NOT NULL,
                    backup_filename TEXT NOT NULL,
                    system_admin_username TEXT NOT NULL,
                    is_used INTEGER DEFAULT 0 CHECK (is_used IN (0, 1)),
                    created_by TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    used_at TEXT,
                    FOREIGN KEY (system_admin_username) REFERENCES users(username)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_travellers_customer_id ON travellers(customer_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_scooters_serial_number ON scooters(serial_number)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_restore_codes_code ON restore_codes(code)')
            
            # Initialize super admin account if it doesn't exist
            self._create_super_admin()
            
            conn.commit()
            self.logger.log_activity("SYSTEM", "Database initialized", "Database schema created/updated")
            
        except Exception as e:
            conn.rollback()
            self.logger.log_activity("SYSTEM", "Database initialization failed", str(e), suspicious=True)
            raise
    
    def _create_super_admin(self):
        """Create the hard-coded super admin account"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if super admin exists
            cursor.execute("SELECT id FROM users WHERE username = ?", ("super_admin",))
            if cursor.fetchone():
                return  # Super admin already exists
            
            # Create super admin account
            password_hash = self.crypto.hash_password("Admin_123?")
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, role, first_name, last_name, registration_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                "super_admin",
                password_hash,
                "super_admin",
                self.crypto.encrypt("Super"),
                self.crypto.encrypt("Administrator"),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            self.logger.log_activity("SYSTEM", "Super admin account created", "Hard-coded super admin account initialized")
            
        except Exception as e:
            conn.rollback()
            self.logger.log_activity("SYSTEM", "Super admin creation failed", str(e), suspicious=True)
            raise
    
    def create_user(self, username: str, password: str, role: str, first_name: str, last_name: str) -> bool:
        """Create a new user account"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Hash password
            password_hash = self.crypto.hash_password(password)
            
            # Encrypt sensitive data
            encrypted_first_name = self.crypto.encrypt(first_name)
            encrypted_last_name = self.crypto.encrypt(last_name)
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, role, first_name, last_name, registration_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                username,
                password_hash,
                role,
                encrypted_first_name,
                encrypted_last_name,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            self.logger.log_activity(username, "User account created", f"New {role} account created")
            return True
            
        except sqlite3.IntegrityError:
            conn.rollback()
            return False  # Username already exists
        except Exception as e:
            conn.rollback()
            self.logger.log_activity("SYSTEM", "User creation failed", str(e), suspicious=True)
            raise
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user credentials"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT username, password_hash, role, first_name, last_name, is_active
                FROM users 
                WHERE username = ? AND is_active = 1
            ''', (username,))
            
            user_row = cursor.fetchone()
            if not user_row:
                return None
            
            # Verify password
            if not self.crypto.verify_password(password, user_row['password_hash']):
                return None
            
            # Decrypt sensitive data
            try:
                first_name = self.crypto.decrypt(user_row['first_name'])
                last_name = self.crypto.decrypt(user_row['last_name'])
            except:
                # Fallback for unencrypted data (backward compatibility)
                first_name = user_row['first_name']
                last_name = user_row['last_name']
            
            return {
                'username': user_row['username'],
                'role': user_row['role'],
                'first_name': first_name,
                'last_name': last_name
            }
            
        except Exception as e:
            self.logger.log_activity("SYSTEM", "Authentication error", str(e), suspicious=True)
            return None
    
    def get_users(self, role_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of users (excluding super_admin)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            if role_filter:
                cursor.execute('''
                    SELECT username, role, first_name, last_name, registration_date, is_active
                    FROM users 
                    WHERE role = ? AND username != 'super_admin'
                    ORDER BY registration_date DESC
                ''', (role_filter,))
            else:
                cursor.execute('''
                    SELECT username, role, first_name, last_name, registration_date, is_active
                    FROM users 
                    WHERE username != 'super_admin'
                    ORDER BY registration_date DESC
                ''')
            
            users = []
            for row in cursor.fetchall():
                try:
                    # Decrypt sensitive data
                    first_name = self.crypto.decrypt(row['first_name'])
                    last_name = self.crypto.decrypt(row['last_name'])
                except:
                    # Fallback for unencrypted data
                    first_name = row['first_name']
                    last_name = row['last_name']
                
                users.append({
                    'username': row['username'],
                    'role': row['role'],
                    'first_name': first_name,
                    'last_name': last_name,
                    'registration_date': row['registration_date'],
                    'is_active': bool(row['is_active'])
                })
            
            return users
            
        except Exception as e:
            self.logger.log_activity("SYSTEM", "Get users failed", str(e), suspicious=True)
            return []
    
    def update_user_password(self, username: str, new_password: str) -> bool:
        """Update user password"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            password_hash = self.crypto.hash_password(new_password)
            
            cursor.execute('''
                UPDATE users 
                SET password_hash = ?, updated_at = CURRENT_TIMESTAMP
                WHERE username = ?
            ''', (password_hash, username))
            
            if cursor.rowcount > 0:
                conn.commit()
                self.logger.log_activity(username, "Password updated", "User password updated")
                return True
            else:
                return False
            
        except Exception as e:
            conn.rollback()
            self.logger.log_activity("SYSTEM", "Password update failed", str(e), suspicious=True)
            return False
    
    def delete_user(self, username: str) -> bool:
        """Delete user account (soft delete by setting is_active to 0)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE users 
                SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                WHERE username = ? AND username != 'super_admin'
            ''', (username,))
            
            if cursor.rowcount > 0:
                conn.commit()
                self.logger.log_activity(username, "User account deleted", f"User {username} deactivated")
                return True
            else:
                return False
            
        except Exception as e:
            conn.rollback()
            self.logger.log_activity("SYSTEM", "User deletion failed", str(e), suspicious=True)
            return False
    
    def create_traveller(self, traveller_data: Dict[str, str]) -> Optional[str]:
        """Create a new traveller record"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Generate unique customer ID
            customer_id = self._generate_customer_id()
            
            # Encrypt sensitive data
            encrypted_data = {}
            sensitive_fields = ['first_name', 'last_name', 'street_name', 'house_number', 
                              'zip_code', 'email_address', 'mobile_phone', 'driving_license_number']
            
            for field in sensitive_fields:
                encrypted_data[field] = self.crypto.encrypt(traveller_data[field])
            
            cursor.execute('''
                INSERT INTO travellers (
                    customer_id, first_name, last_name, birthday, gender,
                    street_name, house_number, zip_code, city, email_address,
                    mobile_phone, driving_license_number, registration_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                customer_id,
                encrypted_data['first_name'],
                encrypted_data['last_name'],
                traveller_data['birthday'],
                traveller_data['gender'],
                encrypted_data['street_name'],
                encrypted_data['house_number'],
                encrypted_data['zip_code'],
                traveller_data['city'],
                encrypted_data['email_address'],
                encrypted_data['mobile_phone'],
                encrypted_data['driving_license_number'],
                datetime.now().isoformat()
            ))
            
            conn.commit()
            self.logger.log_activity("SYSTEM", "Traveller created", f"New traveller created with ID: {customer_id}")
            return customer_id
            
        except Exception as e:
            conn.rollback()
            self.logger.log_activity("SYSTEM", "Traveller creation failed", str(e), suspicious=True)
            return None
    
    def _generate_customer_id(self) -> str:
        """Generate unique customer ID"""
        import random
        while True:
            customer_id = str(random.randint(1000000000, 9999999999))
            
            # Check if ID already exists
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM travellers WHERE customer_id = ?", (customer_id,))
            
            if not cursor.fetchone():
                return customer_id
    
    def search_travellers(self, search_term: str) -> List[Dict[str, Any]]:
        """Search travellers by partial match"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT customer_id, first_name, last_name, email_address, mobile_phone, registration_date
                FROM travellers
                ORDER BY registration_date DESC
            ''')
            
            travellers = []
            search_lower = search_term.lower()
            
            for row in cursor.fetchall():
                try:
                    # Decrypt sensitive data
                    first_name = self.crypto.decrypt(row['first_name'])
                    last_name = self.crypto.decrypt(row['last_name'])
                    email = self.crypto.decrypt(row['email_address'])
                    phone = self.crypto.decrypt(row['mobile_phone'])
                    
                    # Check if search term matches
                    full_name = f"{first_name} {last_name}".lower()
                    customer_id = row['customer_id']
                    
                    if (search_lower in full_name or 
                        search_lower in customer_id or
                        search_lower in email.lower() or
                        search_lower in phone):
                        
                        travellers.append({
                            'customer_id': customer_id,
                            'first_name': first_name,
                            'last_name': last_name,
                            'email_address': email,
                            'mobile_phone': phone,
                            'registration_date': row['registration_date']
                        })
                        
                except Exception:
                    # Skip records with decryption issues
                    continue
            
            return travellers
            
        except Exception as e:
            self.logger.log_activity("SYSTEM", "Traveller search failed", str(e), suspicious=True)
            return []
    
    def create_scooter(self, scooter_data: Dict[str, Any]) -> bool:
        """Create a new scooter record"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO scooters (
                    brand, model, serial_number, top_speed, battery_capacity,
                    state_of_charge, target_range_soc_min, target_range_soc_max,
                    latitude, longitude, out_of_service_status, mileage,
                    last_maintenance_date, in_service_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                scooter_data['brand'],
                scooter_data['model'],
                scooter_data['serial_number'],
                scooter_data['top_speed'],
                scooter_data['battery_capacity'],
                scooter_data['state_of_charge'],
                scooter_data['target_range_soc_min'],
                scooter_data['target_range_soc_max'],
                scooter_data['latitude'],
                scooter_data['longitude'],
                scooter_data.get('out_of_service_status', 0),
                scooter_data.get('mileage', 0),
                scooter_data.get('last_maintenance_date'),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            self.logger.log_activity("SYSTEM", "Scooter created", f"New scooter created: {scooter_data['serial_number']}")
            return True
            
        except sqlite3.IntegrityError:
            conn.rollback()
            return False  # Serial number already exists
        except Exception as e:
            conn.rollback()
            self.logger.log_activity("SYSTEM", "Scooter creation failed", str(e), suspicious=True)
            return False
    
    def search_scooters(self, search_term: str) -> List[Dict[str, Any]]:
        """Search scooters by partial match"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM scooters 
                WHERE brand LIKE ? OR model LIKE ? OR serial_number LIKE ?
                ORDER BY in_service_date DESC
            ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
            
            scooters = []
            for row in cursor.fetchall():
                scooter_dict = dict(row)
                scooters.append(scooter_dict)
            
            return scooters
            
        except Exception as e:
            self.logger.log_activity("SYSTEM", "Scooter search failed", str(e), suspicious=True)
            return []
    
    def close_connection(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
