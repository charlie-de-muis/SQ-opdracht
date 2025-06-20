#!/usr/bin/env python3

import os
import shutil
import zipfile
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

class BackupManager:   
    def __init__(self, database_manager, logger):
        self.db_manager = database_manager
        self.logger = logger
        # check is backup dir exists
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.backup_dir = os.path.join(script_dir, 'backups')
        self.restore_codes = {}  
        
        # Create backup dir if it doesn't exist
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_backup(self, created_by: str) -> Optional[str]:
        try:
            # Generate backup filename with time
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"urban_mobility_backup_{timestamp}.zip"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Create backup zip file
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if os.path.exists(self.db_manager.db_file):
                    zipf.write(self.db_manager.db_file, 'urban_mobility.db')

                if os.path.exists('system.key'):
                    zipf.write('system.key', 'system.key')
                
                if os.path.exists('system_logs.dat'):
                    zipf.write('system_logs.dat', 'system_logs.dat')
                
                backup_metadata = {
                    'created_by': created_by,
                    'created_at': datetime.now().isoformat(),
                    'backup_version': '1.0',
                    'system_version': 'Urban Mobility Backend v1.0'
                }
                
                zipf.writestr('backup_metadata.json', json.dumps(backup_metadata, indent=2))
            
            self.logger.log_activity(
                created_by,
                "Backup created",
                f"System backup created: {backup_filename}"
            )
            
            return backup_filename
            
        except Exception as e:
            self.logger.log_activity(
                created_by,
                "Backup creation failed",
                f"Failed to create backup: {str(e)}",
                suspicious=True
            )
            return None
    
    def restore_backup(self, backup_filename: str, restored_by: str) -> bool:
        try:
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            if not os.path.exists(backup_path):
                self.logger.log_activity(
                    restored_by,
                    "Restore failed",
                    f"Backup file not found: {backup_filename}",
                    suspicious=True
                )
                return False
            
            current_backup = self.create_backup(f"AUTO_BACKUP_BEFORE_RESTORE_{restored_by}")
            
            # get backup
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                if not self._verify_backup_integrity(zipf):
                    self.logger.log_activity(
                        restored_by,
                        "Restore failed",
                        f"Backup integrity check failed: {backup_filename}",
                        suspicious=True
                    )
                    return False
                
                self.db_manager.close_connection()
                if 'urban_mobility.db' in zipf.namelist():
                    zipf.extract('urban_mobility.db', '.')
                if 'system.key' in zipf.namelist():
                    zipf.extract('system.key', '.')
                if 'system_logs.dat' in zipf.namelist():
                    zipf.extract('system_logs.dat', '.')
            
            # Restart database connection
            self.db_manager._get_connection()
            
            self.logger.log_activity(
                restored_by,
                "System restored",
                f"System restored from backup: {backup_filename}"
            )
            
            return True
            
        except Exception as e:
            self.logger.log_activity(
                restored_by,
                "Restore failed",
                f"Failed to restore backup {backup_filename}: {str(e)}",
                suspicious=True
            )
            return False
    
    def restore_with_code(self, restore_code: str, restored_by: str) -> bool:
        try:
            conn = self.db_manager._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT backup_filename, system_admin_username, is_used, created_at
                FROM restore_codes
                WHERE code = ? AND is_used = 0
            ''', (restore_code,))
            
            code_info = cursor.fetchone()
            
            if not code_info:
                self.logger.log_activity(
                    restored_by,
                    "Restore code invalid",
                    f"Invalid or used restore code attempted: {restore_code}",
                    suspicious=True
                )
                return False
            
            if code_info['system_admin_username'] != restored_by:
                self.logger.log_activity(
                    restored_by,
                    "Restore code unauthorized",
                    f"Unauthorized use of restore code by {restored_by}",
                    suspicious=True
                )
                return False
            
            cursor.execute('''
                UPDATE restore_codes
                SET is_used = 1, used_at = ?
                WHERE code = ?
            ''', (datetime.now().isoformat(), restore_code))
            
            conn.commit()

            backup_filename = code_info['backup_filename']
            success = self.restore_backup(backup_filename, restored_by)
            
            if success:
                self.logger.log_activity(
                    restored_by,
                    "Restore with code successful",
                    f"System restored using restore code. Backup: {backup_filename}"
                )
            else:
                cursor.execute('''
                    UPDATE restore_codes
                    SET is_used = 0, used_at = NULL
                    WHERE code = ?
                ''', (restore_code,))
                conn.commit()
            
            return success
            
        except Exception as e:
            self.logger.log_activity(
                restored_by,
                "Restore with code failed",
                f"Failed to restore with code: {str(e)}",
                suspicious=True
            )
            return False
    
    def generate_restore_code(self, backup_filename: str, admin_username: str, created_by: str) -> Optional[str]:
        try:
            backup_path = os.path.join(self.backup_dir, backup_filename)
            if not os.path.exists(backup_path):
                return None
            
            import secrets
            restore_code = secrets.token_urlsafe(16)

            conn = self.db_manager._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO restore_codes (code, backup_filename, system_admin_username, created_by)
                VALUES (?, ?, ?, ?)
            ''', (restore_code, backup_filename, admin_username, created_by))
            
            conn.commit()
            
            self.logger.log_activity(
                created_by,
                "Restore code generated",
                f"Generated restore code for {admin_username}, backup: {backup_filename}"
            )
            
            return restore_code
            
        except Exception as e:
            self.logger.log_activity(
                created_by,
                "Restore code generation failed",
                f"Failed to generate restore code: {str(e)}",
                suspicious=True
            )
            return None
    
    def revoke_restore_code(self, restore_code: str, revoked_by: str) -> bool:
        try:
            conn = self.db_manager._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT system_admin_username, backup_filename, is_used
                FROM restore_codes
                WHERE code = ?
            ''', (restore_code,))
            
            code_info = cursor.fetchone()
            
            if not code_info:
                return False
            
            if code_info['is_used']:
                return False  
            
            cursor.execute('''
                UPDATE restore_codes
                SET is_used = 1, used_at = ?
                WHERE code = ?
            ''', (datetime.now().isoformat(), restore_code))
            
            conn.commit()
            
            self.logger.log_activity(
                revoked_by,
                "Restore code revoked",
                f"Revoked restore code for {code_info['system_admin_username']}"
            )
            
            return True
            
        except Exception as e:
            self.logger.log_activity(
                revoked_by,
                "Restore code revocation failed",
                f"Failed to revoke restore code: {str(e)}",
                suspicious=True
            )
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        backups = []
        
        try:
            if not os.path.exists(self.backup_dir):
                return backups
            
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.zip'):
                    backup_path = os.path.join(self.backup_dir, filename)
                    
                    try:
                        # Get file stats
                        stats = os.stat(backup_path)
                        file_size = stats.st_size
                        created_time = datetime.fromtimestamp(stats.st_mtime)
                        
                        metadata = self._read_backup_metadata(backup_path)
                        
                        backups.append({
                            'filename': filename,
                            'size': file_size,
                            'created_at': created_time.isoformat(),
                            'created_by': metadata.get('created_by', 'Unknown'),
                            'metadata': metadata
                        })
                        
                    except Exception:
                        backups.append({
                            'filename': filename,
                            'size': file_size,
                            'created_at': created_time.isoformat(),
                            'created_by': 'Unknown',
                            'metadata': {}
                        })
            
            # Sort by time
            backups.sort(key=lambda x: x['created_at'], reverse=True)
            
        except Exception as e:
            self.logger.log_activity(
                "SYSTEM",
                "List backups failed",
                f"Failed to list backups: {str(e)}",
                suspicious=True
            )
        
        return backups
    
    def _verify_backup_integrity(self, zipf: zipfile.ZipFile) -> bool:
        """Verify backup file integrity"""
        try:
            # Check if files are present
            required_files = ['urban_mobility.db', 'backup_metadata.json']
            namelist = zipf.namelist()
            
            for required_file in required_files:
                if required_file not in namelist:
                    return False
            
            metadata_content = zipf.read('backup_metadata.json')
            metadata = json.loads(metadata_content)

            required_metadata = ['created_by', 'created_at', 'backup_version']
            for field in required_metadata:
                if field not in metadata:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _read_backup_metadata(self, backup_path: str) -> Dict[str, Any]:
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                if 'backup_metadata.json' in zipf.namelist():
                    metadata_content = zipf.read('backup_metadata.json')
                    return json.loads(metadata_content)
        except Exception:
            pass
        
        return {}
    
    def get_restore_codes(self, admin_username: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            conn = self.db_manager._get_connection()
            cursor = conn.cursor()
            
            if admin_username:
                cursor.execute('''
                    SELECT code, backup_filename, system_admin_username, is_used, created_by, created_at, used_at
                    FROM restore_codes
                    WHERE system_admin_username = ?
                    ORDER BY created_at DESC
                ''', (admin_username,))
            else:
                cursor.execute('''
                    SELECT code, backup_filename, system_admin_username, is_used, created_by, created_at, used_at
                    FROM restore_codes
                    ORDER BY created_at DESC
                ''')
            
            codes = []
            for row in cursor.fetchall():
                codes.append({
                    'code': row['code'],
                    'backup_filename': row['backup_filename'],
                    'system_admin_username': row['system_admin_username'],
                    'is_used': bool(row['is_used']),
                    'created_by': row['created_by'],
                    'created_at': row['created_at'],
                    'used_at': row['used_at']
                })
            
            return codes
            
        except Exception as e:
            self.logger.log_activity(
                "SYSTEM",
                "Get restore codes failed",
                f"Failed to get restore codes: {str(e)}",
                suspicious=True
            )
            return []
