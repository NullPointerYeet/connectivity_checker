from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QCheckBox, 
                           QPushButton, QGroupBox, QSpinBox, QLabel, QHBoxLayout, 
                           QDialogButtonBox, QApplication, QMainWindow, QWidget,
                           QTextEdit, QSplitter, QSystemTrayIcon, QSystemTrayIcon)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
from src.ui.icons import create_app_icon
import json
import os

class MainWindow(QMainWindow):
    def __init__(self, monitor, settings, parent=None):
        super().__init__(parent)
        self.monitor = monitor
        self.settings = settings
        self.setWindowTitle("Network Monitor")
        self.setMinimumSize(800, 600)
        self.setWindowIcon(create_app_icon())
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        
        # Create a splitter for resizable sections
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Settings
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        
        # Notification Group
        notif_group = QGroupBox("Notifications")
        notif_layout = QVBoxLayout()
        
        self.cb_disconnect = QCheckBox("Notify on disconnect")
        self.cb_reconnect = QCheckBox("Notify on reconnect")
        self.cb_poor = QCheckBox("Notify on poor connection")
        
        # Threshold input
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Poor connection threshold (ms):"))
        self.threshold_input = QSpinBox()
        self.threshold_input.setRange(50, 1000)
        
        notif_layout.addWidget(self.cb_disconnect)
        notif_layout.addWidget(self.cb_reconnect)
        notif_layout.addWidget(self.cb_poor)
        notif_layout.addLayout(threshold_layout)
        notif_layout.addWidget(self.threshold_input)
        notif_group.setLayout(notif_layout)
        
        # Log Rotation Group
        log_group = QGroupBox("Log Rotation")
        log_layout = QVBoxLayout()
        
        self.cb_enable_rotation = QCheckBox("Enable log rotation")
        
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Maximum log size (MB):"))
        self.max_size_input = QSpinBox()
        self.max_size_input.setRange(1, 1000)
        size_layout.addWidget(self.max_size_input)
        
        backup_layout = QHBoxLayout()
        backup_layout.addWidget(QLabel("Number of backup files:"))
        self.backup_count_input = QSpinBox()
        self.backup_count_input.setRange(1, 10)
        backup_layout.addWidget(self.backup_count_input)
        
        log_layout.addWidget(self.cb_enable_rotation)
        log_layout.addLayout(size_layout)
        log_layout.addLayout(backup_layout)
        log_group.setLayout(log_layout)
        
        # Add groups to settings layout
        settings_layout.addWidget(notif_group)
        settings_layout.addWidget(log_group)
        settings_layout.addStretch()
        
        # Save button
        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self.save_settings)
        settings_layout.addWidget(save_button)
        
        # Right side - Connection Status
        status_widget = QWidget()
        status_layout = QVBoxLayout(status_widget)
        
        status_group = QGroupBox("Connection Status")
        status_inner_layout = QVBoxLayout()
        
        # Current status
        self.current_status_label = QLabel("Current Status: Unknown")
        self.current_ping_label = QLabel("Current Ping: N/A")
        
        # Connection log
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        
        status_inner_layout.addWidget(self.current_status_label)
        status_inner_layout.addWidget(self.current_ping_label)
        status_inner_layout.addWidget(QLabel("Connection Log:"))
        status_inner_layout.addWidget(self.log_text)
        
        status_group.setLayout(status_inner_layout)
        status_layout.addWidget(status_group)
        
        # Add widgets to splitter
        splitter.addWidget(settings_widget)
        splitter.addWidget(status_widget)
        
        # Set initial splitter sizes (40% settings, 60% status)
        splitter.setSizes([400, 600])
        
        main_layout.addWidget(splitter)
        self.setCentralWidget(central_widget)
        
        # Load current settings
        self.load_settings()

    def load_settings(self):
        notifications = self.settings.get('notifications', {})
        self.cb_disconnect.setChecked(notifications.get("notify_on_disconnect", True))
        self.cb_reconnect.setChecked(notifications.get("notify_on_reconnect", True))
        self.cb_poor.setChecked(notifications.get("notify_on_poor_connection", True))
        self.threshold_input.setValue(notifications.get("poor_connection_threshold", 200))
        
        log_settings = self.settings.get("log_rotation", {
            "enabled": False,
            "max_size_mb": 10,
            "backup_count": 3
        })
        self.cb_enable_rotation.setChecked(log_settings["enabled"])
        self.max_size_input.setValue(log_settings["max_size_mb"])
        self.backup_count_input.setValue(log_settings["backup_count"])

    def save_settings(self):
        self.settings['notifications'] = {
            "notify_on_disconnect": self.cb_disconnect.isChecked(),
            "notify_on_reconnect": self.cb_reconnect.isChecked(),
            "notify_on_poor_connection": self.cb_poor.isChecked(),
            "poor_connection_threshold": self.threshold_input.value(),
        }
        self.settings['log_rotation'] = {
            "enabled": self.cb_enable_rotation.isChecked(),
            "max_size_mb": self.max_size_input.value(),
            "backup_count": self.backup_count_input.value()
        }
        # If you need to persist the settings, you might want to call a method on the monitor
        if self.monitor:
            self.monitor.save_settings(self.settings)

    def update_status(self, result):
        """Update the connection status display"""
        status = result.status
        ping = result.ping_time if result.is_connected else "N/A"
        
        self.current_status_label.setText(f"Current Status: {status}")
        self.current_ping_label.setText(f"Current Ping: {ping}")
        
        # Add to log with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] Status: {status}, Ping: {ping}"
        self.log_text.append(log_entry)

    def closeEvent(self, event):
        """Hide window instead of closing it"""
        event.ignore()
        self.hide()

    def changeEvent(self, event):
        if event.type() == event.Type.WindowStateChange:  # Use event.Type.WindowStateChange
            if self.isMinimized():  # Simpler way to check if window is minimized
                # Hide the window and show notification
                self.hide()
                self.monitor.system_tray.showMessage(
                    "Network Monitor",
                    "Application is still running in the system tray",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )