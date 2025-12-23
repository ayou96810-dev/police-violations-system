#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Police Violations System - Main Application Entry Point

A desktop application for managing police violations using PyQt6 with
offline functionality, database persistence, and Arabic language support.

Author: Police Violations System Team
Date: 2025-12-23
Version: 1.0.0
"""

import sys
import os
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from PyQt6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt6.QtCore import Qt, QTimer, QThread
from PyQt6.QtGui import QPixmap, QFont

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('police_violations_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DatabaseInitializer(QThread):
    """Worker thread for database initialization to prevent UI blocking."""
    
    def __init__(self):
        super().__init__()
        self.error: Optional[Exception] = None
        self.success = False
    
    def run(self):
        """Initialize database in background thread."""
        try:
            logger.info("Starting database initialization...")
            # Import database module
            from src.database.db_manager import DatabaseManager
            
            # Initialize database
            db_manager = DatabaseManager()
            db_manager.initialize_database()
            
            logger.info("Database initialization completed successfully")
            self.success = True
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}", exc_info=True)
            self.error = e
            self.success = False


class PoliceViolationsApp:
    """Main application controller for Police Violations System."""
    
    def __init__(self):
        """Initialize the application."""
        self.app: Optional[QApplication] = None
        self.login_window = None
        self.main_window = None
        self.db_initializer: Optional[DatabaseInitializer] = None
        self.is_offline = False
        
    def setup_application(self) -> bool:
        """
        Setup QApplication and initial configurations.
        
        Returns:
            bool: True if setup successful, False otherwise
        """
        try:
            # Create QApplication instance
            self.app = QApplication(sys.argv)
            
            # Set application properties
            self.app.setApplicationName("نظام إدارة مخالفات المرور")  # Arabic name
            self.app.setApplicationVersion("1.0.0")
            self.app.setApplicationDisplayName("Police Violations Management System")
            
            # Configure application style
            self._setup_application_style()
            
            logger.info("QApplication setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup QApplication: {str(e)}", exc_info=True)
            return False
    
    def _setup_application_style(self):
        """Configure application style, theme, and fonts."""
        try:
            # Set application style
            self.app.setStyle('Fusion')
            
            # Setup Arabic font support
            font = QFont()
            font.setFamily("Arial")  # Fallback for Arabic
            self.app.setFont(font)
            
            # Optional: Apply stylesheet for consistent UI
            self._load_stylesheet()
            
        except Exception as e:
            logger.warning(f"Failed to apply application style: {str(e)}")
    
    def _load_stylesheet(self):
        """Load application stylesheet if available."""
        try:
            stylesheet_path = Path("resources/styles/application.qss")
            if stylesheet_path.exists():
                with open(stylesheet_path, 'r', encoding='utf-8') as f:
                    stylesheet = f.read()
                    self.app.setStyleSheet(stylesheet)
                logger.info("Application stylesheet loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load stylesheet: {str(e)}")
    
    def show_splash_screen(self) -> QSplashScreen:
        """
        Display splash screen during initialization.
        
        Returns:
            QSplashScreen: The splash screen instance
        """
        try:
            splash_pixmap = QPixmap(600, 400)
            splash_pixmap.fill(Qt.GlobalColor.white)
            
            splash = QSplashScreen(splash_pixmap)
            splash.show()
            splash.showMessage(
                "تحميل التطبيق...",  # Arabic: "Loading application..."
                Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
                Qt.GlobalColor.black
            )
            
            self.app.processEvents()
            return splash
            
        except Exception as e:
            logger.warning(f"Failed to display splash screen: {str(e)}")
            return None
    
    def initialize_database(self, splash: Optional[QSplashScreen] = None) -> bool:
        """
        Initialize the application database.
        
        Args:
            splash: Optional splash screen to update during initialization
            
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            if splash:
                splash.showMessage(
                    "جاري تهيئة قاعدة البيانات...",  # Arabic: "Initializing database..."
                    Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
                    Qt.GlobalColor.black
                )
                self.app.processEvents()
            
            # Start database initialization in background thread
            self.db_initializer = DatabaseInitializer()
            self.db_initializer.start()
            
            # Wait for initialization with timeout
            self.db_initializer.wait(timeout=30000)  # 30 second timeout
            
            if not self.db_initializer.success:
                error_msg = str(self.db_initializer.error) if self.db_initializer.error else "Unknown error"
                logger.error(f"Database initialization failed: {error_msg}")
                self.is_offline = True
                return False
            
            logger.info("Database initialization successful")
            return True
            
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}", exc_info=True)
            self.is_offline = True
            return False
    
    def show_login_window(self, splash: Optional[QSplashScreen] = None) -> bool:
        """
        Display login window and handle authentication.
        
        Args:
            splash: Optional splash screen to close
            
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            if splash:
                splash.showMessage(
                    "جاري عرض نافذة تسجيل الدخول...",  # Arabic: "Displaying login window..."
                    Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
                    Qt.GlobalColor.black
                )
                self.app.processEvents()
            
            from src.gui.login_window import LoginWindow
            
            self.login_window = LoginWindow(is_offline=self.is_offline)
            
            if splash:
                splash.finish(self.login_window)
            
            # Show login window and wait for authentication
            self.login_window.show()
            
            # Process events to ensure window is displayed
            self.app.processEvents()
            
            logger.info("Login window displayed successfully")
            return True
            
        except ImportError as e:
            logger.error(f"Failed to import LoginWindow: {str(e)}", exc_info=True)
            self._show_error_dialog(
                "خطأ في التحميل",
                "فشل تحميل واجهة تسجيل الدخول"
            )
            return False
        except Exception as e:
            logger.error(f"Failed to display login window: {str(e)}", exc_info=True)
            self._show_error_dialog(
                "خطأ في الواجهة",
                f"حدث خطأ عند عرض نافذة تسجيل الدخول: {str(e)}"
            )
            return False
    
    def show_main_window(self) -> bool:
        """
        Display main application window after successful authentication.
        
        Returns:
            bool: True if main window displayed successfully, False otherwise
        """
        try:
            from src.gui.main_window import MainWindow
            
            # Get authenticated user info from login window
            user_info = None
            if self.login_window and hasattr(self.login_window, 'get_user_info'):
                user_info = self.login_window.get_user_info()
            
            # Create and show main window
            self.main_window = MainWindow(
                user_info=user_info,
                is_offline=self.is_offline
            )
            self.main_window.show()
            
            # Close login window if still open
            if self.login_window:
                self.login_window.close()
            
            logger.info("Main window displayed successfully")
            return True
            
        except ImportError as e:
            logger.error(f"Failed to import MainWindow: {str(e)}", exc_info=True)
            self._show_error_dialog(
                "خطأ في التحميل",
                "فشل تحميل الواجهة الرئيسية"
            )
            return False
        except Exception as e:
            logger.error(f"Failed to display main window: {str(e)}", exc_info=True)
            self._show_error_dialog(
                "خطأ في الواجهة",
                f"حدث خطأ عند عرض الواجهة الرئيسية: {str(e)}"
            )
            return False
    
    def _show_error_dialog(self, title: str, message: str):
        """
        Display error dialog to user.
        
        Args:
            title: Dialog title
            message: Error message
        """
        try:
            QMessageBox.critical(None, title, message)
        except Exception as e:
            logger.error(f"Failed to display error dialog: {str(e)}")
            print(f"ERROR: {title} - {message}")
    
    def _show_info_dialog(self, title: str, message: str):
        """
        Display info dialog to user.
        
        Args:
            title: Dialog title
            message: Info message
        """
        try:
            QMessageBox.information(None, title, message)
        except Exception as e:
            logger.error(f"Failed to display info dialog: {str(e)}")
            print(f"INFO: {title} - {message}")
    
    def handle_database_error(self):
        """Handle database initialization errors gracefully."""
        logger.warning("Operating in offline mode due to database initialization failure")
        
        self._show_info_dialog(
            "وضع بدون اتصال",  # Arabic: "Offline Mode"
            "فشلت قاعدة البيانات. سيتم تشغيل التطبيق في وضع بدون اتصال.\n"  # Arabic: Failed database, offline mode
            "قد تكون بعض الميزات غير متاحة."  # Arabic: Some features may be unavailable
        )
    
    def run(self) -> int:
        """
        Run the application main loop.
        
        Returns:
            int: Application exit code
        """
        try:
            logger.info("="*60)
            logger.info("Starting Police Violations Management System")
            logger.info(f"Timestamp: {datetime.now().isoformat()}")
            logger.info("="*60)
            
            # Step 1: Setup application
            if not self.setup_application():
                self._show_error_dialog(
                    "خطأ في بدء التطبيق",
                    "فشل إنشاء تطبيق PyQt6"
                )
                logger.critical("Application setup failed")
                return 1
            
            # Step 2: Show splash screen
            splash = self.show_splash_screen()
            
            # Step 3: Initialize database
            db_initialized = self.initialize_database(splash)
            if not db_initialized:
                self.handle_database_error()
            
            # Step 4: Show login window
            if not self.show_login_window(splash):
                logger.critical("Login window failed to display")
                return 1
            
            # Step 5: Handle login signal and show main window
            if hasattr(self.login_window, 'login_successful'):
                self.login_window.login_successful.connect(self.show_main_window)
            
            # Step 6: Handle logout signal
            def handle_logout():
                """Handle user logout."""
                logger.info("User logged out")
                self.show_login_window()
            
            if self.main_window and hasattr(self.main_window, 'logout_requested'):
                self.main_window.logout_requested.connect(handle_logout)
            
            logger.info("Application startup completed successfully")
            logger.info("Entering application main loop")
            
            # Run application
            return self.app.exec()
            
        except Exception as e:
            logger.critical(f"Unhandled exception in application: {str(e)}", exc_info=True)
            self._show_error_dialog(
                "خطأ حرج",
                f"حدث خطأ غير متوقع: {str(e)}"
            )
            return 1


def main() -> int:
    """
    Main entry point for the Police Violations System application.
    
    Returns:
        int: Application exit code (0 for success, 1 for failure)
    """
    try:
        # Create application instance
        app = PoliceViolationsApp()
        
        # Run application
        exit_code = app.run()
        
        logger.info(f"Application exited with code: {exit_code}")
        return exit_code
        
    except Exception as e:
        logger.critical(f"Fatal error in main: {str(e)}", exc_info=True)
        print(f"FATAL ERROR: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
