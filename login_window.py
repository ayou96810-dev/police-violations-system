"""
Login Window Module for Police Violations System
Provides PyQt6 GUI for user authentication with Arabic language support
Features:
    - Username/Password authentication
    - Password hashing using bcrypt
    - Arabic language support (RTL layout)
    - Input validation
    - Login attempt tracking
    - Remember me functionality
"""

import sys
import json
import hashlib
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Tuple

import bcrypt
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QMessageBox, QProgressBar, QApplication,
    QStyleFactory
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QFont, QColor, QPixmap, QPalette
from PyQt6.QtCore import QRect


class LoginWindow(QMainWindow):
    """
    Main login window class with PyQt6 interface supporting Arabic language.
    Handles user authentication with hashed password verification.
    
    Signals:
        login_successful: Emitted when user successfully logs in
        login_failed: Emitted when login attempt fails
    """
    
    # Signals
    login_successful = pyqtSignal(str)  # Emits username on successful login
    login_failed = pyqtSignal(str)  # Emits error message
    
    # Constants
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION = 15  # minutes
    CREDENTIALS_FILE = "credentials.json"
    SETTINGS_FILE = "user_settings.json"
    
    def __init__(self, parent=None, language: str = "ar"):
        """
        Initialize the login window.
        
        Args:
            parent: Parent widget
            language: Language code ('ar' for Arabic, 'en' for English)
        """
        super().__init__(parent)
        self.language = language
        self.login_attempts = 0
        self.locked_until = None
        self.failed_attempts_tracker = {}
        
        # Translations
        self.translations = {
            "ar": {
                "title": "نظام المخالفات المرورية - تسجيل الدخول",
                "username": "اسم المستخدم",
                "password": "كلمة المرور",
                "login": "تسجيل الدخول",
                "remember_me": "تذكرني",
                "forgot_password": "هل نسيت كلمة المرور؟",
                "login_success": "تم تسجيل الدخول بنجاح!",
                "login_failed": "فشل تسجيل الدخول. تحقق من بيانات المستخدم.",
                "invalid_input": "يرجى إدخال اسم المستخدم وكلمة المرور.",
                "account_locked": "تم قفل الحساب بسبب محاولات تسجيل دخول متعددة. يرجى المحاولة لاحقاً.",
                "attempt_exceeded": "تم تجاوز عدد محاولات تسجيل الدخول المسموح به.",
                "weak_password": "كلمة المرور ضعيفة. يجب أن تحتوي على 8 أحرف على الأقل.",
                "user_not_found": "المستخدم غير موجود.",
                "invalid_credentials": "بيانات المستخدم غير صحيحة.",
                "close": "إغلاق",
                "retry": "إعادة محاولة",
                "loading": "جاري التحميل...",
            },
            "en": {
                "title": "Police Violations System - Login",
                "username": "Username",
                "password": "Password",
                "login": "Login",
                "remember_me": "Remember me",
                "forgot_password": "Forgot password?",
                "login_success": "Login successful!",
                "login_failed": "Login failed. Check your credentials.",
                "invalid_input": "Please enter both username and password.",
                "account_locked": "Account locked due to multiple login attempts. Please try later.",
                "attempt_exceeded": "Maximum login attempts exceeded.",
                "weak_password": "Password is weak. It must contain at least 8 characters.",
                "user_not_found": "User not found.",
                "invalid_credentials": "Invalid credentials.",
                "close": "Close",
                "retry": "Retry",
                "loading": "Loading...",
            }
        }
        
        self.init_ui()
        self.load_user_settings()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(self.get_text("title"))
        self.setGeometry(100, 100, 500, 600)
        self.setStyleSheet(self.get_stylesheet())
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Set layout direction based on language
        if self.language == "ar":
            central_widget.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title_label = QLabel("شرطة المرور" if self.language == "ar" else "Police System")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Username section
        username_label = QLabel(self.get_text("username"))
        username_font = QFont()
        username_font.setPointSize(11)
        username_label.setFont(username_font)
        main_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText(
            "أدخل اسم المستخدم" if self.language == "ar" else "Enter username"
        )
        self.username_input.setMinimumHeight(40)
        self.username_input.setFont(username_font)
        self.username_input.textChanged.connect(self.on_input_change)
        main_layout.addWidget(self.username_input)
        
        # Password section
        password_label = QLabel(self.get_text("password"))
        password_label.setFont(username_font)
        main_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText(
            "أدخل كلمة المرور" if self.language == "ar" else "Enter password"
        )
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(40)
        self.password_input.setFont(username_font)
        self.password_input.returnPressed.connect(self.on_login_clicked)
        main_layout.addWidget(self.password_input)
        
        # Remember me checkbox
        self.remember_me_checkbox = QCheckBox(self.get_text("remember_me"))
        self.remember_me_checkbox.setFont(username_font)
        main_layout.addWidget(self.remember_me_checkbox)
        
        # Login button
        self.login_button = QPushButton(self.get_text("login"))
        self.login_button.setMinimumHeight(45)
        self.login_button.setFont(username_font)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.clicked.connect(self.on_login_clicked)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        main_layout.addWidget(self.login_button)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(20)
        main_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        main_layout.addWidget(self.status_label)
        
        # Add stretch to push everything to the top
        main_layout.addStretch()
        
        central_widget.setLayout(main_layout)
        
        # Timer for lockout countdown
        self.lockout_timer = QTimer()
        self.lockout_timer.timeout.connect(self.update_lockout_status)
        
    def get_text(self, key: str) -> str:
        """Get translated text."""
        return self.translations.get(self.language, self.translations["en"]).get(key, key)
    
    def get_stylesheet(self) -> str:
        """Return stylesheet for the application."""
        return """
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333333;
            }
            QLineEdit {
                border: 2px solid #cccccc;
                border-radius: 5px;
                padding: 8px;
                background-color: white;
                color: #333333;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
            QCheckBox {
                color: #333333;
                spacing: 5px;
            }
            QMessageBox {
                background-color: #f5f5f5;
            }
        """
    
    def on_input_change(self):
        """Clear status message when user types."""
        self.status_label.setText("")
    
    def on_login_clicked(self):
        """Handle login button click."""
        if self.is_account_locked():
            remaining = self.get_lockout_remaining_time()
            self.show_error(
                f"{self.get_text('account_locked')} ({remaining} {self.get_text('retry')})"
            )
            return
        
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            self.show_error(self.get_text("invalid_input"))
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.login_button.setEnabled(False)
        
        # Simulate authentication process
        self.authenticate_user(username, password)
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """
        Authenticate user credentials.
        
        Args:
            username: Username to authenticate
            password: Password to verify
            
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Load credentials
            credentials = self.load_credentials()
            
            if username not in credentials:
                self.record_failed_attempt(username)
                self.show_error(self.get_text("user_not_found"))
                return False
            
            # Verify password
            stored_hash = credentials[username]["password_hash"]
            if self.verify_password(password, stored_hash):
                self.progress_bar.setValue(100)
                self.show_success(self.get_text("login_success"))
                self.login_successful.emit(username)
                
                # Save user settings if remember me is checked
                if self.remember_me_checkbox.isChecked():
                    self.save_user_settings(username)
                
                # Clear login attempts
                self.failed_attempts_tracker.pop(username, None)
                self.save_failed_attempts()
                
                # Close window after short delay
                QTimer.singleShot(1500, self.close)
                return True
            else:
                self.record_failed_attempt(username)
                self.show_error(self.get_text("invalid_credentials"))
                return False
                
        except Exception as e:
            self.show_error(f"خطأ في المصادقة: {str(e)}")
            return False
        finally:
            self.progress_bar.setVisible(False)
            self.login_button.setEnabled(True)
    
    def record_failed_attempt(self, username: str):
        """
        Record a failed login attempt.
        
        Args:
            username: Username of failed attempt
        """
        if username not in self.failed_attempts_tracker:
            self.failed_attempts_tracker[username] = {
                "attempts": 0,
                "locked_until": None
            }
        
        self.failed_attempts_tracker[username]["attempts"] += 1
        
        if self.failed_attempts_tracker[username]["attempts"] >= self.MAX_LOGIN_ATTEMPTS:
            lockout_time = datetime.now() + timedelta(minutes=self.LOCKOUT_DURATION)
            self.failed_attempts_tracker[username]["locked_until"] = lockout_time.isoformat()
            self.status_label.setText(self.get_text("account_locked"))
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
        
        self.save_failed_attempts()
    
    def is_account_locked(self, username: str = None) -> bool:
        """
        Check if account is locked.
        
        Args:
            username: Username to check (uses current input if not provided)
            
        Returns:
            True if account is locked, False otherwise
        """
        if username is None:
            username = self.username_input.text().strip()
        
        if username not in self.failed_attempts_tracker:
            return False
        
        tracker = self.failed_attempts_tracker[username]
        if tracker.get("locked_until"):
            locked_until = datetime.fromisoformat(tracker["locked_until"])
            if datetime.now() < locked_until:
                return True
            else:
                # Lockout expired, reset
                self.failed_attempts_tracker[username] = {
                    "attempts": 0,
                    "locked_until": None
                }
                self.save_failed_attempts()
                return False
        
        return False
    
    def get_lockout_remaining_time(self, username: str = None) -> str:
        """Get remaining lockout time."""
        if username is None:
            username = self.username_input.text().strip()
        
        if username in self.failed_attempts_tracker:
            locked_until = self.failed_attempts_tracker[username].get("locked_until")
            if locked_until:
                locked_time = datetime.fromisoformat(locked_until)
                remaining = locked_time - datetime.now()
                minutes = int(remaining.total_seconds() / 60)
                return f"{minutes} min"
        
        return ""
    
    def update_lockout_status(self):
        """Update lockout status display."""
        username = self.username_input.text().strip()
        if self.is_account_locked(username):
            remaining = self.get_lockout_remaining_time(username)
            self.status_label.setText(f"تم قفل الحساب - {remaining} متبقي")
        else:
            self.lockout_timer.stop()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            password: Plain text password to verify
            password_hash: Hash to verify against
            
        Returns:
            True if password matches hash, False otherwise
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception:
            return False
    
    def load_credentials(self) -> dict:
        """
        Load credentials from file.
        
        Returns:
            Dictionary of credentials
        """
        credentials_path = Path(self.CREDENTIALS_FILE)
        
        if not credentials_path.exists():
            # Create default credentials for testing
            return self._create_default_credentials()
        
        try:
            with open(credentials_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading credentials: {e}")
            return self._create_default_credentials()
    
    def _create_default_credentials(self) -> dict:
        """Create default credentials for testing."""
        default_password = "password123"
        credentials = {
            "admin": {
                "password_hash": self.hash_password(default_password),
                "role": "admin",
                "created_at": datetime.now().isoformat()
            },
            "user": {
                "password_hash": self.hash_password(default_password),
                "role": "user",
                "created_at": datetime.now().isoformat()
            }
        }
        
        # Save default credentials
        self.save_credentials(credentials)
        return credentials
    
    def save_credentials(self, credentials: dict):
        """Save credentials to file."""
        try:
            with open(self.CREDENTIALS_FILE, 'w', encoding='utf-8') as f:
                json.dump(credentials, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving credentials: {e}")
    
    def load_failed_attempts(self):
        """Load failed attempts tracker from file."""
        attempts_file = Path("failed_attempts.json")
        
        if not attempts_file.exists():
            return
        
        try:
            with open(attempts_file, 'r', encoding='utf-8') as f:
                self.failed_attempts_tracker = json.load(f)
        except Exception as e:
            print(f"Error loading failed attempts: {e}")
    
    def save_failed_attempts(self):
        """Save failed attempts tracker to file."""
        try:
            with open("failed_attempts.json", 'w', encoding='utf-8') as f:
                json.dump(self.failed_attempts_tracker, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving failed attempts: {e}")
    
    def load_user_settings(self):
        """Load user settings from file."""
        settings_path = Path(self.SETTINGS_FILE)
        
        if not settings_path.exists():
            return
        
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                if settings.get("remember_me"):
                    self.username_input.setText(settings.get("username", ""))
                    self.remember_me_checkbox.setChecked(True)
        except Exception as e:
            print(f"Error loading user settings: {e}")
    
    def save_user_settings(self, username: str):
        """Save user settings to file."""
        settings = {
            "username": username,
            "remember_me": True,
            "last_login": datetime.now().isoformat()
        }
        
        try:
            with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving user settings: {e}")
    
    def show_error(self, message: str):
        """Display error message."""
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        
        if self.language == "ar":
            self.status_label.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    def show_success(self, message: str):
        """Display success message."""
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        
        if self.language == "ar":
            self.status_label.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    def closeEvent(self, event):
        """Handle window close event."""
        event.accept()


def main():
    """Main entry point for the login window."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle(QStyleFactory.create('Fusion'))
    
    # Create and show login window
    login_window = LoginWindow(language="ar")  # Use Arabic by default
    login_window.login_successful.connect(lambda username: print(f"User {username} logged in successfully"))
    login_window.login_failed.connect(lambda error: print(f"Login failed: {error}"))
    login_window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
