"""
Police Violations System - Database Module
Handles SQLite database operations for violations, seizures, infractions, users, and statistics.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import os


class Database:
    """SQLite Database handler for Police Violations System"""
    
    def __init__(self, db_path: str = "police_violations.db"):
        """Initialize database connection and create tables if needed"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.init_connection()
        self.create_tables()
    
    def init_connection(self):
        """Initialize database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            raise
    
    def create_tables(self):
        """Create all required tables for the system"""
        try:
            # Users table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    badge_number TEXT UNIQUE,
                    role TEXT NOT NULL CHECK(role IN ('admin', 'officer', 'supervisor', 'analyst')),
                    department TEXT,
                    phone_number TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Violations table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS violations (
                    violation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    violation_number TEXT UNIQUE NOT NULL,
                    violator_name TEXT NOT NULL,
                    violator_license_number TEXT,
                    violator_phone TEXT,
                    violator_address TEXT,
                    violation_date TIMESTAMP NOT NULL,
                    violation_type TEXT NOT NULL CHECK(
                        violation_type IN ('traffic', 'parking', 'criminal', 'administrative', 'other')
                    ),
                    severity_level TEXT NOT NULL CHECK(
                        severity_level IN ('minor', 'moderate', 'serious', 'critical')
                    ),
                    description TEXT,
                    location TEXT NOT NULL,
                    latitude REAL,
                    longitude REAL,
                    officer_id INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'open' CHECK(
                        status IN ('open', 'closed', 'appealed', 'dismissed', 'resolved')
                    ),
                    fine_amount REAL,
                    paid_date TIMESTAMP,
                    notes TEXT,
                    evidence_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (officer_id) REFERENCES users(user_id)
                )
            ''')
            
            # Seizures table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS seizures (
                    seizure_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    seizure_number TEXT UNIQUE NOT NULL,
                    violation_id INTEGER NOT NULL,
                    item_description TEXT NOT NULL,
                    item_quantity INTEGER NOT NULL DEFAULT 1,
                    item_category TEXT NOT NULL CHECK(
                        item_category IN ('vehicle', 'documents', 'contraband', 'weapon', 'currency', 'other')
                    ),
                    estimated_value REAL,
                    serial_number TEXT,
                    storage_location TEXT,
                    officer_id INTEGER NOT NULL,
                    seizure_date TIMESTAMP NOT NULL,
                    release_date TIMESTAMP,
                    release_authorized_by INTEGER,
                    release_reason TEXT,
                    status TEXT NOT NULL DEFAULT 'stored' CHECK(
                        status IN ('stored', 'released', 'destroyed', 'auctioned', 'pending')
                    ),
                    condition_notes TEXT,
                    photo_evidence_urls TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (violation_id) REFERENCES violations(violation_id),
                    FOREIGN KEY (officer_id) REFERENCES users(user_id),
                    FOREIGN KEY (release_authorized_by) REFERENCES users(user_id)
                )
            ''')
            
            # Infractions table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS infractions (
                    infraction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    infraction_number TEXT UNIQUE NOT NULL,
                    violation_id INTEGER NOT NULL,
                    infraction_type TEXT NOT NULL,
                    points INTEGER DEFAULT 0,
                    description TEXT,
                    statute_reference TEXT,
                    minimum_fine REAL,
                    maximum_fine REAL,
                    status TEXT NOT NULL DEFAULT 'pending' CHECK(
                        status IN ('pending', 'contested', 'resolved', 'dismissed', 'appealed')
                    ),
                    court_appearance_date TIMESTAMP,
                    court_location TEXT,
                    case_number TEXT,
                    prosecutor_id INTEGER,
                    judge_id INTEGER,
                    outcome TEXT,
                    sentence_details TEXT,
                    probation_period_months INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (violation_id) REFERENCES violations(violation_id),
                    FOREIGN KEY (prosecutor_id) REFERENCES users(user_id),
                    FOREIGN KEY (judge_id) REFERENCES users(user_id)
                )
            ''')
            
            # Evidence table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS evidence (
                    evidence_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    evidence_number TEXT UNIQUE NOT NULL,
                    violation_id INTEGER NOT NULL,
                    evidence_type TEXT NOT NULL CHECK(
                        evidence_type IN ('photo', 'video', 'audio', 'document', 'physical', 'digital', 'witness_statement')
                    ),
                    description TEXT NOT NULL,
                    file_path TEXT,
                    file_size INTEGER,
                    mime_type TEXT,
                    collected_by INTEGER NOT NULL,
                    collection_date TIMESTAMP NOT NULL,
                    collection_location TEXT,
                    chain_of_custody TEXT,
                    storage_location TEXT,
                    status TEXT NOT NULL DEFAULT 'stored' CHECK(
                        status IN ('stored', 'destroyed', 'released', 'lost', 'pending')
                    ),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (violation_id) REFERENCES violations(violation_id),
                    FOREIGN KEY (collected_by) REFERENCES users(user_id)
                )
            ''')
            
            # Activity Log table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS activity_log (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    action_type TEXT NOT NULL,
                    entity_type TEXT,
                    entity_id INTEGER,
                    description TEXT,
                    changes TEXT,
                    ip_address TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # Statistics/Metrics table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS statistics (
                    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL UNIQUE,
                    total_violations INTEGER DEFAULT 0,
                    total_seizures INTEGER DEFAULT 0,
                    total_infractions INTEGER DEFAULT 0,
                    total_fines REAL DEFAULT 0,
                    violations_by_type TEXT,
                    violations_by_severity TEXT,
                    top_violators TEXT,
                    officer_performance TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.conn.commit()
            print("Database tables created successfully")
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    # ==================== USER MANAGEMENT ====================
    
    def create_user(self, username: str, email: str, password_hash: str, 
                   full_name: str, role: str, badge_number: str = None,
                   department: str = None, phone_number: str = None) -> int:
        """Create a new user"""
        try:
            self.cursor.execute('''
                INSERT INTO users (username, email, password_hash, full_name, 
                                 badge_number, role, department, phone_number)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, email, password_hash, full_name, badge_number, 
                  role, department, phone_number))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            print(f"User creation error: {e}")
            raise
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        self.cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        self.cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user information"""
        allowed_fields = ['email', 'full_name', 'badge_number', 'role', 
                         'department', 'phone_number', 'is_active']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        updates['updated_at'] = datetime.utcnow()
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [user_id]
        
        try:
            self.cursor.execute(f'UPDATE users SET {set_clause} WHERE user_id = ?', values)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"User update error: {e}")
            return False
    
    def list_users(self, role: str = None, is_active: bool = None) -> List[Dict]:
        """List users with optional filters"""
        query = 'SELECT * FROM users'
        params = []
        
        filters = []
        if role:
            filters.append('role = ?')
            params.append(role)
        if is_active is not None:
            filters.append('is_active = ?')
            params.append(is_active)
        
        if filters:
            query += ' WHERE ' + ' AND '.join(filters)
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    # ==================== VIOLATIONS MANAGEMENT ====================
    
    def create_violation(self, violation_number: str, violator_name: str, 
                        violation_date: datetime, violation_type: str, 
                        severity_level: str, location: str, officer_id: int,
                        violator_license_number: str = None, violator_phone: str = None,
                        violator_address: str = None, description: str = None,
                        latitude: float = None, longitude: float = None,
                        fine_amount: float = None) -> int:
        """Create a new violation record"""
        try:
            self.cursor.execute('''
                INSERT INTO violations (violation_number, violator_name, violation_date,
                                      violation_type, severity_level, location, officer_id,
                                      violator_license_number, violator_phone, violator_address,
                                      description, latitude, longitude, fine_amount)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (violation_number, violator_name, violation_date, violation_type,
                  severity_level, location, officer_id, violator_license_number,
                  violator_phone, violator_address, description, latitude, longitude,
                  fine_amount))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            print(f"Violation creation error: {e}")
            raise
    
    def get_violation(self, violation_id: int) -> Optional[Dict]:
        """Get violation by ID"""
        self.cursor.execute('SELECT * FROM violations WHERE violation_id = ?', (violation_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def update_violation(self, violation_id: int, **kwargs) -> bool:
        """Update violation information"""
        allowed_fields = ['violator_name', 'violator_license_number', 'violator_phone',
                         'violator_address', 'violation_type', 'severity_level', 
                         'description', 'location', 'latitude', 'longitude', 'status',
                         'fine_amount', 'paid_date', 'notes']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        updates['updated_at'] = datetime.utcnow()
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [violation_id]
        
        try:
            self.cursor.execute(f'UPDATE violations SET {set_clause} WHERE violation_id = ?', values)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Violation update error: {e}")
            return False
    
    def list_violations(self, officer_id: int = None, status: str = None, 
                       violation_type: str = None, severity_level: str = None,
                       start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """List violations with optional filters"""
        query = 'SELECT * FROM violations WHERE 1=1'
        params = []
        
        if officer_id:
            query += ' AND officer_id = ?'
            params.append(officer_id)
        if status:
            query += ' AND status = ?'
            params.append(status)
        if violation_type:
            query += ' AND violation_type = ?'
            params.append(violation_type)
        if severity_level:
            query += ' AND severity_level = ?'
            params.append(severity_level)
        if start_date:
            query += ' AND violation_date >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND violation_date <= ?'
            params.append(end_date)
        
        query += ' ORDER BY violation_date DESC'
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    # ==================== SEIZURES MANAGEMENT ====================
    
    def create_seizure(self, seizure_number: str, violation_id: int, 
                      item_description: str, item_quantity: int, item_category: str,
                      officer_id: int, seizure_date: datetime,
                      estimated_value: float = None, serial_number: str = None,
                      storage_location: str = None, condition_notes: str = None) -> int:
        """Create a new seizure record"""
        try:
            self.cursor.execute('''
                INSERT INTO seizures (seizure_number, violation_id, item_description,
                                    item_quantity, item_category, estimated_value,
                                    serial_number, storage_location, officer_id,
                                    seizure_date, condition_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (seizure_number, violation_id, item_description, item_quantity,
                  item_category, estimated_value, serial_number, storage_location,
                  officer_id, seizure_date, condition_notes))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            print(f"Seizure creation error: {e}")
            raise
    
    def get_seizure(self, seizure_id: int) -> Optional[Dict]:
        """Get seizure by ID"""
        self.cursor.execute('SELECT * FROM seizures WHERE seizure_id = ?', (seizure_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def update_seizure(self, seizure_id: int, **kwargs) -> bool:
        """Update seizure information"""
        allowed_fields = ['item_description', 'item_quantity', 'item_category',
                         'estimated_value', 'serial_number', 'storage_location',
                         'status', 'condition_notes', 'release_date', 'release_reason',
                         'release_authorized_by', 'photo_evidence_urls']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        updates['updated_at'] = datetime.utcnow()
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [seizure_id]
        
        try:
            self.cursor.execute(f'UPDATE seizures SET {set_clause} WHERE seizure_id = ?', values)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Seizure update error: {e}")
            return False
    
    def list_seizures(self, violation_id: int = None, status: str = None,
                     item_category: str = None, officer_id: int = None) -> List[Dict]:
        """List seizures with optional filters"""
        query = 'SELECT * FROM seizures WHERE 1=1'
        params = []
        
        if violation_id:
            query += ' AND violation_id = ?'
            params.append(violation_id)
        if status:
            query += ' AND status = ?'
            params.append(status)
        if item_category:
            query += ' AND item_category = ?'
            params.append(item_category)
        if officer_id:
            query += ' AND officer_id = ?'
            params.append(officer_id)
        
        query += ' ORDER BY seizure_date DESC'
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    # ==================== INFRACTIONS MANAGEMENT ====================
    
    def create_infraction(self, infraction_number: str, violation_id: int,
                         infraction_type: str, description: str = None,
                         statute_reference: str = None, points: int = 0,
                         minimum_fine: float = None, maximum_fine: float = None) -> int:
        """Create a new infraction record"""
        try:
            self.cursor.execute('''
                INSERT INTO infractions (infraction_number, violation_id, infraction_type,
                                       description, statute_reference, points, minimum_fine,
                                       maximum_fine)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (infraction_number, violation_id, infraction_type, description,
                  statute_reference, points, minimum_fine, maximum_fine))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            print(f"Infraction creation error: {e}")
            raise
    
    def get_infraction(self, infraction_id: int) -> Optional[Dict]:
        """Get infraction by ID"""
        self.cursor.execute('SELECT * FROM infractions WHERE infraction_id = ?', (infraction_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def update_infraction(self, infraction_id: int, **kwargs) -> bool:
        """Update infraction information"""
        allowed_fields = ['infraction_type', 'description', 'statute_reference', 'points',
                         'minimum_fine', 'maximum_fine', 'status', 'court_appearance_date',
                         'court_location', 'case_number', 'prosecutor_id', 'judge_id',
                         'outcome', 'sentence_details', 'probation_period_months']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        updates['updated_at'] = datetime.utcnow()
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [infraction_id]
        
        try:
            self.cursor.execute(f'UPDATE infractions SET {set_clause} WHERE infraction_id = ?', values)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Infraction update error: {e}")
            return False
    
    def list_infractions(self, violation_id: int = None, status: str = None,
                        infraction_type: str = None) -> List[Dict]:
        """List infractions with optional filters"""
        query = 'SELECT * FROM infractions WHERE 1=1'
        params = []
        
        if violation_id:
            query += ' AND violation_id = ?'
            params.append(violation_id)
        if status:
            query += ' AND status = ?'
            params.append(status)
        if infraction_type:
            query += ' AND infraction_type = ?'
            params.append(infraction_type)
        
        query += ' ORDER BY created_at DESC'
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    # ==================== EVIDENCE MANAGEMENT ====================
    
    def create_evidence(self, evidence_number: str, violation_id: int, 
                       evidence_type: str, description: str, collected_by: int,
                       collection_date: datetime, file_path: str = None,
                       file_size: int = None, mime_type: str = None,
                       collection_location: str = None, storage_location: str = None,
                       notes: str = None) -> int:
        """Create a new evidence record"""
        try:
            self.cursor.execute('''
                INSERT INTO evidence (evidence_number, violation_id, evidence_type,
                                    description, collected_by, collection_date, file_path,
                                    file_size, mime_type, collection_location, storage_location, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (evidence_number, violation_id, evidence_type, description, collected_by,
                  collection_date, file_path, file_size, mime_type, collection_location,
                  storage_location, notes))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            print(f"Evidence creation error: {e}")
            raise
    
    def get_evidence(self, evidence_id: int) -> Optional[Dict]:
        """Get evidence by ID"""
        self.cursor.execute('SELECT * FROM evidence WHERE evidence_id = ?', (evidence_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def list_evidence_by_violation(self, violation_id: int) -> List[Dict]:
        """List all evidence for a specific violation"""
        self.cursor.execute('''
            SELECT * FROM evidence WHERE violation_id = ?
            ORDER BY collection_date DESC
        ''', (violation_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_evidence(self, evidence_id: int, **kwargs) -> bool:
        """Update evidence information"""
        allowed_fields = ['description', 'storage_location', 'status', 'chain_of_custody', 'notes']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        updates['updated_at'] = datetime.utcnow()
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [evidence_id]
        
        try:
            self.cursor.execute(f'UPDATE evidence SET {set_clause} WHERE evidence_id = ?', values)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Evidence update error: {e}")
            return False
    
    # ==================== ACTIVITY LOGGING ====================
    
    def log_activity(self, user_id: int, action_type: str, description: str,
                    entity_type: str = None, entity_id: int = None,
                    changes: str = None, ip_address: str = None) -> int:
        """Log user activity"""
        try:
            self.cursor.execute('''
                INSERT INTO activity_log (user_id, action_type, description, entity_type,
                                        entity_id, changes, ip_address)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, action_type, description, entity_type, entity_id, changes, ip_address))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Activity log error: {e}")
            raise
    
    def get_activity_log(self, user_id: int = None, limit: int = 100) -> List[Dict]:
        """Get activity log entries"""
        query = 'SELECT * FROM activity_log'
        params = []
        
        if user_id:
            query += ' WHERE user_id = ?'
            params.append(user_id)
        
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    # ==================== STATISTICS & REPORTING ====================
    
    def get_violation_statistics(self, start_date: datetime = None, 
                                end_date: datetime = None) -> Dict:
        """Get violation statistics"""
        query = 'SELECT * FROM violations WHERE 1=1'
        params = []
        
        if start_date:
            query += ' AND violation_date >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND violation_date <= ?'
            params.append(end_date)
        
        self.cursor.execute(query, params)
        violations = [dict(row) for row in self.cursor.fetchall()]
        
        stats = {
            'total_violations': len(violations),
            'violations_by_type': {},
            'violations_by_severity': {},
            'violations_by_status': {},
            'total_fines': 0
        }
        
        for violation in violations:
            # Count by type
            v_type = violation['violation_type']
            stats['violations_by_type'][v_type] = stats['violations_by_type'].get(v_type, 0) + 1
            
            # Count by severity
            severity = violation['severity_level']
            stats['violations_by_severity'][severity] = stats['violations_by_severity'].get(severity, 0) + 1
            
            # Count by status
            status = violation['status']
            stats['violations_by_status'][status] = stats['violations_by_status'].get(status, 0) + 1
            
            # Total fines
            if violation['fine_amount']:
                stats['total_fines'] += violation['fine_amount']
        
        return stats
    
    def get_officer_performance(self, officer_id: int = None, 
                               start_date: datetime = None, 
                               end_date: datetime = None) -> Dict:
        """Get officer performance metrics"""
        query = 'SELECT officer_id, COUNT(*) as violations_count, SUM(fine_amount) as total_fines'
        query += ' FROM violations WHERE 1=1'
        params = []
        
        if officer_id:
            query += ' AND officer_id = ?'
            params.append(officer_id)
        if start_date:
            query += ' AND violation_date >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND violation_date <= ?'
            params.append(end_date)
        
        query += ' GROUP BY officer_id ORDER BY violations_count DESC'
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_seizure_statistics(self, start_date: datetime = None,
                              end_date: datetime = None) -> Dict:
        """Get seizure statistics"""
        query = 'SELECT * FROM seizures WHERE 1=1'
        params = []
        
        if start_date:
            query += ' AND seizure_date >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND seizure_date <= ?'
            params.append(end_date)
        
        self.cursor.execute(query, params)
        seizures = [dict(row) for row in self.cursor.fetchall()]
        
        stats = {
            'total_seizures': len(seizures),
            'seizures_by_category': {},
            'seizures_by_status': {},
            'total_estimated_value': 0
        }
        
        for seizure in seizures:
            # Count by category
            category = seizure['item_category']
            stats['seizures_by_category'][category] = stats['seizures_by_category'].get(category, 0) + 1
            
            # Count by status
            status = seizure['status']
            stats['seizures_by_status'][status] = stats['seizures_by_status'].get(status, 0) + 1
            
            # Total value
            if seizure['estimated_value']:
                stats['total_estimated_value'] += seizure['estimated_value']
        
        return stats
    
    def get_infraction_statistics(self, start_date: datetime = None,
                                 end_date: datetime = None) -> Dict:
        """Get infraction statistics"""
        query = 'SELECT * FROM infractions WHERE 1=1'
        params = []
        
        if start_date:
            query += ' AND created_at >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND created_at <= ?'
            params.append(end_date)
        
        self.cursor.execute(query, params)
        infractions = [dict(row) for row in self.cursor.fetchall()]
        
        stats = {
            'total_infractions': len(infractions),
            'infractions_by_type': {},
            'infractions_by_status': {},
            'total_points': 0
        }
        
        for infraction in infractions:
            # Count by type
            i_type = infraction['infraction_type']
            stats['infractions_by_type'][i_type] = stats['infractions_by_type'].get(i_type, 0) + 1
            
            # Count by status
            status = infraction['status']
            stats['infractions_by_status'][status] = stats['infractions_by_status'].get(status, 0) + 1
            
            # Total points
            stats['total_points'] += infraction['points']
        
        return stats
    
    def save_daily_statistics(self, date: datetime) -> bool:
        """Calculate and save daily statistics"""
        try:
            stats = self.get_violation_statistics(
                start_date=date.replace(hour=0, minute=0, second=0),
                end_date=date.replace(hour=23, minute=59, second=59)
            )
            seizure_stats = self.get_seizure_statistics(
                start_date=date.replace(hour=0, minute=0, second=0),
                end_date=date.replace(hour=23, minute=59, second=59)
            )
            
            violations_by_type = json.dumps(stats['violations_by_type'])
            violations_by_severity = json.dumps(stats['violations_by_severity'])
            officer_perf = json.dumps(self.get_officer_performance(
                start_date=date.replace(hour=0, minute=0, second=0),
                end_date=date.replace(hour=23, minute=59, second=59)
            ))
            
            self.cursor.execute('''
                INSERT OR REPLACE INTO statistics (date, total_violations, total_seizures,
                                                  total_fines, violations_by_type,
                                                  violations_by_severity, officer_performance)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (date.date(), stats['total_violations'], seizure_stats['total_seizures'],
                  stats['total_fines'], violations_by_type, violations_by_severity, officer_perf))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error saving statistics: {e}")
            return False
    
    def get_daily_statistics(self, date: datetime) -> Optional[Dict]:
        """Get statistics for a specific date"""
        self.cursor.execute('SELECT * FROM statistics WHERE date = ?', (date.date(),))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    # ==================== BULK OPERATIONS ====================
    
    def export_violations_report(self, output_file: str, start_date: datetime = None,
                                end_date: datetime = None) -> bool:
        """Export violations to CSV report"""
        try:
            violations = self.list_violations(start_date=start_date, end_date=end_date)
            
            if not violations:
                print("No violations to export")
                return False
            
            import csv
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=violations[0].keys())
                writer.writeheader()
                writer.writerows(violations)
            
            print(f"Exported {len(violations)} violations to {output_file}")
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False
    
    def get_violation_details(self, violation_id: int) -> Optional[Dict]:
        """Get comprehensive violation details including related records"""
        violation = self.get_violation(violation_id)
        if not violation:
            return None
        
        # Get related seizures
        seizures = self.list_seizures(violation_id=violation_id)
        
        # Get related infractions
        infractions = self.list_infractions(violation_id=violation_id)
        
        # Get related evidence
        evidence = self.list_evidence_by_violation(violation_id)
        
        # Get officer details
        officer = self.get_user(violation['officer_id'])
        
        return {
            'violation': dict(violation),
            'officer': officer,
            'seizures': seizures,
            'infractions': infractions,
            'evidence': evidence
        }


# ==================== DATABASE INITIALIZATION ====================

def initialize_database(db_path: str = "police_violations.db") -> Database:
    """Initialize and return database instance"""
    return Database(db_path)


if __name__ == "__main__":
    # Example usage
    db = initialize_database()
    print("Database initialized successfully")
    db.close()
