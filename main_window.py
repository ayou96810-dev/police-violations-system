"""
Main Application Window for Police Violations System

This module provides the main application window with tabbed interface for managing:
- Violations
- Seizures
- Infractions
- Statistics

Author: ayou96810-dev
Date: 2025-12-23
"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QPushButton, QStatusBar, QLabel, QMenuBar, QMenu
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction

from tabs.violations_tab import ViolationsTab
from tabs.seizures_tab import SeizuresTab
from tabs.infractions_tab import InfractionsTab
from tabs.statistics_tab import StatisticsTab


class MainWindow(QMainWindow):
    """Main application window with tabbed interface for police violations system."""
    
    def __init__(self):
        """Initialize the main application window."""
        super().__init__()
        self.setWindowTitle("Police Violations System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set window icon (if available)
        try:
            self.setWindowIcon(QIcon("assets/icon.png"))
        except Exception:
            pass  # Icon file not required
        
        # Initialize tabs
        self.tabs = {}
        self.init_ui()
        self.setup_menu_bar()
        self.setup_status_bar()
        
    def init_ui(self):
        """Initialize the user interface with tabs and layout."""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setMovable(False)
        
        # Create and add tabs
        self.create_tabs()
        
        # Add tab widget to layout
        main_layout.addWidget(self.tab_widget)
        
        # Create bottom control panel
        control_panel = self.create_control_panel()
        main_layout.addLayout(control_panel)
        
        # Set layout
        central_widget.setLayout(main_layout)
        
    def create_tabs(self):
        """Create and add all application tabs."""
        try:
            # Violations Tab
            self.tabs['violations'] = ViolationsTab()
            self.tab_widget.addTab(self.tabs['violations'], "Violations")
            
            # Seizures Tab
            self.tabs['seizures'] = SeizuresTab()
            self.tab_widget.addTab(self.tabs['seizures'], "Seizures")
            
            # Infractions Tab
            self.tabs['infractions'] = InfractionsTab()
            self.tab_widget.addTab(self.tabs['infractions'], "Infractions")
            
            # Statistics Tab
            self.tabs['statistics'] = StatisticsTab()
            self.tab_widget.addTab(self.tabs['statistics'], "Statistics")
            
        except ImportError as e:
            print(f"Warning: Could not import tab modules: {e}")
            # Create placeholder tabs if modules are not available
            self.create_placeholder_tabs()
    
    def create_placeholder_tabs(self):
        """Create placeholder tabs if modules are unavailable."""
        from PyQt6.QtWidgets import QTextEdit
        
        tab_names = ["Violations", "Seizures", "Infractions", "Statistics"]
        for tab_name in tab_names:
            placeholder = QTextEdit()
            placeholder.setReadOnly(True)
            placeholder.setText(f"{tab_name} Tab\n\nThis tab will contain {tab_name.lower()} management features.")
            self.tab_widget.addTab(placeholder, tab_name)
    
    def create_control_panel(self) -> QHBoxLayout:
        """Create the bottom control panel with buttons and information.
        
        Returns:
            QHBoxLayout: Layout containing control panel widgets
        """
        control_layout = QHBoxLayout()
        
        # Info label
        self.info_label = QLabel("Ready")
        self.info_label.setStyleSheet("font-weight: bold; color: #333;")
        control_layout.addWidget(self.info_label)
        
        # Stretch to push buttons to the right
        control_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedWidth(100)
        refresh_btn.clicked.connect(self.refresh_current_tab)
        control_layout.addWidget(refresh_btn)
        
        # Export button
        export_btn = QPushButton("Export")
        export_btn.setFixedWidth(100)
        export_btn.clicked.connect(self.export_data)
        control_layout.addWidget(export_btn)
        
        # Settings button
        settings_btn = QPushButton("Settings")
        settings_btn.setFixedWidth(100)
        settings_btn.clicked.connect(self.open_settings)
        control_layout.addWidget(settings_btn)
        
        # Exit button
        exit_btn = QPushButton("Exit")
        exit_btn.setFixedWidth(100)
        exit_btn.clicked.connect(self.close)
        exit_btn.setStyleSheet("background-color: #ff6b6b; color: white;")
        control_layout.addWidget(exit_btn)
        
        return control_layout
    
    def setup_menu_bar(self):
        """Set up the application menu bar."""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit Menu
        edit_menu = menubar.addMenu("Edit")
        
        refresh_action = QAction("Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_current_tab)
        edit_menu.addAction(refresh_action)
        
        edit_menu.addSeparator()
        
        settings_action = QAction("Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.open_settings)
        edit_menu.addAction(settings_action)
        
        # View Menu
        view_menu = menubar.addMenu("View")
        
        fullscreen_action = QAction("Fullscreen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # Help Menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        documentation_action = QAction("Documentation", self)
        documentation_action.setShortcut("F1")
        documentation_action.triggered.connect(self.show_documentation)
        help_menu.addAction(documentation_action)
    
    def setup_status_bar(self):
        """Set up the status bar at the bottom of the window."""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Application started successfully")
    
    def refresh_current_tab(self):
        """Refresh the data in the currently active tab."""
        current_tab = self.tab_widget.currentWidget()
        
        if hasattr(current_tab, 'refresh'):
            current_tab.refresh()
            self.update_status("Tab refreshed successfully")
        else:
            self.update_status("Current tab does not support refresh")
    
    def export_data(self):
        """Export data from the current tab."""
        current_tab = self.tab_widget.currentWidget()
        
        if hasattr(current_tab, 'export'):
            current_tab.export()
            self.update_status("Data exported successfully")
        else:
            self.update_status("Current tab does not support export")
    
    def new_file(self):
        """Create a new file (placeholder)."""
        self.update_status("New file action triggered")
    
    def open_file(self):
        """Open a file (placeholder)."""
        self.update_status("Open file action triggered")
    
    def save_file(self):
        """Save current file (placeholder)."""
        self.update_status("File saved successfully")
    
    def open_settings(self):
        """Open application settings."""
        self.update_status("Settings dialog opened")
        # TODO: Implement settings dialog
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()
            self.update_status("Exited fullscreen mode")
        else:
            self.showFullScreen()
            self.update_status("Entered fullscreen mode")
    
    def show_about(self):
        """Show about dialog."""
        self.update_status("About dialog opened")
        # TODO: Implement about dialog
    
    def show_documentation(self):
        """Show documentation."""
        self.update_status("Documentation opened")
        # TODO: Implement documentation viewer
    
    def update_status(self, message: str):
        """Update the status bar message.
        
        Args:
            message (str): Status message to display
        """
        self.status_bar.showMessage(message)
    
    def closeEvent(self, event):
        """Handle application close event.
        
        Args:
            event: Close event
        """
        # TODO: Add confirmation dialog if needed
        event.accept()


def main():
    """Main entry point for the application."""
    app = None
    try:
        from PyQt6.QtWidgets import QApplication
        
        # Create application
        app = QApplication(sys.argv)
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        # Run application
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"Error: Required PyQt6 library not found: {e}")
        print("Please install it using: pip install PyQt6")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        if app:
            sys.exit(app.exec())
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
