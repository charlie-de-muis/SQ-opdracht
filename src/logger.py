#!/usr/bin/env python3

import os
import json
import threading
from datetime import datetime
from typing import Optional, List, Dict, Any

class SystemLogger:   
    def __init__(self, crypto_manager):
        self.crypto = crypto_manager

        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.log_file = os.path.join(script_dir, 'system_logs.dat')
        self.lock = threading.Lock()
        self.log_counter = 0
        self._initialize_log_file()
    
    def _initialize_log_file(self):
        if not os.path.exists(self.log_file):
            empty_logs = []
            self._write_logs(empty_logs)
        
        # Get current log counter
        logs = self._read_logs()
        if logs:
            self.log_counter = max(log.get('id', 0) for log in logs)
    
    def _read_logs(self) -> List[Dict[str, Any]]:
        try:
            if not os.path.exists(self.log_file):
                return []
            
            with open(self.log_file, 'r') as f:
                encrypted_content = f.read()
            
            if not encrypted_content:
                return []
            
            # Decrypt the log content
            decrypted_content = self.crypto.decrypt(encrypted_content)
            
            logs = json.loads(decrypted_content)
            return logs if isinstance(logs, list) else []
        
        except Exception as e:
            print(f"Warning: Could not read log file: {e}")
            return []
    
    def _write_logs(self, logs: List[Dict[str, Any]]):
        try:
            # Convert logs to JSON
            json_content = json.dumps(logs, indent=2, default=str)
            
            # Encrypt the content
            encrypted_content = self.crypto.encrypt(json_content)
            
            # Write to file
            with open(self.log_file, 'w') as f:
                f.write(encrypted_content)
        
        except Exception as e:
            print(f"Warning: Could not write to log file: {e}")
    
    def log_activity(self, username: str, activity: str, details: str = "", suspicious: bool = False):
        with self.lock:
            try:
                logs = self._read_logs()
                
                # Create new log entry
                self.log_counter += 1
                log_entry = {
                    'id': self.log_counter,
                    'timestamp': datetime.now().isoformat(),
                    'date': datetime.now().strftime('%d-%m-%Y'),
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'username': username,
                    'activity': activity,
                    'details': details,
                    'suspicious': suspicious,
                    'read': False  
                }
                
                logs.append(log_entry)
                if len(logs) > 1000:
                    logs = logs[-1000:]
                
                self._write_logs(logs)
                
            except Exception as e:
                print(f"Warning: Could not log activity: {e}")
    
    def get_logs(self, limit: Optional[int] = None, suspicious_only: bool = False) -> List[Dict[str, Any]]:
        logs = self._read_logs()
        
        if suspicious_only:
            logs = [log for log in logs if log.get('suspicious', False)]

        # sort by time
        logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        if limit:
            logs = logs[:limit]
        
        return logs
    
    def get_unread_suspicious_count(self) -> int:
        logs = self._read_logs()
        count = sum(1 for log in logs if log.get('suspicious', False) and not log.get('read', True))
        return count
    
    def mark_suspicious_as_read(self):
        with self.lock:
            try:
                logs = self._read_logs()
            
                for log in logs:
                    if log.get('suspicious', False):
                        log['read'] = True
            
                self._write_logs(logs)
                
            except Exception as e:
                print(f"Warning: Could not mark logs as read: {e}")
    
    def search_logs(self, search_term: str) -> List[Dict[str, Any]]:
        logs = self._read_logs()
        search_term = search_term.lower()
        
        matching_logs = []
        for log in logs:
            # Search in username, activity, and details
            if (search_term in log.get('username', '').lower() or
                search_term in log.get('activity', '').lower() or
                search_term in log.get('details', '').lower()):
                matching_logs.append(log)
        
        # Sort by time
        matching_logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return matching_logs
    
    def get_logs_by_user(self, username: str) -> List[Dict[str, Any]]:
        logs = self._read_logs()
        user_logs = [log for log in logs if log.get('username', '').lower() == username.lower()]
        
        # Sort by time
        user_logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return user_logs
    
    def get_logs_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        logs = self._read_logs()
        
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            filtered_logs = []
            for log in logs:
                try:
                    log_dt = datetime.fromisoformat(log.get('timestamp', ''))
                    if start_dt <= log_dt <= end_dt:
                        filtered_logs.append(log)
                except:
                    continue
        
            filtered_logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return filtered_logs
        
        except ValueError:
            return []
    
    def clear_old_logs(self, days_to_keep: int = 90):
        with self.lock:
            try:
                logs = self._read_logs()
                cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
                
                filtered_logs = []
                for log in logs:
                    try:
                        log_dt = datetime.fromisoformat(log.get('timestamp', ''))
                        if log_dt.timestamp() >= cutoff_date:
                            filtered_logs.append(log)
                    except:
                        filtered_logs.append(log)
                
                self._write_logs(filtered_logs)
                
                return len(logs) - len(filtered_logs)  # Return number of logs deleted
            
            except Exception as e:
                print(f"Warning: Could not clear old logs: {e}")
                return 0
    
    def export_logs(self, filename: str, suspicious_only: bool = False) -> bool:
        try:
            logs = self.get_logs(suspicious_only=suspicious_only)
            
            with open(filename, 'w') as f:
                f.write("Urban Mobility System - Security Log Export\n")
                f.write("=" * 60 + "\n")
                f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Entries: {len(logs)}\n")
                if suspicious_only:
                    f.write("Filter: Suspicious Activities Only\n")
                f.write("=" * 60 + "\n\n")
                
                for log in logs:
                    f.write(f"ID: {log.get('id', 'N/A')}\n")
                    f.write(f"Date: {log.get('date', 'N/A')}\n")
                    f.write(f"Time: {log.get('time', 'N/A')}\n")
                    f.write(f"User: {log.get('username', 'N/A')}\n")
                    f.write(f"Activity: {log.get('activity', 'N/A')}\n")
                    f.write(f"Details: {log.get('details', 'N/A')}\n")
                    f.write(f"Suspicious: {'Yes' if log.get('suspicious', False) else 'No'}\n")
                    f.write("-" * 40 + "\n")
            
            return True
        
        except Exception as e:
            print(f"Error exporting logs: {e}")
            return False
