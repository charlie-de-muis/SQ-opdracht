# Urban Mobility Backend System - Quick Start Guide

## System Startup

1. **Run the system:**
   ```
   python um_members.py
   ```

2. **Login with Super Administrator:**
   - Username: `super_admin`
   - Password: `Admin_123?`

## Main Features Demonstration

### 1. User Management
- **Create System Admin:** Use "User Management" → "Create New User"
  - Choose role: `system_admin`
  - Username: 8-10 chars (e.g., `admin_001`)
  - Password: 12-30 chars with mixed case, digits, special chars
  - Example: `AdminPass123!`

- **Create Service Engineer:** System/Super admin can create
  - Role: `service_engineer`
  - Username: e.g., `engineer01`
  - Password: e.g., `EngPass456@`

### 2. Traveller Management
**Add New Traveller:**
- First/Last Name: e.g., `John Smith`
- Birthday: `1990-05-15` (YYYY-MM-DD)
- Gender: `male` or `female`
- Address: Street, house number
- Zip Code: `3011AB` (DDDDXX format)
- City: Choose from predefined list (Rotterdam, Amsterdam, etc.)
- Email: `john.smith@email.com`
- Phone: `12345678` (8 digits, +31-6 automatic)
- License: `AB1234567` (XXDDDDDDD) or `A12345678` (XDDDDDDDD)

**Search Travellers:**
- Enter partial name, customer ID, email, or phone
- Case-insensitive search

### 3. Scooter Management
**Add New Scooter:**
- Brand: `Segway`, `NIU`, etc.
- Model: e.g., `Ninebot Max`
- Serial: `ABC1234567890` (10-17 alphanumeric)
- Top Speed: `25` (km/h)
- Battery Capacity: `551` (Wh)
- Current Charge: `85` (0-100%)
- Target Range: Min `20`, Max `80` (0-100%)
- Location: Rotterdam coordinates
  - Latitude: `51.9225` (51.8-52.0, 5 decimals)
  - Longitude: `4.47917` (4.3-4.6, 5 decimals)
- Mileage: `1250` (km)
- Maintenance: `2024-01-15` (YYYY-MM-DD)

**Search Scooters:**
- Search by brand, model, or serial number

### 4. System Administration
**Backup Operations:**
- Create backup: Automatic timestamp naming
- List backups: View all available backups
- Restore: Super admin only

**Restore Codes:**
- Generate: Super admin creates codes for system admins
- Use: System admin can restore with valid code
- Revoke: Super admin can invalidate codes

**System Logs:**
- View all activities
- Filter suspicious activities
- Search logs by term
- Export to file

### 5. Security Features Demo

**Failed Login Protection:**
- Try logging in with wrong password 3 times
- Account gets locked for 5 minutes
- Suspicious activity logged

**Input Validation:**
- Try entering invalid data formats
- System rejects with helpful error messages
- All input sanitized against null-byte attacks

**SQL Injection Protection:**
- All queries use parameterized statements
- No dynamic SQL construction
- Safe against injection attacks

**Data Encryption:**
- All sensitive data encrypted in database
- Passwords hashed with salt
- Log files encrypted

## Testing Scenarios

### Authentication & Authorization
1. Login as super_admin
2. Create system_admin user
3. Logout and login as system_admin
4. Try to access super_admin functions (should be denied)
5. Create service_engineer user
6. Login as service_engineer
7. Try to manage users (should be denied)

### Input Validation
1. Try invalid username formats:
   - Too short: `abc`
   - Too long: `verylongusername`
   - Invalid chars: `user@name`
   - Starting with number: `1username`

2. Try invalid passwords:
   - Too short: `pass`
   - No uppercase: `password123!`
   - No special chars: `Password123`

3. Try invalid traveller data:
   - Invalid zip: `123AB` (should be `1234AB`)
   - Invalid phone: `123` (should be 8 digits)
   - Invalid license: `123456789` (should start with letter)

### Data Management
1. Add travellers with valid data
2. Search for travellers using partial terms
3. Add scooters with Rotterdam coordinates
4. Update scooter battery levels (service engineer)
5. Try to delete scooter as service engineer (should fail)

### Logging & Monitoring
1. Perform various actions
2. View system logs
3. Check for suspicious activities
4. Export logs to file

### Backup & Recovery
1. Create system backup
2. Add some test data
3. Generate restore code for system admin
4. Restore from backup using code
5. Verify data is restored

## System Requirements Verification

### C1: Authentication & Authorization
- ✓ Secure password hashing
- ✓ Role-based access control
- ✓ Session management
- ✓ Failed login protection

### C2: Input Validation
- ✓ Whitelisting approach
- ✓ Format validation
- ✓ Length checks
- ✓ Null-byte protection

### C3: SQL Injection Protection
- ✓ Parameterized queries only
- ✓ No dynamic SQL
- ✓ Input sanitization

### C4: Error Handling
- ✓ Graceful error recovery
- ✓ User-friendly messages
- ✓ Security logging

### C5: Logging & Backup
- ✓ Comprehensive activity logging
- ✓ Suspicious activity detection
- ✓ Encrypted log storage
- ✓ Backup/restore functionality

## File Structure Overview
```
src/
├── um_members.py           # Main entry point
├── urban_mobility_system.py # Core system
├── auth_manager.py         # Authentication
├── database_manager.py     # Database operations
├── input_validator.py      # Input validation
├── crypto_manager.py       # Encryption
├── logger.py              # Logging system
├── backup_manager.py      # Backup operations
├── user_interface.py      # User interface
└── test_system.py         # Test suite
```

## Security Notes
- All sensitive data encrypted at rest
- Passwords never stored, only hashes
- Activity logging for audit trail
- Role-based access prevents privilege escalation
- Input validation prevents injection attacks
- Backup system protects against data loss
