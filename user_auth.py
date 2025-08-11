# User authentication and database models
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import sqlite3
import secrets
import os
import hashlib

class UserDatabase:
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize the user database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                date_of_birth DATE,
                gender TEXT,
                age INTEGER,
                password_hash TEXT NOT NULL,
                is_verified BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                newsletter_subscribed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                profile_picture TEXT,
                dosha_type TEXT,
                health_goals TEXT
            )
        """)
        
        # User sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_agent TEXT,
                ip_address TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Chat history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                message_type TEXT DEFAULT 'health_query',
                symptoms_detected TEXT,
                remedies_suggested TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Health profiles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                height REAL,
                weight REAL,
                blood_type TEXT,
                allergies TEXT,
                chronic_conditions TEXT,
                current_medications TEXT,
                emergency_contact_name TEXT,
                emergency_contact_phone TEXT,
                doctor_name TEXT,
                doctor_contact TEXT,
                insurance_info TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Email verification tokens table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS verification_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                token_type TEXT NOT NULL,  -- 'email_verification', 'password_reset'
                expires_at TIMESTAMP NOT NULL,
                used BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        conn.commit()
        conn.close()

    def create_user(self, user_data):
        """Create a new user account"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (user_data['email'],))
            if cursor.fetchone():
                return {"success": False, "message": "Email address is already registered"}
            
            # Hash password
            password_hash = generate_password_hash(user_data['password'])
            
            # Insert new user
            cursor.execute("""
                INSERT INTO users (
                    first_name, last_name, email, phone, date_of_birth, gender, age,
                    password_hash, newsletter_subscribed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_data['firstName'],
                user_data['lastName'],
                user_data['email'],
                user_data.get('phone', ''),
                user_data['dateOfBirth'],
                user_data['gender'],
                user_data['age'],
                password_hash,
                user_data.get('newsletter', False)
            ))
            
            user_id = cursor.lastrowid
            
            # Create empty health profile
            cursor.execute("""
                INSERT INTO health_profiles (user_id) VALUES (?)
            """, (user_id,))
            
            conn.commit()
            conn.close()
            
            # Generate verification token
            self.generate_verification_token(user_id, 'email_verification')
            
            return {"success": True, "user_id": user_id, "message": "Account created successfully"}
            
        except Exception as e:
            print(f"Error creating user: {e}")
            return {"success": False, "message": "Failed to create account"}

    def authenticate_user(self, email, password):
        """Authenticate user login"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, first_name, last_name, email, password_hash, is_verified, is_active
                FROM users WHERE email = ?
            """, (email,))
            
            user = cursor.fetchone()
            
            if not user:
                return {"success": False, "message": "Invalid email or password"}
            
            user_id, first_name, last_name, user_email, password_hash, is_verified, is_active = user
            
            if not is_active:
                return {"success": False, "message": "Account is deactivated"}
            
            if not check_password_hash(password_hash, password):
                return {"success": False, "message": "Invalid email or password"}
            
            # Update last login
            cursor.execute("""
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            """, (user_id,))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "user": {
                    "id": user_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": user_email,
                    "is_verified": is_verified
                }
            }
            
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return {"success": False, "message": "Authentication failed"}

    def create_session(self, user_id, user_agent=None, ip_address=None, remember_me=False):
        """Create a new user session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Generate session token
            session_token = secrets.token_urlsafe(32)
            
            # Set expiration time
            if remember_me:
                expires_at = datetime.now() + timedelta(days=30)  # 30 days
            else:
                expires_at = datetime.now() + timedelta(days=7)   # 7 days
            
            # Clean up old sessions for this user (optional)
            cursor.execute("DELETE FROM user_sessions WHERE user_id = ? AND expires_at < CURRENT_TIMESTAMP", (user_id,))
            
            # Insert new session
            cursor.execute("""
                INSERT INTO user_sessions (user_id, session_token, expires_at, user_agent, ip_address)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, session_token, expires_at, user_agent, ip_address))
            
            conn.commit()
            conn.close()
            
            return {"success": True, "session_token": session_token, "expires_at": expires_at}
            
        except Exception as e:
            print(f"Error creating session: {e}")
            return {"success": False, "message": "Failed to create session"}

    def validate_session(self, session_token):
        """Validate a user session token"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.user_id, u.first_name, u.last_name, u.email, u.is_verified, u.is_active
                FROM user_sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token = ? AND s.expires_at > CURRENT_TIMESTAMP
            """, (session_token,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                user_id, first_name, last_name, email, is_verified, is_active = result
                
                if not is_active:
                    return {"success": False, "message": "Account is deactivated"}
                
                return {
                    "success": True,
                    "user": {
                        "id": user_id,
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "is_verified": is_verified
                    }
                }
            else:
                return {"success": False, "message": "Invalid or expired session"}
                
        except Exception as e:
            print(f"Error validating session: {e}")
            return {"success": False, "message": "Session validation failed"}

    def logout_session(self, session_token):
        """Logout a user session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM user_sessions WHERE session_token = ?", (session_token,))
            
            conn.commit()
            conn.close()
            
            return {"success": True}
            
        except Exception as e:
            print(f"Error logging out session: {e}")
            return {"success": False}

    def save_chat_message(self, user_id, message, response, message_type="health_query", symptoms=None, remedies=None):
        """Save chat message to history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO chat_history (user_id, message, response, message_type, symptoms_detected, remedies_suggested)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, message, response, message_type, symptoms, remedies))
            
            conn.commit()
            conn.close()
            
            return {"success": True}
            
        except Exception as e:
            print(f"Error saving chat message: {e}")
            return {"success": False}

    def get_chat_history(self, user_id, limit=50):
        """Get user's chat history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT message, response, message_type, symptoms_detected, remedies_suggested, created_at
                FROM chat_history
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    "message": row[0],
                    "response": row[1],
                    "message_type": row[2],
                    "symptoms_detected": row[3],
                    "remedies_suggested": row[4],
                    "created_at": row[5]
                })
            
            conn.close()
            return {"success": True, "history": history}
            
        except Exception as e:
            print(f"Error getting chat history: {e}")
            return {"success": False, "history": []}

    def generate_verification_token(self, user_id, token_type, expires_hours=24):
        """Generate verification token for email verification or password reset"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Generate secure token
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=expires_hours)
            
            # Delete old tokens of the same type for this user
            cursor.execute("""
                DELETE FROM verification_tokens 
                WHERE user_id = ? AND token_type = ?
            """, (user_id, token_type))
            
            # Insert new token
            cursor.execute("""
                INSERT INTO verification_tokens (user_id, token, token_type, expires_at)
                VALUES (?, ?, ?, ?)
            """, (user_id, token, token_type, expires_at))
            
            conn.commit()
            conn.close()
            
            return {"success": True, "token": token}
            
        except Exception as e:
            print(f"Error generating verification token: {e}")
            return {"success": False}

    def get_user_profile(self, user_id):
        """Get complete user profile"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get user basic info
            cursor.execute("""
                SELECT first_name, last_name, email, phone, date_of_birth, gender, age,
                       is_verified, newsletter_subscribed, created_at, last_login, dosha_type
                FROM users WHERE id = ?
            """, (user_id,))
            
            user_info = cursor.fetchone()
            if not user_info:
                return {"success": False, "message": "User not found"}
            
            # Get health profile
            cursor.execute("""
                SELECT height, weight, blood_type, allergies, chronic_conditions,
                       current_medications, emergency_contact_name, emergency_contact_phone,
                       doctor_name, doctor_contact, insurance_info
                FROM health_profiles WHERE user_id = ?
            """, (user_id,))
            
            health_info = cursor.fetchone()
            
            conn.close()
            
            profile = {
                "user_id": user_id,
                "first_name": user_info[0],
                "last_name": user_info[1],
                "email": user_info[2],
                "phone": user_info[3] or "",
                "date_of_birth": user_info[4],
                "gender": user_info[5],
                "age": user_info[6],
                "is_verified": user_info[7],
                "newsletter_subscribed": user_info[8],
                "created_at": user_info[9],
                "last_login": user_info[10],
                "dosha_type": user_info[11] or "",
                "health_profile": {
                    "height": health_info[0] if health_info else None,
                    "weight": health_info[1] if health_info else None,
                    "blood_type": health_info[2] if health_info else "",
                    "allergies": health_info[3] if health_info else "",
                    "chronic_conditions": health_info[4] if health_info else "",
                    "current_medications": health_info[5] if health_info else "",
                    "emergency_contact_name": health_info[6] if health_info else "",
                    "emergency_contact_phone": health_info[7] if health_info else "",
                    "doctor_name": health_info[8] if health_info else "",
                    "doctor_contact": health_info[9] if health_info else "",
                    "insurance_info": health_info[10] if health_info else "",
                } if health_info else {}
            }
            
            return {"success": True, "profile": profile}
            
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return {"success": False, "message": "Failed to get user profile"}

# Global user database instance
user_db = UserDatabase()
