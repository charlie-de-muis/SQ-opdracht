#!/usr/bin/env python3

import os
from typing import List, Dict, Any, Optional

class UserInterface:
    """Handles user interface display and input"""
    
    def __init__(self):
        """Initialize the user interface"""
        self.screen_width = 80
        
    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_welcome(self):
        """Display welcome screen"""
        self.clear_screen()
        print("=" * self.screen_width)
        print(" " * 20 + "URBAN MOBILITY BACKEND SYSTEM")
        print(" " * 25 + "Secure Management Console")
        print("=" * self.screen_width)
        print()
        print("Security Features:")
        print("• Encrypted data storage")
        print("• Secure user authentication")
        print("• Comprehensive activity logging")
        print("• Role-based access control")
        print("• Input validation and SQL injection protection")
        print()
        print("Press Ctrl+C at any time to exit")
        print("=" * self.screen_width)
    
    def display_menu(self, title: str, options: List[str], user_info: Optional[str] = None) -> str:
        """Display a menu and get user choice"""
        print(f"\n{'='*self.screen_width}")
        print(f"    {title}")
        if user_info:
            print(f"    {user_info}")
        print(f"{'='*self.screen_width}")
        
        for option in options:
            print(f"  {option}")
        
        print(f"{'='*self.screen_width}")
        choice = input("Enter your choice: ").strip()
        return choice
    
    def display_table(self, title: str, headers: List[str], rows: List[List[str]], max_width: int = 15):
        """Display data in table format"""
        print(f"\n{title}")
        print("=" * len(title))
        
        if not rows:
            print("No data to display.")
            return
        
        # Calculate column widths
        col_widths = []
        for i, header in enumerate(headers):
            max_len = len(header)
            for row in rows:
                if i < len(row):
                    max_len = max(max_len, len(str(row[i])))
            col_widths.append(min(max_len, max_width))
        
        # Print header
        header_row = " | ".join(header.ljust(col_widths[i]) for i, header in enumerate(headers))
        print(header_row)
        print("-" * len(header_row))
        
        # Print rows
        for row in rows:
            formatted_row = []
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    cell_str = str(cell)
                    if len(cell_str) > max_width:
                        cell_str = cell_str[:max_width-3] + "..."
                    formatted_row.append(cell_str.ljust(col_widths[i]))
            print(" | ".join(formatted_row))
    
    def display_form(self, title: str, fields: List[Dict[str, str]]) -> Dict[str, str]:
        """Display a form and collect input"""
        print(f"\n{'='*self.screen_width}")
        print(f"    {title}")
        print(f"{'='*self.screen_width}")
        
        form_data = {}
        
        for field in fields:
            field_name = field['name']
            field_label = field.get('label', field_name)
            field_type = field.get('type', 'text')
            field_help = field.get('help', '')
            required = field.get('required', True)
            
            while True:
                print(f"\n{field_label}:")
                if field_help:
                    print(f"  {field_help}")
                
                if field_type == 'password':
                    import getpass
                    value = getpass.getpass("  Enter value: ")
                elif field_type == 'choice':
                    choices = field.get('choices', [])
                    for i, choice in enumerate(choices, 1):
                        print(f"  {i}. {choice}")
                    choice_input = input("  Select option (number): ").strip()
                    try:
                        choice_idx = int(choice_input) - 1
                        if 0 <= choice_idx < len(choices):
                            value = choices[choice_idx]
                        else:
                            print("  Invalid choice. Please try again.")
                            continue
                    except ValueError:
                        print("  Invalid choice. Please enter a number.")
                        continue
                else:
                    value = input("  Enter value: ").strip()
                
                if not value and required:
                    print("  This field is required. Please enter a value.")
                    continue
                
                form_data[field_name] = value
                break
        
        return form_data
    
    def display_confirmation(self, message: str) -> bool:
        """Display confirmation dialog"""
        while True:
            response = input(f"\n{message} (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")
    
    def display_message(self, message: str, message_type: str = "info"):
        """Display a message with appropriate formatting"""
        if message_type == "success":
            print(f"\n✓ SUCCESS: {message}")
        elif message_type == "error":
            print(f"\n✗ ERROR: {message}")
        elif message_type == "warning":
            print(f"\n⚠ WARNING: {message}")
        elif message_type == "info":
            print(f"\nℹ INFO: {message}")
        else:
            print(f"\n{message}")
    
    def display_logs(self, logs: List[Dict[str, Any]], show_suspicious_only: bool = False):
        """Display system logs in formatted view"""
        if show_suspicious_only:
            title = "SUSPICIOUS ACTIVITIES LOG"
            logs = [log for log in logs if log.get('suspicious', False)]
        else:
            title = "SYSTEM ACTIVITY LOG"
        
        print(f"\n{'='*self.screen_width}")
        print(f"    {title}")
        print(f"{'='*self.screen_width}")
        
        if not logs:
            print("No log entries to display.")
            return
        
        for log in logs[:50]:  # Limit to 50 most recent entries
            print(f"\nID: {log.get('id', 'N/A')}")
            print(f"Date/Time: {log.get('date', 'N/A')} {log.get('time', 'N/A')}")
            print(f"User: {log.get('username', 'N/A')}")
            print(f"Activity: {log.get('activity', 'N/A')}")
            if log.get('details'):
                print(f"Details: {log.get('details')}")
            if log.get('suspicious', False):
                print("⚠ SUSPICIOUS ACTIVITY")
            print("-" * 60)
        
        if len(logs) > 50:
            print(f"\n... and {len(logs) - 50} more entries")
    
    def display_search_results(self, title: str, results: List[Dict[str, Any]], result_type: str):
        """Display search results"""
        print(f"\n{'='*self.screen_width}")
        print(f"    {title}")
        print(f"    Found {len(results)} results")
        print(f"{'='*self.screen_width}")
        
        if not results:
            print("No results found.")
            return
        
        if result_type == "traveller":
            for i, traveller in enumerate(results, 1):
                print(f"\n{i}. Customer ID: {traveller.get('customer_id', 'N/A')}")
                print(f"   Name: {traveller.get('first_name', '')} {traveller.get('last_name', '')}")
                print(f"   Email: {traveller.get('email_address', 'N/A')}")
                print(f"   Phone: +31-6-{traveller.get('mobile_phone', 'N/A')}")
                print(f"   Registered: {traveller.get('registration_date', 'N/A')}")
        
        elif result_type == "scooter":
            for i, scooter in enumerate(results, 1):
                print(f"\n{i}. Serial: {scooter.get('serial_number', 'N/A')}")
                print(f"   Brand/Model: {scooter.get('brand', 'N/A')} {scooter.get('model', 'N/A')}")
                print(f"   Battery: {scooter.get('state_of_charge', 'N/A')}%")
                print(f"   Location: {scooter.get('latitude', 'N/A')}, {scooter.get('longitude', 'N/A')}")
                print(f"   Status: {'Out of Service' if scooter.get('out_of_service_status') else 'In Service'}")
        
        elif result_type == "user":
            for i, user in enumerate(results, 1):
                print(f"\n{i}. Username: {user.get('username', 'N/A')}")
                print(f"   Name: {user.get('first_name', '')} {user.get('last_name', '')}")
                print(f"   Role: {user.get('role', 'N/A')}")
                print(f"   Status: {'Active' if user.get('is_active') else 'Inactive'}")
                print(f"   Registered: {user.get('registration_date', 'N/A')}")
    
    def get_input(self, prompt: str, input_type: str = "text", required: bool = True) -> str:
        """Get validated input from user"""
        while True:
            if input_type == "password":
                import getpass
                value = getpass.getpass(f"{prompt}: ")
            else:
                value = input(f"{prompt}: ").strip()
            
            if not value and required:
                print("This field is required. Please enter a value.")
                continue
            
            return value
    
    def display_progress(self, message: str):
        """Display progress message"""
        print(f"\n⏳ {message}...")
    
    def display_backup_list(self, backups: List[Dict[str, Any]]):
        """Display list of available backups"""
        print(f"\n{'='*self.screen_width}")
        print("    AVAILABLE BACKUPS")
        print(f"{'='*self.screen_width}")
        
        if not backups:
            print("No backups available.")
            return
        
        for i, backup in enumerate(backups, 1):
            size_mb = backup['size'] / (1024 * 1024)
            print(f"\n{i}. {backup['filename']}")
            print(f"   Created by: {backup.get('created_by', 'Unknown')}")
            print(f"   Created: {backup['created_at']}")
            print(f"   Size: {size_mb:.2f} MB")
    
    def display_restore_codes(self, codes: List[Dict[str, Any]]):
        """Display list of restore codes"""
        print(f"\n{'='*self.screen_width}")
        print("    RESTORE CODES")
        print(f"{'='*self.screen_width}")
        
        if not codes:
            print("No restore codes available.")
            return
        
        for i, code in enumerate(codes, 1):
            status = "USED" if code['is_used'] else "ACTIVE"
            print(f"\n{i}. Code: {code['code']}")
            print(f"   For Admin: {code['system_admin_username']}")
            print(f"   Backup: {code['backup_filename']}")
            print(f"   Status: {status}")
            print(f"   Created: {code['created_at']}")
            if code['used_at']:
                print(f"   Used: {code['used_at']}")
    
    def wait_for_enter(self, message: str = "Press Enter to continue..."):
        """Wait for user to press Enter"""
        input(f"\n{message}")
    
    def display_error_details(self, error_message: str, suggestions: List[str] = None):
        """Display detailed error information"""
        print(f"\n{'='*self.screen_width}")
        print("    ERROR DETAILS")
        print(f"{'='*self.screen_width}")
        print(f"\n✗ {error_message}")
        
        if suggestions:
            print("\nSuggestions:")
            for suggestion in suggestions:
                print(f"  • {suggestion}")
        
        print(f"\n{'='*self.screen_width}")
    
    def display_help(self, topic: str):
        """Display help information"""
        help_content = {
            "navigation": [
                "Use menu numbers or letters to navigate",
                "Press Ctrl+C to exit at any time",
                "Follow the prompts for data entry",
                "Required fields are marked and must be filled"
            ],
            "search": [
                "Enter partial terms to search (minimum 2 characters)",
                "Search is case-insensitive",
                "You can search by name, ID, email, or other relevant fields",
                "Use specific terms for better results"
            ],
            "passwords": [
                "Passwords must be 12-30 characters long",
                "Must contain: lowercase, uppercase, digit, special character",
                "Allowed special characters: ~!@#$%&_-+=`|\\(){}[]:;'<>,.?/",
                "Passwords are never stored, only their hashes"
            ],
            "security": [
                "All sensitive data is encrypted in storage",
                "System logs all activities for security monitoring",
                "Failed login attempts are tracked and may lock accounts",
                "Suspicious activities are flagged for review"
            ]
        }
        
        content = help_content.get(topic, ["No help available for this topic"])
        
        print(f"\n{'='*self.screen_width}")
        print(f"    HELP: {topic.upper()}")
        print(f"{'='*self.screen_width}")
        
        for item in content:
            print(f"  • {item}")
        
        print(f"\n{'='*self.screen_width}")
