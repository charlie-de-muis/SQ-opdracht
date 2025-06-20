#!/usr/bin/env python3

import os
import sys
import time
import getpass
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

from database_manager import DatabaseManager
from auth_manager import AuthManager
from input_validator import InputValidator
from crypto_manager import CryptoManager
from logger import SystemLogger
from backup_manager import BackupManager
from user_interface import UserInterface

class UrbanMobilitySystem:   
    def __init__(self):
        self.current_user = None
        self.user_role = None
        self.session_active = False
        self.failed_login_attempts = 0
        self.max_failed_attempts = 3
        self._initialize_components()
        
    def _initialize_components(self):
        try:
            self.crypto = CryptoManager()
            self.logger = SystemLogger(self.crypto)
            self.db_manager = DatabaseManager(self.crypto, self.logger)
            self.auth_manager = AuthManager(self.db_manager, self.logger)
            self.validator = InputValidator()
            self.backup_manager = BackupManager(self.db_manager, self.logger)
            self.ui = UserInterface()
            self.db_manager.initialize_database()
            self.logger.log_activity("SYSTEM", "System startup", "System initialized successfully")
            
        except Exception as e:
            print(f"Failed to initialize system components: {e}")
            sys.exit(1)
    
    def run(self):
        self.ui.display_welcome()
        
        while True:
            try:
                if not self.session_active:
                    if not self._handle_login():
                        continue
                
                self._check_suspicious_activity()
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

        user_info = self.auth_manager.authenticate_user(username, password)
        
        if user_info:
            self.current_user = username
            self.user_role = user_info['role']
            self.session_active = True
            self.failed_login_attempts = 0

            self.logger.log_activity(username, "Logged in", "Successful login")
            
            print(f"\nWelcome, {user_info['first_name']} {user_info['last_name']}!")
            print(f"Role: {self.user_role}")
            return True
        else:
            self.failed_login_attempts += 1
            print("Invalid username or password.")

            self.logger.log_activity(
                username,
                "Failed login",
                f"Failed login attempt for username: {username}",
                suspicious=(self.failed_login_attempts >= 2)
            )
            return False
    
    def _handle_logout(self):
        if self.current_user:
            self.logger.log_activity(self.current_user, "Logged out", "User logged out")
            print(f"\nGoodbye, {self.current_user}!")
        
        self.current_user = None
        self.user_role = None
        self.session_active = False
    
    def _check_suspicious_activity(self):
        if self.user_role in ['super_admin', 'system_admin']:
            suspicious_count = self.logger.get_unread_suspicious_count()
            if suspicious_count > 0:
                print(f"\n⚠️  ALERT: {suspicious_count} suspicious activities detected!")
                print("Use 'View Logs' option to review suspicious activities.")
    
    def _show_main_menu(self):
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

    def _handle_user_management(self):
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
        self._handle_user_management()
    
    def _handle_backup_system(self):
        self._create_backup()
    
    def _handle_restore_with_code(self):
        restore_code = self.ui.get_input("Enter restore code", required=True)
        
        if self.ui.display_confirmation(f"Are you sure you want to restore the system using this code?"):
            self.ui.display_progress("Restoring system")
            
            if self.backup_manager.restore_with_code(restore_code, self.current_user):
                self.ui.display_message("System restored successfully.", "success")
            else:
                self.ui.display_message("Failed to restore system. Invalid or expired code.", "error")
        
        self.ui.wait_for_enter()
    
    def _handle_update_password(self):
        current_password = self.ui.get_input("Enter current password", "password", required=True)
        
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
        
        valid, msg = self.validator.validate_password(new_password)
        if not valid:
            self.ui.display_message(f"Invalid password: {msg}", "error")
            self.ui.wait_for_enter()
            return
        
        if self.db_manager.update_user_password(self.current_user, new_password):
            self.ui.display_message("Password updated successfully.", "success")
        else:
            self.ui.display_message("Failed to update password.", "error")
        
        self.ui.wait_for_enter()
    
    def _handle_update_scooter(self):
        serial_number = self.ui.get_input("Enter scooter serial number", required=True)
        
        results = self.db_manager.search_scooters(serial_number)
        if not results:
            self.ui.display_message("Scooter not found.", "error")
            self.ui.wait_for_enter()
            return
        
        scooter = results[0] 

        print(f"\nCurrent scooter information:")
        print(f"Serial: {scooter.get('serial_number')}")
        print(f"Brand/Model: {scooter.get('brand')} {scooter.get('model')}")
        print(f"Battery: {scooter.get('state_of_charge')}%")
        print(f"Location: {scooter.get('latitude')}, {scooter.get('longitude')}")
        
        permissions = self.auth_manager.get_scooter_update_permissions(self.user_role)
        
        updateable_fields = [k for k, v in permissions.items() if v]
        if not updateable_fields:
            self.ui.display_message("You don't have permission to update any scooter fields.", "error")
            self.ui.wait_for_enter()
            return
        
        print(f"\nYou can update the following fields:")
        for i, field in enumerate(updateable_fields, 1):
            print(f"{i}. {field.replace('_', ' ').title()}")
     
        self.ui.display_message("Scooter update functionality - Select field to update", "info")
        self.ui.wait_for_enter()
    
    def _handle_search_scooter(self):
        self._search_scooters()
    
    def _view_system_info(self):
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
            self._show_database_statistics()
        elif choice == '3':
            self.ui.display_message("Security status - All systems operational", "success")
        
        if choice != '4':
            self.ui.wait_for_enter()
    
    def _create_backup(self):
        if self.ui.display_confirmation("Create a backup of the system?"):
            self.ui.display_progress("Creating backup")
            
            backup_filename = self.backup_manager.create_backup(self.current_user)
            if backup_filename:
                self.ui.display_message(f"Backup created successfully: {backup_filename}", "success")
            else:
                self.ui.display_message("Failed to create backup.", "error")
        
        self.ui.wait_for_enter()
    
    def _list_backups(self):
        backups = self.backup_manager.list_backups()
        
        if backups:
            self.ui.display_backup_list(backups)
        else:
            self.ui.display_message("No backups available.", "info")
        
        self.ui.wait_for_enter()
    
    def _restore_backup(self):
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
        logs = self.logger.get_logs(limit=100)
        self.ui.display_logs(logs)
        
        self.logger.mark_suspicious_as_read()
        self.ui.wait_for_enter()
    
    def _view_suspicious_logs(self):
        logs = self.logger.get_logs(suspicious_only=True)
        self.ui.display_logs(logs, show_suspicious_only=True)
        
        self.logger.mark_suspicious_as_read()
        self.ui.wait_for_enter()
    
    def _search_logs(self):
        search_term = self.ui.get_input("Enter search term", required=True)
        
        logs = self.logger.search_logs(search_term)
        
        print(f"\nFound {len(logs)} matching log entries:")
        self.ui.display_logs(logs)
        self.ui.wait_for_enter()
    
    def _export_logs(self):
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
        codes = self.backup_manager.get_restore_codes()
        
        if codes:
            self.ui.display_restore_codes(codes)
        else:
            self.ui.display_message("No restore codes available.", "info")
        
        self.ui.wait_for_enter()
    
    def _revoke_restore_code(self):
        restore_code = self.ui.get_input("Enter restore code to revoke", required=True)
        
        if self.ui.display_confirmation(f"Are you sure you want to revoke this restore code?"):
            if self.backup_manager.revoke_restore_code(restore_code, self.current_user):
                self.ui.display_message("Restore code revoked successfully.", "success")
            else:
                self.ui.display_message("Failed to revoke restore code. Code may not exist or already be used.", "error")
        
        self.ui.wait_for_enter()
    
    def _update_user(self):
        if not self.auth_manager.check_permission(self.user_role, 'update_user'):
            self.ui.display_message("You don't have permission to update users.", "error")
            self.ui.wait_for_enter()
            return
        
        # Get list of users 
        if self.user_role == 'super_admin':
            users = self.db_manager.get_users()
        else:
            users = self.db_manager.get_users('service_engineer')
        
        if not users:
            self.ui.display_message("No users found to update.", "info")
            self.ui.wait_for_enter()
            return
    
        self.ui.display_search_results("SELECT USER TO UPDATE", users, "user")
        
        username = self.ui.get_input("Enter username to update", required=True)
        
        # Find user
        user_to_update = None
        for user in users:
            if user['username'].lower() == username.lower():
                user_to_update = user
                break
        
        if not user_to_update:
            self.ui.display_message("User not found.", "error")
            self.ui.wait_for_enter()
            return
        
        fields = [
            {'name': 'first_name', 'label': 'First Name', 'required': False},
            {'name': 'last_name', 'label': 'Last Name', 'required': False}
        ]
        
        print(f"\nCurrent information for {username}:")
        print(f"First Name: {user_to_update['first_name']}")
        print(f"Last Name: {user_to_update['last_name']}")
        print("\nLeave fields empty to keep current values.")
        
        update_data = self.ui.display_form("UPDATE USER INFORMATION", fields)
        
        if update_data['first_name']:
            valid, msg = self.validator.validate_name(update_data['first_name'], "First name")
            if not valid:
                self.ui.display_message(f"Invalid first name: {msg}", "error")
                self.ui.wait_for_enter()
                return
        
        if update_data['last_name']:
            valid, msg = self.validator.validate_name(update_data['last_name'], "Last name")
            if not valid:
                self.ui.display_message(f"Invalid last name: {msg}", "error")
                self.ui.wait_for_enter()
                return
        
        # Update user in database
        if self.db_manager.update_user_info(username, update_data):
            self.ui.display_message(f"User '{username}' updated successfully.", "success")
            self.logger.log_activity(
                self.current_user,
                "User updated",
                f"Updated user information for: {username}"
            )
        else:
            self.ui.display_message("Failed to update user.", "error")
        
        self.ui.wait_for_enter()
    
    def _delete_user(self):
        if not self.auth_manager.check_permission(self.user_role, 'delete_user'):
            self.ui.display_message("You don't have permission to delete users.", "error")
            self.ui.wait_for_enter()
            return

        if self.user_role == 'super_admin':
            users = self.db_manager.get_users()
        else:
            users = self.db_manager.get_users('service_engineer')
        
        if not users:
            self.ui.display_message("No users found to delete.", "info")
            self.ui.wait_for_enter()
            return
        
        # Display users
        self.ui.display_search_results("SELECT USER TO DELETE", users, "user")
        
        username = self.ui.get_input("Enter username to delete", required=True)
        
        # Prevent deletion of super_admin
        if username.lower() == 'super_admin':
            self.ui.display_message("Cannot delete super administrator account.", "error")
            self.ui.wait_for_enter()
            return
        
        if username.lower() == self.current_user.lower() and self.user_role == 'system_admin':
            if not self.ui.display_confirmation("You are about to delete your own account. This will log you out immediately. Are you sure?"):
                return
        
        user_exists = any(user['username'].lower() == username.lower() for user in users)
        if not user_exists:
            self.ui.display_message("User not found.", "error")
            self.ui.wait_for_enter()
            return
        
        if self.ui.display_confirmation(f"Are you sure you want to delete user '{username}'? This cannot be undone."):
            if self.db_manager.delete_user(username):
                self.ui.display_message(f"User '{username}' deleted successfully.", "success")
                self.logger.log_activity(
                    self.current_user,
                    "User deleted",
                    f"Deleted user account: {username}"
                )
                
                if username.lower() == self.current_user.lower():
                    self.ui.display_message("You have deleted your own account. Logging out...", "warning")
                    self.ui.wait_for_enter()
                    self._handle_logout()
                    return
            else:
                self.ui.display_message("Failed to delete user.", "error")
        
        self.ui.wait_for_enter()
    
    def _reset_user_password(self):
        if not self.auth_manager.check_permission(self.user_role, 'reset_password'):
            self.ui.display_message("You don't have permission to reset passwords.", "error")
            self.ui.wait_for_enter()
            return
        
        if self.user_role == 'super_admin':
            users = self.db_manager.get_users()
        else:
            users = self.db_manager.get_users('service_engineer')
        
        if not users:
            self.ui.display_message("No users found.", "info")
            self.ui.wait_for_enter()
            return
        
        self.ui.display_search_results("SELECT USER FOR PASSWORD RESET", users, "user")
        
        username = self.ui.get_input("Enter username for password reset", required=True)
        
        user_exists = any(user['username'].lower() == username.lower() for user in users)
        if not user_exists:
            self.ui.display_message("User not found.", "error")
            self.ui.wait_for_enter()
            return
        
        new_password = self.ui.get_input("Enter new temporary password", "password", required=True)
        confirm_password = self.ui.get_input("Confirm new password", "password", required=True)
        
        if new_password != confirm_password:
            self.ui.display_message("Passwords do not match.", "error")
            self.ui.wait_for_enter()
            return
        
        valid, msg = self.validator.validate_password(new_password)
        if not valid:
            self.ui.display_message(f"Invalid password: {msg}", "error")
            self.ui.wait_for_enter()
            return
        
        if self.ui.display_confirmation(f"Reset password for user '{username}'?"):
            if self.db_manager.update_user_password(username, new_password):
                self.ui.display_message(f"Password reset successfully for '{username}'.", "success")
                print(f"Temporary password: {new_password}")
                print("User should change this password on next login.")
                
                self.logger.log_activity(
                    self.current_user,
                    "Password reset",
                    f"Reset password for user: {username}"
                )
            else:
                self.ui.display_message("Failed to reset password.", "error")
        
        self.ui.wait_for_enter()
    def _update_traveller(self):
        if not self.auth_manager.check_permission(self.user_role, 'update_traveller'):
            self.ui.display_message("You don't have permission to update travellers.", "error")
            self.ui.wait_for_enter()

        search_term = self.ui.get_input("Enter customer ID or name to find traveller", required=True)
        
        results = self.db_manager.search_travellers(search_term)
        if not results:
            self.ui.display_message("Traveller not found.", "error")
            self.ui.wait_for_enter()
            return
        
        if len(results) > 1:
            self.ui.display_search_results("FOUND TRAVELLERS", results, "traveller")
            customer_id = self.ui.get_input("Enter customer ID to update", required=True)
            
            traveller = None
            for result in results:
                if result['customer_id'] == customer_id:
                    traveller = result
                    break
            
            if not traveller:
                self.ui.display_message("Invalid customer ID selected.", "error")
                self.ui.wait_for_enter()
                return
        else:
            traveller = results[0]
        
        # Show current information
        print(f"\nCurrent traveller information:")
        print(f"Customer ID: {traveller.get('customer_id')}")
        print(f"Name: {traveller.get('first_name')} {traveller.get('last_name')}")
        print(f"Email: {traveller.get('email_address')}")
        print(f"Phone: +31-6-{traveller.get('mobile_phone')}")
        
        fields = [
            {'name': 'first_name', 'label': f"First Name (current: {traveller.get('first_name')})", 'required': False},
            {'name': 'last_name', 'label': f"Last Name (current: {traveller.get('last_name')})", 'required': False},
            {'name': 'email_address', 'label': f"Email (current: {traveller.get('email_address')})", 'required': False},
            {'name': 'mobile_phone', 'label': f"Mobile Phone (current: {traveller.get('mobile_phone')})", 'required': False}
        ]
        
        updated_data = self.ui.display_form("UPDATE TRAVELLER (leave empty to keep current)", fields)
        
        update_fields = {}
        for field, value in updated_data.items():
            if value:
                update_fields[field] = value
        
        if not update_fields:
            self.ui.display_message("No changes specified.", "info")
            self.ui.wait_for_enter()
            return
        
        for field, value in update_fields.items():
            if field in ['first_name', 'last_name']:
                valid, msg = self.validator.validate_name(value, field.replace('_', ' ').title())
            elif field == 'email_address':
                valid, msg = self.validator.validate_email(value)
            elif field == 'mobile_phone':
                valid, msg = self.validator.validate_phone_number(value)
            else:
                valid, msg = True, "Valid"
            
            if not valid:
                self.ui.display_message(f"Invalid {field}: {msg}", "error")
                self.ui.wait_for_enter()
                return
        
        # Update in database
        if self.db_manager.update_traveller(traveller['customer_id'], update_fields):
            self.ui.display_message("Traveller updated successfully.", "success")
            self.logger.log_activity(
                self.current_user,
                "Traveller updated",
                f"Updated traveller {traveller['customer_id']}: {', '.join(update_fields.keys())}"
            )
        else:
            self.ui.display_message("Failed to update traveller.", "error")
        
        self.ui.wait_for_enter()
    
    def _delete_traveller(self):

        if not self.auth_manager.check_permission(self.user_role, 'delete_traveller'):
            self.ui.display_message("You don't have permission to delete travellers.", "error")
            self.ui.wait_for_enter()
            return
        
        search_term = self.ui.get_input("Enter customer ID or name to find traveller", required=True)
        
        results = self.db_manager.search_travellers(search_term)
        if not results:
            self.ui.display_message("Traveller not found.", "error")
            self.ui.wait_for_enter()
            return
        
        self.ui.display_search_results("FOUND TRAVELLERS", results, "traveller")
        
        customer_id = self.ui.get_input("Enter customer ID to delete", required=True)
        
        # Find the specific traveller
        traveller = None
        for result in results:
            if result['customer_id'] == customer_id:
                traveller = result
                break
        
        if not traveller:
            self.ui.display_message("Invalid customer ID.", "error")
            self.ui.wait_for_enter()
            return
        
        traveller_name = f"{traveller.get('first_name')} {traveller.get('last_name')}"
        if not self.ui.display_confirmation(f"Are you sure you want to delete traveller {traveller_name} (ID: {customer_id})?"):
            self.ui.display_message("Deletion cancelled.", "info")
            self.ui.wait_for_enter()
            return
        
        if self.db_manager.delete_traveller(customer_id):
            self.ui.display_message("Traveller deleted successfully.", "success")
            self.logger.log_activity(
                self.current_user,
                "Traveller deleted",
                f"Deleted traveller {customer_id}: {traveller_name}"
            )
        else:
            self.ui.display_message("Failed to delete traveller.", "error")
        
        self.ui.wait_for_enter()

    def _update_scooter(self):
        if not self.auth_manager.check_permission(self.user_role, 'update_scooter'):
            self.ui.display_message("You don't have permission to update scooters.", "error")
            self.ui.wait_for_enter()
            return
        
        # Search for scooter
        search_term = self.ui.get_input("Enter serial number, brand, or model to find scooter", required=True)
        
        results = self.db_manager.search_scooters(search_term)
        if not results:
            self.ui.display_message("Scooter not found.", "error")
            self.ui.wait_for_enter()
            return
        
        # Show results and let user pick
        if len(results) > 1:
            self.ui.display_search_results("FOUND SCOOTERS", results, "scooter")
            serial_number = self.ui.get_input("Enter serial number to update", required=True)
            
            # Find the specific scooter
            scooter = None
            for result in results:
                if result['serial_number'] == serial_number:
                    scooter = result
                    break
            
            if not scooter:
                self.ui.display_message("Invalid serial number selected.", "error")
                self.ui.wait_for_enter()
                return
        else:
            scooter = results[0]
        e
        permissions = self.auth_manager.get_scooter_update_permissions(self.user_role)
        
        print(f"\nCurrent scooter information:")
        print(f"Serial: {scooter.get('serial_number')}")
        print(f"Brand/Model: {scooter.get('brand')} {scooter.get('model')}")
        print(f"Battery: {scooter.get('state_of_charge')}%")
        print(f"Location: {scooter.get('latitude')}, {scooter.get('longitude')}")
        print(f"Status: {'Out of Service' if scooter.get('out_of_service_status') else 'In Service'}")
        
        fields = []
        if permissions.get('state_of_charge'):
            fields.append({
                'name': 'state_of_charge',
                'label': f"Battery Charge % (current: {scooter.get('state_of_charge')})",
                'required': False,
                'help': '0-100'
            })
        
        if permissions.get('latitude') and permissions.get('longitude'):
            fields.extend([
                {
                    'name': 'latitude',
                    'label': f"Latitude (current: {scooter.get('latitude')})",
                    'required': False,
                    'help': 'Rotterdam region: 51.8-52.0'
                },
                {
                    'name': 'longitude', 
                    'label': f"Longitude (current: {scooter.get('longitude')})",
                    'required': False,
                    'help': 'Rotterdam region: 4.3-4.6'
                }
            ])
        
        if permissions.get('out_of_service_status'):
            current_status = 'Out of Service' if scooter.get('out_of_service_status') else 'In Service'
            fields.append({
                'name': 'out_of_service_status',
                'label': f"Service Status (current: {current_status})",
                'type': 'choice',
                'choices': ['In Service', 'Out of Service'],
                'required': False
            })
        
        if permissions.get('mileage'):
            fields.append({
                'name': 'mileage',
                'label': f"Mileage km (current: {scooter.get('mileage')})",
                'required': False
            })
        
        if permissions.get('last_maintenance_date'):
            fields.append({
                'name': 'last_maintenance_date',
                'label': f"Last Maintenance (current: {scooter.get('last_maintenance_date')})",
                'required': False,
                'help': 'YYYY-MM-DD format'
            })
        
        if not fields:
            self.ui.display_message("You don't have permission to update any scooter fields.", "error")
            self.ui.wait_for_enter()
            return

        updated_data = self.ui.display_form("UPDATE SCOOTER (leave empty to keep current)", fields)
        update_fields = {}
        for field, value in updated_data.items():
            if value: 
                if field == 'out_of_service_status':
                    update_fields[field] = 1 if value == 'Out of Service' else 0
                else:
                    update_fields[field] = value
        
        if not update_fields:
            self.ui.display_message("No changes specified.", "info")
            self.ui.wait_for_enter()
            return
        
        for field, value in update_fields.items():
            if field == 'state_of_charge':
                valid, msg = self.validator.validate_percentage(str(value), "State of charge")
            elif field in ['latitude', 'longitude']:
                if field == 'latitude':
                    lon_val = update_fields.get('longitude', scooter.get('longitude'))
                    valid, msg = self.validator.validate_coordinates(str(value), str(lon_val))
                elif field == 'longitude':
                    lat_val = update_fields.get('latitude', scooter.get('latitude'))
                    valid, msg = self.validator.validate_coordinates(str(lat_val), str(value))
            elif field == 'mileage':
                valid, msg = self.validator.validate_positive_number(str(value), "Mileage")
            elif field == 'last_maintenance_date':
                valid, msg = self.validator.validate_date(value, "Maintenance date")
            else:
                valid, msg = True, "Valid"
            
            if not valid:
                self.ui.display_message(f"Invalid {field}: {msg}", "error")
                self.ui.wait_for_enter()
                return
        
        try:
            for field in ['state_of_charge', 'latitude', 'longitude', 'mileage']:
                if field in update_fields:
                    update_fields[field] = float(update_fields[field])
        except ValueError:
            self.ui.display_message("Invalid numeric values entered.", "error")
            self.ui.wait_for_enter()
            return
        
        if self.db_manager.update_scooter(scooter['serial_number'], update_fields):
            self.ui.display_message("Scooter updated successfully.", "success")
            self.logger.log_activity(
                self.current_user,
                "Scooter updated",
                f"Updated scooter {scooter['serial_number']}: {', '.join(update_fields.keys())}"
            )
        else:
            self.ui.display_message("Failed to update scooter.", "error")
        
        self.ui.wait_for_enter()
    
    def _delete_scooter(self):
        if not self.auth_manager.check_permission(self.user_role, 'delete_scooter'):
            self.ui.display_message("You don't have permission to delete scooters.", "error")
            self.ui.wait_for_enter()
            return
        
        # Search for scooter
        search_term = self.ui.get_input("Enter serial number, brand, or model to find scooter", required=True)
        
        results = self.db_manager.search_scooters(search_term)
        if not results:
            self.ui.display_message("Scooter not found.", "error")
            self.ui.wait_for_enter()
            return
        
        self.ui.display_search_results("FOUND SCOOTERS", results, "scooter")
        
        serial_number = self.ui.get_input("Enter serial number to delete", required=True)
        
        # Find the specific scooter
        scooter = None
        for result in results:
            if result['serial_number'] == serial_number:
                scooter = result
                break
        
        if not scooter:
            self.ui.display_message("Invalid serial number.", "error")
            self.ui.wait_for_enter()
            return
        
        scooter_info = f"{scooter.get('brand')} {scooter.get('model')} (Serial: {serial_number})"
        if not self.ui.display_confirmation(f"Are you sure you want to delete scooter {scooter_info}?"):
            self.ui.display_message("Deletion cancelled.", "info")
            self.ui.wait_for_enter()
            return
        
        # Delete from database
        if self.db_manager.delete_scooter(serial_number):
            self.ui.display_message("Scooter deleted successfully.", "success")
            self.logger.log_activity(
                self.current_user,
                "Scooter deleted",
                f"Deleted scooter {serial_number}: {scooter_info}"
            )
        else:
            self.ui.display_message("Failed to delete scooter.", "error")
        
        self.ui.wait_for_enter()

    def _list_users(self):
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
                    user.get('registration_date', '')[:10]  
                ])
            self.ui.display_table("SYSTEM USERS", headers, rows)
        else:
            self.ui.display_message("No users found.", "info")
        
        self.ui.wait_for_enter()
    
    def _create_user(self):
        if self.user_role == 'super_admin':
            role_choices = ['system_admin', 'service_engineer']
        elif self.user_role == 'system_admin':
            role_choices = ['service_engineer']
        else:
            self.ui.display_message("You don't have permission to create users.", "error")
            self.ui.wait_for_enter()
            return
        
        fields = [
            {'name': 'username', 'label': 'Username', 'help': '8-10 chars, start with letter/underscore'},
            {'name': 'password', 'label': 'Password', 'type': 'password', 'help': '12-30 chars, mixed case, digits, special chars'},
            {'name': 'role', 'label': 'User Role', 'type': 'choice', 'choices': role_choices},
            {'name': 'first_name', 'label': 'First Name'},
            {'name': 'last_name', 'label': 'Last Name'}
        ]
        
        user_data = self.ui.display_form("CREATE NEW USER", fields)
        
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
        search_term = self.ui.get_input("Enter search term (brand, model, serial number)", required=True)
        
        valid, msg = self.validator.validate_search_term(search_term)
        if not valid:
            self.ui.display_message(f"Invalid search term: {msg}", "error")
            self.ui.wait_for_enter()
            return
        
        results = self.db_manager.search_scooters(search_term)
        
        self.ui.display_search_results(f"SCOOTER SEARCH RESULTS", results, "scooter")
        self.ui.wait_for_enter()
    
    def _show_database_statistics(self):
        try:
            conn = self.db_manager._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT role, COUNT(*) FROM users WHERE is_active = 1 GROUP BY role")
            user_stats = cursor.fetchall()
            
            cursor.execute("SELECT COUNT(*) FROM travellers")
            traveller_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM scooters")
            scooter_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT out_of_service_status, COUNT(*) FROM scooters GROUP BY out_of_service_status")
            scooter_status = cursor.fetchall()
            
            cursor.execute("SELECT is_used, COUNT(*) FROM restore_codes GROUP BY is_used")
            restore_codes = cursor.fetchall()
            
            print(f"\n{'='*60}")
            print("    DATABASE STATISTICS")
            print(f"{'='*60}")
            
            print("\nUser Statistics:")
            for role, count in user_stats:
                print(f"  {role.replace('_', ' ').title()}: {count}")
            
            print(f"\nData Statistics:")
            print(f"  Total Travellers: {traveller_count}")
            print(f"  Total Scooters: {scooter_count}")
            
            print(f"\nScooter Status:")
            for status, count in scooter_status:
                status_text = "Out of Service" if status else "In Service"
                print(f"  {status_text}: {count}")
            
            print(f"\nRestore Codes:")
            for used, count in restore_codes:
                status_text = "Used" if used else "Active"
                print(f"  {status_text}: {count}")
            
            logs = self.logger.get_logs()
            suspicious_logs = [log for log in logs if log.get('suspicious', False)]
            
            print(f"\nLog Statistics:")
            print(f"  Total Log Entries: {len(logs)}")
            print(f"  Suspicious Activities: {len(suspicious_logs)}")
            
            print(f"\n{'='*60}")
            
        except Exception as e:
            self.ui.display_message(f"Failed to retrieve database statistics: {e}", "error")
        
        self.ui.wait_for_enter()
