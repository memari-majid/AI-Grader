"""
Database manager for CS AI Grader
Handles SQLite database operations, user management, and secure data storage
"""

import sqlite3
import hashlib
import secrets
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path


class DatabaseManager:
    """Secure database manager for CS AI Grader"""
    
    def __init__(self, db_path: str = "database/cs_ai_grader.db"):
        self.db_path = db_path
        self.ensure_database()
    
    def ensure_database(self):
        """Create database and tables if they don't exist"""
        # Create database directory
        Path(self.db_path).parent.mkdir(exist_ok=True)
        
        # Read schema and create tables
        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path, 'r') as f:
            schema = f.read()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(schema)
            conn.commit()
            
            # Check if admin user exists, create if not
            conn.row_factory = sqlite3.Row
            admin_exists = conn.execute(
                "SELECT COUNT(*) as count FROM users WHERE username = 'admin'"
            ).fetchone()['count']
            
            if admin_exists == 0:
                self._create_default_admin(conn)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _create_default_admin(self, conn: sqlite3.Connection):
        """Create default admin user (admin/admin)"""
        # Generate salt and hash password
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', 'admin'.encode(), salt.encode(), 100000)
        password_hash_hex = password_hash.hex()
        
        courses_json = json.dumps(['CS 1400', 'CS 1410', 'CS 2420'])
        
        conn.execute("""
            INSERT INTO users (username, email, password_hash, salt, role, department, courses)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ('admin', 'admin@uvu.edu', password_hash_hex, salt, 'admin', 'Computer Science', courses_json))
        
        conn.commit()
        print("✅ Created default admin user (admin/admin)")
    
    # User Management
    def create_user(self, username: str, email: str, password: str, role: str, 
                   department: str = "Computer Science", courses: List[str] = None) -> str:
        """Create new user with secure password hashing"""
        
        # Generate salt and hash password
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        password_hash_hex = password_hash.hex()
        
        courses_json = json.dumps(courses or [])
        
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO users (username, email, password_hash, salt, role, department, courses)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (username, email, password_hash_hex, salt, role, department, courses_json))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            # Log user creation
            self.log_action(user_id, None, 'user_created', 'user', str(user_id))
            
            return str(user_id)
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return user data if valid"""
        
        with self.get_connection() as conn:
            user = conn.execute("""
                SELECT id, username, email, password_hash, salt, role, department, courses, is_active
                FROM users WHERE username = ? OR email = ?
            """, (username, username)).fetchone()
            
            if not user or not user['is_active']:
                return None
            
            # Verify password
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), 
                                              user['salt'].encode(), 100000)
            
            if password_hash.hex() == user['password_hash']:
                # Update last login
                conn.execute("""
                    UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
                """, (user['id'],))
                conn.commit()
                
                # Log successful login
                self.log_action(user['id'], None, 'login_success', 'user', str(user['id']))
                
                return dict(user)
            else:
                # Log failed login
                self.log_action(None, None, 'login_failed', 'user', username)
                return None
    
    def create_session(self, user_id: int, ip_address: str = None, 
                      user_agent: str = None, duration_hours: int = 8) -> str:
        """Create secure user session"""
        
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=duration_hours)
        
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO user_sessions (id, user_id, expires_at, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, user_id, expires_at, ip_address, user_agent))
            conn.commit()
        
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Validate session and return user data if valid"""
        
        with self.get_connection() as conn:
            result = conn.execute("""
                SELECT s.id as session_id, s.expires_at, s.is_active as session_active,
                       u.id, u.username, u.email, u.role, u.department, u.courses, u.is_active
                FROM user_sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.id = ? AND s.is_active = TRUE AND s.expires_at > CURRENT_TIMESTAMP
            """, (session_id,)).fetchone()
            
            if result and result['is_active']:
                return dict(result)
            else:
                return None
    
    def invalidate_session(self, session_id: str):
        """Invalidate user session"""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE user_sessions SET is_active = FALSE WHERE id = ?
            """, (session_id,))
            conn.commit()
    
    # Assignment Management
    def save_assignment(self, name: str, course_code: str, prompt: str, 
                       rubric: Dict[str, Any], created_by: int, 
                       learning_objectives: List[str] = None) -> str:
        """Save assignment with rubric"""
        
        assignment_id = str(secrets.token_urlsafe(16))
        rubric_json = json.dumps(rubric)
        objectives_json = json.dumps(learning_objectives or [])
        
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO assignments (id, name, course_code, prompt, rubric_json, 
                                       created_by, learning_objectives)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (assignment_id, name, course_code, prompt, rubric_json, 
                  created_by, objectives_json))
            conn.commit()
        
        self.log_action(created_by, None, 'assignment_created', 'assignment', assignment_id)
        return assignment_id
    
    def get_assignments_for_user(self, user_id: int, course_code: str = None) -> List[Dict[str, Any]]:
        """Get assignments accessible to user"""
        
        with self.get_connection() as conn:
            if course_code:
                assignments = conn.execute("""
                    SELECT * FROM assignments 
                    WHERE created_by = ? AND course_code = ? AND is_active = TRUE
                    ORDER BY created_at DESC
                """, (user_id, course_code)).fetchall()
            else:
                assignments = conn.execute("""
                    SELECT * FROM assignments 
                    WHERE created_by = ? AND is_active = TRUE
                    ORDER BY created_at DESC
                """, (user_id,)).fetchall()
        
        return [dict(row) for row in assignments]
    
    # Grading Data Management
    def save_grading_session(self, assignment_id: str, grader_id: int, 
                           student_code: str, ai_results: Dict[str, Any],
                           final_results: Dict[str, Any], 
                           student_identifier: str = None) -> str:
        """Save grading session with AI and final results"""
        
        session_id = str(secrets.token_urlsafe(16))
        
        # Hash student identifier for privacy
        student_hash = None
        if student_identifier:
            student_hash = hashlib.sha256(f"{student_identifier}_{assignment_id}".encode()).hexdigest()
        
        # Calculate metrics
        ai_scores = ai_results.get('scores', {})
        final_scores = final_results.get('scores', {})
        
        # Calculate AI acceptance rate
        total_criteria = len(ai_scores)
        unchanged_scores = sum(1 for k in ai_scores.keys() 
                             if ai_scores.get(k) == final_scores.get(k))
        acceptance_rate = unchanged_scores / total_criteria if total_criteria > 0 else 0
        
        total_score = sum(final_scores.values())
        max_score = len(final_scores) * 3
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO grading_sessions (
                    id, assignment_id, grader_id, student_identifier_hash, student_code,
                    code_metrics_json, ai_scores_json, ai_feedback_json,
                    final_scores_json, final_feedback_json, total_score, percentage,
                    status, ai_acceptance_rate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id, assignment_id, grader_id, student_hash, student_code,
                json.dumps(ai_results.get('metrics', {})),
                json.dumps(ai_scores),
                json.dumps(ai_results.get('feedback', {})),
                json.dumps(final_scores),
                json.dumps(final_results.get('feedback', {})),
                total_score, percentage, 'completed', acceptance_rate
            ))
            conn.commit()
        
        self.log_action(grader_id, None, 'grading_completed', 'grading_session', session_id)
        return session_id
    
    # Knowledge Base Management
    def add_knowledge_item(self, category: str, topic: str, content: str, 
                          created_by: int) -> int:
        """Add item to knowledge base"""
        
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO knowledge_base (category, topic, content, created_by)
                VALUES (?, ?, ?, ?)
            """, (category, topic, content, created_by))
            
            knowledge_id = cursor.lastrowid
            conn.commit()
        
        return knowledge_id
    
    def search_knowledge_base(self, topic: str = None, category: str = None) -> List[Dict[str, Any]]:
        """Search knowledge base for relevant content"""
        
        with self.get_connection() as conn:
            if topic and category:
                results = conn.execute("""
                    SELECT * FROM knowledge_base 
                    WHERE topic LIKE ? AND category = ? AND is_active = TRUE
                    ORDER BY usage_count DESC, effectiveness_rating DESC
                """, (f"%{topic}%", category)).fetchall()
            elif topic:
                results = conn.execute("""
                    SELECT * FROM knowledge_base 
                    WHERE topic LIKE ? AND is_active = TRUE
                    ORDER BY usage_count DESC, effectiveness_rating DESC
                """, (f"%{topic}%",)).fetchall()
            elif category:
                results = conn.execute("""
                    SELECT * FROM knowledge_base 
                    WHERE category = ? AND is_active = TRUE
                    ORDER BY usage_count DESC, effectiveness_rating DESC
                """, (category,)).fetchall()
            else:
                results = conn.execute("""
                    SELECT * FROM knowledge_base 
                    WHERE is_active = TRUE
                    ORDER BY usage_count DESC, effectiveness_rating DESC
                    LIMIT 50
                """).fetchall()
        
        return [dict(row) for row in results]
    
    def update_knowledge_usage(self, knowledge_id: int, effectiveness_rating: float = None):
        """Update knowledge base item usage statistics"""
        
        with self.get_connection() as conn:
            if effectiveness_rating is not None:
                conn.execute("""
                    UPDATE knowledge_base 
                    SET usage_count = usage_count + 1, 
                        last_used = CURRENT_TIMESTAMP,
                        effectiveness_rating = COALESCE(
                            (effectiveness_rating * 0.3 + ? * 0.7), ?
                        )
                    WHERE id = ?
                """, (effectiveness_rating, effectiveness_rating, knowledge_id))
            else:
                conn.execute("""
                    UPDATE knowledge_base 
                    SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (knowledge_id,))
            conn.commit()
    
    # Audit Logging
    def log_action(self, user_id: Optional[int], session_id: Optional[str], 
                  action: str, resource_type: str = None, resource_id: str = None,
                  details: Dict[str, Any] = None, ip_address: str = None, 
                  user_agent: str = None):
        """Log user action for audit trail"""
        
        details_json = json.dumps(details) if details else None
        
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO audit_log (user_id, session_id, action, resource_type, 
                                     resource_id, details_json, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, session_id, action, resource_type, resource_id, 
                  details_json, ip_address, user_agent))
            conn.commit()
    
    # Research Analytics
    def get_grading_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get grading analytics for research"""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with self.get_connection() as conn:
            # Basic metrics
            total_sessions = conn.execute("""
                SELECT COUNT(*) as count FROM grading_sessions 
                WHERE time_started > ?
            """, (cutoff_date,)).fetchone()['count']
            
            # AI acceptance rates
            avg_acceptance = conn.execute("""
                SELECT AVG(ai_acceptance_rate) as avg_rate FROM grading_sessions 
                WHERE time_started > ? AND ai_acceptance_rate IS NOT NULL
            """, (cutoff_date,)).fetchone()['avg_rate']
            
            # Grading efficiency
            avg_duration = conn.execute("""
                SELECT AVG(grading_duration_seconds) as avg_duration FROM grading_sessions 
                WHERE time_started > ? AND grading_duration_seconds IS NOT NULL
            """, (cutoff_date,)).fetchone()['avg_duration']
            
            # Score distributions
            score_dist = conn.execute("""
                SELECT percentage, COUNT(*) as count FROM grading_sessions 
                WHERE time_started > ? AND percentage IS NOT NULL
                GROUP BY ROUND(percentage/10)*10
                ORDER BY percentage
            """, (cutoff_date,)).fetchall()
        
        return {
            'total_sessions': total_sessions,
            'avg_ai_acceptance_rate': avg_acceptance or 0,
            'avg_grading_duration_minutes': (avg_duration or 0) / 60,
            'score_distribution': [dict(row) for row in score_dist],
            'period_days': days
        }
    
    def export_research_data(self, anonymize: bool = True) -> Dict[str, Any]:
        """Export data for research analysis"""
        
        with self.get_connection() as conn:
            # Get grading sessions
            sessions = conn.execute("""
                SELECT gs.*, a.name as assignment_name, a.course_code,
                       u.role as grader_role, u.department
                FROM grading_sessions gs
                JOIN assignments a ON gs.assignment_id = a.id
                JOIN users u ON gs.grader_id = u.id
                WHERE gs.research_consent = TRUE
            """).fetchall()
            
            sessions_data = []
            for session in sessions:
                session_dict = dict(session)
                
                if anonymize:
                    # Remove identifying information
                    session_dict.pop('student_identifier_hash', None)
                    session_dict['grader_id'] = f"grader_{hash(session_dict['grader_id']) % 1000}"
                
                sessions_data.append(session_dict)
        
        return {
            'export_timestamp': datetime.now().isoformat(),
            'total_sessions': len(sessions_data),
            'anonymized': anonymize,
            'sessions': sessions_data
        }


# Global database instance
db = DatabaseManager()
