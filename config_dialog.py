from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QCheckBox, 
                           QPushButton, QGroupBox, QSpinBox, QLabel, QHBoxLayout, 
                           QDialogButtonBox, QApplication, QMainWindow, QWidget,
                           QTextEdit, QSplitter)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
import json
import os

class NotificationSettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Notification Settings")
        self.setModal(True)
        layout = QVBoxLayout()
        
        # Notifications Group
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
        
        # Load current settings
        self.cb_disconnect.setChecked(settings["notify_on_disconnect"])
        self.cb_reconnect.setChecked(settings["notify_on_reconnect"])
        self.cb_poor.setChecked(settings["notify_on_poor_connection"])
        self.threshold_input.setValue(settings["poor_connection_threshold"])
        
        # Load log rotation settings
        log_settings = settings.get("log_rotation", {
            "enabled": False,
            "max_size_mb": 10,
            "backup_count": 3
        })
        self.cb_enable_rotation.setChecked(log_settings["enabled"])
        self.max_size_input.setValue(log_settings["max_size_mb"])
        self.backup_count_input.setValue(log_settings["backup_count"])
        
        # Add groups to main layout
        layout.addWidget(notif_group)
        layout.addWidget(log_group)
        
        # Add OK/Cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_settings(self):
        return {
            "notify_on_disconnect": self.cb_disconnect.isChecked(),
            "notify_on_reconnect": self.cb_reconnect.isChecked(),
            "notify_on_poor_connection": self.cb_poor.isChecked(),
            "poor_connection_threshold": self.threshold_input.value(),
            "log_rotation": {
                "enabled": self.cb_enable_rotation.isChecked(),
                "max_size_mb": self.max_size_input.value(),
                "backup_count": self.backup_count_input.value()
            }
        }

class MainWindow(QMainWindow):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Network Monitor")
        self.setMinimumSize(800, 600)
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
        self.cb_disconnect.setChecked(self.settings["notify_on_disconnect"])
        self.cb_reconnect.setChecked(self.settings["notify_on_reconnect"])
        self.cb_poor.setChecked(self.settings["notify_on_poor_connection"])
        self.threshold_input.setValue(self.settings["poor_connection_threshold"])
        
        log_settings = self.settings.get("log_rotation", {
            "enabled": False,
            "max_size_mb": 10,
            "backup_count": 3
        })
        self.cb_enable_rotation.setChecked(log_settings["enabled"])
        self.max_size_input.setValue(log_settings["max_size_mb"])
        self.backup_count_input.setValue(log_settings["backup_count"])

    def save_settings(self):
        self.settings.update({
            "notify_on_disconnect": self.cb_disconnect.isChecked(),
            "notify_on_reconnect": self.cb_reconnect.isChecked(),
            "notify_on_poor_connection": self.cb_poor.isChecked(),
            "poor_connection_threshold": self.threshold_input.value(),
            "log_rotation": {
                "enabled": self.cb_enable_rotation.isChecked(),
                "max_size_mb": self.max_size_input.value(),
                "backup_count": self.backup_count_input.value()
            }
        })

    def update_connection_status(self, status, ping):
        """Update the connection status display"""
        self.current_status_label.setText(f"Current Status: {status}")
        self.current_ping_label.setText(f"Current Ping: {ping}ms")
        
        # Add to log with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.append(f"[{timestamp}] Status: {status}, Ping: {ping}ms")

class SplashScreen(QDialog):
    def __init__(self, version):
        super().__init__()
        self.setWindowTitle("Network Monitor")
        self.setFixedSize(400, 300)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        
        layout = QVBoxLayout()
        
        # App name and version
        title = QLabel("Network Monitor")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        version_label = QLabel(f"Version {version}")
        version_label.setStyleSheet("font-size: 14px;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Loading text
        loading = QLabel("Initializing...")
        loading.setStyleSheet("font-size: 12px; color: #666;")
        loading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(version_label)
        layout.addWidget(loading)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Center on screen
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
        
        # Auto close after 2 seconds
        QTimer.singleShot(2000, self.close)