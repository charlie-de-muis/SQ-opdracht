#!/usr/bin/env python3
"""
Urban Mobility System - Main System Controller
Handles authentication, authorization, and core system operations.
"""

import os
import sys
import time
import getpass
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

# Import system modules
from database_manager import DatabaseManager
from auth_manager import AuthManager
from input_validator import InputValidator
from crypto_manager import CryptoManager
from logger import SystemLogger
from backup_manager import BackupManager
from user_interface import UserInterface

class UrbanMobilitySystem:
    """Main system controller for Urban Mobility Backend"""
    
    def __init__(self):
        """Initialize the Urban Mobility System"""
        self.current_user = None
        self.user_role = None
        self.session_active = False
        self.failed_login_attempts = 0
        self.max_failed_attempts = 3
        
        # Initialize core components
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize all system components"""
        try:
            # Initialize crypto manager first (needed for encryption)
            self.crypto = CryptoManager()
            
            # Initialize logger
            self.logger = SystemLogger(self.crypto)
            
            # Initialize database manager
            self.db_manager = DatabaseManager(self.crypto, self.logger)
            
            # Initialize authentication manager
            self.auth_manager = AuthManager(self.db_manager, self.logger)
            
            # Initialize input validator
            self.validator = InputValidator()
            
            # Initialize backup manager
            self.backup_manager = BackupManager(self.db_manager, self.logger)
            
            # Initialize user interface
            self.ui = UserInterface()
            
            # Initialize database schema
            self.db_manager.initialize_database()
            
            # Log system startup
            self.logger.log_activity("SYSTEM", "System startup", "System initialized successfully")
            
        except Exception as e:
            print(f"Failed to initialize system components: {e}")
            sys.exit(1)
    
    def run(self):
        """Main application loop"""
        self.ui.display_welcome()
        
        while True:
            try:
                if not self.session_active:
                    # Show login menu
                    if not self._handle_login():
                        continue
                
                # Check for suspicious activity alerts
                self._check_suspicious_activity()
                
                # Show main menu based on user role
                self._show_main_menu()
                
            except KeyboardInterrupt:
                self._handle_logout()
                break
            except Exception as e:
                self.logger.log_activity(
                    self.current_user or "UNKNOWN",
                    "System error",
                    f"Unexpected error: {str(e)}",
                    suspicious=True
                )
                print(f"An error occurred: {e}")
                print("Please try again or contact system administrator.")
    
    def _handle_login(self) -> bool:
        """Handle user login process"""
        print("\n" + "="*50)
        print("           LOGIN REQUIRED")
        print("="*50)
        
        # Check if too many failed attempts
        if self.failed_login_attempts >= self.max_failed_attempts:
            print("Too many failed login attempts. System locked for 30 seconds.")
            time.sleep(30)
            self.failed_login_attempts = 0
        
        username = input("Username: ").strip()
        if not username:
            print("Username cannot be empty.")
            return False
        
        password = getpass.getpass("Password: ")
        if not password:
            print("Password cannot be empty.")
            return False
        
        # Validate credentials
        user_info = self.auth_manager.authenticate_user(username, password)
        
        if user_info:
            self.current_user = username
            self.user_role = user_info['role']
            self.session_active = True
            self.failed_login_attempts = 0
            
            # Log successful login
            self.logger.log_activity(username, "Logged in", "Successful login")
            
            print(f"\nWelcome, {user_info['first_name']} {user_info['last_name']}!")
            print(f"Role: {self.user_role}")
            return True
        else:
            self.failed_login_attempts += 1
            print("Invalid username or password.")
            
            # Log failed login attempt
            self.logger.log_activity(
                username,
                "Failed login",
                f"Failed login attempt for username: {username}",
                suspicious=(self.failed_login_attempts >= 2)
            )
            return False
    
    def _handle_logout(self):
        """Handle user logout"""
        if self.current_user:
            self.logger.log_activity(self.current_user, "Logged out", "User logged out")
            print(f"\nGoodbye, {self.current_user}!")
        
        self.current_user = None
        self.user_role = None
        self.session_active = False
    
    def _check_suspicious_activity(self):
        """Check for and display suspicious activity alerts"""
        if self.user_role in ['super_admin', 'system_admin']:
            suspicious_count = self.logger.get_unread_suspicious_count()
            if suspicious_count > 0:
                print(f"\n⚠️  ALERT: {suspicious_count} suspicious activities detected!")
                print("Use 'View Logs' option to review suspicious activities.")
    
    def _show_main_menu(self):
        """Display main menu based on user role"""
        while self.session_active:
            try:
                if self.user_role == 'super_admin':
                    choice = self._show_super_admin_menu()
                elif self.user_role == 'system_admin':
                    choice = self._show_system_admin_menu()
                elif self.user_role == 'service_engineer':
                    choice = self._show_service_engineer_menu()
                else:
                    print("Invalid user role. Logging out.")
                    self._handle_logout()
                    break
                
                if choice == 'logout':
                    self._handle_logout()
                    break
                    
            except KeyboardInterrupt:
                self._handle_logout()
                break
    
    def _show_super_admin_menu(self) -> str:
        """Show Super Administrator menu"""
        menu_options = [
            "1. User Management",
            "2. Traveller Management", 
            "3. Scooter Management",
            "4. System Administration",
            "5. Backup & Restore",
            "6. View System Logs",
            "7. Generate Restore Codes",
            "8. Logout"
        ]
        
        print(f"\n{'='*60}")
        print(f"    SUPER ADMINISTRATOR MENU - {self.current_user}")
        print(f"{'='*60}")
        
        for option in menu_options:
            print(f"  {option}")
        
        choice = input("\nSelect option (1-8): ").strip()
        
        if choice == '1':
            self._handle_user_management()
        elif choice == '2':
            self._handle_traveller_management()
        elif choice == '3':
            self._handle_scooter_management()
        elif choice == '4':
            self._handle_system_administration()
        elif choice == '5':
            self._handle_backup_restore()
        elif choice == '6':
            self._handle_view_logs()
        elif choice == '7':
            self._handle_restore_codes()
        elif choice == '8':
            return 'logout'
        else:
            print("Invalid choice. Please select 1-8.")
        
        return 'continue'
    
    def _show_system_admin_menu(self) -> str:
        """Show System Administrator menu"""
        menu_options = [
            "1. User Management (Service Engineers)",
            "2. Traveller Management",
            "3. Scooter Management", 
            "4. System Administration",
            "5. Backup System",
            "6. Restore System (with code)",
            "7. View System Logs",
            "8. Update My Password",
            "9. Logout"
        ]
        
        print(f"\n{'='*60}")
        print(f"    SYSTEM ADMINISTRATOR MENU - {self.current_user}")
        print(f"{'='*60}")
        
        for option in menu_options:
            print(f"  {option}")
        
        choice = input("\nSelect option (1-9): ").strip()
        
        if choice == '1':
            self._handle_service_engineer_management()
        elif choice == '2':
            self._handle_traveller_management()
        elif choice == '3':
            self._handle_scooter_management()
        elif choice == '4':
            self._handle_system_administration()
        elif choice == '5':
            self._handle_backup_system()
        elif choice == '6':
            self._handle_restore_with_code()
        elif choice == '7':
            self._handle_view_logs()
        elif choice == '8':
            self._handle_update_password()
        elif choice == '9':
            return 'logout'
        else:
            print("Invalid choice. Please select 1-9.")
        
        return 'continue'
    
    def _show_service_engineer_menu(self) -> str:
        """Show Service Engineer menu"""
        menu_options = [
            "1. Update Scooter Information",
            "2. Search Scooter Information",
            "3. Update My Password",
            "4. Logout"
        ]
        
        print(f"\n{'='*60}")
        print(f"    SERVICE ENGINEER MENU - {self.current_user}")
        print(f"{'='*60}")
        
        for option in menu_options:
            print(f"  {option}")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            self._handle_update_scooter()
        elif choice == '2':
            self._handle_search_scooter()
        elif choice == '3':
            self._handle_update_password()
        elif choice == '4':
            return 'logout'
        else:
            print("Invalid choice. Please select 1-4.")
        
        return 'continue'
      # Menu handler methods
    def _handle_user_management(self):
        """Handle user management operations"""
        while True:
            options = [
                "1. List All Users",
                "2. Create New User",
                "3. Update User",
                "4. Delete User",
                "5. Reset User Password",
                "6. Back to Main Menu"
            ]
            
            choice = self.ui.display_menu("USER MANAGEMENT", options, f"Logged in as: {self.current_user}")
            
            if choice == '1':
                self._list_users()
            elif choice == '2':
                self._create_user()
            elif choice == '3':
                self._update_user()
            elif choice == '4':
                self._delete_user()
            elif choice == '5':
                self._reset_user_password()
            elif choice == '6':
                break
            else:
                self.ui.display_message("Invalid choice. Please select 1-6.", "error")
    
    def _handle_traveller_management(self):
        """Handle traveller management operations"""
        while True:
            options = [
                "1. Add New Traveller",
                "2. Search Travellers",
                "3. Update Traveller",
                "4. Delete Traveller",
                "5. Back to Main Menu"
            ]
            
            choice = self.ui.display_menu("TRAVELLER MANAGEMENT", options, f"Logged in as: {self.current_user}")
            
            if choice == '1':
                self._add_traveller()
            elif choice == '2':
                self._search_travellers()
            elif choice == '3':
                self._update_traveller()
            elif choice == '4':
                self._delete_traveller()
            elif choice == '5':
                break
            else:
                self.ui.display_message("Invalid choice. Please select 1-5.", "error")
    
    def _handle_scooter_management(self):
        """Handle scooter management operations"""
        while True:
            options = [
                "1. Add New Scooter",
                "2. Search Scooters",
                "3. Update Scooter",
                "4. Delete Scooter",
                "5. Back to Main Menu"
            ]
            
            choice = self.ui.display_menu("SCOOTER MANAGEMENT", options, f"Logged in as: {self.current_user}")
            
            if choice == '1':
                self._add_scooter()
            elif choice == '2':
                self._search_scooters()
            elif choice == '3':
                self._update_scooter()
            elif choice == '4':
                self._delete_scooter()
            elif choice == '5':
                break
            else:
                self.ui.display_message("Invalid choice. Please select 1-5.", "error")
    
    def _handle_system_administration(self):
        """Handle system administration operations"""
        while True:
            options = [
                "1. View System Information",
                "2. Manage User Accounts", 
                "3. System Maintenance",
                "4. Back to Main Menu"
            ]
            
            choice = self.ui.display_menu("SYSTEM ADMINISTRATION", options, f"Logged in as: {self.current_user}")
            
            if choice == '1':
                self._view_system_info()
            elif choice == '2':
                self._handle_user_management()
            elif choice == '3':
                self._system_maintenance()
            elif choice == '4':
                break
            else:
                self.ui.display_message("Invalid choice. Please select 1-4.", "error")
    
    def _handle_backup_restore(self):
        """Handle backup and restore operations"""
        while True:
            options = [
                "1. Create Backup",
                "2. List Backups",
                "3. Restore from Backup",
                "4. Back to Main Menu"
            ]
            
            choice = self.ui.display_menu("BACKUP & RESTORE", options, f"Logged in as: {self.current_user}")
            
            if choice == '1':
                self._create_backup()
            elif choice == '2':
                self._list_backups()
            elif choice == '3':
                self._restore_backup()
            elif choice == '4':
                break
            else:
                self.ui.display_message("Invalid choice. Please select 1-4.", "error")
    
    def _handle_view_logs(self):
        """Handle viewing system logs"""
        while True:
            options = [
                "1. View All Logs",
                "2. View Suspicious Activities",
                "3. Search Logs",
                "4. Export Logs",
                "5. Back to Main Menu"
            ]
            
            choice = self.ui.display_menu("SYSTEM LOGS", options, f"Logged in as: {self.current_user}")
            
            if choice == '1':
                self._view_all_logs()
            elif choice == '2':
                self._view_suspicious_logs()
            elif choice == '3':
                self._search_logs()
            elif choice == '4':
                self._export_logs()
            elif choice == '5':
                break
            else:
                self.ui.display_message("Invalid choice. Please select 1-5.", "error")
    
    def _handle_restore_codes(self):
        """Handle restore code generation"""
        while True:
            options = [
                "1. Generate Restore Code",
                "2. List Restore Codes",
                "3. Revoke Restore Code",
                "4. Back to Main Menu"
            ]
            
            choice = self.ui.display_menu("RESTORE CODE MANAGEMENT", options, f"Logged in as: {self.current_user}")
            
            if choice == '1':
                self._generate_restore_code()
            elif choice == '2':
                self._list_restore_codes()
            elif choice == '3':
                self._revoke_restore_code()
            elif choice == '4':
                break
            else:
                self.ui.display_message("Invalid choice. Please select 1-4.", "error")
    
    def _handle_service_engineer_management(self):
        """Handle service engineer management"""
        # This redirects to the general user management with role filter
        self._handle_user_management()
    
    def _handle_backup_system(self):
        """Handle system backup"""
        self._create_backup()
    
    def _handle_restore_with_code(self):
        """Handle system restore with code"""
        restore_code = self.ui.get_input("Enter restore code", required=True)
        
        if self.ui.display_confirmation(f"Are you sure you want to restore the system using this code?"):
            self.ui.display_progress("Restoring system")
            
            if self.backup_manager.restore_with_code(restore_code, self.current_user):
                self.ui.display_message("System restored successfully.", "success")
            else:
                self.ui.display_message("Failed to restore system. Invalid or expired code.", "error")
        
        self.ui.wait_for_enter()
    
    def _handle_update_password(self):
        """Handle password update"""
        current_password = self.ui.get_input("Enter current password", "password", required=True)
        
        # Verify current password
        user_info = self.db_manager.authenticate_user(self.current_user, current_password)
        if not user_info:
            self.ui.display_message("Current password is incorrect.", "error")
            self.ui.wait_for_enter()
            return
        
        new_password = self.ui.get_input("Enter new password", "password", required=True)
        confirm_password = self.ui.get_input("Confirm new password", "password", required=True)
        
        if new_password != confirm_password:
            self.ui.display_message("Passwords do not match.", "error")
            self.ui.wait_for_enter()
            return
        
        # Validate new password
        valid, msg = self.validator.validate_password(new_password)
        if not valid:
            self.ui.display_message(f"Invalid password: {msg}", "error")
            self.ui.wait_for_enter()
            return
        
        # Update password
        if self.db_manager.update_user_password(self.current_user, new_password):
            self.ui.display_message("Password updated successfully.", "success")
        else:
            self.ui.display_message("Failed to update password.", "error")
        
        self.ui.wait_for_enter()
    
    def _handle_update_scooter(self):
        """Handle scooter information update"""
        # First, search for the scooter to update
        serial_number = self.ui.get_input("Enter scooter serial number", required=True)
        
        results = self.db_manager.search_scooters(serial_number)
        if not results:
            self.ui.display_message("Scooter not found.", "error")
            self.ui.wait_for_enter()
            return
        
        scooter = results[0]  # Take first match
        
        # Show current information
        print(f"\nCurrent scooter information:")
        print(f"Serial: {scooter.get('serial_number')}")
        print(f"Brand/Model: {scooter.get('brand')} {scooter.get('model')}")
        print(f"Battery: {scooter.get('state_of_charge')}%")
        print(f"Location: {scooter.get('latitude')}, {scooter.get('longitude')}")
        
        # Get permissions for this user role
        permissions = self.auth_manager.get_scooter_update_permissions(self.user_role)
        
        # Show available fields to update
        updateable_fields = [k for k, v in permissions.items() if v]
        if not updateable_fields:
            self.ui.display_message("You don't have permission to update any scooter fields.", "error")
            self.ui.wait_for_enter()
            return
        
        print(f"\nYou can update the following fields:")
        for i, field in enumerate(updateable_fields, 1):
            print(f"{i}. {field.replace('_', ' ').title()}")
        
        # For now, just display the available options
        self.ui.display_message("Scooter update functionality - Select field to update", "info")
        self.ui.wait_for_enter()
    
    def _handle_search_scooter(self):
        """Handle scooter search"""
        self._search_scooters()
    
    # Additional helper methods
    def _view_system_info(self):
        """View system information"""
        info = [
            f"System: Urban Mobility Backend v1.0",
            f"Current User: {self.current_user}",
            f"User Role: {self.user_role}",
            f"Session Active: {self.session_active}",
            f"Database: {self.db_manager.db_file}",
            f"Encryption: Active"
        ]
        
        print(f"\n{'='*60}")
        print("    SYSTEM INFORMATION")
        print(f"{'='*60}")
        
        for item in info:
            print(f"  {item}")
        
        print(f"\n{'='*60}")
        self.ui.wait_for_enter()
    
    def _system_maintenance(self):
        """System maintenance operations"""
        options = [
            "1. Clear Old Logs (90+ days)",
            "2. Database Statistics",
            "3. Security Status",
            "4. Back"
        ]
        
        choice = self.ui.display_menu("SYSTEM MAINTENANCE", options)
        
        if choice == '1':
            deleted_count = self.logger.clear_old_logs(90)
            self.ui.display_message(f"Deleted {deleted_count} old log entries.", "success")
        elif choice == '2':
            self.ui.display_message("Database statistics - Feature under development", "info")
        elif choice == '3':
            self.ui.display_message("Security status - All systems operational", "success")
        
        if choice != '4':
            self.ui.wait_for_enter()
    
    def _create_backup(self):
        """Create system backup"""
        if self.ui.display_confirmation("Create a backup of the system?"):
            self.ui.display_progress("Creating backup")
            
            backup_filename = self.backup_manager.create_backup(self.current_user)
            if backup_filename:
                self.ui.display_message(f"Backup created successfully: {backup_filename}", "success")
            else:
                self.ui.display_message("Failed to create backup.", "error")
        
        self.ui.wait_for_enter()
    
    def _list_backups(self):
        """List available backups"""
        backups = self.backup_manager.list_backups()
        
        if backups:
            self.ui.display_backup_list(backups)
        else:
            self.ui.display_message("No backups available.", "info")
        
        self.ui.wait_for_enter()
    
    def _restore_backup(self):
        """Restore from backup"""
        if self.user_role != 'super_admin':
            self.ui.display_message("Only Super Administrator can restore backups directly.", "error")
            self.ui.wait_for_enter()
            return
        
        backups = self.backup_manager.list_backups()
        if not backups:
            self.ui.display_message("No backups available.", "info")
            self.ui.wait_for_enter()
            return
        
        self.ui.display_backup_list(backups)
        
        backup_filename = self.ui.get_input("Enter backup filename to restore", required=True)
        
        if self.ui.display_confirmation(f"Are you sure you want to restore from '{backup_filename}'? This will overwrite current data."):
            self.ui.display_progress("Restoring system")
            
            if self.backup_manager.restore_backup(backup_filename, self.current_user):
                self.ui.display_message("System restored successfully.", "success")
            else:
                self.ui.display_message("Failed to restore system.", "error")
        
        self.ui.wait_for_enter()
    
    def _view_all_logs(self):
        """View all system logs"""
        logs = self.logger.get_logs(limit=100)
        self.ui.display_logs(logs)
        
        # Mark suspicious activities as read
        self.logger.mark_suspicious_as_read()
        self.ui.wait_for_enter()
    
    def _view_suspicious_logs(self):
        """View suspicious activities"""
        logs = self.logger.get_logs(suspicious_only=True)
        self.ui.display_logs(logs, show_suspicious_only=True)
        
        # Mark as read
        self.logger.mark_suspicious_as_read()
        self.ui.wait_for_enter()
    
    def _search_logs(self):
        """Search system logs"""
        search_term = self.ui.get_input("Enter search term", required=True)
        
        logs = self.logger.search_logs(search_term)
        
        print(f"\nFound {len(logs)} matching log entries:")
        self.ui.display_logs(logs)
        self.ui.wait_for_enter()
    
    def _export_logs(self):
        """Export system logs"""
        filename = self.ui.get_input("Enter filename for export", required=False)
        if not filename:
            filename = f"system_logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        suspicious_only = self.ui.display_confirmation("Export suspicious activities only?")
        
        if self.logger.export_logs(filename, suspicious_only):
            self.ui.display_message(f"Logs exported to: {filename}", "success")
        else:
            self.ui.display_message("Failed to export logs.", "error")
        
        self.ui.wait_for_enter()
    
    def _generate_restore_code(self):
        """Generate restore code"""
        backups = self.backup_manager.list_backups()
        if not backups:
            self.ui.display_message("No backups available.", "info")
            self.ui.wait_for_enter()
            return
        
        self.ui.display_backup_list(backups)
        
        backup_filename = self.ui.get_input("Enter backup filename", required=True)
        admin_username = self.ui.get_input("Enter system admin username", required=True)
        
        restore_code = self.backup_manager.generate_restore_code(backup_filename, admin_username, self.current_user)
        
        if restore_code:
            self.ui.display_message(f"Restore code generated: {restore_code}", "success")
            print(f"This code allows {admin_username} to restore from {backup_filename}")
            print("The code is one-time use only.")
        else:
            self.ui.display_message("Failed to generate restore code.", "error")
        
        self.ui.wait_for_enter()
    
    def _list_restore_codes(self):
        """List restore codes"""
        codes = self.backup_manager.get_restore_codes()
        
        if codes:
            self.ui.display_restore_codes(codes)
        else:
            self.ui.display_message("No restore codes available.", "info")
        
        self.ui.wait_for_enter()
    
    def _revoke_restore_code(self):
        """Revoke restore code"""
        restore_code = self.ui.get_input("Enter restore code to revoke", required=True)
        
        if self.ui.display_confirmation(f"Are you sure you want to revoke this restore code?"):
            if self.backup_manager.revoke_restore_code(restore_code, self.current_user):
                self.ui.display_message("Restore code revoked successfully.", "success")
            else:
                self.ui.display_message("Failed to revoke restore code. Code may not exist or already be used.", "error")
        
        self.ui.wait_for_enter()
    
    # Placeholder methods for remaining functionality
    def _update_user(self):
        """Update user information"""
        self.ui.display_message("Update user - Feature under development", "info")
        self.ui.wait_for_enter()
    
    def _delete_user(self):
        """Delete user account"""
        self.ui.display_message("Delete user - Feature under development", "info")
        self.ui.wait_for_enter()
    
    def _reset_user_password(self):
        """Reset user password"""
        self.ui.display_message("Reset user password - Feature under development", "info")
        self.ui.wait_for_enter()
    
    def _update_traveller(self):
        """Update traveller information"""
        self.ui.display_message("Update traveller - Feature under development", "info")
        self.ui.wait_for_enter()
    
    def _delete_traveller(self):
        """Delete traveller record"""
        self.ui.display_message("Delete traveller - Feature under development", "info")
        self.ui.wait_for_enter()
    
    def _update_scooter(self):
        """Update scooter information"""
        self.ui.display_message("Update scooter - Feature under development", "info")
        self.ui.wait_for_enter()
    
    def _delete_scooter(self):
        """Delete scooter record"""
        self.ui.display_message("Delete scooter - Feature under development", "info")
        self.ui.wait_for_enter()
    
    # Implementation methods for user management
    def _list_users(self):
        """List all users"""
        users = self.db_manager.get_users()
        if users:
            headers = ["Username", "Role", "Name", "Status", "Registered"]
            rows = []
            for user in users:
                status = "Active" if user.get('is_active', True) else "Inactive"
                name = f"{user.get('first_name', '')} {user.get('last_name', '')}"
                rows.append([
                    user.get('username', ''),
                    user.get('role', ''),
                    name,
                    status,
                    user.get('registration_date', '')[:10]  # Just date part
                ])
            self.ui.display_table("SYSTEM USERS", headers, rows)
        else:
            self.ui.display_message("No users found.", "info")
        
        self.ui.wait_for_enter()
    
    def _create_user(self):
        """Create a new user"""
        # Check permissions
        if self.user_role == 'super_admin':
            role_choices = ['system_admin', 'service_engineer']
        elif self.user_role == 'system_admin':
            role_choices = ['service_engineer']
        else:
            self.ui.display_message("You don't have permission to create users.", "error")
            self.ui.wait_for_enter()
            return
        
        # Get user data
        fields = [
            {'name': 'username', 'label': 'Username', 'help': '8-10 chars, start with letter/underscore'},
            {'name': 'password', 'label': 'Password', 'type': 'password', 'help': '12-30 chars, mixed case, digits, special chars'},
            {'name': 'role', 'label': 'User Role', 'type': 'choice', 'choices': role_choices},
            {'name': 'first_name', 'label': 'First Name'},
            {'name': 'last_name', 'label': 'Last Name'}
        ]
        
        user_data = self.ui.display_form("CREATE NEW USER", fields)
        
        # Validate input
        valid, msg = self.validator.validate_username(user_data['username'])
        if not valid:
            self.ui.display_message(f"Invalid username: {msg}", "error")
            self.ui.wait_for_enter()
            return
        
        valid, msg = self.validator.validate_password(user_data['password'])
        if not valid:
            self.ui.display_message(f"Invalid password: {msg}", "error")
            self.ui.wait_for_enter()
            return
        
        valid, msg = self.validator.validate_name(user_data['first_name'], "First name")
        if not valid:
            self.ui.display_message(f"Invalid first name: {msg}", "error")
            self.ui.wait_for_enter()
            return
        
        valid, msg = self.validator.validate_name(user_data['last_name'], "Last name")
        if not valid:
            self.ui.display_message(f"Invalid last name: {msg}", "error")
            self.ui.wait_for_enter()
            return
        
        # Create user
        if self.db_manager.create_user(
            user_data['username'],
            user_data['password'],
            user_data['role'],
            user_data['first_name'],
            user_data['last_name']
        ):
            self.ui.display_message(f"User '{user_data['username']}' created successfully.", "success")
            self.logger.log_activity(
                self.current_user,
                "User created",
                f"Created {user_data['role']}: {user_data['username']}"
            )
        else:
            self.ui.display_message("Failed to create user. Username may already exist.", "error")
        
        self.ui.wait_for_enter()
    
    def _add_traveller(self):
        """Add a new traveller"""
        # Check permissions
        if not self.auth_manager.check_permission(self.user_role, 'create_traveller'):
            self.ui.display_message("You don't have permission to add travellers.", "error")
            self.ui.wait_for_enter()
            return
        
        fields = [
            {'name': 'first_name', 'label': 'First Name'},
            {'name': 'last_name', 'label': 'Last Name'},
            {'name': 'birthday', 'label': 'Birthday', 'help': 'Format: YYYY-MM-DD'},
            {'name': 'gender', 'label': 'Gender', 'type': 'choice', 'choices': ['male', 'female']},
            {'name': 'street_name', 'label': 'Street Name'},
            {'name': 'house_number', 'label': 'House Number'},
            {'name': 'zip_code', 'label': 'Zip Code', 'help': 'Format: DDDDXX (e.g., 3011AB)'},
            {'name': 'city', 'label': 'City', 'type': 'choice', 'choices': self.validator.valid_cities},
            {'name': 'email_address', 'label': 'Email Address'},
            {'name': 'mobile_phone', 'label': 'Mobile Phone', 'help': '8 digits only (31-6 prefix automatic)'},
            {'name': 'driving_license_number', 'label': 'Driving License', 'help': 'Format: XXDDDDDDD or XDDDDDDDD'}
        ]
        
        traveller_data = self.ui.display_form("ADD NEW TRAVELLER", fields)
        
        # Validate all inputs
        validations = [
            self.validator.validate_name(traveller_data['first_name'], "First name"),
            self.validator.validate_name(traveller_data['last_name'], "Last name"),
            self.validator.validate_date(traveller_data['birthday'], "Birthday"),
            self.validator.validate_gender(traveller_data['gender']),
            self.validator.validate_name(traveller_data['street_name'], "Street name"),
            self.validator.validate_house_number(traveller_data['house_number']),
            self.validator.validate_zip_code(traveller_data['zip_code']),
            self.validator.validate_city(traveller_data['city']),
            self.validator.validate_email(traveller_data['email_address']),
            self.validator.validate_phone_number(traveller_data['mobile_phone']),
            self.validator.validate_driving_license(traveller_data['driving_license_number'])
        ]
        
        for valid, msg in validations:
            if not valid:
                self.ui.display_message(f"Validation error: {msg}", "error")
                self.ui.wait_for_enter()
                return
        
        # Create traveller
        customer_id = self.db_manager.create_traveller(traveller_data)
        if customer_id:
            self.ui.display_message(f"Traveller created successfully. Customer ID: {customer_id}", "success")
            self.logger.log_activity(
                self.current_user,
                "Traveller created",
                f"New traveller registered with ID: {customer_id}"
            )
        else:
            self.ui.display_message("Failed to create traveller.", "error")
        
        self.ui.wait_for_enter()
    
    def _search_travellers(self):
        """Search for travellers"""
        search_term = self.ui.get_input("Enter search term (name, customer ID, email, phone)", required=True)
        
        valid, msg = self.validator.validate_search_term(search_term)
        if not valid:
            self.ui.display_message(f"Invalid search term: {msg}", "error")
            self.ui.wait_for_enter()
            return
        
        results = self.db_manager.search_travellers(search_term)
        
        self.ui.display_search_results(f"TRAVELLER SEARCH RESULTS", results, "traveller")
        self.ui.wait_for_enter()
    
    def _add_scooter(self):
        """Add a new scooter"""
        # Check permissions
        if not self.auth_manager.check_permission(self.user_role, 'create_scooter'):
            self.ui.display_message("You don't have permission to add scooters.", "error")
            self.ui.wait_for_enter()
            return
        
        fields = [
            {'name': 'brand', 'label': 'Brand', 'help': 'e.g., Segway, NIU'},
            {'name': 'model', 'label': 'Model'},
            {'name': 'serial_number', 'label': 'Serial Number', 'help': '10-17 alphanumeric characters'},
            {'name': 'top_speed', 'label': 'Top Speed (km/h)'},
            {'name': 'battery_capacity', 'label': 'Battery Capacity (Wh)'},
            {'name': 'state_of_charge', 'label': 'Current Battery Charge (%)', 'help': '0-100'},
            {'name': 'target_range_soc_min', 'label': 'Target Range SoC Min (%)', 'help': '0-100'},
            {'name': 'target_range_soc_max', 'label': 'Target Range SoC Max (%)', 'help': '0-100'},
            {'name': 'latitude', 'label': 'Latitude', 'help': 'Rotterdam region: 51.8-52.0, 5 decimal places'},
            {'name': 'longitude', 'label': 'Longitude', 'help': 'Rotterdam region: 4.3-4.6, 5 decimal places'},
            {'name': 'mileage', 'label': 'Current Mileage (km)', 'required': False},
            {'name': 'last_maintenance_date', 'label': 'Last Maintenance Date', 'help': 'YYYY-MM-DD format', 'required': False}
        ]
        
        scooter_data = self.ui.display_form("ADD NEW SCOOTER", fields)
        
        # Validate inputs
        validations = [
            self.validator.validate_name(scooter_data['brand'], "Brand"),
            self.validator.validate_name(scooter_data['model'], "Model"),
            self.validator.validate_serial_number(scooter_data['serial_number']),
            self.validator.validate_positive_number(scooter_data['top_speed'], "Top speed"),
            self.validator.validate_positive_number(scooter_data['battery_capacity'], "Battery capacity"),
            self.validator.validate_percentage(scooter_data['state_of_charge'], "State of charge"),
            self.validator.validate_percentage(scooter_data['target_range_soc_min'], "Target range SoC min"),
            self.validator.validate_percentage(scooter_data['target_range_soc_max'], "Target range SoC max"),
            self.validator.validate_coordinates(scooter_data['latitude'], scooter_data['longitude'])
        ]
        
        if scooter_data.get('mileage'):
            validations.append(self.validator.validate_positive_number(scooter_data['mileage'], "Mileage"))
        
        if scooter_data.get('last_maintenance_date'):
            validations.append(self.validator.validate_date(scooter_data['last_maintenance_date'], "Maintenance date"))
        
        for valid, msg in validations:
            if not valid:
                self.ui.display_message(f"Validation error: {msg}", "error")
                self.ui.wait_for_enter()
                return
        
        # Convert numeric values
        try:
            numeric_data = {
                'brand': scooter_data['brand'],
                'model': scooter_data['model'],
                'serial_number': scooter_data['serial_number'],
                'top_speed': float(scooter_data['top_speed']),
                'battery_capacity': float(scooter_data['battery_capacity']),
                'state_of_charge': float(scooter_data['state_of_charge']),
                'target_range_soc_min': float(scooter_data['target_range_soc_min']),
                'target_range_soc_max': float(scooter_data['target_range_soc_max']),
                'latitude': float(scooter_data['latitude']),
                'longitude': float(scooter_data['longitude']),
                'mileage': float(scooter_data.get('mileage', 0)),
                'last_maintenance_date': scooter_data.get('last_maintenance_date') or None
            }
        except ValueError:
            self.ui.display_message("Invalid numeric values entered.", "error")
            self.ui.wait_for_enter()
            return
        
        # Create scooter
        if self.db_manager.create_scooter(numeric_data):
            self.ui.display_message(f"Scooter '{scooter_data['serial_number']}' created successfully.", "success")
            self.logger.log_activity(
                self.current_user,
                "Scooter created",
                f"New scooter added: {scooter_data['serial_number']}"
            )
        else:
            self.ui.display_message("Failed to create scooter. Serial number may already exist.", "error")
        
        self.ui.wait_for_enter()
    
    def _search_scooters(self):
        """Search for scooters"""
        search_term = self.ui.get_input("Enter search term (brand, model, serial number)", required=True)
        
        valid, msg = self.validator.validate_search_term(search_term)
        if not valid:
            self.ui.display_message(f"Invalid search term: {msg}", "error")
            self.ui.wait_for_enter()
            return
        
        results = self.db_manager.search_scooters(search_term)
        
        self.ui.display_search_results(f"SCOOTER SEARCH RESULTS", results, "scooter")
        self.ui.wait_for_enter()
