# Urban Mobility Backend System

## Overview
This is a secure backend system for Urban Mobility, a network of shared electric scooters in Rotterdam. The system provides role-based access control for managing travellers, scooters, and system administration.

## Security Features
- **Encryption**: All sensitive data encrypted using symmetric encryption
- **Authentication**: Secure password hashing with salt
- **Authorization**: Role-based access control with three user levels
- **Input Validation**: Comprehensive whitelisting-based validation
- **SQL Injection Protection**: Parameterized queries throughout
- **Activity Logging**: All actions logged with suspicious activity detection
- **Failed Login Protection**: Account lockout after multiple failed attempts

## User Roles

### Super Administrator (Hard-coded)
- **Username**: `super_admin`
- **Password**: `Admin_123?`
- **Capabilities**: Full system control, user management, backup/restore

### System Administrator
- **Capabilities**: Manage service engineers, travellers, scooters, system backup
- **Created by**: Super Administrator

### Service Engineer
- **Capabilities**: Update scooter information, search scooters, change own password
- **Created by**: Super Administrator or System Administrator

## System Requirements
- Python 3.7 or higher
- Standard library modules only (sqlite3, re, hashlib, secrets, etc.)
- Windows or macOS compatible

## Installation & Setup
1. Ensure Python 3.7+ is installed
2. Place all files in the `src` directory
3. Run: `python um_members.py`

## File Structure
```
src/
├── um_members.py           # Main entry point
├── urban_mobility_system.py # Core system controller
├── auth_manager.py         # Authentication and authorization
├── database_manager.py     # Database operations with encryption
├── input_validator.py      # Input validation (whitelisting)
├── crypto_manager.py       # Encryption and password hashing
├── logger.py              # Secure activity logging
├── backup_manager.py      # System backup and restore
└── user_interface.py      # Console user interface
```

## Data Formats

### Traveller Data
- **Zip Code**: DDDDXX (4 digits + 2 letters)
- **Mobile Phone**: DDDDDDDD (8 digits, +31-6- prefix automatic)
- **Driving License**: XXDDDDDDD or XDDDDDDDD
- **Cities**: Predefined list of 10 Dutch cities

### Scooter Data
- **Serial Number**: 10-17 alphanumeric characters
- **Location**: Rotterdam region coordinates (5 decimal places)
- **Battery**: State of charge and target range (0-100%)
- **Maintenance Date**: ISO 8601 format (YYYY-MM-DD)

### User Credentials
- **Username**: 8-10 characters, start with letter/underscore
- **Password**: 12-30 characters with mixed case, digits, special chars

## Security Implementation

### Encryption
- Symmetric encryption for sensitive database fields
- Password hashing with individual salts
- Encrypted log files

### SQL Injection Prevention
- Parameterized queries exclusively
- No dynamic SQL construction
- Input sanitization before database operations

### Input Validation
- Whitelisting approach for all inputs
- Regular expression patterns for format validation
- Length and range checks
- Null-byte attack prevention

### Logging
- Encrypted log storage
- Suspicious activity detection
- Failed login attempt tracking
- Admin notification system

## Features

### User Management
- Create/update/delete users by role
- Password reset functionality
- Account activation/deactivation

### Traveller Management
- Complete traveller registration
- Search with partial matching
- Customer ID auto-generation
- Address and contact validation

### Scooter Management
- Fleet registration and tracking
- Location and battery monitoring
- Maintenance scheduling
- Service status management

### System Administration
- Database backup/restore
- One-time restore codes
- Activity log monitoring
- System maintenance tools

## Testing the System

### Initial Login
1. Start the system: `python um_members.py`
2. Login with super admin credentials:
   - Username: `super_admin`
   - Password: `Admin_123?`

### Creating Users
1. Super admin can create system administrators
2. System administrators can create service engineers
3. All users can update their own passwords

### Data Management
1. Add travellers with proper format validation
2. Register scooters with location tracking
3. Search functionality with partial matching

## Security Compliance

This system meets the assignment requirements:
- **C1**: Authentication/Authorization - L3 (Secure implementation)
- **C2**: Input Validation - L3 (Comprehensive whitelisting)
- **C3**: SQL Injection Protection - L1 (Parameterized queries)
- **C4**: Invalid Input Handling - L3 (Proper error handling)
- **C5**: Logging/Backup - L3 (Complete implementation)

## Architecture Notes

### Database Schema
- SQLite with foreign key constraints
- Encrypted sensitive fields
- Indexed for performance
- Audit trail timestamps

### Error Handling
- Graceful degradation
- User-friendly error messages
- Security event logging
- System recovery procedures

## Backup System
- Automated backup creation
- Encrypted backup files
- One-time restore codes
- Version control for backups

## Known Limitations
- Single-user concurrent access (SQLite)
- No network communication
- Console-based interface only
- Symmetric encryption (acceptable for assignment)

## Author Information
Replace with your team details in `um_members.py`:
- Team members and student numbers
- Course: ANALYSIS 8: SOFTWARE QUALITY
- Academic year: 2024-2025
