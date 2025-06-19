#!/usr/bin/env python3

import re
from typing import Optional, List, Tuple
from datetime import datetime

class InputValidator:
    """Handles all input validation for the system"""
    
    def __init__(self):
        """Initialize the input validator"""
        # Predefined city list as per assignment requirements
        self.valid_cities = [
            "Rotterdam", "Amsterdam", "Den Haag", "Utrecht", "Eindhoven",
            "Tilburg", "Groningen", "Almere", "Breda", "Nijmegen"
        ]
        
        # Character whitelists
        self.name_chars = re.compile(r'^[a-zA-Z\s\-\'\.]+$')
        self.username_chars = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_\'\.]*$')
        self.alphanumeric_chars = re.compile(r'^[a-zA-Z0-9]+$')
        self.numeric_chars = re.compile(r'^[0-9]+$')
        self.decimal_chars = re.compile(r'^[0-9]+\.?[0-9]*$')
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        # Password requirements
        self.password_pattern = re.compile(r'^[a-zA-Z0-9~!@#$%&_\-+=`|\\(){}[\]:;\'<>,.?/]+$')
    
    def validate_username(self, username: str) -> Tuple[bool, str]:
        """Validate username according to assignment requirements"""
        if not isinstance(username, str):
            return False, "Username must be a string"
        
        # Remove null bytes and trim
        username = self._sanitize_input(username)
        
        if len(username) < 8:
            return False, "Username must be at least 8 characters long"
        
        if len(username) > 10:
            return False, "Username must be no longer than 10 characters"
        
        if not self.username_chars.match(username):
            return False, "Username can only contain letters, numbers, underscores, apostrophes, and periods"
        
        if not (username[0].isalpha() or username[0] == '_'):
            return False, "Username must start with a letter or underscore"
        
        return True, "Valid username"
    
    def validate_password(self, password: str) -> Tuple[bool, str]:
        """Validate password according to assignment requirements"""
        if not isinstance(password, str):
            return False, "Password must be a string"
        
        # Don't sanitize password as it might contain special characters
        if '\x00' in password:
            return False, "Password contains invalid characters"
        
        if len(password) < 12:
            return False, "Password must be at least 12 characters long"
        
        if len(password) > 30:
            return False, "Password must be no longer than 30 characters"
        
        if not self.password_pattern.match(password):
            return False, "Password contains invalid characters"
        
        # Check for required character types
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "~!@#$%&_-+=`|\\(){}[]:;'<>,.?/" for c in password)
        
        if not has_lower:
            return False, "Password must contain at least one lowercase letter"
        
        if not has_upper:
            return False, "Password must contain at least one uppercase letter"
        
        if not has_digit:
            return False, "Password must contain at least one digit"
        
        if not has_special:
            return False, "Password must contain at least one special character"
        
        return True, "Valid password"
    
    def validate_name(self, name: str, field_name: str = "Name") -> Tuple[bool, str]:
        """Validate first name or last name"""
        if not isinstance(name, str):
            return False, f"{field_name} must be a string"
        
        name = self._sanitize_input(name)
        
        if not name:
            return False, f"{field_name} cannot be empty"
        
        if len(name) > 50:
            return False, f"{field_name} must be no longer than 50 characters"
        
        if not self.name_chars.match(name):
            return False, f"{field_name} can only contain letters, spaces, hyphens, apostrophes, and periods"
        
        return True, f"Valid {field_name.lower()}"
    
    def validate_email(self, email: str) -> Tuple[bool, str]:
        """Validate email address"""
        if not isinstance(email, str):
            return False, "Email must be a string"
        
        email = self._sanitize_input(email)
        
        if not email:
            return False, "Email cannot be empty"
        
        if len(email) > 100:
            return False, "Email must be no longer than 100 characters"
        
        if not self.email_pattern.match(email):
            return False, "Invalid email format"
        
        return True, "Valid email"
    
    def validate_phone_number(self, phone: str) -> Tuple[bool, str]:
        """Validate Dutch mobile phone number (format: DDDDDDDD)"""
        if not isinstance(phone, str):
            return False, "Phone number must be a string"
        
        phone = self._sanitize_input(phone)
        
        if not phone:
            return False, "Phone number cannot be empty"
        
        if len(phone) != 8:
            return False, "Phone number must be exactly 8 digits"
        
        if not self.numeric_chars.match(phone):
            return False, "Phone number can only contain digits"
        
        return True, "Valid phone number"
    
    def validate_zip_code(self, zip_code: str) -> Tuple[bool, str]:
        """Validate Dutch zip code (format: DDDDXX)"""
        if not isinstance(zip_code, str):
            return False, "Zip code must be a string"
        
        zip_code = self._sanitize_input(zip_code).upper()
        
        if not zip_code:
            return False, "Zip code cannot be empty"
        
        if len(zip_code) != 6:
            return False, "Zip code must be exactly 6 characters (DDDDXX format)"
        
        if not zip_code[:4].isdigit():
            return False, "First 4 characters of zip code must be digits"
        
        if not zip_code[4:].isalpha():
            return False, "Last 2 characters of zip code must be letters"
        
        return True, "Valid zip code"
    
    def validate_driving_license(self, license_num: str) -> Tuple[bool, str]:
        """Validate Dutch driving license number (format: XXDDDDDDD or XDDDDDDDD)"""
        if not isinstance(license_num, str):
            return False, "Driving license number must be a string"
        
        license_num = self._sanitize_input(license_num).upper()
        
        if not license_num:
            return False, "Driving license number cannot be empty"
        
        if len(license_num) not in [9, 10]:
            return False, "Driving license number must be 9 or 10 characters"
        
        # Format 1: XXDDDDDDD (2 letters + 7 digits)
        if len(license_num) == 9:
            if not (license_num[:2].isalpha() and license_num[2:].isdigit()):
                return False, "Invalid format. Expected: 2 letters followed by 7 digits"
        
        # Format 2: XDDDDDDDD (1 letter + 8 digits)
        elif len(license_num) == 10:
            if not (license_num[0].isalpha() and license_num[1:].isdigit()):
                return False, "Invalid format. Expected: 1 letter followed by 8 digits"
        
        return True, "Valid driving license number"
    
    def validate_city(self, city: str) -> Tuple[bool, str]:
        """Validate city name against predefined list"""
        if not isinstance(city, str):
            return False, "City must be a string"
        
        city = self._sanitize_input(city)
        
        if not city:
            return False, "City cannot be empty"
        
        if city not in self.valid_cities:
            return False, f"City must be one of: {', '.join(self.valid_cities)}"
        
        return True, "Valid city"
    
    def validate_date(self, date_str: str, field_name: str = "Date") -> Tuple[bool, str]:
        """Validate date in ISO format (YYYY-MM-DD)"""
        if not isinstance(date_str, str):
            return False, f"{field_name} must be a string"
        
        date_str = self._sanitize_input(date_str)
        
        if not date_str:
            return False, f"{field_name} cannot be empty"
        
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True, f"Valid {field_name.lower()}"
        except ValueError:
            return False, f"{field_name} must be in YYYY-MM-DD format"
    
    def validate_gender(self, gender: str) -> Tuple[bool, str]:
        """Validate gender (male or female)"""
        if not isinstance(gender, str):
            return False, "Gender must be a string"
        
        gender = self._sanitize_input(gender).lower()
        
        if gender not in ['male', 'female']:
            return False, "Gender must be 'male' or 'female'"
        
        return True, "Valid gender"
    
    def validate_house_number(self, house_num: str) -> Tuple[bool, str]:
        """Validate house number"""
        if not isinstance(house_num, str):
            return False, "House number must be a string"
        
        house_num = self._sanitize_input(house_num)
        
        if not house_num:
            return False, "House number cannot be empty"
        
        if len(house_num) > 10:
            return False, "House number must be no longer than 10 characters"
        
        # Allow numbers with optional letters (e.g., "123A", "45bis")
        if not re.match(r'^[0-9]+[a-zA-Z]*$', house_num):
            return False, "House number must start with digits and may end with letters"
        
        return True, "Valid house number"
    
    def validate_serial_number(self, serial: str) -> Tuple[bool, str]:
        """Validate scooter serial number (10-17 alphanumeric characters)"""
        if not isinstance(serial, str):
            return False, "Serial number must be a string"
        
        serial = self._sanitize_input(serial)
        
        if not serial:
            return False, "Serial number cannot be empty"
        
        if len(serial) < 10 or len(serial) > 17:
            return False, "Serial number must be between 10 and 17 characters"
        
        if not self.alphanumeric_chars.match(serial):
            return False, "Serial number can only contain letters and numbers"
        
        return True, "Valid serial number"
    
    def validate_coordinates(self, latitude: str, longitude: str) -> Tuple[bool, str]:
        """Validate GPS coordinates for Rotterdam region"""
        try:
            lat = float(latitude)
            lon = float(longitude)
            
            # Rotterdam region boundaries (approximate)
            if not (51.8 <= lat <= 52.0):
                return False, "Latitude must be within Rotterdam region (51.8 - 52.0)"
            
            if not (4.3 <= lon <= 4.6):
                return False, "Longitude must be within Rotterdam region (4.3 - 4.6)"
            
            # Check for 5 decimal places precision
            if len(str(lat).split('.')[-1]) > 5 or len(str(lon).split('.')[-1]) > 5:
                return False, "Coordinates must have maximum 5 decimal places"
            
            return True, "Valid coordinates"
        
        except ValueError:
            return False, "Coordinates must be valid numbers"
    
    def validate_percentage(self, value: str, field_name: str = "Value") -> Tuple[bool, str]:
        """Validate percentage value (0-100)"""
        if not isinstance(value, str):
            return False, f"{field_name} must be a string"
        
        value = self._sanitize_input(value)
        
        try:
            num_value = float(value)
            if not (0 <= num_value <= 100):
                return False, f"{field_name} must be between 0 and 100"
            return True, f"Valid {field_name.lower()}"
        except ValueError:
            return False, f"{field_name} must be a valid number"
    
    def validate_positive_number(self, value: str, field_name: str = "Value") -> Tuple[bool, str]:
        """Validate positive number"""
        if not isinstance(value, str):
            return False, f"{field_name} must be a string"
        
        value = self._sanitize_input(value)
        
        try:
            num_value = float(value)
            if num_value < 0:
                return False, f"{field_name} must be positive"
            return True, f"Valid {field_name.lower()}"
        except ValueError:
            return False, f"{field_name} must be a valid number"
    
    def _sanitize_input(self, input_str: str) -> str:
        """Sanitize input string by removing null bytes and trimming"""
        if not isinstance(input_str, str):
            return ""
        
        # Remove null bytes
        sanitized = input_str.replace('\x00', '')
        
        # Trim whitespace
        sanitized = sanitized.strip()
        
        return sanitized
    
    def validate_search_term(self, search_term: str) -> Tuple[bool, str]:
        """Validate search term for partial matching"""
        if not isinstance(search_term, str):
            return False, "Search term must be a string"
        
        search_term = self._sanitize_input(search_term)
        
        if not search_term:
            return False, "Search term cannot be empty"
        
        if len(search_term) < 2:
            return False, "Search term must be at least 2 characters"
        
        if len(search_term) > 50:
            return False, "Search term must be no longer than 50 characters"
        
        # Allow alphanumeric characters, spaces, and common punctuation
        if not re.match(r'^[a-zA-Z0-9 \-\'\.@_]+$', search_term):
            return False, "Search term contains invalid characters"
        
        return True, "Valid search term"
