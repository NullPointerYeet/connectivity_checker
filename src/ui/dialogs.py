from PyQt6.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QWidget, 
                            QInputDialog, QMessageBox, QDialog, QVBoxLayout, 
                            QLabel, QComboBox, QPushButton, QHBoxLayout, 
                            QCheckBox, QSpinBox, QDialogButtonBox, QGroupBox)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QDesktopServices
from PyQt6.QtCore import QTimer, Qt, QUrl
import sys
import ping3
import datetime
import csv
import os
import json
from icon import create_app_icon
from config_dialog import NotificationSettingsDialog, SplashScreen, MainWindow

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

class PresetServersDialog(QDialog):
    def __init__(self, current_server, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Server")
        self.setModal(True)
        layout = QVBoxLayout()

        # Predefined servers with descriptions
        self.servers = {
            "Google DNS (8.8.8.8)": "8.8.8.8",
            "Cloudflare DNS (1.1.1.1)": "1.1.1.1",
            "OpenDNS (208.67.222.222)": "208.67.222.222",
            "Quad9 DNS (9.9.9.9)": "9.9.9.9",
            "Custom...": "custom"
        }

        self.combo = QComboBox()
        for server in self.servers.keys():
            self.combo.addItem(server)
        
        # Set current selection
        for i, (name, ip) in enumerate(self.servers.items()):
            if ip == current_server:
                self.combo.setCurrentIndex(i)
                break

        layout.addWidget(QLabel("Select a server to monitor:"))
        layout.addWidget(self.combo)
        
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok)
        
        self.setLayout(layout)

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
